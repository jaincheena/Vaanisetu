"""
VaaniSetu — File Utilities
SHA-256 hashing, deduplication, safe filenames.
"""

import hashlib
import re
import uuid
from pathlib import Path


def sha256_file(path: str | Path) -> str:
    """Return hex SHA-256 of file contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def tm_cache_key(src_lang: str, tgt_lang: str, text: str) -> str:
    """Translation Memory cache key per spec."""
    raw = f"{src_lang}|{tgt_lang}|{text.strip().lower()}"
    return sha256_text(raw)


def safe_filename(name: str) -> str:
    """Strip unsafe chars, keep extension."""
    stem = Path(name).stem
    suffix = Path(name).suffix
    stem = re.sub(r"[^\w\-.]", "_", stem)[:80]
    return stem + suffix


def new_job_id() -> str:
    return str(uuid.uuid4())


def job_workspace(job_id: str) -> Path:
    from backend.config import WORKSPACE_DIR
    p = WORKSPACE_DIR / job_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def job_zip_path(job_id: str) -> Path:
    from backend.config import OUTPUTS_DIR
    return OUTPUTS_DIR / f"{job_id}.zip"
