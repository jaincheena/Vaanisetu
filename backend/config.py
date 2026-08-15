"""
VaaniSetu — Central Configuration
All paths and constants live here. Change once, applies everywhere.
"""

import logging
import os
import secrets
import sys
from pathlib import Path

logger = logging.getLogger("vaanisetu.config")

# ---------------------------------------------------------------------------
# Base directories
# ---------------------------------------------------------------------------
# Models, uploads and the database are deliberately kept off the repo drive.
# The default is per-OS so that importing this module works everywhere; a
# deployment can always pin it with VAANISETU_BASE.
def _default_base_dir() -> Path:
    if os.name == "nt":
        return Path(r"C:\VaaniSetu")
    return Path.home() / ".vaanisetu"


BASE_DIR = Path(os.getenv("VAANISETU_BASE", str(_default_base_dir())))
MODEL_DIR      = BASE_DIR / "models"
WORKSPACE_DIR  = BASE_DIR / "workspace"
OUTPUTS_DIR    = BASE_DIR / "outputs"
UPLOADS_DIR    = BASE_DIR / "uploads"
DB_PATH        = BASE_DIR / "vaanisetu.db"
FONTS_DIR      = Path(__file__).parent.parent / "fonts"

# Create dirs at import time (setup.bat also does this, belt-and-suspenders).
# A read-only or missing base path is an operator problem, so say so clearly
# instead of surfacing a bare PermissionError from an unrelated import.
try:
    for _d in [MODEL_DIR, WORKSPACE_DIR, OUTPUTS_DIR, UPLOADS_DIR]:
        _d.mkdir(parents=True, exist_ok=True)
except OSError as exc:
    sys.exit(
        f"VaaniSetu cannot create its data directories under {BASE_DIR}: {exc}\n"
        f"Set VAANISETU_BASE to a writable location and start again."
    )

# ---------------------------------------------------------------------------
# Security / auth
# ---------------------------------------------------------------------------
# The JWT signing key must never live in source control. Resolution order:
#   1. VAANISETU_JWT_SECRET               (preferred for real deployments)
#   2. <BASE_DIR>/.jwt_secret             (auto-generated once, chmod 0600)
#   3. a process-random key               (tokens die with the process)
# Option 3 is the safe-fail path: sessions break on restart, nothing leaks.
JWT_SECRET_FILE = BASE_DIR / ".jwt_secret"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("VAANISETU_TOKEN_TTL_MINUTES", str(60 * 24 * 7)))


def _resolve_jwt_secret() -> str:
    from_env = os.getenv("VAANISETU_JWT_SECRET", "").strip()
    if from_env:
        return from_env

    try:
        if JWT_SECRET_FILE.exists():
            existing = JWT_SECRET_FILE.read_text(encoding="utf-8").strip()
            if existing:
                return existing

        generated = secrets.token_urlsafe(64)
        JWT_SECRET_FILE.write_text(generated, encoding="utf-8")
        try:
            os.chmod(JWT_SECRET_FILE, 0o600)
        except OSError:
            # Windows ACLs do not map onto POSIX modes; the file is still
            # outside the repo and readable only by the running account.
            pass
        logger.info(f"Generated a new JWT signing key at {JWT_SECRET_FILE}")
        return generated
    except OSError as exc:
        logger.warning(
            f"Could not persist a JWT signing key ({exc}); using an ephemeral "
            "key. All sessions will be invalidated when the server restarts."
        )
        return secrets.token_urlsafe(64)


JWT_SECRET_KEY = _resolve_jwt_secret()

# Bootstrap administrator. There is no shared default password: either the
# operator supplies one, or the server generates a single-use random password
# and prints it to the startup log exactly once.
ADMIN_USERNAME = os.getenv("VAANISETU_ADMIN_USER", "admin").strip() or "admin"
ADMIN_PASSWORD = os.getenv("VAANISETU_ADMIN_PASSWORD", "").strip() or None
MIN_PASSWORD_LENGTH = int(os.getenv("VAANISETU_MIN_PASSWORD_LENGTH", "10"))

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
HOST = os.getenv("VAANISETU_HOST", "0.0.0.0")
PORT = int(os.getenv("VAANISETU_PORT", "8765"))

# CORS. The production build is served from this same origin, so the browser
# never needs a cross-origin grant; the allowlist exists for the Vite dev
# server and for LAN tablets hitting the box by IP. A wildcard origin is not
# valid alongside credentialed requests and is never used here.
def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


