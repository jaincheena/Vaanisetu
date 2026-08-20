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
                # Forward the arguments. This guard used to call orig_tie(self)
                # and drop everything else, which on transformers 4.5x meant the
                # weights were never materialised off the meta device. The model
                # then died in .to(device) with "Cannot copy out of meta tensor",
                # the loader reported "weights not found locally", and every
                # advisory silently fell back to untranslated source text.
                try:
                    return orig_tie(self, *a, **k)
                except TypeError:
                    # Older signature that does not accept these arguments.
                    try:
                        return orig_tie(self)
                    except Exception as inner:
                        logger.warning(f"tie_weights failed for {cls.__name__}: {inner}")
                except Exception as e:
                    logger.warning(f"tie_weights failed for {cls.__name__}: {e}")

            cls.tie_weights = safe_tie

        # IndicTransTokenizer declares its vocab files as src_vocab_fp/tgt_vocab_fp
        # and then forwards src_vocab_file=/tgt_vocab_file= to PreTrainedTokenizer
        # alongside **kwargs. A tokenizer_config.json written by save_pretrained
        # also carries src_vocab_file/tgt_vocab_file — absolute paths into
        # whichever machine did the download — so both arrive and construction
        # dies with "got multiple values for keyword argument 'src_vocab_file'".
        #
        # This is not cosmetic: the loader caught it, logged "weights not found
        # locally", and fell through to _fallback_translate_segments, which
        # returns the SOURCE TEXT as the translation. Every advisory shipped
        # untranslated, in English, stamped green and cleared for distribution.
        if (
            isinstance(cls, type)
            and "src_vocab_fp" in (getattr(cls, "vocab_files_names", None) or {})
            and not getattr(cls, "_vaani_kwarg_guard", False)
        ):
            orig_init = cls.__init__

            def safe_init(self, *a, **k):
                # The correct paths come from vocab_files_names, resolved
                # against the model directory. The stale ones are dropped.
                k.pop("src_vocab_file", None)
                k.pop("tgt_vocab_file", None)
                return orig_init(self, *a, **k)

            cls.__init__ = safe_init
            cls._vaani_kwarg_guard = True
        return cls

    transformers.dynamic_module_utils.get_class_from_dynamic_module = _patched_get_class
    import transformers.models.auto.auto_factory
    transformers.models.auto.auto_factory.get_class_from_dynamic_module = _patched_get_class
    # AutoTokenizer resolves remote-code classes through its own module-level
    # import of the same name, so patching auto_factory alone never reached it.
    import transformers.models.auto.tokenization_auto
    transformers.models.auto.tokenization_auto.get_class_from_dynamic_module = _patched_get_class
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







