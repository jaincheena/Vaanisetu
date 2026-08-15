"""
VaaniSetu -- Piper Voice Downloader
Downloads ONNX voice models from the official rhasspy/piper-voices repository on Hugging Face.

Voices are saved to C:\\VaaniSetu\\models\\piper\\ (PIPER_VOICES_DIR in config).
Each voice needs two files: <stem>.onnx + <stem>.onnx.json.
"""

import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

HF_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"

# Exact Hugging Face paths for available Piper Indic and English voices
VOICE_PATHS = {
    "hi_IN-pratham-medium":   "hi/hi_IN/pratham/medium",
    "hi_IN-priyamvada-medium":"hi/hi_IN/priyamvada/medium",
    "hi_IN-rohan-medium":     "hi/hi_IN/rohan/medium",
    "mr_IN-google-medium":    "mr/mr_IN/google/medium",
    "te_IN-maya-medium":      "te/te_IN/maya/medium",
    "te_IN-padmavathi-medium":"te/te_IN/padmavathi/medium",
    "te_IN-venkatesh-medium": "te/te_IN/venkatesh/medium",
    "ne_NP-google-medium":    "ne/ne_NP/google/medium",
    "en_US-amy-medium":       "en/en_US/amy/medium",
    "en_US-ryan-medium":      "en/en_US/ryan/medium",
}

def download_voice(stem, rel_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    onnx_dest = dest_dir / f"{stem}.onnx"
    json_dest = dest_dir / f"{stem}.onnx.json"

    if onnx_dest.exists() and json_dest.exists() and onnx_dest.stat().st_size > 1000:
        print(f"  [OK] Already installed: {stem}")
        return True

    print(f"  [DL] {stem} ...")
    onnx_url = f"{HF_BASE}/{rel_dir}/{stem}.onnx"
    json_url = f"{HF_BASE}/{rel_dir}/{stem}.onnx.json"

    try:
        # Download JSON
        req = urllib.request.Request(json_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(json_dest, "wb") as f:
            f.write(resp.read())

        # Download ONNX
        req = urllib.request.Request(onnx_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(onnx_dest, "wb") as f:
            while chunk := resp.read(65536):
                f.write(chunk)

        print(f"  [OK] Successfully installed: {stem}")
        return True
    except Exception as e:
        print(f"  [ERR] Download failed for {stem}: {e}")
        if json_dest.exists():
            json_dest.unlink()
        if onnx_dest.exists():
            onnx_dest.unlink()
        return False

def main():
    from backend.config import PIPER_VOICES_DIR
    print(f"\nTarget directory: {PIPER_VOICES_DIR}")
    print(f"Downloading {len(VOICE_PATHS)} voice(s)...\n")

    ok = sum(download_voice(stem, rel_dir, PIPER_VOICES_DIR) for stem, rel_dir in VOICE_PATHS.items())
    print(f"\nDone: {ok}/{len(VOICE_PATHS)} voices ready.")

if __name__ == "__main__":
    main()