CORS_ALLOWED_ORIGINS = _csv_env(
    "VAANISETU_CORS_ORIGINS",
    f"http://localhost:{PORT},http://127.0.0.1:{PORT},http://localhost:5173,http://127.0.0.1:5173",
)

# Private-LAN ranges only (RFC 1918). Public origins must be listed explicitly.
CORS_ALLOW_ORIGIN_REGEX = os.getenv(
    "VAANISETU_CORS_ORIGIN_REGEX",
    r"^https?://(localhost|127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|192\.168\.\d{1,3}\.\d{1,3}"
    r"|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(:\d+)?$",
)

# ---------------------------------------------------------------------------
# Model paths
# ---------------------------------------------------------------------------
WHISPER_MODEL        = os.getenv("WHISPER_MODEL", "large-v3-turbo")
WHISPER_MODEL_DIR    = MODEL_DIR / "whisper"

# FFmpeg / ffprobe executable paths
FFMPEG_PATH = os.getenv("VAANISETU_FFMPEG", "ffmpeg")
FFPROBE_PATH = os.getenv("VAANISETU_FFPROBE", "ffprobe")

INDIC_EN_INDIC_PATH  = str(MODEL_DIR / "indictrans2-en-indic")
INDIC_INDIC_EN_PATH  = str(MODEL_DIR / "indictrans2-indic-en")

# Remote IDs (used during download_models.bat only)
INDIC_EN_INDIC_HF    = "ai4bharat/indictrans2-en-indic-dist-200M"
INDIC_INDIC_EN_HF    = "ai4bharat/indictrans2-indic-en-dist-200M"

COQUI_TTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
COQUI_TTS_MODEL_DIR  = str(MODEL_DIR / "tts_models/multilingual/multi-dataset/xtts_v2")

# ---------------------------------------------------------------------------
# Concurrency (see backend/utils/resources.py)
# ---------------------------------------------------------------------------
# RAM left to the OS before we allocate any worker.
CONCURRENCY_HEADROOM_GB = float(os.getenv("VAANISETU_RAM_HEADROOM_GB", "2.0"))

# Peak additional RSS one unit of work needs. "job" covers a whole pipeline
# (Whisper activations + ffmpeg + buffers); "generate" is one language's
# output set, dominated by the ffmpeg subtitle burn.
CONCURRENCY_TASK_COST_GB = {
    "job":      float(os.getenv("VAANISETU_JOB_COST_GB", "1.5")),
    "generate": float(os.getenv("VAANISETU_GEN_COST_GB", "0.6")),
}

def _optional_int(name: str):
    """An env-var ceiling, or None meaning 'let the hardware decide'."""
    raw = os.getenv(name)
    return int(raw) if raw else None


# No fixed ceiling — width comes from free RAM and the machine's core count.
# Set these only to pin a deployment to a known number.
CONCURRENCY_MAX = {
    "job":      _optional_int("VAANISETU_MAX_JOBS"),
    "generate": _optional_int("VAANISETU_MAX_GENERATE"),
}

# ---------------------------------------------------------------------------
# Model replica pools (see backend/models/pool.py)
# ---------------------------------------------------------------------------
# Extra copies of a model let two jobs use it at once instead of queueing.
# Cost is per additional replica, measured as loaded weights + inference
# activations. Whisper is deliberately absent — at ~5 GB a copy it is far too
# expensive to duplicate, and it runs once per job rather than once per language.
MODEL_REPLICA_COST_GB = {
    "translate": float(os.getenv("VAANISETU_TRANSLATE_REPLICA_GB", "1.2")),
    "tts":       float(os.getenv("VAANISETU_TTS_REPLICA_GB", "2.5")),
}

# Again no fixed number — replica count is free RAM divided by replica cost.
MODEL_POOL_MAX = {
    "translate": _optional_int("VAANISETU_TRANSLATE_POOL"),
    "tts":       _optional_int("VAANISETU_TTS_POOL"),
}

# Resident size of each model once loaded. Used by the startup preflight to
# tell a user their machine is too small BEFORE it spends ten minutes swapping.
MODEL_FOOTPRINT_GB = {
    "whisper":  float(os.getenv("VAANISETU_WHISPER_GB", "5.0")),
    "en_indic": float(os.getenv("VAANISETU_EN_INDIC_GB", "1.2")),
    "indic_en": float(os.getenv("VAANISETU_INDIC_EN_GB", "1.2")),
    "tts":      float(os.getenv("VAANISETU_TTS_GB", "2.5")),
}