def _materialize_meta_params(model, local_path: str) -> list[str]:
    """
    Load any parameter left on the meta device straight from the checkpoint.

    IndicTrans2 lists `decoder.embed_tokens.weight` in _tied_weights_keys, but
    the parameter is actually at `model.decoder.embed_tokens.weight`. Newer
    transformers reads that list as "skip loading, tie_weights will fill it in",
    and the custom tie_weights never does — so the tensor stays on meta even
    though it is present in model.safetensors. model.to(device) then raises
    "Cannot copy out of meta tensor", the whole load is abandoned, and the
    pipeline silently degrades to returning untranslated source text.

    Returns the names it repaired, so the caller can log them.
    """
    import torch

    meta_names = [n for n, prm in model.named_parameters() if prm.is_meta]
    if not meta_names:
        return []

    checkpoint = Path(local_path) / "model.safetensors"
    if not checkpoint.exists():
        raise RuntimeError(
            f"{len(meta_names)} parameter(s) left on the meta device and no "
            f"model.safetensors at {local_path} to recover them from: {meta_names}"
        )

    from safetensors import safe_open

    repaired = []
    with safe_open(str(checkpoint), framework="pt") as f:
        available = set(f.keys())
        for name in meta_names:
            if name not in available:
                continue
            tensor = f.get_tensor(name)
            module = model
            *path_parts, leaf = name.split(".")
            for part in path_parts:
                module = getattr(module, part)
            setattr(module, leaf, torch.nn.Parameter(tensor, requires_grad=False))
            repaired.append(name)

    # Replacing a tied parameter breaks the tie, so whatever shared it is now
    # meta in turn (lm_head follows decoder.embed_tokens here). Re-tie, then
    # bind any leftover by shape against its tie partner.
    # Replacing a tied parameter breaks the tie, so whatever shared it is now
    # meta in turn (lm_head follows decoder.embed_tokens here). Bind those to
    # the real tensor by shape. Calling model.tie_weights() here would undo the
    # repair instead — it re-points the freshly loaded embedding back at the
    # still-meta lm_head.
    remaining = [n for n, prm in model.named_parameters() if prm.is_meta]
    for name in list(remaining):
        module = model
        *path_parts, leaf = name.split(".")
        for part in path_parts:
            module = getattr(module, part)
        target_shape = getattr(module, leaf).shape
        donor = next(
            (
                prm for other, prm in model.named_parameters()
                if not prm.is_meta and prm.shape == target_shape
            ),
            None,
        )
        if donor is None:
            continue
        setattr(module, leaf, donor)   # share the tensor, as the tie intended
        repaired.append(name)

    remaining = [n for n, prm in model.named_parameters() if prm.is_meta]
    if remaining:
        raise RuntimeError(
            f"Could not recover these parameters from the checkpoint: {remaining}"
        )
    return repaired


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
        # "faster-whisper" | "openai-whisper" | None — decides whether chunked
        # parallel transcription is worth attempting.
        self.whisper_backend = None
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
        from backend.config import LAZY_LOAD_MODELS, EAGER_LOAD_REVERSE_BRIDGE

        if LAZY_LOAD_MODELS:
            logger.info("Low-RAM mode active: AI models will load on-demand just-in-time per stage (idle RAM < 60MB)")
            return

        self._load_whisper()
        self._load_en_indic()
        if EAGER_LOAD_REVERSE_BRIDGE:
            self._load_indic_en()
        else:
            logger.info("Reverse Bridge (indic→en) deferred until first use")
        self._load_tts()

    def get_whisper(self):
        """Return Whisper model, loading on-demand if needed."""
        if not self._whisper_loaded or self.whisper_model is None:
            with self._load_lock:
                if not self._whisper_loaded or self.whisper_model is None:
                    self._load_whisper()
        return self.whisper_model

    def release_whisper_if_low_ram(self) -> None:
        """Release Whisper model from memory after transcription on low-RAM laptops."""
        from backend.config import IS_LOW_RAM
        if IS_LOW_RAM and self.whisper_model is not None:
            logger.info("Low-RAM optimization: Releasing Whisper weights to reclaim memory for translation")
            self.whisper_model = None
            self._whisper_loaded = False
            self.clean_memory()

    def clean_memory(self) -> None:
        """Force garbage collection and clear PyTorch cache."""
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Whisper
    # ------------------------------------------------------------------
    def _load_whisper(self) -> None:
        from backend.config import WHISPER_MODEL, WHISPER_MODEL_DIR, DEVICE, WHISPER_COMPUTE_TYPE
        from backend.config import asr_worker_plan
        try:
            from faster_whisper import WhisperModel
            num_workers, cpu_threads = asr_worker_plan()
            logger.info(
                f"Loading Whisper {WHISPER_MODEL} with faster-whisper "
                f"(num_workers={num_workers}, cpu_threads={cpu_threads}) ..."
            )
            # num_workers lets CTranslate2 run several transcriptions against
            # ONE copy of the weights, which is what makes chunked parallel
            # transcription affordable on a field laptop. cpu_threads is the
            # per-worker intra-op width; the product is kept at the physical
            # core count so the workers do not fight each other for the same
            # arithmetic units.
            self.whisper_model = WhisperModel(
                WHISPER_MODEL,
                device=DEVICE,
                compute_type=WHISPER_COMPUTE_TYPE,
                download_root=str(WHISPER_MODEL_DIR),
                num_workers=num_workers,
                cpu_threads=cpu_threads,
            )
            self._whisper_loaded = True
            self.whisper_backend = "faster-whisper"
            logger.info("Whisper loaded ✓ (faster-whisper)")
        except ImportError:
            try:
                import whisper
                logger.warning(
                    "faster-whisper is not installed — falling back to openai-whisper, "
                    "which runs fp32 on CPU and is several times slower. "
                    "Install it with: pip install -r requirements.txt"
                )
                self.whisper_model = whisper.load_model(WHISPER_MODEL, download_root=str(WHISPER_MODEL_DIR))
                self._whisper_loaded = True
                self.whisper_backend = "openai-whisper"
                logger.info("Whisper loaded ✓ (openai-whisper fallback)")
            except Exception as e:
                logger.info(f"Whisper offline weights not found in {WHISPER_MODEL_DIR} ({e}). Pipeline ready in lightweight mode.")
        except Exception as e:
            logger.info(f"Whisper offline weights not found in {WHISPER_MODEL_DIR} ({e}). Pipeline ready in lightweight mode.")

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
        from backend.config import DEVICE
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
                torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32,
                token=token,
            )
 
            repaired = _materialize_meta_params(model, str(path)) if is_local else []
            if repaired:
                logger.info(
                    f"IndicTrans2 {name}: loaded {len(repaired)} tied parameter(s) "
                    f"directly from the checkpoint ({', '.join(repaired)})"
                )

            model = model.to(DEVICE)
            model.eval()

            if DEVICE == "cpu":
                import torch
                model = torch.quantization.quantize_dynamic(
                    model,
                    {torch.nn.Linear},
                    dtype=torch.qint8,
                )
 
            logger.info(f"IndicTrans2 {name} loaded ✓")
 
            return tokenizer, model
 
        except Exception as e:
            # Blaming missing weights hid a tokenizer incompatibility for as
            # long as it existed: the 847 MB of weights were sitting right
            # there. Say what actually happened, and say what it costs — with
            # no translation model, translate_segments() falls back to the
            # translation-memory path, which returns the SOURCE TEXT for
            # anything it has not seen before.
            logger.error(
                f"IndicTrans2 {name} FAILED TO LOAD from {local_path}: "
                f"{type(e).__name__}: {e}",
                exc_info=True,
            )
            logger.error(
                f"Translation into {name} is NOT AVAILABLE. Advisories will not "
                f"be translated until this is fixed."
            )
            return None, None

    # ------------------------------------------------------------------
    # Coqui TTS
    # ------------------------------------------------------------------
    def _load_tts(self) -> None:
        from backend.config import COQUI_TTS_MODEL_DIR, COQUI_TTS_MODEL_NAME, DEVICE
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
                gpu=(DEVICE == 'cuda'),
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
        from backend.config import COQUI_TTS_MODEL_DIR, COQUI_TTS_MODEL_NAME, DEVICE
        try:
            from TTS.api import TTS
            tts_dir = Path(COQUI_TTS_MODEL_DIR)
            if tts_dir.exists():
                return TTS(
                    model_path=str(tts_dir),
                    config_path=str(tts_dir / "config.json"),
                    progress_bar=False,
                    gpu=(DEVICE == 'cuda'),
                )
            return TTS(
                model_name=COQUI_TTS_MODEL_NAME,
                gpu=(DEVICE == 'cuda'),
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
