"""
VaaniSetu — Whisper Transcriber
Transcribes audio to timestamped segments.
"""

import logging
from pathlib import Path
from typing import Optional

from backend.utils.ffmpeg import ensure_ffmpeg_on_path

logger = logging.getLogger("vaanisetu.transcriber")

ensure_ffmpeg_on_path()


def transcribe(
    wav_path: str,
    source_lang: Optional[str] = None,
    task: str = "transcribe",
) -> tuple[list[dict], str]:
    """
    Transcribe a WAV file using faster-whisper (CTranslate2 INT8) with Silero VAD.

    Args:
        wav_path: Path to 16 kHz mono WAV
        source_lang: Optional Whisper language code hint (e.g. 'hi', 'en')
        task: 'transcribe' or 'translate' (translate → English)

    Returns:
        tuple[list of dicts, str]: ([{text, start, end}, ...], detected_language_code)
    """
    from backend.models.registry import registry

    if not registry.whisper_model:
        raise RuntimeError("Whisper model not loaded")

    # Map display name → Whisper lang code
    whisper_lang = _display_to_whisper(source_lang) if source_lang else None

    logger.info(f"Transcribing {wav_path} with faster-whisper (lang={whisper_lang or 'auto'}) ...")

    # One shared Whisper instance across concurrent jobs — serialize it.
    from backend.pipeline.locks import TRANSCRIBE_LOCK
    with TRANSCRIBE_LOCK:
        segments_gen, info = registry.whisper_model.transcribe(
            wav_path,
            language=whisper_lang,
            task=task,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        # Materialise the generator inside the lock so the model stays
        # exclusively ours for the full duration of transcription.
        raw_segments = list(segments_gen)

    detected_language = info.language or whisper_lang or "en"

    logger.info(f"Detected language: {detected_language}")

    segments = [
        {
            "text": seg.text.strip(),
            "start": seg.start,
            "end": seg.end,
        }
        for seg in raw_segments
        if seg.text.strip()
    ]

    logger.info(f"Transcribed {len(segments)} segments")

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
