"""
VaaniSetu — FFmpeg utilities
Centralizes ffmpeg/ffprobe discovery and PATH handling.
"""

import os
import shutil
from pathlib import Path

from backend.config import FFMPEG_PATH, FFPROBE_PATH


def _add_to_path(directory: str) -> None:
    if not directory:
        return

    paths = os.environ.get("PATH", "").split(os.pathsep)
    if directory not in paths:
        os.environ["PATH"] = os.pathsep.join([directory] + paths)


def ensure_ffmpeg_on_path() -> None:
    for executable in (FFMPEG_PATH, FFPROBE_PATH):
        if executable:
            directory = str(Path(executable).parent)
            if Path(executable).exists():
                _add_to_path(directory)


def ffmpeg_executable() -> str:
    if FFMPEG_PATH and Path(FFMPEG_PATH).exists():
        return str(FFMPEG_PATH)
    found = shutil.which("ffmpeg")
    if found:
        return found
    raise FileNotFoundError(
        "FFmpeg executable not found. Install FFmpeg and add it to PATH, "
        "or set the VAANISETU_FFMPEG environment variable."
    )


def ffprobe_executable() -> str:
    if FFPROBE_PATH and Path(FFPROBE_PATH).exists():
        return str(FFPROBE_PATH)
    found = shutil.which("ffprobe")
    if found:
        return found
    raise FileNotFoundError(
        "ffprobe executable not found. Install FFmpeg and add it to PATH, "
        "or set the VAANISETU_FFPROBE environment variable."
    )
