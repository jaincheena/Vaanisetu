"""
VaaniSetu — 7-Stage Job Processor
Orchestrates: queued → validating → extracting → transcribing →
              translating → generating → packaging
"""

import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config import LANG_CODES, ALLOWED_EXTENSIONS, ENGLISH_CODE
from backend.pipeline.transcriber import _whisper_to_display
from backend.database import get_db
from backend.utils.file_utils import sha256_file, job_workspace, job_zip_path
from backend.utils.sse import sse_manager, publish_threadsafe
from backend.services.confidence import confidence_level, avg_confidence

logger = logging.getLogger("vaanisetu.processor")


def _now() -> str:
    return datetime.utcnow().isoformat()


def _publish(job_id: str, stage: str, msg: str, extra: dict | None = None) -> None:
    """
    Threadsafe SSE publish — called from thread-pool executor.
    """
    publish_threadsafe(job_id, stage, msg, extra)


def _update_job(job_id: str, **kwargs) -> None:
    with get_db() as conn:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [job_id]
        conn.execute(f"UPDATE jobs SET {sets} WHERE id=?", vals)


CANCELLED_JOBS: set[str] = set()


class JobCancelledError(Exception):
    """Raised when a job is cancelled by the user."""
    pass


def request_cancellation(job_id: str) -> bool:
    """Flag a job as cancelled both in-memory and in SQLite database."""
    CANCELLED_JOBS.add(job_id)
    _update_job(job_id, status="cancelled", error_log="Cancelled by user", completed_at=_now())
    _publish(job_id, "failed", "Job cancelled by user")
    logger.info(f"Cancellation requested for job {job_id}")
    return True


def is_cancelled(job_id: str) -> bool:
    if job_id in CANCELLED_JOBS:
        return True
    try:
        with get_db() as conn:
            row = conn.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row and row["status"] == "cancelled":
                CANCELLED_JOBS.add(job_id)
                return True
    except Exception:
        pass
    return False


def check_cancelled(job_id: str) -> None:
    if is_cancelled(job_id):
        raise JobCancelledError(f"Job {job_id} was cancelled by user")


def run_pipeline(job_id: str) -> None:
    """
    Main pipeline — runs synchronously in a thread-pool executor.
    SSE events are published at each stage.
    """
    upload_path = None
    try:
        check_cancelled(job_id)
        _stage_validating(job_id)
        check_cancelled(job_id)
        upload_path, source_lang, target_langs, mode, farmer_context, quality_mode, output_formats = _load_job_params(job_id)

        # Hardware Resource Saver logic (auto-enabled on low-RAM machines)
        from backend.config import IS_LOW_RAM
        resource_saver = IS_LOW_RAM
        if farmer_context and "[RESOURCE_SAVER]" in farmer_context:
            resource_saver = True
            farmer_context = farmer_context.replace("[RESOURCE_SAVER]", "").strip()

        # Give torch the machine it is actually on. Without this the saver
        # branch was the only one that set anything, so an unthrottled run
        # inherited torch's default of one thread per *logical* core — two
        # per physical core, contending for the same arithmetic units.
        from backend.config import inference_threads
        threads = inference_threads(resource_saver)
        os.environ["OMP_NUM_THREADS"] = str(threads)
        os.environ["MKL_NUM_THREADS"] = str(threads)
        try:
            import torch
            torch.set_num_threads(threads)
        except Exception:
            pass
        logger.info(
            f"Resource Saver Mode {'ON' if resource_saver else 'OFF'} — "
            f"{threads} inference thread(s)"
        )

        check_cancelled(job_id)
        _stage_extracting(job_id, upload_path)  # This stage might modify upload_path if it's a document
        check_cancelled(job_id)
        wav_path = _get_wav_path(job_id)  # This gets the WAV path if it's audio/video

        # Detect speaker gender and extract reference clip for voice cloning
        voice_gender = "female"
        speaker_wav = None
        if wav_path:
            logger.info("Detecting voice gender for TTS matching…")
            from backend.pipeline.voice_detector import detect_voice
            ws = job_workspace(job_id)
            voice_gender, speaker_wav = detect_voice(wav_path, str(ws))
            logger.info(f"Voice profile: gender={voice_gender}, clip={'yes' if speaker_wav else 'no'}")

        check_cancelled(job_id)
        segments, detected_whisper_lang_code = _stage_transcribing(job_id, wav_path, source_lang, upload_path, resource_saver)
        
        check_cancelled(job_id)
        # Pipelined Translation & Generation
        translated_map, output_files = _stage_translating(
            job_id=job_id,
            segments=segments,
            source_lang=source_lang,
            target_langs=target_langs,
            whisper_detected_lang_code=detected_whisper_lang_code,
            upload_path=upload_path,
            resource_saver=resource_saver,
            farmer_context=farmer_context,
            mode=mode,
            quality_mode=quality_mode,
            output_formats=output_formats,
            voice_gender=voice_gender,
            speaker_wav=speaker_wav,
        )
        
        check_cancelled(job_id)
        _stage_packaging(job_id, output_files, source_lang, target_langs)
        _finish_job(job_id, translated_map)

    except JobCancelledError as ce:
        logger.info(f"Job {job_id} stopped cleanly due to cancellation: {ce}")
        _update_job(job_id, status="cancelled", error_log="Cancelled by user", completed_at=_now())
        _publish(job_id, "failed", "Job cancelled by user")
    except Exception as e:
        logger.error(f"Pipeline error for {job_id}: {e}", exc_info=True)
        _update_job(job_id, status="failed", error_log=str(e)[:2000], completed_at=_now())
        _publish(job_id, "failed", str(e))
    finally:
        CANCELLED_JOBS.discard(job_id)
        _cleanup_job(job_id, upload_path)


