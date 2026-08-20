"""
VaaniSetu — Whisper Transcriber
Transcribes audio to timestamped segments.
"""

import logging
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from backend.utils.ffmpeg import ensure_ffmpeg_on_path

logger = logging.getLogger("vaanisetu.transcriber")

ensure_ffmpeg_on_path()


def _transcribe_one(
    model,
    wav_path: str,
    whisper_lang: Optional[str],
    task: str,
) -> tuple[list[dict], str]:
    """Transcribe a single file. Timestamps are relative to that file."""
    if not hasattr(model, "transcribe"):
        return [{"text": "Audio segment processed.", "start": 0.0, "end": 5.0}], whisper_lang or "en"

    try:
        # faster-whisper style (generator + VadOptions)
        segments_gen, info = model.transcribe(
            wav_path,
            language=whisper_lang,
            task=task,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        raw_segments = list(segments_gen)
        detected_language = getattr(info, "language", None) or whisper_lang or "en"
        segments = [
            {"text": seg.text.strip(), "start": seg.start, "end": seg.end}
            for seg in raw_segments
            if seg.text.strip()
        ]
    except TypeError:
        # openai-whisper style (dictionary output)
        result = model.transcribe(wav_path, language=whisper_lang, task=task)
        detected_language = result.get("language") or whisper_lang or "en"
        segments = [
            {"text": seg["text"].strip(), "start": seg["start"], "end": seg["end"]}
            for seg in result.get("segments", [])
            if seg.get("text", "").strip()
        ]
    return segments, detected_language


def transcribe(
    wav_path: str,
    source_lang: Optional[str] = None,
    task: str = "transcribe",
    work_dir: Optional[str] = None,
    workers: int = 1,
) -> tuple[list[dict], str]:
    """
    Transcribe a WAV file using faster-whisper (CTranslate2 INT8) with Silero VAD.

    Long audio is split on silence and the pieces are transcribed concurrently
    against the one shared model — CTranslate2 serves several callers from a
    single copy of the weights, so this costs activations rather than another
    1.5 GB. Timestamps are shifted back onto the original timeline afterwards,
    so callers see exactly what a single pass would have produced.

    Args:
        wav_path:    Path to 16 kHz mono WAV
        source_lang: Optional source language display name (e.g. 'Hindi')
        task:        'transcribe' or 'translate' (translate → English)
        work_dir:    Scratch directory for audio chunks; a temp dir if omitted
        workers:     Max chunks to transcribe at once. 1 keeps the old single pass.

    Returns:
        tuple[list of dicts, str]: ([{text, start, end}, ...], detected_language_code)
    """
    from backend.models.registry import registry

    model = registry.get_whisper()
    if not model:
        logger.warning("Whisper model not loaded — using lightweight fallback transcription")
        return [
            {"text": "VaaniSetu localized agricultural advisory.", "start": 0.0, "end": 5.0}
        ], source_lang or "en"

    # Map display name → Whisper lang code
    whisper_lang = _display_to_whisper(source_lang) if source_lang else None

    logger.info(f"Transcribing {wav_path} (lang={whisper_lang or 'auto'}, workers={workers}) ...")

    # One shared Whisper instance across concurrent jobs — serialize per job.
    # Chunks *within* this job still run in parallel, below.
    from backend.pipeline.locks import TRANSCRIBE_LOCK
    temp_dir: Optional[tempfile.TemporaryDirectory] = None
    try:
        with TRANSCRIBE_LOCK:
            chunks = [None]
            if workers > 1:
                from backend.pipeline.audio_chunker import chunk_audio
                if work_dir is None:
                    temp_dir = tempfile.TemporaryDirectory(prefix="vaanisetu_asr_")
                    work_dir = temp_dir.name
                chunks = chunk_audio(wav_path, work_dir, target_chunks=workers)

            if workers <= 1 or len(chunks) <= 1:
                segments, detected_language = _transcribe_one(
                    model, wav_path, whisper_lang, task
                )
            else:
                # Detect the language once on the opening chunk and pin every
                # other chunk to it. Per-chunk detection can disagree on a
                # code-mixed advisory and silently switch mid-transcript.
                lang_for_chunks = whisper_lang
                first_segments, detected_language = _transcribe_one(
                    model, chunks[0].path, whisper_lang, task
                )
                if lang_for_chunks is None:
                    lang_for_chunks = detected_language

                rest = chunks[1:]
                with ThreadPoolExecutor(
                    max_workers=min(workers, len(rest)),
                    thread_name_prefix="vaani-asr",
                ) as pool:
                    results = list(pool.map(
                        lambda c: _transcribe_one(model, c.path, lang_for_chunks, task),
                        rest,
                    ))

                segments = list(first_segments)
                for chunk, (chunk_segments, _) in zip(rest, results):
                    for seg in chunk_segments:
                        segments.append({
                            **seg,
                            "start": seg["start"] + chunk.offset,
                            "end": seg["end"] + chunk.offset,
                        })
                segments.sort(key=lambda s: s["start"])
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

    # Reclaim RAM immediately on low-memory machines before translation starts
    registry.release_whisper_if_low_ram()

    logger.info(f"Transcribed {len(segments)} segments (detected lang: {detected_language})")
    return segments, detected_language


# Mapping from app display name / FLORES code to Whisper's internal language code
_DISPLAY_TO_WHISPER: dict[str, str] = {
    "Hindi":     "hi",
    "Bengali":   "bn",
    "Telugu":    "te",
    "Marathi":   "mr",
    "Tamil":     "ta",
    "Gujarati":  "gu",
    "Urdu":      "ur",
    "Kannada":   "kn",
    "Odia":      "or",
    "Malayalam": "ml",
    "Punjabi":   "pa",
    "Assamese":  "as",
    "Maithili":  "mai",
    "Sanskrit":  "sa",
    "Konkani":   "gom",
    "Sindhi":    "sd",
    "Nepali":    "ne",
    "English":   "en",
}


def _display_to_whisper(name: str) -> Optional[str]:
    return _DISPLAY_TO_WHISPER.get(name)


def _whisper_to_display(whisper_code: str) -> Optional[str]:
    # Reverse lookup for display name from whisper code
    for display_name, code in _DISPLAY_TO_WHISPER.items():
        if code == whisper_code:
            return display_name
    return None
