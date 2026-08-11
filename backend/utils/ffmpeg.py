"""
VaaniSetu — FFmpeg utilities
Centralizes ffmpeg/ffprobe discovery and PATH handling.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from backend.config import FFMPEG_PATH, FFPROBE_PATH


def _add_to_path(directory: str) -> None:
    if not directory:
        return

    paths = os.environ.get("PATH", "").split(os.pathsep)
    if directory not in paths:
        os.environ["PATH"] = os.pathsep.join([directory] + paths)


def _local_bundle_dir() -> Optional[Path]:
    root = Path(__file__).resolve().parent.parent.parent
    local_bin = root / "ffmpeg-8.1.2-essentials_build" / "ffmpeg-8.1.2-essentials_build" / "bin"
    if local_bin.exists():
        return local_bin
    return None


def ensure_ffmpeg_on_path() -> None:
    for executable in (FFMPEG_PATH, FFPROBE_PATH):
        if executable and Path(executable).exists():
            _add_to_path(str(Path(executable).parent))
    bundle = _local_bundle_dir()
    if bundle:
        _add_to_path(str(bundle))


def ffmpeg_executable() -> str:
    if FFMPEG_PATH and Path(FFMPEG_PATH).exists():
        return str(FFMPEG_PATH)
    found = shutil.which("ffmpeg")
    if found:
        return found
    bundle = _local_bundle_dir()
    if bundle and (bundle / "ffmpeg.exe").exists():
        return str(bundle / "ffmpeg.exe")
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
    bundle = _local_bundle_dir()
    if bundle and (bundle / "ffprobe.exe").exists():
        return str(bundle / "ffprobe.exe")
    raise FileNotFoundError(
        "ffprobe executable not found. Install FFmpeg and add it to PATH, "
        "or set the VAANISETU_FFPROBE environment variable."
    )