def _cleanup_job(job_id: str, upload_path: Optional[str]) -> None:
    """Edge Case Optimization: Prevent disk space exhaustion by clearing intermediate files."""
    import shutil
    try:
        if upload_path and os.path.exists(upload_path):
            os.remove(upload_path)
        ws = job_workspace(job_id)
        if ws.exists():
            shutil.rmtree(str(ws), ignore_errors=True)
        logger.info(f"Disk cleanup completed for job {job_id}")
    except Exception as e:
        logger.warning(f"Failed to cleanup disk for job {job_id}: {e}")


# ---------------------------------------------------------------------------
# Stage 1 — Validating
# ---------------------------------------------------------------------------
def _stage_validating(job_id: str) -> None:
    _publish(job_id, "validating", "Checking file …")
    _update_job(job_id, status="validating", started_at=_now())

    with get_db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()

    upload_path = _find_upload(job_id, row["filename"])
    if not upload_path:
        raise FileNotFoundError(f"Upload file not found for job {job_id}")

    suffix = Path(upload_path).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS and suffix != ".txt":
        raise ValueError(f"Unsupported file type: {suffix}")


def _find_upload(job_id: str, filename: str) -> Optional[str]:
    from backend.config import UPLOADS_DIR
    # Look for any file matching job_id prefix in uploads dir
    for f in UPLOADS_DIR.iterdir():
        if f.name.startswith(job_id):
            return str(f)
    return None


