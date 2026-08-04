"""
Helper script for downloading and saving AI models for VaaniSetu.
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)

MODELS_DIR = Path(r"C:\VaaniSetu\models")


def download_whisper():
    try:
        import whisper

        logging.info("Downloading Whisper large-v3-turbo...")
        whisper.load_model(
            "large-v3-turbo",
            download_root=str(MODELS_DIR / "whisper")
        )
        logging.info("Whisper OK")
        return 0

    except Exception as e:
        logging.exception(f"Whisper download failed: {e}")
        return 1


def download_indictrans(model_id: str, save_dir_name: str):
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        logging.info(f"Downloading {model_id}...")

        model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        tokenizer = AutoTokenizer.from_pretrained(model_id)

        save_path = MODELS_DIR / save_dir_name
        save_path.mkdir(parents=True, exist_ok=True)

        model.save_pretrained(save_path)
        tokenizer.save_pretrained(save_path)

        logging.info(f"{model_id} OK")
        return 0

    except Exception as e:
        logging.exception(f"IndicTrans download failed: {e}")
        return 1


def download_tts():
    try:
        from TTS.api import TTS

        model_name = "tts_models/en/ljspeech/tacotron2-DDC"

        logging.info(f"Downloading {model_name} ...")

        # This downloads the model automatically.
        tts = TTS(model_name=model_name)

        logging.info("Coqui TTS downloaded successfully.")
        logging.info(f"Model path: {tts.synthesizer.tts_model}")

        return 0

    except Exception as e:
        logging.exception(f"Coqui TTS download failed: {e}")
        return 1


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("python download_helper.py whisper")
        print("python download_helper.py en-indic")
        print("python download_helper.py indic-en")
        print("python download_helper.py tts")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "whisper":
        sys.exit(download_whisper())

    elif cmd == "en-indic":
        sys.exit(
            download_indictrans(
                "Helsinki-NLP/opus-mt-en-hi",
                "helsinki-en-hi",
            )
        )

    elif cmd == "indic-en":
        sys.exit(
            download_indictrans(
                "Helsinki-NLP/opus-mt-hi-en",
                "helsinki-hi-en",
            )
        )

    elif cmd == "tts":
        sys.exit(download_tts())

    else:
        print(f"Unknown model: {cmd}")
        sys.exit(1)