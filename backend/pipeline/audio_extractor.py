"""
VaaniSetu — Audio Extractor
Uses FFmpeg to extract/convert audio to 16 kHz mono WAV.
"""

import logging
import os
import shutil
import subprocess
import wave
from pathlib import Path

from backend.utils.ffmpeg import ensure_ffmpeg_on_path, ffmpeg_executable, ffprobe_executable

logger = logging.getLogger("vaanisetu.audio")

ensure_ffmpeg_on_path()


def _is_wav_16khz_mono(path: str) -> bool:
    try:
        with wave.open(path, "rb") as wf:
            return (
                wf.getnchannels() == 1
                and wf.getsampwidth() == 2
                and wf.getframerate() == 16000
            )
    except Exception:
        return False


def extract_audio(input_path: str, output_dir: Path) -> str:
    """
    Extract audio from any media file, apply filters, and convert to 16 kHz mono WAV.
    Returns path to the WAV file.
    """
    out_wav = str(output_dir / "audio.wav")

    # Optimization: if input is already a 16kHz mono WAV, just copy it.
    # This avoids unnecessary re-encoding, saving CPU and preserving quality.
    if Path(input_path).suffix.lower() == ".wav" and _is_wav_16khz_mono(input_path):
        logger.info(f"Input is already 16kHz mono WAV, copying: {input_path} -> {out_wav}")
        shutil.copy(input_path, out_wav)
        return out_wav

    # Audio filters for cleaning speech before ASR:
    # - highpass: removes low-frequency noise (e.g., rumble, hum) below 80 Hz.
    # - lowpass: removes high-frequency noise (e.g., hiss) above 7500 Hz.
    # - loudnorm: normalizes loudness to a standard level (I=-16 LUFS, LRA=11, TP=-1.5).
    #   This is crucial for Whisper's performance on varied recordings.
    audio_filters = "highpass=f=80,lowpass=f=7500,loudnorm=I=-16:LRA=11:TP=-1.5"

    cmd = [
        ffmpeg_executable(), "-y",
        "-i", input_path,
        "-af", audio_filters,
        "-ac", "1",              # mono
        "-ar", "16000",          # 16 kHz
        "-vn",                   # no video
        "-acodec", "pcm_s16le",  # signed 16-bit little-endian PCM
        out_wav,
    ]
    logger.info(f"FFmpeg extract & filter: {input_path} → {out_wav}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Fallback for any failure (e.g., loudnorm's 2-pass on very short files).
    if result.returncode != 0:
        logger.warning(
            "FFmpeg with loudnorm failed (retrying with simpler filters). "
            f"Original error: {result.stderr[-500:]}"
        )
        cmd = [
            ffmpeg_executable(), "-y",
            "-i", input_path,
            "-af", "highpass=f=80,lowpass=f=7500",  # No loudnorm
            "-ac", "1",
            "-ar", "16000",
            "-vn",
            "-acodec", "pcm_s16le",
            out_wav,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed on second attempt: {result.stderr[-500:]}")

    # Final validation of the output file.
    if not Path(out_wav).exists() or not _is_wav_16khz_mono(out_wav):
        raise RuntimeError(
            f"FFmpeg output file is missing or not a valid 16kHz mono WAV: {out_wav}"
        )
    return out_wav


def get_media_duration_seconds(input_path: str) -> float:
    """Get duration of media file in seconds via ffprobe."""
    cmd = [
        ffprobe_executable(), "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def burn_subtitles(video_path: str, srt_path: str, output_path: str) -> str:
    """
    Burn SRT subtitles into a copy of the video.
    Requires FFmpeg with libass support.
    """
    cmd = [
        ffmpeg_executable(), "-y",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        "-c:a", "copy",
        output_path,
    ]
    logger.info(f"Burning subtitles: {srt_path} → {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg subtitle burn failed: {result.stderr[-500:]}")
    return output_path
