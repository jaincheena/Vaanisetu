"""
VaaniSetu — Robust AI Model Downloader Helper
Downloads Whisper, IndicTrans2, Coqui XTTS, and Piper TTS voices.
Uses huggingface_hub snapshot_download to prevent dynamic import issues across all transformers versions.
"""

import sys
import os
import types
import logging
from pathlib import Path

# download_piper() imports scripts.download_piper_voices, but running this file
# directly puts scripts/ on sys.path rather than the repo root, so that import
# failed with "No module named 'scripts'" and the Piper voices never downloaded.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)

# Compatibility shims for transformers dynamic modules
try:
    import transformers.onnx
except (ImportError, ModuleNotFoundError):
    dummy_onnx = types.ModuleType("transformers.onnx")
    dummy_onnx.OnnxConfig = object
    dummy_onnx.OnnxSeq2SeqConfigWithPast = object
    dummy_onnx.__path__ = []

    dummy_onnx_utils = types.ModuleType("transformers.onnx.utils")
    dummy_onnx_utils.compute_effective_axis_dimension = lambda *args, **kwargs: None

    sys.modules["transformers.onnx"] = dummy_onnx
    sys.modules["transformers.onnx.utils"] = dummy_onnx_utils

MODELS_DIR = Path(r"C:\VaaniSetu\models")


def get_token():
    return os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or "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"


def download_whisper():
    try:
        logging.info("Downloading Whisper large-v3-turbo...")
        save_dir = MODELS_DIR / "whisper"
        save_dir.mkdir(parents=True, exist_ok=True)

        try:
            from faster_whisper import WhisperModel
            logging.info("Downloading via faster-whisper (CTranslate2 INT8)...")
            WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", download_root=str(save_dir))
            logging.info("Whisper (faster-whisper) OK")
            return 0
        except Exception:
            pass

        import whisper
        whisper.load_model("large-v3-turbo", download_root=str(save_dir))
        logging.info("Whisper OK")
        return 0

    except Exception as e:
        logging.exception(f"Whisper download failed: {e}")
        return 1


def download_indictrans(model_id: str, save_dir_name: str):
    try:
        from huggingface_hub import snapshot_download

        logging.info(f"Downloading {model_id} via snapshot_download...")
        save_path = MODELS_DIR / save_dir_name
        save_path.mkdir(parents=True, exist_ok=True)

        token = get_token()

        snapshot_download(
            repo_id=model_id,
            local_dir=str(save_path),
            token=token,
            ignore_patterns=["*.msgpack", "*.h5", "*.tflite", "*.ot"]
        )

        logging.info(f"{model_id} downloaded successfully to {save_path}")
        return 0

    except Exception as e:
        logging.exception(f"IndicTrans download failed for {model_id}: {e}")
        return 1


def download_piper():
    try:
        from scripts.download_piper_voices import main as piper_main
        logging.info("Downloading Piper TTS voices...")
        piper_main()
        return 0
    except Exception as e:
        logging.exception(f"Piper voice download failed: {e}")
        return 1


def download_tts():
    try:
        logging.info("Downloading XTTS v2...")
        from TTS.utils.manage import ModelManager
        mm = ModelManager(models_file=None, output_prefix=str(MODELS_DIR))
        model_path, _, _ = mm.download_model("tts_models/multilingual/multi-dataset/xtts_v2")
        mm.unpack_model(model_path)
        logging.info("XTTS v2 downloaded successfully.")
        return 0
    except Exception as e:
        logging.warning(f"Coqui XTTS download note: {e}")
        logging.info("Falling back to Piper ONNX & gTTS (fully supported).")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_helper.py [whisper|en-indic|indic-en|piper|tts|all]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "whisper":
        sys.exit(download_whisper())
    elif cmd == "en-indic":
        sys.exit(download_indictrans("ai4bharat/indictrans2-en-indic-dist-200M", "indictrans2-en-indic"))
    elif cmd == "indic-en":
        sys.exit(download_indictrans("ai4bharat/indictrans2-indic-en-dist-200M", "indictrans2-indic-en"))
    elif cmd == "piper":
        sys.exit(download_piper())
    elif cmd == "tts":
        sys.exit(download_tts())
    elif cmd == "all":
        code = download_whisper()
        if code != 0: sys.exit(code)
        code = download_indictrans("ai4bharat/indictrans2-en-indic-dist-200M", "indictrans2-en-indic")
        if code != 0: sys.exit(code)
        code = download_indictrans("ai4bharat/indictrans2-indic-en-dist-200M", "indictrans2-indic-en")
        if code != 0: sys.exit(code)
        code = download_piper()
        if code != 0: sys.exit(code)
        download_tts()
        sys.exit(0)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)