# Python + torch + FastAPI before any model is loaded.
RUNTIME_OVERHEAD_GB = float(os.getenv("VAANISETU_RUNTIME_GB", "1.5"))

# Reverse Bridge (Indian language → English) loads a second IndicTrans2 set.
# English-source deployments never touch it, so it loads on first use instead
# of at startup — saving ~1.2 GB for the common case without losing the mode.
EAGER_LOAD_REVERSE_BRIDGE = os.getenv("VAANISETU_EAGER_REVERSE_BRIDGE", "0") == "1"

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
BATCH_SIZE = 8            # IndicTrans2 segments per batch
AUDIO_SAMPLE_RATE = 16000 # Whisper expects 16 kHz mono WAV
TRANSLATION_MAX_LENGTH = 256  # Maximum sequence length for IndicTrans2

# ---------------------------------------------------------------------------
# Confidence thresholds
# ---------------------------------------------------------------------------
CONFIDENCE_GREEN  = 0.85
CONFIDENCE_AMBER  = 0.65
TM_CACHE_HIT_MIN  = 0.85     # min confidence to use TM hit
TM_STORE_MIN      = 0.70     # min confidence to store in TM
GLOSSARY_MIN_USES = 3
GLOSSARY_MIN_CONF = 0.85

# ---------------------------------------------------------------------------
# 22 official Indian languages — IndicTrans2 FLORES-200 codes
# ---------------------------------------------------------------------------
LANG_CODES: dict[str, str] = {
    "Hindi":     "hin_Deva",
    "Bengali":   "ben_Beng",
    "Telugu":    "tel_Telu",
    "Marathi":   "mar_Deva",
    "Tamil":     "tam_Taml",
    "Gujarati":  "guj_Gujr",
    "Urdu":      "urd_Arab",
    "Kannada":   "kan_Knda",
    "Odia":      "ory_Orya",
    "Malayalam": "mal_Mlym",
    "Punjabi":   "pan_Guru",
    "Assamese":  "asm_Beng",
    "Maithili":  "mai_Deva",
    "Sanskrit":  "san_Deva",
    "Konkani":   "kok_Deva",
    "Sindhi":    "snd_Arab",
    "Dogri":     "doi_Deva",
    "Kashmiri":  "kas_Arab",
    "Manipuri":  "mni_Mtei",
    "Nepali":    "npi_Deva",
    "Bodo":      "brx_Deva",
    "Santhali":  "sat_Olck",
}

LANG_NAMES_BY_CODE: dict[str, str] = {v: k for k, v in LANG_CODES.items()}

ENGLISH_CODE = "eng_Latn"

# ---------------------------------------------------------------------------
# Whisper language codes — single source of truth
# ---------------------------------------------------------------------------
# The transcriber maps a display name to Whisper's own two/three-letter code;
# the processor needs the reverse to resolve an Auto-Detect job. Both live
# here so the two directions can never drift apart.
WHISPER_LANG_CODES: dict[str, str] = {
    "Hindi":     "hi",
    "Bengali":   "bn",
    "Telugu":    "te",
    "Marathi":   "mr",
    "Tamil":     "ta",
    "Gujarati":  "gu",
    "Urdu":      "ur",
    "Kannada":   "kn",
    "Odia":      "or",
    "Malayalam": "ml",
    "Punjabi":   "pa",
    "Assamese":  "as",
    "Maithili":  "mai",
    "Sanskrit":  "sa",
    "Konkani":   "gom",
    "Sindhi":    "sd",
    "Nepali":    "ne",
    "English":   "en",
}

WHISPER_TO_NAME: dict[str, str] = {v: k for k, v in WHISPER_LANG_CODES.items()}

# ---------------------------------------------------------------------------
# Impact ledger defaults
# ---------------------------------------------------------------------------
DEFAULT_FARMERS_PER_HOUR  = 120
DEFAULT_RATE_PER_MIN      = 850   # ₹ per minute of translation

# ---------------------------------------------------------------------------
# File limits
# ---------------------------------------------------------------------------
MAX_UPLOAD_MB = 2048   # 2 GB
ALLOWED_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".webm",  # video
    ".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".opus", ".3gp", ".amr", ".caf", ".wma",  # phone/offline audio
    ".txt", ".pdf", ".docx", ".csv",          # text/docs
}
