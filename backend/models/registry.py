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

    # ------------------------------------------------------------------
    # Public load method (called once at FastAPI startup)
    # ------------------------------------------------------------------
    def load_all(self) -> None:
        """Load all models. Called from FastAPI lifespan."""
        self._load_whisper()
        self._load_en_indic()
        self._load_indic_en()
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
            import os
            import torch
            from pathlib import Path
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
 
            path = Path(local_path)
            # Prefer local saved weights; fall back to HF hub during setup
            source = str(path) if (path / "config.json").exists() else hf_id
            logger.info(f"Loading IndicTrans2 {name} from {source} ...")
 

            is_local = source == str(path)
            token = os.getenv("HF_TOKEN") if not is_local else None

            tokenizer = AutoTokenizer.from_pretrained(
                source,
                trust_remote_code=True,
                use_fast=False,
                local_files_only=is_local,
                token=token,
            )
 
            model = AutoModelForSeq2SeqLM.from_pretrained(
                source,
                trust_remote_code=True,
                local_files_only=is_local,
                torch_dtype=torch.float32,
                token=token,
            )
 
            model = model.to("cpu")
            model.eval()
 
            logger.info(f"IndicTrans2 {name} loaded ✓")
 
            return tokenizer, model
 
        except Exception as e:
            logger.exception(f"IndicTrans2 {name} load failed")
            return None, None

    # ------------------------------------------------------------------
    # Coqui TTS (optional — graceful degrade if model absent)
    # ------------------------------------------------------------------
    def _load_tts(self) -> None:
        from backend.config import COQUI_TTS_MODEL_DIR, COQUI_TTS_MODEL_NAME
        try:
            # Workaround for PyTorch 2.x `weights_only` security change. The XTTS
            # model checkpoint contains pickled Python objects, which torch.load now
            # blocks by default. We need to explicitly allowlist the required classes.
            try:
                import torch
 
                if hasattr(torch.serialization, "add_safe_globals"):
                    from TTS.tts.models.xtts import (
                        XttsAudioConfig,
                        XttsArgs,
                    )
                    from TTS.tts.configs.xtts_config import XttsConfig
 
                    torch.serialization.add_safe_globals([
                        XttsConfig,
                        XttsArgs,
                        XttsAudioConfig,
                    ])
            except Exception as e:
                logger.warning(f"Safe globals registration failed: {e}")

            from TTS.api import TTS
 
            logger.info("Loading XTTS...")
 
            self.tts_model = TTS(
                model_name=COQUI_TTS_MODEL_NAME,
                gpu=False,
            )
 
            self._tts_loaded = True
 
            logger.info("XTTS loaded ✓")
 
        except Exception:
            logger.exception("XTTS failed to load")

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
        """Return (tokenizer, model) for correct direction."""
        from backend.config import LANG_CODES
        if source_lang == "English":
            return self.en_indic_tokenizer, self.en_indic_model
        return self.indic_en_tokenizer, self.indic_en_model


# Global singleton instance
registry = ModelRegistry()
