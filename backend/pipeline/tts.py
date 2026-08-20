"""
VaaniSetu — TTS Wrapper
Generates MP3 audio from translated text.

Engine priority (can be overridden by quality_mode):
  1. Piper TTS  — ONNX-based, near-real-time on CPU, default draft engine
  2. Coqui XTTS — High-quality voice cloning, used in full-quality mode
  3. gTTS       — Online fallback when both local engines are unavailable
"""

import logging
import os
import shutil
import subprocess
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor
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


def split_text(text: str, max_chars: int = 220) -> list[str]:
    """
    Splits a long text into smaller chunks based on sentence boundaries,
    ensuring no chunk exceeds max_chars.
    """
    if not text:
        return []

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


# ---------------------------------------------------------------------------
# Piper TTS — lightweight ONNX engine, near-real-time on CPU
# ---------------------------------------------------------------------------

_piper_voice_cache: dict[str, object] = {}  # language_name → PiperVoice instance


def _get_piper_voice(language_name: str, voice_gender: str = "female"):
    """Load (and cache) a Piper voice for the given language and gender, or return None."""
    cache_key = f"{language_name}_{voice_gender}"
    if cache_key in _piper_voice_cache:
        return _piper_voice_cache[cache_key]

    from backend.config import PIPER_VOICES_DIR, PIPER_VOICE_MAP, PIPER_VOICE_MAP_MALE
    # Try gender-specific voice first, fall back to default map
    if voice_gender == "male":
        voice_stem = PIPER_VOICE_MAP_MALE.get(language_name) or PIPER_VOICE_MAP.get(language_name)
    else:
        voice_stem = PIPER_VOICE_MAP.get(language_name)
    if not voice_stem:
        return None  # Language not supported by Piper

    onnx_path = PIPER_VOICES_DIR / f"{voice_stem}.onnx"
    config_path = PIPER_VOICES_DIR / f"{voice_stem}.onnx.json"

    if not onnx_path.exists() or not config_path.exists():
        logger.info(
            f"Piper voice not found for {language_name} at {onnx_path}. "
            f"Run scripts/download_piper_voices.py to download."
        )
        return None

    try:
        from piper import PiperVoice
        voice = PiperVoice.load(str(onnx_path), config_path=str(config_path), use_cuda=False)
        _piper_voice_cache[cache_key] = voice
        logger.info(f"Piper voice loaded for {language_name} ({voice_gender}): {voice_stem}")
        return voice
    except Exception as e:
        logger.warning(f"Failed to load Piper voice for {language_name}: {e}")
        return None


def _generate_piper_for_segments(
    segments: list[dict],
    language_name: str,
    output_path: str,
    voice_gender: str = "female",
) -> Optional[str]:
    """Synthesise segments with Piper TTS (ONNX, CPU-only, near-real-time)."""
    voice = _get_piper_voice(language_name, voice_gender=voice_gender)
    if voice is None:
        return None

    texts = [seg.get("translated", "").strip() for seg in segments if seg.get("translated", "").strip()]
    if not texts:
        return None

    temp_dir = None
    try:
        import wave
        import io
        temp_dir = tempfile.mkdtemp(prefix="vaanisetu_piper_")
        chunk_wav_paths = []

        for i, text in enumerate(texts):
            pieces = split_text(text)
            for j, piece in enumerate(pieces):
                if not piece.strip():
                    continue
                chunk_path = os.path.join(temp_dir, f"chunk_{i:04d}_{j:02d}.wav")
                try:
                    with wave.open(chunk_path, "wb") as wav_file:
                        voice.synthesize_wav(piece, wav_file)
                    chunk_wav_paths.append(chunk_path)
                except Exception as e:
                    logger.warning(f"Piper synthesis failed for chunk {j} of seg {i}: {e}")

        if not chunk_wav_paths:
            return None

        final_wav = os.path.join(temp_dir, "final.wav")
        if not _concat_wavs(chunk_wav_paths, final_wav):
            return None

        _wav_to_mp3(final_wav, output_path)
        logger.info(f"Piper TTS MP3 generated: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Piper TTS generation failed for {language_name}: {e}")
        return None
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Coqui XTTS — high-quality voice cloning (full-quality mode only)
# ---------------------------------------------------------------------------

