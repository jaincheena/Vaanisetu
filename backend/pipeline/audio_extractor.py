"""
VaaniSetu — Audio Extractor
Uses FFmpeg to extract/convert audio to 16 kHz mono WAV.
"""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("vaanisetu.audio")


def extract_audio(input_path: str, output_dir: Path) -> str:
    """
    Extract audio from any media file and convert to 16 kHz mono WAV.
    Returns path to the WAV file.
    """
    out_wav = str(output_dir / "audio.wav")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",               # mono
        "-ar", "16000",           # 16 kHz
        "-vn",                    # no video
        "-acodec", "pcm_s16le",   # signed 16-bit little-endian PCM
        out_wav,
    ]
    logger.info(f"FFmpeg extract: {input_path} → {out_wav}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr[-500:]}")
    return out_wav


def get_media_duration_seconds(input_path: str) -> float:
    """Get duration of media file in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
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
        "ffmpeg", "-y",
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
