"""
VaaniSetu — Central Configuration
All paths and constants live here. Change once, applies everywhere.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger("vaanisetu.config")


# ---------------------------------------------------------------------------
# Device auto-detection
# ---------------------------------------------------------------------------
def detect_device() -> str:
    """Return 'cuda' if a usable GPU is present, else 'cpu'.

    Most BAIF field laptops have no GPU — the entire pipeline is optimised
    for CPU-first operation.  When a GPU *is* available this gives a 10-30×
    boost across Whisper, IndicTrans2 and XTTS with zero user configuration.
    """
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            logger.info(f"GPU detected: {name} — using CUDA")
            return "cuda"
    except Exception:
        pass
    logger.info("No GPU detected — running on CPU")
    return "cpu"


def detect_gpu_available() -> bool:
    return detect_device() == "cuda"


# Cached at import time so every loader reads the same value.
DEVICE = os.getenv("VAANISETU_DEVICE", "") or detect_device()

# ---------------------------------------------------------------------------
# Base directories (stored on C:\VaaniSetu\ to keep models off repo drive)
# ---------------------------------------------------------------------------
BASE_DIR = Path(os.getenv("VAANISETU_BASE", r"C:\VaaniSetu"))
MODEL_DIR      = BASE_DIR / "models"
WORKSPACE_DIR  = BASE_DIR / "workspace"
OUTPUTS_DIR    = BASE_DIR / "outputs"
UPLOADS_DIR    = BASE_DIR / "uploads"
LOGS_DIR       = BASE_DIR / "logs"
DB_PATH        = BASE_DIR / "vaanisetu.db"
FONTS_DIR      = Path(__file__).parent.parent / "fonts"

# Create dirs at import time (setup.bat also does this, belt-and-suspenders)
for _d in [MODEL_DIR, WORKSPACE_DIR, OUTPUTS_DIR, UPLOADS_DIR, LOGS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# Configure rotating file logging for operational readiness
try:
    from logging.handlers import RotatingFileHandler
    log_file = str(LOGS_DIR / "vaanisetu.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"))
    logging.getLogger("vaanisetu").addHandler(file_handler)
    logging.getLogger("vaanisetu").setLevel(logging.INFO)
except Exception as e:
    logger.warning(f"Could not initialize rotating file log handler: {e}")

# ---------------------------------------------------------------------------
# Model paths
# ---------------------------------------------------------------------------
def _get_default_whisper_model() -> str:
    user_set = os.getenv("WHISPER_MODEL")
    if user_set:
        return user_set
    try:
        import psutil
        vm = psutil.virtual_memory()
        free_gb = vm.available / (1024 ** 3)
        total_gb = vm.total / (1024 ** 3)
        if total_gb <= 8.5 or free_gb < 3.0:
            return "tiny"   # ~75MB weights, uses only ~120MB RAM
        elif free_gb < 6.0:
            return "base"   # ~140MB weights, uses only ~220MB RAM
        elif free_gb < 10.0:
            return "small"  # ~460MB weights, uses ~700MB RAM
        else:
            return "large-v3-turbo"
    except Exception:
        return "base" if DEVICE == "cpu" else "large-v3-turbo"

WHISPER_MODEL        = _get_default_whisper_model()
WHISPER_MODEL_DIR    = MODEL_DIR / "whisper"
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE",
                                  "float16" if DEVICE == "cuda" else "int8")

def is_low_ram_device() -> bool:
    try:
        import psutil
        vm = psutil.virtual_memory()
        return (vm.total / (1024 ** 3)) <= 8.5 or (vm.available / (1024 ** 3)) < 4.0 or DEVICE == "cpu"
    except Exception:
        return DEVICE == "cpu"

IS_LOW_RAM = is_low_ram_device()
LAZY_LOAD_MODELS = os.getenv("VAANISETU_LAZY_LOAD", "1" if IS_LOW_RAM else "0") == "1"

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

# Piper TTS (ONNX-based, lightweight CPU engine)
PIPER_VOICES_DIR     = MODEL_DIR / "piper"
PIPER_VOICES_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_TTS_ENGINE   = os.getenv("VAANISETU_TTS_ENGINE", "piper")  # piper | xtts | gtts

# Map display language name → Piper voice model stem (without .onnx)
# Only languages with available Piper voices are listed; others fall back.
PIPER_VOICE_MAP: dict[str, str] = {
    "Hindi":     "hi_IN-swara-medium",
    "Bengali":   "bn_BD-sishir-medium",
    "Gujarati":  "gu_IN-bagicha-medium",
    "Kannada":   "kn_IN-lili-medium",
    "Marathi":   "mr_IN-vani-medium",
    "Tamil":     "ta_IN-anbu-medium",
    "Telugu":    "te_IN-anu-medium",
    "Nepali":    "ne_NP-google-medium",
    "English":   "en_US-amy-medium",
}

# Gender-specific Piper voice overrides for male voices.
# Most Indic Piper voices are female; only list languages where a
# distinct male voice model is available. For unlisted languages,
# voice_detector falls back to PIPER_VOICE_MAP (female) or XTTS cloning.
PIPER_VOICE_MAP_MALE: dict[str, str] = {
    "English":   "en_US-ryan-medium",      # en_US-ryan is a male voice
    "Hindi":     "hi_IN-swara-medium",     # Only one Piper Hindi voice currently
    "Bengali":   "bn_BD-sishir-medium",    # sishir is male
    "Gujarati":  "gu_IN-bagicha-medium",   # Fallback: single voice
    "Kannada":   "kn_IN-lili-medium",      # Fallback: single voice
    "Marathi":   "mr_IN-vani-medium",      # Fallback: single voice
}

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
HOST = "0.0.0.0"
PORT = 8765

# ---------------------------------------------------------------------------
# Concurrency (see backend/utils/resources.py)
# ---------------------------------------------------------------------------
# RAM left to the OS before we allocate any worker.
CONCURRENCY_HEADROOM_GB = float(os.getenv("VAANISETU_RAM_HEADROOM_GB", "2.0"))

# Peak additional RSS one unit of work needs. "job" covers a whole pipeline
# (Whisper activations + ffmpeg + buffers); "generate" is one language's
# output set, dominated by the ffmpeg subtitle burn.
CONCURRENCY_TASK_COST_GB = {
    "job":       float(os.getenv("VAANISETU_JOB_COST_GB", "1.5")),
    "generate":  float(os.getenv("VAANISETU_GEN_COST_GB", "0.6")),
    "translate": float(os.getenv("VAANISETU_TRANSLATE_COST_GB", "0.3")),
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
    "whisper":  float(os.getenv("VAANISETU_WHISPER_GB", "1.5")),   # INT8 via faster-whisper
    "en_indic": float(os.getenv("VAANISETU_EN_INDIC_GB", "0.8")),  # INT8 dynamic quantized
    "indic_en": float(os.getenv("VAANISETU_INDIC_EN_GB", "0.8")),  # INT8 dynamic quantized
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
TRANSLATION_NUM_BEAMS  = int(os.getenv("VAANISETU_BEAMS", "4"))
TRANSLATION_DRAFT_BEAMS = 2   # Fewer beams for draft mode speed

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
