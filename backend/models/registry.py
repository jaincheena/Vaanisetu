"""
VaaniSetu — Model Registry (Singleton)
Loads Whisper + both IndicTrans2 models at startup.
Never reloads mid-operation. Thread-safe via asyncio.Lock.
"""

import logging
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger("vaanisetu.registry")


class ModelRegistry:
    """Singleton model store. Load once, use everywhere."""

    _instance: Optional["ModelRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.whisper_model = None
        self.en_indic_model = None
        self.en_indic_tokenizer = None
        self.indic_en_model = None
        self.indic_en_tokenizer = None
        self.tts_model = None

        self._whisper_loaded = False
        self._en_indic_loaded = False
        self._indic_en_loaded = False
        self._tts_loaded = False

        # Guards the on-demand indic→en load so two concurrent Reverse Bridge
        # jobs don't both try to load it.
        self._load_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public load method (called once at FastAPI startup)
    # ------------------------------------------------------------------
    def load_all(self) -> None:
        """
        Load the models a job actually needs at startup.

        indic→en (Reverse Bridge) is skipped unless asked for: an
        English-source deployment never uses it, and holding it costs ~1.2 GB
        for nothing. get_indic_pair() loads it on first use, so the mode still
        works — it just pays the load time once, when someone selects it.
        """
        from backend.config import EAGER_LOAD_REVERSE_BRIDGE

        self._load_whisper()
        self._load_en_indic()
        if EAGER_LOAD_REVERSE_BRIDGE:
            self._load_indic_en()
        else:
            logger.info("Reverse Bridge (indic→en) deferred until first use")
        self._load_tts()

    # ------------------------------------------------------------------
    # Whisper
    # ------------------------------------------------------------------
    def _load_whisper(self) -> None:
        from backend.config import WHISPER_MODEL, WHISPER_MODEL_DIR
        try:
            import whisper
            logger.info(f"Loading Whisper {WHISPER_MODEL} ...")
            self.whisper_model = whisper.load_model(
                WHISPER_MODEL,
                download_root=str(WHISPER_MODEL_DIR),
                device="cpu",
            )
            self._whisper_loaded = True
            logger.info("Whisper loaded ✓")
        except Exception as e:
            logger.error(f"Whisper load failed: {e}")

    # ------------------------------------------------------------------
    # IndicTrans2 en→indic
    # ------------------------------------------------------------------
    def _load_en_indic(self) -> None:
        from backend.config import INDIC_EN_INDIC_PATH, INDIC_EN_INDIC_HF
        self.en_indic_tokenizer, self.en_indic_model = self._load_indic_model(
            "en-indic", INDIC_EN_INDIC_PATH, INDIC_EN_INDIC_HF
        )
        if self.en_indic_model:
            self._en_indic_loaded = True

    # ------------------------------------------------------------------
    # IndicTrans2 indic→en
    # ------------------------------------------------------------------
    def _load_indic_en(self) -> None:
        from backend.config import INDIC_INDIC_EN_PATH, INDIC_INDIC_EN_HF
        self.indic_en_tokenizer, self.indic_en_model = self._load_indic_model(
            "indic-en", INDIC_INDIC_EN_PATH, INDIC_INDIC_EN_HF
        )
        if self.indic_en_model:
            self._indic_en_loaded = True

    def _load_indic_model(self, name: str, local_path: str, hf_id: str):
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            import torch

            path = Path(local_path)
            # Prefer local saved weights; fall back to HF hub during setup
            source = str(path) if (path / "config.json").exists() else hf_id
            logger.info(f"Loading IndicTrans2 {name} from {source} ...")

            kwargs = {"trust_remote_code": True}
            if source == str(path):
                kwargs["local_files_only"] = True

            tokenizer = AutoTokenizer.from_pretrained(source, **kwargs)
            model = AutoModelForSeq2SeqLM.from_pretrained(
                source,
                torch_dtype=torch.float32,
                **kwargs,
            )
            model = model.to("cpu")
            model.eval()
            logger.info(f"IndicTrans2 {name} loaded ✓")
            return tokenizer, model
        except Exception as e:
            logger.error(f"IndicTrans2 {name} load failed: {e}")
            return None, None

    # ------------------------------------------------------------------
    # Coqui TTS (optional — graceful degrade if model absent)
    # ------------------------------------------------------------------
    def _load_tts(self) -> None:
        from backend.config import COQUI_TTS_MODEL_DIR, COQUI_TTS_MODEL_NAME
        try:
            from TTS.api import TTS
            tts_dir = Path(COQUI_TTS_MODEL_DIR)
            if not tts_dir.exists():
                logger.warning("Coqui TTS model directory not found — TTS disabled")
                return
            logger.info("Loading Coqui TTS ...")
            self.tts_model = TTS(
                model_path=str(tts_dir),
                config_path=str(tts_dir / "config.json"),
                progress_bar=False,
            )
            self._tts_loaded = True
            logger.info("Coqui TTS loaded ✓")
        except Exception as e:
            logger.warning(f"Coqui TTS load failed (TTS disabled): {e}")

    # ------------------------------------------------------------------
    # Replica factories (see backend/models/pool.py)
    # ------------------------------------------------------------------
    # Each call returns an INDEPENDENT instance. Two threads holding separate
    # replicas can run inference at the same time; two threads sharing one
    # cannot. Returning None means "no more replicas" and the pool stops asking.
    def make_en_indic_replica(self):
        """A fresh (tokenizer, model) pair for en→indic, or None on failure."""
        from backend.config import INDIC_EN_INDIC_PATH, INDIC_EN_INDIC_HF
        tokenizer, model = self._load_indic_model(
            "en-indic replica", INDIC_EN_INDIC_PATH, INDIC_EN_INDIC_HF
        )
        return (tokenizer, model) if model is not None else None

    def make_tts_replica(self):
        """A fresh Coqui TTS instance, or None if TTS is unavailable."""
        from backend.config import COQUI_TTS_MODEL_DIR
        try:
            from TTS.api import TTS
            tts_dir = Path(COQUI_TTS_MODEL_DIR)
            if not tts_dir.exists():
                return None
            return TTS(
                model_path=str(tts_dir),
                config_path=str(tts_dir / "config.json"),
                progress_bar=False,
            )
        except Exception as e:
            logger.warning(f"TTS replica load failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------
    @property
    def models_status(self) -> dict[str, bool]:
        return {
            "whisper":   self._whisper_loaded,
            "en_indic":  self._en_indic_loaded,
            "indic_en":  self._indic_en_loaded,
            "tts":       self._tts_loaded,
        }

    def get_indic_pair(self, source_lang: str):
        """
        Return (tokenizer, model) for the correct direction.

        indic→en is loaded on demand: startup skips it unless
        EAGER_LOAD_REVERSE_BRIDGE is set, so the first Reverse Bridge job pays
        the load once and every English-source job saves the memory entirely.
        """
        if source_lang == "English":
            return self.en_indic_tokenizer, self.en_indic_model

        if not self._indic_en_loaded:
            with self._load_lock:
                if not self._indic_en_loaded:
                    logger.info("Reverse Bridge selected — loading indic→en now")
                    self._load_indic_en()

        return self.indic_en_tokenizer, self.indic_en_model


# Global singleton instance
registry = ModelRegistry()
