"""
VaaniSetu — Silence-Aware Audio Chunker

Whisper transcribes one stream at a time, so a 10-minute advisory is a single
long serial pass however many cores the laptop has. Splitting it lets several
chunks run at once (see transcriber.transcribe).

Cuts are placed inside silences found by ffmpeg's `silencedetect`, never at a
fixed clock position — slicing mid-word costs accuracy at both sides of the
seam, which is the one thing this pipeline cannot trade away. When no usable
silence exists near a target boundary the audio is left unsplit rather than
cut blind: a slower correct transcript beats a fast wrong one.
"""

import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from backend.utils.ffmpeg import ffmpeg_executable

logger = logging.getLogger("vaanisetu.chunker")

# Below this there is nothing to gain — model warm-up dominates.
MIN_SPLIT_DURATION_S = 240.0

# Keep chunks long enough that Whisper still sees sentence context.
MIN_CHUNK_S = 90.0

# ffmpeg silencedetect tuning. -30 dB over 0.4 s reliably finds the pauses
# between spoken sentences without tripping on room tone in field recordings.
SILENCE_NOISE_DB = -30
SILENCE_MIN_DURATION_S = 0.4


@dataclass
class AudioChunk:
    """One slice of the source audio, with the offset needed to restore timing."""
    path: str
    offset: float      # seconds from the start of the original audio
    duration: float


def _detect_silences(wav_path: str) -> list[tuple[float, float]]:
    """Return [(silence_start, silence_end), …] as reported by ffmpeg."""
    cmd = [
        ffmpeg_executable(), "-hide_banner", "-nostats", "-i", wav_path,
        "-af", f"silencedetect=noise={SILENCE_NOISE_DB}dB:d={SILENCE_MIN_DURATION_S}",
        "-f", "null", "-",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as e:
        logger.warning(f"silencedetect failed, will not split: {e}")
        return []

    # silencedetect writes to stderr; both are checked in case ffmpeg changes.
    output = (proc.stderr or "") + (proc.stdout or "")
    starts = [float(m) for m in re.findall(r"silence_start:\s*(-?[\d.]+)", output)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*(-?[\d.]+)", output)]

    silences = []
    for i, start in enumerate(starts):
        end = ends[i] if i < len(ends) else None
        if end is not None and end > start:
            silences.append((start, end))
    return silences


def plan_cut_points(
    duration: float,
    silences: list[tuple[float, float]],
    target_chunks: int,
) -> list[float]:
    """
    Choose up to target_chunks-1 cut points, each inside a detected silence.

    Walks ideal evenly-spaced boundaries and snaps each to the midpoint of the
    nearest silence, provided that lands within tolerance and leaves both
    neighbours at least MIN_CHUNK_S long. Boundaries with no usable silence are
    simply skipped, so the result may contain fewer chunks than requested.
    """
    if target_chunks < 2 or duration <= 0 or not silences:
        return []

    ideal_len = duration / target_chunks
    tolerance = max(ideal_len * 0.4, 20.0)
    midpoints = sorted((s + e) / 2 for s, e in silences)

    cuts: list[float] = []
    for i in range(1, target_chunks):
        ideal = ideal_len * i
        candidate = min(midpoints, key=lambda m: abs(m - ideal))
        if abs(candidate - ideal) > tolerance:
            continue
        prev = cuts[-1] if cuts else 0.0
        if candidate - prev < MIN_CHUNK_S or duration - candidate < MIN_CHUNK_S:
            continue
        cuts.append(candidate)

    return cuts


def _slice(wav_path: str, out_path: str, start: float, end: float) -> bool:
    """Cut [start, end) into out_path, re-encoding to the same 16 kHz mono PCM."""
    cmd = [
        ffmpeg_executable(), "-y", "-hide_banner", "-loglevel", "error",
        "-i", wav_path,
        "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        out_path,
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=False)
    except Exception as e:
        logger.warning(f"Failed to slice {start:.1f}-{end:.1f}s: {e}")
        return False
    return os.path.exists(out_path) and os.path.getsize(out_path) > 0


def chunk_audio(wav_path: str, work_dir: str, target_chunks: int) -> list[AudioChunk]:
    """
    Split wav_path into at most target_chunks pieces on silence boundaries.

    Returns a single chunk covering the whole file when splitting is not
    worthwhile or not safely possible — callers can treat the result uniformly.
    """
    from backend.pipeline.audio_extractor import get_media_duration_seconds

    duration = get_media_duration_seconds(wav_path) or 0.0
    whole = [AudioChunk(path=wav_path, offset=0.0, duration=duration)]

    if target_chunks < 2 or duration < MIN_SPLIT_DURATION_S:
        return whole

    silences = _detect_silences(wav_path)
    cuts = plan_cut_points(duration, silences, target_chunks)
    if not cuts:
        logger.info(
            f"No usable silence boundary in {duration:.0f}s of audio — "
            f"transcribing as one piece to protect accuracy"
        )
        return whole

    boundaries = [0.0, *cuts, duration]
    out_dir = Path(work_dir) / "asr_chunks"
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks: list[AudioChunk] = []
    for i in range(len(boundaries) - 1):
        start, end = boundaries[i], boundaries[i + 1]
        out_path = str(out_dir / f"chunk_{i:03d}.wav")
        if not _slice(wav_path, out_path, start, end):
            logger.warning("Chunk slicing failed midway — falling back to single pass")
            return whole
        chunks.append(AudioChunk(path=out_path, offset=start, duration=end - start))

    logger.info(
        f"Split {duration:.0f}s audio into {len(chunks)} chunks at silences: "
        + ", ".join(f"{c.offset:.0f}s" for c in chunks)
    )
    return chunks
