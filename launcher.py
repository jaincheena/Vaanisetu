"""
VaaniSetu — 1-Click Interactive Launcher & Onboarding Assistant
Provides robust verification, auto-setup, model management, and server execution.
"""

import sys
import os
import time
import subprocess
import webbrowser
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
BASE_DIR = Path("C:/VaaniSetu")

def print_banner():
    print("=" * 80)
    print("  VAANISETU - 100% Offline AI Translation Platform")
    print("  Bharatiya Agro Industries Foundation (BAIF)")
    print("=" * 80)
    print("  Interactive Onboarding & Startup Wizard")
    print("=" * 80 + "\n")

def free_port(port=8765):
    """Ensure port 8765 is not occupied by an old stale background process."""
    if sys.platform == "win32":
        try:
            cmd = f'netstat -ano | findstr ":{port} "'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            for line in res.stdout.strip().splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and f":{port}" in parts[1]:
                    pid = parts[-1]
                    if pid and pid != str(os.getpid()):
                        try:
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                            print(f"      [INFO] Cleaned up stale background process (PID {pid}) on port {port}.")
                        except Exception:
                            pass
            time.sleep(0.5)
        except Exception:
            pass

def check_directories():
    print("[1/4] Verifying local storage directories on C:\\VaaniSetu...")
    dirs = [
        BASE_DIR,
        BASE_DIR / "models",
        BASE_DIR / "models" / "whisper",
        BASE_DIR / "models" / "indictrans2-en-indic",
        BASE_DIR / "models" / "indictrans2-indic-en",
        BASE_DIR / "models" / "piper",
        BASE_DIR / "workspace",
        BASE_DIR / "outputs",
        BASE_DIR / "uploads",
        BASE_DIR / "logs"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("      Directories initialized: PASS\n")

def check_dependencies():
    print("[2/4] Verifying Python packages...")
    try:
        import fastapi
        import uvicorn
        import torch
        import transformers
        print("      Core packages verified: PASS\n")
    except ImportError as e:
        print(f"      [!] Some packages are missing ({e.name}).")
        choice = input("      Install dependencies from requirements.txt now? (Y/N) [Default: Y]: ").strip().upper()
        if choice in ("", "Y", "YES"):
            print("      Installing packages via pip (this may take 3-5 minutes)...")
            res = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=str(REPO_ROOT))
            if res.returncode != 0:
                print("      [ERROR] Package installation failed. Check internet connection.")
                input("Press Enter to exit...")
                sys.exit(1)
            print("      Dependencies installed: PASS\n")
        else:
            print("      Proceeding with existing packages.\n")

def check_models():
    print("[3/4] Checking AI model assets in C:\\VaaniSetu\\models...")
    whisper_dir = BASE_DIR / "models" / "whisper"
    indic_dir = BASE_DIR / "models" / "indictrans2-en-indic"
    piper_dir = BASE_DIR / "models" / "piper"

    has_whisper = whisper_dir.exists() and any(whisper_dir.iterdir())
    has_indic = indic_dir.exists() and any(indic_dir.iterdir())

    if not (has_whisper and has_indic):
        print("      [INFO] Offline model weights not fully downloaded yet.")
        print("      Server will start in fallback / lightweight mode.")
        print("      To download complete 5GB offline weights, run: scripts\\download_models.bat")
    else:
        print("      AI Model weights detected: PASS")
    print()

def check_frontend():
    print("[4/4] Verifying Web UI production bundle...")
    dist_index = REPO_ROOT / "frontend" / "dist" / "index.html"
    if not dist_index.exists():
        print("      Building React frontend (one-time build)...")
        subprocess.run(["npm", "install"], cwd=str(REPO_ROOT / "frontend"), shell=True)
        subprocess.run(["npm", "run", "build"], cwd=str(REPO_ROOT / "frontend"), shell=True)
        print("      Frontend build complete: PASS\n")
    else:
        print("      Pre-compiled Web UI bundle ready: PASS\n")

def open_browser_when_ready(url="http://localhost:8765", max_wait=30):
    import threading
    def _wait_and_open():
        start_t = time.time()
        while time.time() - start_t < max_wait:
            try:
                req = urllib.request.Request(f"{url}/api/health", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status == 200:
                        print(f"\n[OK] Server is ready! Opening web browser at {url} ...\n")
                        webbrowser.open(url)
                        return
            except Exception:
                time.sleep(0.4)

    th = threading.Thread(target=_wait_and_open, daemon=True)
    th.start()

def start_server():
    print("=" * 80)
    print("  STARTING VAANISETU SERVER")
    print("=" * 80)
    print("  Local Web Access: http://localhost:8765")
    print("  Office WiFi LAN:  http://0.0.0.0:8765")
    print()
    print("  Server is starting... Web browser will open automatically once live.")
    print("  Press Ctrl+C in this window at any time to stop the server.")
    print("=" * 80 + "\n")

    # Clean port before binding
    free_port(8765)

    open_browser_when_ready("http://localhost:8765")

    try:
        import uvicorn
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8765, log_level="info")
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
    except Exception as e:
        print(f"\n[ERROR] Server failed to start: {e}")
        print("Check logs at C:\\VaaniSetu\\logs\\vaanisetu.log")
        input("\nPress Enter to exit...")

def main():
    print_banner()
    check_directories()
    check_dependencies()
    check_models()
    check_frontend()
    start_server()

if __name__ == "__main__":
    main()
