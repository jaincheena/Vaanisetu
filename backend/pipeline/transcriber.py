"""
VaaniSetu — Whisper Transcriber
Transcribes audio to timestamped segments.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("vaanisetu.transcriber")


def transcribe(
    wav_path: str,
    source_lang: Optional[str] = None,
    task: str = "transcribe",
) -> list[dict]:
    """
    Transcribe a WAV file using Whisper.

    Args:
        wav_path: Path to 16 kHz mono WAV
        source_lang: Optional Whisper language code hint (e.g. 'hi', 'en')
        task: 'transcribe' or 'translate' (translate → English)

    Returns:
        list of dicts: [{text, start, end}, ...]
    """
    from backend.models.registry import registry

    if not registry.whisper_model:
        raise RuntimeError("Whisper model not loaded")

    # Map display name → Whisper lang code
    whisper_lang = _display_to_whisper(source_lang) if source_lang else None

    logger.info(f"Transcribing {wav_path} (lang={whisper_lang or 'auto'}) ...")
    result = registry.whisper_model.transcribe(
        wav_path,
        language=whisper_lang,
        task=task,
        word_timestamps=False,
        verbose=False,
    )

    segments = [
        {
            "text":  seg["text"].strip(),
            "start": seg["start"],
            "end":   seg["end"],
        }
        for seg in result.get("segments", [])
        if seg["text"].strip()
    ]

    logger.info(f"Transcribed {len(segments)} segments")
    return segments


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
