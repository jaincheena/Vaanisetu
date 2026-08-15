"""
VaaniSetu — Model Registry (Singleton)
Loads Whisper + both IndicTrans2 models at startup.
Never reloads mid-operation. Thread-safe via asyncio.Lock.
"""

import sys
import types
import logging
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger("vaanisetu.registry")

# Compatibility patch for IndicTrans2 custom config (references removed transformers.onnx)
try:
    import transformers.onnx
except ModuleNotFoundError:
    dummy_onnx = types.ModuleType("transformers.onnx")
    dummy_onnx.OnnxConfig = object
    dummy_onnx.OnnxSeq2SeqConfigWithPast = object
    dummy_onnx.__path__ = []  # Make transformers.onnx a package

    dummy_onnx_utils = types.ModuleType("transformers.onnx.utils")
    dummy_onnx_utils.compute_effective_axis_dimension = lambda *args, **kwargs: None

    sys.modules["transformers.onnx"] = dummy_onnx
    sys.modules["transformers.onnx.utils"] = dummy_onnx_utils

# Compatibility patch for IndicTransTokenizer in newer transformers (_special_tokens_map)
try:
    from transformers.tokenization_utils_base import PreTrainedTokenizerBase
    _orig_setattr = PreTrainedTokenizerBase.__setattr__
    def _patched_setattr(self, key, value):
        if key in ("unk_token", "bos_token", "eos_token", "pad_token") and not hasattr(self, "_special_tokens_map"):
            object.__setattr__(self, "_special_tokens_map", {})
        _orig_setattr(self, key, value)
    PreTrainedTokenizerBase.__setattr__ = _patched_setattr
except Exception:
    pass

# Compatibility patch for dynamic HuggingFace modules (IndicTrans2 tie_weights)
try:
    import transformers.dynamic_module_utils
    _orig_get_class = transformers.dynamic_module_utils.get_class_from_dynamic_module
    def _patched_get_class(*args, **kwargs):
        cls = _orig_get_class(*args, **kwargs)
        if isinstance(cls, type) and hasattr(cls, "tie_weights"):
            orig_tie = getattr(cls, "tie_weights")
            def safe_tie(self, *a, **k):
                try:
                    return orig_tie(self)
                except Exception:
                    pass
            cls.tie_weights = safe_tie
        return cls

    transformers.dynamic_module_utils.get_class_from_dynamic_module = _patched_get_class
    import transformers.models.auto.auto_factory
    transformers.models.auto.auto_factory.get_class_from_dynamic_module = _patched_get_class
except Exception:
    pass
try:
    import transformers.cache_utils as cu
    if hasattr(cu, "EncoderDecoderCache") and not hasattr(cu.EncoderDecoderCache, "__getitem__"):
        def _edc_getitem(self, idx):
            try:
                return (self.self_attention_cache.key_cache[idx], self.self_attention_cache.value_cache[idx])
            except Exception:
                return (None, None)
        cu.EncoderDecoderCache.__getitem__ = _edc_getitem
    if hasattr(cu, "DynamicCache") and not hasattr(cu.DynamicCache, "__getitem__"):
        def _dc_getitem(self, idx):
            try:
                return (self.key_cache[idx], self.value_cache[idx])
            except Exception:
                return (None, None)
        cu.DynamicCache.__getitem__ = _dc_getitem
except Exception:
    pass





# Compatibility patch for Coqui TTS / torchaudio (torchcodec missing in PyTorch 2.4+)
try:
    import torchcodec
except ModuleNotFoundError:
    import importlib.machinery
    dummy_tc = types.ModuleType("torchcodec")
    dummy_tc.__spec__ = importlib.machinery.ModuleSpec("torchcodec", None)
    dummy_tc_dec = types.ModuleType("torchcodec.decoders")
    dummy_tc_dec.__spec__ = importlib.machinery.ModuleSpec("torchcodec.decoders", None)
    sys.modules["torchcodec"] = dummy_tc
    sys.modules["torchcodec.decoders"] = dummy_tc_dec



