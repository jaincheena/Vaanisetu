"""
VaaniSetu — Coqui TTS Wrapper
Generates MP3 audio from translated text.
Gracefully disabled if model not loaded.
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger("vaanisetu.tts")

# Map display language name → Coqui XTTS language code
_LANG_TO_COQUI: dict[str, str] = {
    "Hindi":     "hi",
    "Bengali":   "bn",
    "Telugu":    "te",
    "Marathi":   "mr",
    "Tamil":     "ta",
    "Gujarati":  "gu",
    "Urdu":      "ur",
    "Kannada":   "kn",
    "Malayalam": "ml",
    "Punjabi":   "pa",
    "Assamese":  "as",
    "Nepali":    "ne",
    "English":   "en",
}


def generate_tts(
    text: str,
    language_name: str,
    output_path: str,
) -> Optional[str]:
    """
    Generate TTS speech for the given text.
    Returns output_path on success, None if TTS is unavailable.
    """
    from backend.models.registry import registry

    if not registry._tts_loaded or registry.tts_model is None:
        logger.warning("TTS not available — skipping audio generation")
        return None

    lang_code = _LANG_TO_COQUI.get(language_name, "hi")

    from backend.models.pool import get_pool

    pool = get_pool("tts")

    try:
        logger.info(f"TTS generating: {language_name} → {output_path}")
        if pool is not None:
            # Check out a replica — one per concurrent language, no waiting.
            with pool.acquire() as model:
                model.tts_to_file(
                    text=text,
                    language=lang_code,
                    file_path=output_path,
                )
        else:
            # Single shared instance — serialize. See backend/pipeline/locks.py.
            from backend.pipeline.locks import TTS_LOCK
            with TTS_LOCK:
                registry.tts_model.tts_to_file(
                    text=text,
                    language=lang_code,
                    file_path=output_path,
                )
        # Convert wav to mp3 via ffmpeg if needed (outside the lock — ffmpeg
        # is a subprocess and parallelizes fine).
        if output_path.endswith(".wav"):
            mp3_path = output_path.replace(".wav", ".mp3")
            _wav_to_mp3(output_path, mp3_path)
            os.remove(output_path)
            return mp3_path
        return output_path
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        return None


def _wav_to_mp3(wav_path: str, mp3_path: str) -> None:
    import subprocess
    cmd = ["ffmpeg", "-y", "-i", wav_path, "-q:a", "4", mp3_path]
    subprocess.run(cmd, capture_output=True, check=False)


def generate_tts_for_segments(
    segments: list[dict],  # translated segments with 'translated' key
    language_name: str,
    output_path: str,
) -> Optional[str]:
    """Generate TTS for all translated segments concatenated."""
    full_text = " ".join(
        s.get("translated", "") for s in segments if s.get("translated")
    )
    if not full_text.strip():
        return None
    return generate_tts(full_text, language_name, output_path)
