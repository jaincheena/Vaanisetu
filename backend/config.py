"""
VaaniSetu — Central Configuration
All paths and constants live here. Change once, applies everywhere.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Base directories (stored on C:\VaaniSetu\ to keep models off repo drive)
# ---------------------------------------------------------------------------
BASE_DIR = Path(os.getenv("VAANISETU_BASE", r"C:\VaaniSetu"))
MODEL_DIR      = BASE_DIR / "models"
WORKSPACE_DIR  = BASE_DIR / "workspace"
OUTPUTS_DIR    = BASE_DIR / "outputs"
UPLOADS_DIR    = BASE_DIR / "uploads"
DB_PATH        = BASE_DIR / "vaanisetu.db"
FONTS_DIR      = Path(__file__).parent.parent / "fonts"

# Create dirs at import time (setup.bat also does this, belt-and-suspenders)
for _d in [MODEL_DIR, WORKSPACE_DIR, OUTPUTS_DIR, UPLOADS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

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
# Server
# ---------------------------------------------------------------------------
HOST = "0.0.0.0"
PORT = 8765

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
    ".mp3", ".wav", ".ogg", ".m4a", ".flac",  # audio
    ".txt", ".pdf", ".docx", ".csv",          # text/docs
}