# Compatibility patch for Coqui TTS (references missing is_torch_greater_or_equal and is_torchcodec_available)
try:
    import transformers.utils.import_utils
    if not hasattr(transformers.utils.import_utils, "is_torch_greater_or_equal"):
        def is_torch_greater_or_equal(version_str):
            if version_str == "2.9":
                return False
            import torch
            from packaging import version
            try:
                return version.parse(torch.__version__.split("+")[0]) >= version.parse(version_str)
            except Exception:
                return False
        transformers.utils.import_utils.is_torch_greater_or_equal = is_torch_greater_or_equal

    if not hasattr(transformers.utils.import_utils, "is_torchcodec_available"):
        transformers.utils.import_utils.is_torchcodec_available = lambda: False
except Exception:
    pass



# Compatibility patch for torchaudio.load when torchcodec is not installed
try:
    import torchaudio
    _orig_ta_load = torchaudio.load
    def _patched_ta_load(uri, *args, **kwargs):
        kwargs.pop("backend", None)
        try:
            return _orig_ta_load(uri, *args, **kwargs)
        except Exception:
            import soundfile as sf
            import torch
            data, samplerate = sf.read(uri)
            tensor = torch.from_numpy(data).float()
            if tensor.dim() == 1:
                tensor = tensor.unsqueeze(0)
            elif tensor.dim() == 2:
                tensor = tensor.t()
            return tensor, samplerate
    torchaudio.load = _patched_ta_load
except Exception:
    pass







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

        # Guards on-demand indic→en load so concurrent Reverse Bridge jobs don't collide
        self._load_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public load method (called once at FastAPI startup)
    # ------------------------------------------------------------------
    def load_all(self) -> None:
        """Load all models. Called from FastAPI lifespan."""
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
    # Coqui TTS
    # ------------------------------------------------------------------
    def _load_tts(self) -> None:
        from backend.config import COQUI_TTS_MODEL_DIR, COQUI_TTS_MODEL_NAME
        try:
            # Compatibility monkey-patch for newer transformers/torch with coqui-tts
            import transformers.utils.import_utils as iu
            import transformers.pytorch_utils as pu
            import torch
            from packaging import version

            def is_torch_greater_or_equal(target_version, *args, **kwargs):
                if target_version == "2.9":
                    return False
                v = torch.__version__.split('+')[0]
                return version.parse(v) >= version.parse(target_version)

            iu.is_torch_greater_or_equal = is_torch_greater_or_equal

            if not hasattr(iu, 'is_torchcodec_available'):
                iu.is_torchcodec_available = lambda: True

            pu.isin_mps_friendly = lambda elements, test_elements: torch.isin(elements, test_elements)

            # Workaround for PyTorch 2.x `weights_only` security change.
            if hasattr(torch.serialization, "add_safe_globals"):
                try:
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
                except Exception:
                    pass

            from TTS.api import TTS

            logger.info("Loading XTTS...")

            self.tts_model = TTS(
                model_name=COQUI_TTS_MODEL_NAME,
                gpu=False,
            )

            self._tts_loaded = True

            logger.info("XTTS loaded ✓")

        except Exception as e:
            logger.warning(f"XTTS failed to load (will fallback to gTTS if needed): {e}")

    # ------------------------------------------------------------------
    # Replica factories (see backend/models/pool.py)
    # ------------------------------------------------------------------
    def make_en_indic_replica(self):
        """A fresh (tokenizer, model) pair for en→indic, or None on failure."""
        from backend.config import INDIC_EN_INDIC_PATH, INDIC_EN_INDIC_HF
        tokenizer, model = self._load_indic_model(
            "en-indic replica", INDIC_EN_INDIC_PATH, INDIC_EN_INDIC_HF
        )
        return (tokenizer, model) if model is not None else None

    def make_tts_replica(self):
        """A fresh Coqui TTS instance, or None if TTS is unavailable."""
        from backend.config import COQUI_TTS_MODEL_DIR, COQUI_TTS_MODEL_NAME
        try:
            from TTS.api import TTS
            tts_dir = Path(COQUI_TTS_MODEL_DIR)
            if tts_dir.exists():
                return TTS(
                    model_path=str(tts_dir),
                    config_path=str(tts_dir / "config.json"),
                    progress_bar=False,
                    gpu=False,
                )
            return TTS(
                model_name=COQUI_TTS_MODEL_NAME,
                gpu=False,
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
        """Return (tokenizer, model) for correct direction."""
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
