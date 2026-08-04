"""
VaaniSetu — 7-Stage Job Processor
Orchestrates: queued → validating → extracting → transcribing →
              translating → generating → packaging
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.config import LANG_CODES, ALLOWED_EXTENSIONS, ENGLISH_CODE
from backend.database import get_db
from backend.utils.file_utils import sha256_file, job_workspace, job_zip_path
from backend.utils.sse import sse_manager
from backend.services.confidence import confidence_level, avg_confidence

logger = logging.getLogger("vaanisetu.processor")


def _now() -> str:
    return datetime.utcnow().isoformat()


def _publish(job_id: str, stage: str, msg: str, extra: dict | None = None) -> None:
    """
    Synchronous SSE publish — called from a thread-pool executor.
    Uses asyncio.run() so each call gets a clean event loop without
    the overhead of manually creating/destroying one.
    """
    try:
        asyncio.run(sse_manager.publish(job_id, stage, msg, extra))
    except Exception:
        pass  # SSE failures must never break the pipeline


def _update_job(job_id: str, **kwargs) -> None:
    with get_db() as conn:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [job_id]
        conn.execute(f"UPDATE jobs SET {sets} WHERE id=?", vals)


def run_pipeline(job_id: str) -> None:
    """
    Main pipeline — runs synchronously in a thread-pool executor.
    SSE events are published at each stage.
    """
    upload_path = None
    try:
        _stage_validating(job_id)
        upload_path, source_lang, target_langs, mode, farmer_context = _load_job_params(job_id)

        # Hardware Resource Saver logic
        resource_saver = False
        if farmer_context and "[RESOURCE_SAVER]" in farmer_context:
            resource_saver = True
            farmer_context = farmer_context.replace("[RESOURCE_SAVER]", "").strip()
            # Throttle Whisper/Torch threads
            os.environ["OMP_NUM_THREADS"] = "2"
            os.environ["MKL_NUM_THREADS"] = "2"
            try:
                import torch
                logger.info("Resource Saver Mode enabled.")
            except ImportError:
                logger.warning("Resource Saver Mode: torch not found.")

        _stage_extracting(job_id, upload_path) # This stage might modify upload_path if it's a document
        wav_path = _get_wav_path(job_id) # This gets the WAV path if it's audio/video
        segments, detected_whisper_lang_code = _stage_transcribing(job_id, wav_path, source_lang, upload_path)
        translated_map = _stage_translating(job_id, segments, source_lang, target_langs, detected_whisper_lang_code)
        output_files = _stage_generating(
            job_id, segments, translated_map,
            source_lang, target_langs, upload_path,
        )
        _stage_packaging(job_id, output_files, source_lang, target_langs)
        _finish_job(job_id, translated_map)

    except Exception as e:
        logger.error(f"Pipeline error for {job_id}: {e}", exc_info=True)
        _update_job(job_id, status="failed", error_log=str(e)[:2000], completed_at=_now())
        _publish(job_id, "failed", str(e))
    finally:
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
    return (
        upload_path,
        row["source_lang"],
        target_langs,
        row["mode"],
        row["farmer_context"],
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
def _stage_transcribing(job_id: str, wav_path: Optional[str], source_lang: str, upload_path: str) -> tuple[list[dict], str]:
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
    segments, detected_whisper_lang_code = transcribe(wav_path, source_lang)
    # Save transcript
    with open(str(ws / "transcript.txt"), "w", encoding="utf-8") as f:
        for s in segments:
            f.write(s["text"] + "\n")

    return segments, detected_whisper_lang_code


# ---------------------------------------------------------------------------
# Stage 4 — Translating
# ---------------------------------------------------------------------------
def _stage_translating(
    job_id: str,
    segments: list[dict],
    source_lang: str,
    target_langs: list[str],
    whisper_detected_lang_code: str,
) -> dict[str, list[dict]]:
    # Handle Auto-Detect
    if source_lang == "Auto-Detect":
        _publish(job_id, "translating", "Detecting source language…")
        from backend.pipeline.transcriber import _whisper_to_display
        detected_display_name = _whisper_to_display(whisper_detected_lang_code)
        if detected_display_name:
            source_lang = detected_display_name
            _update_job(job_id, source_lang=source_lang)
            logger.info(f"Auto-detected source language: {source_lang} (from Whisper)")
        else:
            logger.warning(f"Whisper detected unknown language code '{whisper_detected_lang_code}'. Falling back to Hindi.")
            source_lang = "Hindi" # Fallback if Whisper detects something not in our map
            _update_job(job_id, source_lang=source_lang)

    total = len(target_langs)
    translated_map: dict[str, list[dict]] = {}

    _publish(job_id, "translating", f"Translating from {source_lang} into {total} language(s) …")
    _update_job(job_id, status="translating")

    # Rationale for not merging segments:
    # Direct merging of segments before translation can break the 1:1 mapping
    # required for accurate timestamping in downstream outputs (SRT, VTT, TTS).
    # The IndicTrans2 model's internal batching mechanism already provides some context
    # for translation quality.

    from backend.pipeline.translator import translate_segments

    for idx, lang_name in enumerate(target_langs):
        lang_code = LANG_CODES.get(lang_name)
        if not lang_code:
            logger.warning(f"Unknown language: {lang_name}, skipping")
            continue

        pct = 60 + int(20 * (idx / max(total, 1)))

        # Case 1: English -> Indic (direct translation)
        if source_lang == "English":
            _publish(job_id, "translating", f"Translating → {lang_name} …", {"pct": pct})
            translated = translate_segments(
                segments=segments, # Use original segments
                source_lang="English",
                target_lang_name=lang_name,
                target_lang_code=lang_code,
                job_id=job_id,
            )
        # Case 2: Indic -> English (direct translation)
        elif lang_name == "English":
            _publish(job_id, "translating", f"Translating → {lang_name} …", {"pct": pct})
            translated = translate_segments(
                segments=segments, # Use original segments
                source_lang=source_lang,
                target_lang_name="English",
                target_lang_code=ENGLISH_CODE,
                job_id=job_id,
            )
        # Case 3: Indic -> Indic (pivot through English)
        else:
            # Step 1: Indic -> English
            _publish(job_id, "translating", f"Translating → {lang_name} (Step 1/2: {source_lang}→English) …", {"pct": pct})
            english_segments = translate_segments(
                segments=segments, # Use original segments
                source_lang=source_lang,
                target_lang_name="English",
                target_lang_code=ENGLISH_CODE,
                job_id=job_id,
            )

            # Remap segments for step 2: the 'translated' text becomes the new 'text'
            remapped_segments = [
                {**seg, "text": seg["translated"]} for seg in english_segments
            ]

            # Step 2: English -> Target Indic
            _publish(job_id, "translating", f"Translating → {lang_name} (Step 2/2: English→{lang_name}) …", {"pct": pct + 5})
            translated = translate_segments(
                segments=remapped_segments,
                source_lang="English",
                target_lang_name=lang_name,
                target_lang_code=lang_code,
                job_id=job_id,
            )

        translated_map[lang_name] = translated

    return translated_map


# ---------------------------------------------------------------------------
# Stage 5 — Generating outputs
# ---------------------------------------------------------------------------
def _stage_generating(
    job_id: str,
    segments: list[dict],
    translated_map: dict[str, list[dict]],
    source_lang: str,
    target_langs: list[str],
    original_path: Optional[str],
) -> list[str]:
    _publish(job_id, "generating", "Generating output files …")
    _update_job(job_id, status="generating")

    from backend.pipeline.packager import (
        write_txt, write_bilingual_docx, write_srt, write_vtt,
        write_tts_mp3, write_captioned_mp4, write_translated_csv,
        write_ivr_wav, write_whatsapp_chunks
    )

    ws = job_workspace(job_id)
    file_paths: list[str] = []

    is_video = original_path and Path(original_path).suffix.lower() in {
        ".mp4", ".mkv", ".avi", ".mov", ".webm"
    }

    for lang_name, trans_segs in translated_map.items():
        txt_p   = write_txt(trans_segs, lang_name, ws)
        docx_p  = write_bilingual_docx(trans_segs, source_lang, lang_name, ws)
        srt_p   = write_srt(trans_segs, lang_name, ws)
        vtt_p   = write_vtt(trans_segs, lang_name, ws)
        mp3_p   = write_tts_mp3(trans_segs, lang_name, ws)
        ivr_p   = write_ivr_wav(mp3_p, lang_name, ws)
        mp4_p   = write_captioned_mp4(
            original_path if is_video else None, srt_p, lang_name, ws
        )
        csv_p   = write_translated_csv(trans_segs, lang_name, ws) if original_path and Path(original_path).suffix.lower() == ".csv" else None
        
        wa_chunks = write_whatsapp_chunks(mp4_p, lang_name, ws)

        for p in [txt_p, docx_p, srt_p, vtt_p, mp3_p, ivr_p, mp4_p, csv_p]:
            if p:
                file_paths.append(p)
        file_paths.extend(wa_chunks)

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
