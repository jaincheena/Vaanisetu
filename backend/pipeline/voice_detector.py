"""
VaaniSetu — Voice Gender Detector
Detects speaker gender from audio using librosa F0 pitch analysis.
Also extracts a 15-second speaker reference clip for XTTS voice cloning.
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("vaanisetu.voice_detector")

# F0 threshold: female voices typically > 165 Hz, male < 165 Hz
GENDER_F0_THRESHOLD_HZ = 165.0
# Duration of speaker reference clip for XTTS voice cloning (seconds)
SPEAKER_CLIP_DURATION_S = 15.0


def extract_speaker_clip(audio_path: str, output_dir: str) -> Optional[str]:
    """
    Extract the first SPEAKER_CLIP_DURATION_S seconds of audio as a WAV clip.
    Returns path to the clip, or None on failure.
    This clip is used as speaker_wav for XTTS voice cloning.
    """
    from backend.utils.ffmpeg import ffmpeg_executable

    clip_path = os.path.join(output_dir, "speaker_ref.wav")
    cmd = [
        ffmpeg_executable(), "-y",
        "-i", audio_path,
        "-t", str(SPEAKER_CLIP_DURATION_S),
        "-ar", "22050",   # XTTS expects 22050 Hz
        "-ac", "1",
        "-acodec", "pcm_s16le",
        clip_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0 and os.path.exists(clip_path):
            logger.info(f"Speaker reference clip extracted: {clip_path}")
            return clip_path
        logger.warning(f"Speaker clip extraction failed: {result.stderr[-300:]}")
        return None
    except Exception as e:
        logger.warning(f"Speaker clip extraction error: {e}")
        return None


def detect_voice_gender(audio_path: str) -> str:
    """
    Detect voice gender from an audio file using librosa pitch (F0) analysis.
    Analyses first SPEAKER_CLIP_DURATION_S seconds for performance.

    Returns 'female' or 'male'. Defaults to 'female' on any failure.
    """
    try:
        import librosa
        import numpy as np

        logger.info(f"Analysing voice gender from: {audio_path}")

        # Load only first 15s at 22050 Hz for speed on CPU
        y, sr = librosa.load(
            audio_path,
            sr=22050,
            mono=True,
            duration=SPEAKER_CLIP_DURATION_S,
        )

        if len(y) < sr * 0.5:  # Less than 0.5s of audio — not enough
            logger.warning("Audio too short for gender detection, defaulting to 'female'")
            return "female"

        # Probabilistic YIN (pyin) for robust F0 estimation
        # fmin=C2 (~65 Hz), fmax=C7 (~2093 Hz) covers all human voices
        f0, voiced_flag, _ = librosa.pyin(
            y,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr,
        )

        # Only use voiced (non-silent, non-NaN) frames
        voiced_f0 = f0[voiced_flag & ~np.isnan(f0)]

        if len(voiced_f0) < 5:
            logger.warning("Not enough voiced frames for gender detection, defaulting to 'female'")
            return "female"

        median_f0 = float(np.median(voiced_f0))
        gender = "female" if median_f0 > GENDER_F0_THRESHOLD_HZ else "male"
        logger.info(f"Detected median F0={median_f0:.1f} Hz → gender={gender}")
        return gender

    except ImportError:
        logger.warning("librosa not installed — voice gender detection unavailable, defaulting to 'female'")
        return "female"
    except Exception as e:
        logger.warning(f"Voice gender detection failed ({e}), defaulting to 'female'")
        return "female"


def detect_voice(
    audio_path: str,
    output_dir: str,
) -> Tuple[str, Optional[str]]:
    """
    Detect voice gender AND extract speaker reference clip in one call.

    Returns:
        (gender, speaker_clip_path)
        gender: 'female' | 'male'
        speaker_clip_path: path to 15s WAV clip, or None if extraction failed
    """
    gender = detect_voice_gender(audio_path)
    clip_path = extract_speaker_clip(audio_path, output_dir)
    return gender, clip_path
