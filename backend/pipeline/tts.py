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


_LANG_TO_GTTS: dict[str, str] = {
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
    "Assamese":  "bn",
    "Nepali":    "ne",
    "English":   "en",
    "Odia":      "or",
    "Sanskrit":  "sa",
    "Sindhi":    "sd",
    "Maithili":  "hi",
    "Konkani":   "mr",
    "Dogri":     "hi",
    "Kashmiri":  "ur",
}


def _generate_gtts_for_segments(
    segments: list[dict],
    language_name: str,
    output_path: str,
) -> Optional[str]:
    try:
        from gtts import gTTS
    except ImportError:
        logger.warning("gTTS not installed — skipping audio generation")
        return None

    lang_code = _LANG_TO_GTTS.get(language_name, "hi")
    texts = [seg.get("translated", "").strip() for seg in segments if seg.get("translated", "").strip()]
    full_text = " ".join(texts)
    if not full_text:
        return None

    try:
        logger.info(f"Generating translated audio via gTTS for {language_name} (code={lang_code}) ...")
        tts = gTTS(text=full_text, lang=lang_code)
        tts.save(output_path)
        logger.info(f"Translated MP3 audio generated: {output_path}")
        return output_path
    except Exception as e:
        logger.warning(f"gTTS audio generation failed for {language_name}: {e}")
        return None


def generate_tts_for_segments(
    segments: list[dict],  # translated segments with 'translated' key
    language_name: str,
    output_path: str,
) -> Optional[str]:
    """
    Generate TTS for all translated segments into output_path MP3.
    Uses Coqui XTTS if loaded, or falls back to gTTS.
    """
    from backend.models.registry import registry

    if registry._tts_loaded and registry.tts_model is not None:
        coqui_res = _generate_coqui_tts_for_segments(segments, language_name, output_path)
        if coqui_res:
            return coqui_res

    # Fallback to gTTS
    return _generate_gtts_for_segments(segments, language_name, output_path)


def _generate_coqui_tts_for_segments(
    segments: list[dict],
    language_name: str,
    output_path: str,
) -> Optional[str]:
    from backend.models.registry import registry

    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="vaanisetu_tts_")
        logger.info(f"Coqui TTS chunking to temporary directory: {temp_dir}")

        chunk_wav_paths = []
        failed_chunks = 0
        lang_code = _LANG_TO_COQUI.get(language_name, "hi")
        speaker_wav = (
            Path(__file__).resolve().parent.parent / "assets" / "default_speaker.wav"
        )

        for i, seg in enumerate(segments):
            text = seg.get("translated", "").strip()
            if not text:
                continue

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
                    logger.warning(f"Coqui TTS piece {j} of seg {i} failed: {e}")
                    failed_chunks += 1

        if not chunk_wav_paths:
            return None

        final_wav_path = os.path.join(temp_dir, "final_concat.wav")
        if not _concat_wavs(chunk_wav_paths, final_wav_path):
            return None

        _wav_to_mp3(final_wav_path, output_path)
        return output_path

    except Exception as e:
        logger.error(f"Coqui TTS generation failed: {e}")
        return None
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