def _load_job_params(job_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    upload_path = _find_upload(job_id, row["filename"])
    target_langs = json.loads(row["target_langs"] or "[]")
    output_formats = None
    if "output_formats" in row.keys() and row["output_formats"]:
        try:
            output_formats = json.loads(row["output_formats"])
        except Exception:
            pass
    return (
        upload_path,
        row["source_lang"],
        target_langs,
        row["mode"],
        row["farmer_context"],
        row["quality_mode"] or "full",
        output_formats,
    )


# ---------------------------------------------------------------------------
# Stage 2 — Extracting
# ---------------------------------------------------------------------------
def _stage_extracting(job_id: str, upload_path: str) -> None:
    _publish(job_id, "extracting", "Extracting audio …")
    _update_job(job_id, status="extracting")

    ws = job_workspace(job_id)
    suffix = Path(upload_path).suffix.lower()

    if suffix in {".txt", ".pdf", ".docx", ".csv"}:
        # Copy document directly for packaging and reference
        import shutil
        shutil.copy(upload_path, str(ws / f"original{suffix}"))
        return

    if suffix in {".wav", ".mp3", ".ogg", ".m4a", ".flac"}:
        # Audio-only — copy raw file then let FFmpeg normalise it
        # BUG FIX: ws / "audio_raw" is a Path; appending suffix must use f-string,
        # not string concat which would break on Windows Path objects.
        import shutil
        target = str(ws / f"audio_raw{suffix}")
        shutil.copy(upload_path, target)

    from backend.pipeline.audio_extractor import extract_audio
    extract_audio(upload_path, ws)


def _get_wav_path(job_id: str) -> Optional[str]:
    ws = job_workspace(job_id)
    # Document job
    if list(ws.glob("original.*")):
        return None
    wav = ws / "audio.wav"
    return str(wav) if wav.exists() else None


# ---------------------------------------------------------------------------
# Stage 3 — Transcribing
# ---------------------------------------------------------------------------
def _stage_transcribing(job_id: str, wav_path: Optional[str], source_lang: str, upload_path: str, resource_saver: bool = False) -> tuple[list[dict], str]:
    _publish(job_id, "transcribing", "Transcribing speech …")
    _update_job(job_id, status="transcribing")

    ws = job_workspace(job_id)
    suffix = Path(upload_path).suffix.lower()

    if suffix in {".txt", ".pdf", ".docx", ".csv"}:
        _publish(job_id, "extracting", f"Parsing {suffix.upper()}...", {"pct": 20})
        from backend.pipeline.document_parser import parse_document
        segments = parse_document(upload_path)
        # For document parsing, we don't have Whisper's detected language.
        # Return source_lang's Whisper code if known, else 'en' as a safe fallback.
        from backend.pipeline.transcriber import _display_to_whisper
        detected_lang_code = _display_to_whisper(source_lang) if source_lang != "Auto-Detect" else "en"
        return segments, detected_lang_code

    if not wav_path:
        raise RuntimeError("No audio file found for transcription")

    from backend.pipeline.transcriber import transcribe
    from backend.config import asr_worker_plan
    asr_workers = 1 if resource_saver else asr_worker_plan()[0]
    segments, detected_whisper_lang_code = transcribe(
        wav_path, source_lang, work_dir=str(ws), workers=asr_workers
    )
    # Save transcript
    with open(str(ws / "transcript.txt"), "w", encoding="utf-8") as f:
        for s in segments:
            f.write(s["text"] + "\n")

    return segments, detected_whisper_lang_code


# ---------------------------------------------------------------------------
# Stage 4 & 5 — Translating & Generating Outputs (Pipelined / Overlapped)
# ---------------------------------------------------------------------------
def _stage_translating(
    job_id: str,
    segments: list[dict],
    source_lang: str,
    target_langs: list[str],
    whisper_detected_lang_code: Optional[str] = None,
    upload_path: Optional[str] = None,
    resource_saver: bool = False,
    farmer_context: Optional[str] = None,
    mode: str = "translate",
    quality_mode: str = "full",
    output_formats: Optional[list[str]] = None,
    voice_gender: str = "female",
    speaker_wav: Optional[str] = None,
) -> tuple[dict[str, list[dict]], list[str]]:
    # Resolve source language if auto-detect requested
    if source_lang == "Auto-Detect":
        from backend.pipeline.transcriber import _whisper_to_display
        _resolved = _whisper_to_display(whisper_detected_lang_code)
        if _resolved:
            source_lang = _resolved
            _update_job(job_id, source_lang=source_lang)
            logger.info(f"Auto-detected source language: {source_lang} (from Whisper)")
        else:
            full_text = " ".join([s["text"] for s in segments[:10]])
            if not full_text.strip():
                source_lang = "English"
            else:
                try:
                    from langdetect import detect
                    detected_code = detect(full_text)
                    ld_to_name = {
                        "hi": "Hindi", "bn": "Bengali", "mr": "Marathi", "te": "Telugu",
                        "ta": "Tamil", "gu": "Gujarati", "ur": "Urdu", "kn": "Kannada",
                        "ml": "Malayalam", "pa": "Punjabi", "ne": "Nepali", "en": "English"
                    }
                    source_lang = ld_to_name.get(detected_code, "Hindi")
                except Exception as e:
                    logger.warning(f"langdetect failed: {e}")
                    source_lang = "Hindi"
            _update_job(job_id, source_lang=source_lang)

    total = len(target_langs)
    translated_map: dict[str, list[dict]] = {}
    file_paths: list[str] = []

    _publish(job_id, "translating", f"Translating from {source_lang} into {total} language(s) …")
    _update_job(job_id, status="translating")

    from backend.pipeline.translator import translate_segments
    from backend.pipeline.job_queue import get_current_jobs
    from backend.utils.resources import plan
    from backend.config import TRANSLATION_NUM_BEAMS, TRANSLATION_DRAFT_BEAMS

    num_beams = TRANSLATION_DRAFT_BEAMS if quality_mode == "draft" else TRANSLATION_NUM_BEAMS

    gen_workers = plan(
        "generate",
        resource_saver=resource_saver,
        share=max(1, len(get_current_jobs())),
    )
    translate_workers = plan(
        "translate",
        resource_saver=resource_saver,
        share=max(1, len(get_current_jobs())),
    )
    ws = job_workspace(job_id)
    is_video = upload_path and Path(upload_path).suffix.lower() in {
        ".mp4", ".mkv", ".avi", ".mov", ".webm"
    }

    logger.info(
        f"Job {job_id}: {total} language(s), "
        f"translate_workers={translate_workers}, gen_workers={gen_workers}"
    )

    # Pre-compute Indic→English pivot ONCE for all Indic→Indic targets.
    _cached_english_segments: Optional[list[dict]] = None
    _needs_pivot = (
        source_lang != "English"
        and any(ln != "English" for ln in target_langs if LANG_CODES.get(ln))
    )
    if _needs_pivot:
        _publish(job_id, "translating", f"Pre-translating {source_lang}→English pivot …")
        _cached_english_segments = translate_segments(
            segments=segments,
            source_lang=source_lang,
            target_lang_name="English",
            target_lang_code=ENGLISH_CODE,
            job_id=job_id,
            num_beams=num_beams,
        )

    def _translate_one_language(lang_name: str) -> tuple[str, list[dict]]:
        """Translate segments for one target language. Runs in the translate pool."""
        lang_code = LANG_CODES.get(lang_name)
        if not lang_code:
            logger.warning(f"Unknown language: {lang_name}, skipping")
            return lang_name, []

        if source_lang == "English":
            # Case 1: English → Indic (direct)
            translated = translate_segments(
                segments=segments,
                source_lang="English",
                target_lang_name=lang_name,
                target_lang_code=lang_code,
                job_id=job_id,
                num_beams=num_beams,
            )
        elif lang_name == "English":
            # Case 2: Indic → English (direct)
            translated = translate_segments(
                segments=segments,
                source_lang=source_lang,
                target_lang_name="English",
                target_lang_code=ENGLISH_CODE,
                job_id=job_id,
                num_beams=num_beams,
            )
        else:
            # Case 3: Indic → Indic via cached English pivot
            if _cached_english_segments is not None:
                english_segs = _cached_english_segments
            else:
                english_segs = translate_segments(
                    segments=segments,
                    source_lang=source_lang,
                    target_lang_name="English",
                    target_lang_code=ENGLISH_CODE,
                    job_id=job_id,
                    num_beams=num_beams,
                )
            remapped = [{**seg, "text": seg["translated"]} for seg in english_segs]
            translated = translate_segments(
                segments=remapped,
                source_lang="English",
                target_lang_name=lang_name,
                target_lang_code=lang_code,
                job_id=job_id,
                num_beams=num_beams,
            )

        return lang_name, translated

    done = 0
    with ThreadPoolExecutor(
        max_workers=gen_workers, thread_name_prefix="vaani-gen"
    ) as gen_pool, ThreadPoolExecutor(
        max_workers=translate_workers, thread_name_prefix="vaani-translate"
    ) as translate_pool:

        gen_futures: dict = {}
        valid_langs = [ln for ln in target_langs if LANG_CODES.get(ln)]

        # Submit all translations concurrently.
        translate_futures = {
            translate_pool.submit(_translate_one_language, lang_name): lang_name
            for lang_name in valid_langs
        }

        # As each translation finishes, immediately dispatch generation.
        for t_fut in as_completed(translate_futures):
            lang_name = translate_futures[t_fut]
            try:
                _, translated = t_fut.result()
            except Exception as e:
                logger.error(f"Translation failed for {lang_name}: {e}", exc_info=True)
                continue

            if not translated:
                continue

            translated_map[lang_name] = translated
            _publish(job_id, "translating", f"Translation done → {lang_name}")

            gen_futures[gen_pool.submit(
                _generate_for_language,
                lang_name, translated, source_lang,
                upload_path, ws, is_video,
                farmer_context, mode, quality_mode,
                output_formats, voice_gender, speaker_wav,
            )] = lang_name

        if gen_futures:
            _publish(job_id, "generating", "Generating output files …")
            _update_job(job_id, status="generating")

        for fut in as_completed(gen_futures):
            lang_name = gen_futures[fut]
            done += 1
            try:
                file_paths.extend(fut.result())
            except Exception as e:
                logger.error(f"Generation failed for {lang_name}: {e}", exc_info=True)
            pct = 80 + int(12 * (done / max(len(gen_futures), 1)))
            _publish(
                job_id, "generating",
                f"Generated {lang_name} ({done}/{len(gen_futures)}) …",
                {"pct": pct},
            )

    return translated_map, file_paths


def _generate_for_language(
    lang_name: str,
    trans_segs: list[dict],
    source_lang: str,
    original_path: Optional[str],
    ws: Path,
    is_video: bool,
    farmer_context: Optional[str] = None,
    mode: str = "translate",
    quality_mode: str = "full",
    output_formats: Optional[list[str]] = None,
    voice_gender: str = "female",
    speaker_wav: Optional[str] = None,
) -> list[str]:
    """
    Produce one language's full output set. Runs in the generation pool.

    Only the TTS call touches a shared model (serialized by TTS_LOCK inside
    backend/pipeline/tts.py); everything else here is file writing and ffmpeg
    subprocesses, which parallelize cleanly. All paths are per-language, so
    concurrent invocations never write the same file.
    """
    # Default: generate all formats if none specified
    if output_formats is None:
        output_formats = ["txt", "docx", "srt", "vtt", "mp3", "dubbed_mp4", "captioned_mp4", "ivr_wav", "whatsapp"]

    from backend.pipeline.packager import (
        write_txt, write_bilingual_docx, write_srt, write_vtt,
        write_tts_mp3, write_dubbed_mp4, write_captioned_mp4, write_translated_csv,
        write_ivr_wav, write_whatsapp_chunks
    )

    out: list[str] = []

    txt_p  = write_txt(trans_segs, lang_name, ws)                    if "txt"  in output_formats else None
    docx_p = write_bilingual_docx(trans_segs, source_lang, lang_name, ws, farmer_context=farmer_context, mode=mode) \
                                                                      if "docx" in output_formats else None
    srt_p  = write_srt(trans_segs, lang_name, ws)                    if "srt"  in output_formats else None
    vtt_p  = write_vtt(trans_segs, lang_name, ws)                    if "vtt"  in output_formats else None

    from backend.pipeline.packager import write_advisory_video

    # TTS — required for audio, dubbed video, captioned video, IVR, WhatsApp
    needs_audio = any(f in output_formats for f in ["mp3", "dubbed_mp4", "captioned_mp4", "ivr_wav", "whatsapp"])
    mp3_p  = write_tts_mp3(
        trans_segs, lang_name, ws,
        quality_mode=quality_mode,
        voice_gender=voice_gender,
        speaker_wav=speaker_wav,
    ) if needs_audio else None

    # IVR 8kHz telecom audio
    ivr_p = write_ivr_wav(mp3_p, lang_name, ws) if "ivr_wav" in output_formats and mp3_p else None

    # Video output: dubbed from source video OR high-res visual advisory MP4 card
    if is_video and original_path:
        dubbed_p = write_dubbed_mp4(original_path, mp3_p, lang_name, ws) if "dubbed_mp4" in output_formats and mp3_p else None
        mp4_p    = write_captioned_mp4(original_path, srt_p, lang_name, ws, audio_path=mp3_p) if "captioned_mp4" in output_formats and srt_p else None
    elif mp3_p:
        dubbed_p = write_advisory_video(trans_segs, lang_name, mp3_p, ws)
        mp4_p    = None
    else:
        dubbed_p = None
        mp4_p    = None

    # WhatsApp auto-split chunks
    wa_chunks = write_whatsapp_chunks(dubbed_p or mp4_p, lang_name, ws) if "whatsapp" in output_formats and (dubbed_p or mp4_p) else []

    csv_p    = (
        write_translated_csv(trans_segs, lang_name, ws)
        if original_path and Path(original_path).suffix.lower() == ".csv"
        else None
    )

    for p in [txt_p, docx_p, srt_p, vtt_p, mp3_p, ivr_p, dubbed_p, mp4_p, csv_p]:
        if p:
            out.append(p)
    out.extend(wa_chunks)

    return out


# ---------------------------------------------------------------------------
# Stage 5 — Generating outputs (Standalone helper for backward compatibility)
# ---------------------------------------------------------------------------
def _stage_generating(
    job_id: str,
    segments: list[dict],
    translated_map: dict[str, list[dict]],
    source_lang: str,
    target_langs: list[str],
    original_path: Optional[str],
    voice_gender: str = "female",
    speaker_wav: Optional[str] = None,
) -> list[str]:
    _publish(job_id, "generating", "Generating output files …")
    _update_job(job_id, status="generating")

    ws = job_workspace(job_id)
    file_paths: list[str] = []
    is_video = original_path and Path(original_path).suffix.lower() in {
        ".mp4", ".mkv", ".avi", ".mov", ".webm"
    }

    for lang_name, trans_segs in translated_map.items():
        file_paths.extend(
            _generate_for_language(lang_name, trans_segs, source_lang, original_path, ws, is_video, quality_mode="full", voice_gender=voice_gender, speaker_wav=speaker_wav)
        )

    return file_paths


# ---------------------------------------------------------------------------
# Stage 6 — Packaging
# ---------------------------------------------------------------------------
def _stage_packaging(
    job_id: str,
    file_paths: list[str],
    source_lang: str,
    target_langs: list[str],
) -> None:
    _publish(job_id, "packaging", "Packaging ZIP …")
    _update_job(job_id, status="packaging")

    from backend.pipeline.packager import create_zip
    zip_path = str(job_zip_path(job_id))
    create_zip(
        job_id=job_id,
        out_dir=job_workspace(job_id),
        file_paths=file_paths,
        job_meta={"source_lang": source_lang, "target_langs": target_langs},
        zip_path=zip_path,
    )
    _update_job(job_id, output_path=zip_path)


# ---------------------------------------------------------------------------
# Finish — update confidence, distribution clearance
# ---------------------------------------------------------------------------
def _finish_job(job_id: str, translated_map: dict[str, list[dict]]) -> None:
    all_confs = [
        seg["confidence"]
        for segs in translated_map.values()
        for seg in segs
        if "confidence" in seg
    ]
    avg = avg_confidence(all_confs)
    level = confidence_level(avg)

    # Check if any amber still pending → no clearance yet
    with get_db() as conn:
        pending = conn.execute(
            "SELECT COUNT(*) as c FROM review_queue WHERE job_id=? AND status='pending'",
            (job_id,),
        ).fetchone()["c"]

    clearance = "pending_review" if pending > 0 else "cleared"

    _update_job(
        job_id,
        status="completed",
        avg_confidence=round(avg, 4),
        confidence_level=level,
        distribution_clearance=clearance,
        completed_at=_now(),
    )
    _publish(job_id, "completed", "Done!", {
        "avg_confidence": avg,
        "confidence_level": level,
        "distribution_clearance": clearance,
    })
    logger.info(f"Job {job_id} completed. avg_conf={avg:.3f} level={level}")


# Alias for backward compatibility
_stage_translate_and_generate = _stage_translating

