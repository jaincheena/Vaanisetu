"""
VaaniSetu -- Piper Voice Downloader
Downloads ONNX voice models for supported Indic languages from the
official Piper releases on GitHub.

Usage:
    python scripts/download_piper_voices.py
    python scripts/download_piper_voices.py --lang Hindi Bengali Tamil

Voices are saved to C:\VaaniSetu\models\piper\ (PIPER_VOICES_DIR in config).
Each voice needs two files: <stem>.onnx + <stem>.onnx.json  (~15-50 MB each).
"""

import argparse
import sys
import urllib.request
import urllib.error
import tarfile
import tempfile
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PIPER_RELEASE_BASE = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2"

VOICE_URLS = {
    "hi_IN-swara-medium":    f"{PIPER_RELEASE_BASE}/voice-hi_IN-swara-medium.tar.gz",
    "bn_BD-sishir-medium":   f"{PIPER_RELEASE_BASE}/voice-bn_BD-sishir-medium.tar.gz",
    "gu_IN-bagicha-medium":  f"{PIPER_RELEASE_BASE}/voice-gu_IN-bagicha-medium.tar.gz",
    "kn_IN-lili-medium":     f"{PIPER_RELEASE_BASE}/voice-kn_IN-lili-medium.tar.gz",
    "mr_IN-vani-medium":     f"{PIPER_RELEASE_BASE}/voice-mr_IN-vani-medium.tar.gz",
    "ta_IN-anbu-medium":     f"{PIPER_RELEASE_BASE}/voice-ta_IN-anbu-medium.tar.gz",
    "te_IN-anu-medium":      f"{PIPER_RELEASE_BASE}/voice-te_IN-anu-medium.tar.gz",
    "ne_NP-google-medium":   f"{PIPER_RELEASE_BASE}/voice-ne_NP-google-medium.tar.gz",
    "en_US-amy-medium":      f"{PIPER_RELEASE_BASE}/voice-en_US-amy-medium.tar.gz",
}


def download_and_extract(url, stem, dest_dir):
    onnx_dest = dest_dir / f"{stem}.onnx"
    json_dest = dest_dir / f"{stem}.onnx.json"
    if onnx_dest.exists() and json_dest.exists():
        print(f"  [OK] Already installed: {stem}")
        return True

    print(f"  [DL] {stem} ...")
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VaaniSetu/1.0"})
        with urllib.request.urlopen(req, timeout=180) as resp:
            with open(tmp_path, "wb") as f:
                while chunk := resp.read(65536):
                    f.write(chunk)
        with tarfile.open(tmp_path, "r:gz") as tar:
            for member in tar.getmembers():
                name = Path(member.name).name
                if name.endswith(".onnx") and not name.endswith(".onnx.json"):
                    member.name = name
                    tar.extract(member, path=dest_dir)
                    extracted = dest_dir / name
                    if extracted.exists() and extracted != onnx_dest:
                        extracted.rename(onnx_dest)
                elif name.endswith(".onnx.json"):
                    member.name = name
                    tar.extract(member, path=dest_dir)
                    extracted = dest_dir / name
                    if extracted.exists() and extracted != json_dest:
                        extracted.rename(json_dest)
        if onnx_dest.exists() and json_dest.exists():
            print(f"  [OK] Installed: {stem}")
            return True
        print(f"  [ERR] Extraction incomplete for {stem}")
        return False
    except Exception as e:
        print(f"  [ERR] {e}")
        return False
    finally:
        if tmp_path.exists():
            os.unlink(tmp_path)


def main():
    from backend.config import PIPER_VOICES_DIR, PIPER_VOICE_MAP
    parser = argparse.ArgumentParser(description="Download Piper TTS voices")
    parser.add_argument("--lang", nargs="*", help="Language names (default: all)")
    args = parser.parse_args()

    if args.lang:
        stems = [PIPER_VOICE_MAP[l] for l in args.lang if l in PIPER_VOICE_MAP]
    else:
        stems = list(PIPER_VOICE_MAP.values())

    print(f"\nTarget directory: {PIPER_VOICES_DIR}")
    print(f"Downloading {len(stems)} voice(s)...\n")

    ok = sum(download_and_extract(VOICE_URLS[s], s, PIPER_VOICES_DIR) for s in stems if s in VOICE_URLS)
    print(f"\nDone: {ok}/{len(stems)} voices ready.")


if __name__ == "__main__":
    main()