def _generate_coqui_tts_for_segments(
    segments: list[dict],
    language_name: str,
    output_path: str,
    speaker_wav: Optional[str] = None,
) -> Optional[str]:
    """
    Synthesise segments with Coqui XTTS v2 (high-quality, full-mode only).
    If speaker_wav is provided (extracted from source video), uses voice cloning
    to match the original speaker's voice. Otherwise falls back to default speaker.
    """
    from backend.models.registry import registry
    from backend.models.pool import get_pool

    pool = get_pool("tts")

    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="vaanisetu_tts_")
        logger.info(f"Coqui TTS chunking to temporary directory: {temp_dir}")

        chunk_wav_paths = []
        failed_chunks = 0
        lang_code = _LANG_TO_COQUI.get(language_name, "hi")

        # Use extracted speaker reference for voice cloning, or fallback default
        if speaker_wav and os.path.exists(speaker_wav):
            logger.info(f"Using extracted speaker reference for voice cloning: {speaker_wav}")
            _speaker_wav = speaker_wav
        else:
            _speaker_wav = str(
                Path(__file__).resolve().parent.parent / "assets" / "default_speaker.wav"
            )
            logger.info(f"Using default speaker reference: {_speaker_wav}")

        # Flatten to a numbered work list first. XTTS is the slowest stage in
        # the pipeline by a wide margin, and every piece is independent, so
        # the order only has to be restored at concat time — not during work.
        work: list[tuple[int, str, str]] = []
        for i, seg in enumerate(segments):
            text = seg.get("translated", "").strip()
            if not text:
                continue
            for j, piece in enumerate(split_text(text)):
                if not piece.strip():
                    continue
                work.append((
                    len(work),
                    piece,
                    os.path.join(temp_dir, f"chunk_{i:04d}_{j:02d}.wav"),
                ))

        if not work:
            return None

        def _synthesize_one(model_instance, piece: str, chunk_path: str) -> bool:
            try:
                model_instance.tts_to_file(
                    text=piece, language=lang_code,
                    speaker_wav=_speaker_wav, file_path=chunk_path,
                )
                return True
            except Exception as e:
                logger.warning(f"Coqui TTS piece failed ({chunk_path}): {e}")
                return False

        done: dict[int, str] = {}

        if pool is not None and pool.size > 1:
            # Each piece checks out its own replica, so concurrency is capped
            # by the pool rather than by how many languages happen to be
            # generating at once — several languages sharing one bounded pool
            # can never oversubscribe RAM.
            def _run(item):
                order, piece, chunk_path = item
                with pool.acquire() as model:
                    return order, chunk_path, _synthesize_one(model, piece, chunk_path)

            logger.info(
                f"Coqui TTS: {len(work)} pieces across {pool.size} replica(s) for {language_name}"
            )
            with ThreadPoolExecutor(
                max_workers=min(pool.size, len(work)),
                thread_name_prefix="vaani-xtts",
            ) as executor:
                for order, chunk_path, ok in executor.map(_run, work):
                    if ok:
                        done[order] = chunk_path
                    else:
                        failed_chunks += 1
        else:
            # Single instance — the original serial path.
            def _serial(model):
                nonlocal failed_chunks
                for order, piece, chunk_path in work:
                    if _synthesize_one(model, piece, chunk_path):
                        done[order] = chunk_path
                    else:
                        failed_chunks += 1

            if pool is not None:
                with pool.acquire() as model:
                    _serial(model)
            else:
                from backend.pipeline.locks import TTS_LOCK
                with TTS_LOCK:
                    _serial(registry.tts_model)

        # Restore source order — concatenating out of order would scramble the
        # advisory into nonsense while still producing a playable file.
        chunk_wav_paths = [done[k] for k in sorted(done)]

        if failed_chunks:
            logger.warning(
                f"Coqui TTS: {failed_chunks}/{len(work)} pieces failed for {language_name}"
            )

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


# ---------------------------------------------------------------------------
# gTTS — online fallback
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_tts_for_segments(
    segments: list[dict],
    language_name: str,
    output_path: str,
    quality_mode: str = "full",
    voice_gender: str = "female",
    speaker_wav: Optional[str] = None,
) -> Optional[str]:
    """
    Generate TTS for all translated segments into output_path MP3.

    Engine cascade:
      draft mode : Piper (gender-aware) → gTTS
      full mode  : XTTS with speaker_wav cloning → Piper → gTTS

    In full mode, XTTS voice cloning is tried first because it produces the
    most natural voice match to the source speaker. Piper is the fast fallback.
    In draft mode, Piper is used exclusively for speed.
    """
    from backend.models.registry import registry

    if quality_mode == "full" and registry._tts_loaded and registry.tts_model is not None:
        # Full mode: XTTS voice cloning gives best speaker match
        coqui_result = _generate_coqui_tts_for_segments(
            segments, language_name, output_path, speaker_wav=speaker_wav
        )
        if coqui_result:
            return coqui_result

    # Draft mode (or XTTS fallback): Piper with gender-aware voice selection
    piper_result = _generate_piper_for_segments(
        segments, language_name, output_path, voice_gender=voice_gender
    )
    if piper_result:
        return piper_result

    # Final fallback: gTTS online
    return _generate_gtts_for_segments(segments, language_name, output_path)


def generate_tts(
    text: str,
    language_name: str,
    output_path: str,
    quality_mode: str = "full",
    voice_gender: str = "female",
    speaker_wav: Optional[str] = None,
) -> Optional[str]:
    """Single-text TTS helper for backward compatibility."""
    return generate_tts_for_segments(
        [{"translated": text}], language_name, output_path,
        quality_mode=quality_mode, voice_gender=voice_gender, speaker_wav=speaker_wav
    )
