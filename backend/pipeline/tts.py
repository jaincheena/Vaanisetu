"""
VaaniSetu — Coqui TTS Wrapper
Generates MP3 audio from translated text.
Gracefully disabled if model not loaded.
"""

import logging
import os
import shutil
import subprocess
import re
import tempfile
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


def split_text(text: str, max_chars: int = 220) -> list[str]:
    """
    Splits a long text into smaller chunks based on sentence boundaries,
    ensuring no chunk exceeds max_chars.
    """
    if not text:
        return []

    # Split text into sentences using common delimiters for English and Indic scripts.
    sentences = re.split(r'(?<=[.!?।])\s*', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return [text] if text else []

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            # If a single sentence is longer than max_chars, it becomes its own chunk.
            # This is a safeguard against extremely long sentences.
            if len(sentence) > max_chars:
                chunks.append(sentence)
                current_chunk = ""
            else:
                current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def _wav_to_mp3(wav_path: str, mp3_path: str) -> None:
    from backend.utils.ffmpeg import ffmpeg_executable

    cmd = [ffmpeg_executable(), "-y", "-i", wav_path, "-q:a", "4", mp3_path]
    subprocess.run(cmd, capture_output=True, check=False)


def _concat_wavs(wav_paths: list[str], output_path: str) -> bool:
    """Concatenate multiple WAV files into one using FFmpeg."""
    from backend.utils.ffmpeg import ffmpeg_executable

    list_path = os.path.join(os.path.dirname(output_path), "concat_list.txt")
    try:
        with open(list_path, "w", encoding="utf-8") as f:
            for p in wav_paths:
                safe_p = p.replace("\\", "/")
                f.write(f"file '{safe_p}'\n")

        cmd = [
            ffmpeg_executable(), "-y", "-f", "concat",
            "-safe", "0", "-i", list_path,
            # Re-encode to a standard format to avoid issues with differing chunk metadata.
            "-c:a", "pcm_s16le", output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, check=False, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg concat failed: {result.stderr}")
            return False
        return True
    finally:
        if os.path.exists(list_path):
            os.remove(list_path)


def generate_tts_for_segments(
    segments: list[dict],  # translated segments with 'translated' key
    language_name: str,
    output_path: str,
) -> Optional[str]:
    """
    Generate TTS for all translated segments by creating and concatenating audio chunks.
    This preserves natural pauses and avoids TTS model character limits.
    """
    from backend.models.registry import registry

    if not registry._tts_loaded or registry.tts_model is None:
        logger.warning("TTS not available — skipping audio generation")
        return None

    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="vaanisetu_tts_")
        logger.info(f"TTS chunking to temporary directory: {temp_dir}")

        chunk_wav_paths = []
        failed_chunks = 0
        lang_code = _LANG_TO_COQUI.get(language_name, "hi")
        # Use a resolved, absolute path to the speaker wav to avoid CWD issues.
        speaker_wav = (
            Path(__file__).resolve().parent.parent / "assets" / "default_speaker.wav"
        )

        for i, seg in enumerate(segments):
            text = seg.get("translated", "").strip()
            if not text:
                continue

            # Split long segments into smaller pieces to avoid TTS token limits.
            pieces = split_text(text)
            for j, piece in enumerate(pieces):
                chunk_path = os.path.join(temp_dir, f"chunk_{i:04d}_{j:02d}.wav")
                try:
                    registry.tts_model.tts_to_file(
                        text=piece, language=lang_code,
                        speaker_wav=str(speaker_wav), file_path=chunk_path,
                    )
                    chunk_wav_paths.append(chunk_path)
                except Exception as e:
                    logger.warning(f"TTS for piece {j} of segment {i} ('{piece[:20]}...') failed, skipping: {e}")
                    failed_chunks += 1

        successful_chunks = len(chunk_wav_paths)
        logger.info(f"Generated {successful_chunks} TTS chunks ({failed_chunks} failed).")

        if not chunk_wav_paths:
            logger.warning("No TTS chunks were successfully generated.")
            return None

        final_wav_path = os.path.join(temp_dir, "final_concat.wav")
        if not _concat_wavs(chunk_wav_paths, final_wav_path):
            return None

        _wav_to_mp3(final_wav_path, output_path)
        return output_path

    except Exception as e:
        logger.error(f"TTS generation for segments failed: {e}", exc_info=True)
        return None
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary TTS directory: {temp_dir}")
