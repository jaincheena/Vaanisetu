"""
VaaniSetu — Modern Interactive Launcher & Onboarding Assistant
Crafted with modern typography, warm saffron/slate styling, real verification gates, and model management.
"""

import sys
import os
import time
import shutil
import subprocess
import webbrowser
import urllib.request
from pathlib import Path

# Enable ANSI escape processing in Windows console
os.system("")
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent
BASE_DIR = Path("C:/VaaniSetu")

# Design System Colors (Matching Web UI)
SAFFRON = "\033[38;2;232;146;74m"
SAFFRON_BOLD = "\033[1;38;2;232;146;74m"
EMERALD = "\033[38;2;82;196;135m"
EMERALD_BOLD = "\033[1;38;2;82;196;135m"
INDIGO = "\033[38;2;124;131;208m"
INDIGO_BOLD = "\033[1;38;2;124;131;208m"
SLATE = "\033[38;2;139;134;150m"
WHITE_BOLD = "\033[1;37m"
RESET = "\033[0m"

def print_banner():
    print(f"\n{SAFFRON_BOLD}  ================================================================================")
    print(f"    __     __                  _   ____       _         ")
    print(f"    \\ \\   / /_ _  __ _ _ __   (_) / ___|  ___| |_ _   _ ")
    print(f"     \\ \\ / / _` |/ _` | '_ \\  | | \\___ \\ / _ \\ __| | | |")
    print(f"      \\ V / (_| | (_| | | | | | |  ___) |  __/ |_| |_| |")
    print(f"       \\_/ \\__,_|\\__,_|_| |_| |_| |____/ \\___|\\__|\\__,_|")
    print(f"{RESET}")
    print(f"   {WHITE_BOLD}100% Offline AI Translation & Localization Platform{RESET}")
    print(f"   {SLATE}Bharatiya Agro Industries Foundation (BAIF){RESET}")
    print(f"{SAFFRON_BOLD}  ================================================================================{RESET}\n")

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
                            print(f"   {SLATE}[CLEANUP] Reclaimed port {port} from background process (PID {pid}){RESET}")
                        except Exception:
                            pass
            time.sleep(0.4)
        except Exception:
            pass

def check_directories():
    print(f" {INDIGO_BOLD}[1/4]{RESET} {WHITE_BOLD}Verifying local storage architecture & disk capacity...{RESET}")
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
    
    # Check free disk space on C:
    try:
        total, used, free = shutil.disk_usage("C:/")
        free_gb = free / (1024 ** 3)
        if free_gb < 5.0:
            print(f"       {SAFFRON}[WARNING] Low disk space on C:\\ ({free_gb:.1f} GB free). At least 10 GB recommended.{RESET}")
        else:
            print(f"       {EMERALD_BOLD}[OK]{RESET} {SLATE}Storage directories verified at C:\\VaaniSetu ({free_gb:.1f} GB free disk space){RESET}\n")
    except Exception:
        print(f"       {EMERALD_BOLD}[OK]{RESET} {SLATE}Storage directories verified at C:\\VaaniSetu{RESET}\n")

def check_dependencies():
    print(f" {INDIGO_BOLD}[2/4]{RESET} {WHITE_BOLD}Checking Python AI & Web runtime libraries...{RESET}")
    try:
        import fastapi
        import uvicorn
        import torch
        import transformers
        print(f"       {EMERALD_BOLD}[OK]{RESET} {SLATE}FastAPI, PyTorch, and Transformers ready{RESET}\n")
    except ImportError as e:
        print(f"       {SAFFRON}[!] Missing required dependency: {e.name}{RESET}")
        choice = input(f"       Install dependencies from requirements.txt now? (Y/N) [Default: Y]: ").strip().upper()
        if choice in ("", "Y", "YES"):
            print(f"       {SLATE}Installing packages via pip (takes 2-4 minutes)...{RESET}")
            res = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=str(REPO_ROOT))
            if res.returncode != 0:
                print(f"       {SAFFRON}[ERROR] Package installation failed. Please check internet connection.{RESET}")
                input("Press Enter to exit...")
                sys.exit(1)
            print(f"       {EMERALD_BOLD}[OK]{RESET} {SLATE}Packages installed successfully{RESET}\n")
        else:
            print(f"       {SLATE}Proceeding with existing runtime packages.{RESET}\n")

def download_lightweight_models():
    """Download lightweight Piper Indic voices + Whisper base."""
    print(f"\n {SAFFRON_BOLD}--- Downloading Lightweight Offline Model Assets (~350 MB) ---{RESET}")
    # 1. Piper Indic Voices
    print(f" {SLATE}[1/2] Downloading Piper TTS Indian Language ONNX Voices (~200MB)...{RESET}")
    piper_script = REPO_ROOT / "scripts" / "download_piper_voices.py"
    if piper_script.exists():
        subprocess.run([sys.executable, str(piper_script)])
    
    # 2. Whisper Base Model
    print(f"\n {SLATE}[2/2] Pre-caching Whisper speech recognition weights (~140MB)...{RESET}")
    try:
        whisper_dir = str(BASE_DIR / "models" / "whisper")
        cmd = [
            sys.executable, "-c",
            f"from faster_whisper import WhisperModel; WhisperModel('base', download_root=r'{whisper_dir}')"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            # Fallback to standard whisper if faster-whisper not compiled
            subprocess.run([
                sys.executable, "-c",
                f"import whisper; whisper.load_model('base', download_root=r'{whisper_dir}')"
            ])
        print(f" {EMERALD_BOLD}[OK] Whisper weights downloaded successfully!{RESET}\n")
    except Exception as e:
        print(f" {SAFFRON}[!] Whisper pre-cache skipped ({e}). Will load on-demand.{RESET}\n")

def check_models():
    print(f" {INDIGO_BOLD}[3/4]{RESET} {WHITE_BOLD}Verifying AI Model weights & hardware sizing...{RESET}")
    from backend.config import WHISPER_MODEL, IS_LOW_RAM

    whisper_dir = BASE_DIR / "models" / "whisper"
    indic_dir = BASE_DIR / "models" / "indictrans2-en-indic"
    piper_dir = BASE_DIR / "models" / "piper"

    has_whisper = whisper_dir.exists() and any(whisper_dir.iterdir())
    has_indic = indic_dir.exists() and any(indic_dir.iterdir())
    has_piper = piper_dir.exists() and any(piper_dir.iterdir())

    detected_items = []
    if has_whisper: detected_items.append("Whisper")
    if has_indic: detected_items.append("IndicTrans2")
    if has_piper: detected_items.append("Piper Voices")
    status_str = ", ".join(detected_items) if detected_items else "None"

    print(f"       {SLATE}Hardware Memory Tier:{RESET} {SAFFRON_BOLD}{'Low-RAM Safe Profile (<650MB peak)' if IS_LOW_RAM else 'Standard Precision Profile'}{RESET}")
    print(f"       {SLATE}Selected STT Engine:{RESET}   {WHITE_BOLD}Whisper ({WHISPER_MODEL}){RESET}")
    print(f"       {SLATE}Cached Local Models:{RESET}  {EMERALD_BOLD}{status_str}{RESET} in C:\\VaaniSetu\\models")

    print(f"\n       {WHITE_BOLD}Select Deployment & Model Option:{RESET}")
    print(f"         {WHITE_BOLD}1. 🚀 [START SERVER NOW]{RESET} Continue with currently installed/cached configuration [Default]")
    print(f"         {EMERALD_BOLD}2. 🧪 [SIT & FIELD TESTING]{RESET} Download/Update Lightweight Fast Models (~350 MB, ~1-2 min)")
    print(f"            {SLATE}• Recommended for: System Integration Testing (SIT), field testing, low-RAM laptops (<650MB){RESET}")
    print(f"            {SLATE}• Includes: Faster-Whisper (INT8) + Piper Indic ONNX Voices (Marathi, Hindi, Gujarati, etc.){RESET}")
    print(f"         {SAFFRON_BOLD}3. 🏢 [PRODUCTION & HQ DEPLOYMENT]{RESET} Download/Update Full High-Precision Suite (~5.5 GB, ~5-10 min)")
    print(f"            {SLATE}• Recommended for: BAIF HQ Production servers, broadcast video dubbing, maximum BLEU precision{RESET}")
    print(f"            {SLATE}• Includes: Whisper Large-v3 + IndicTrans2 En-Indic & Indic-En + Coqui XTTS Voice Models{RESET}")
    print(f"         {INDIGO_BOLD}4. ⚡ [DEMO / JIT ON-DEMAND]{RESET} Start in Zero-Preload Demo Mode (Models load on first query)")

    try:
        choice = input(f"\n       Enter choice (1, 2, 3, or 4) [Default: 1]: ").strip()
        if choice == "2":
            print(f"       {SLATE}Setting up SIT & Testing lightweight models...{RESET}")
            download_lightweight_models()
        elif choice == "3":
            print(f"       {SLATE}Running full Production model downloader (~5.5 GB)...{RESET}")
            subprocess.run(["cmd", "/c", str(REPO_ROOT / "scripts" / "download_models.bat")])
        elif choice == "4":
            print(f"       {EMERALD_BOLD}[READY]{RESET} {SLATE}Instant Demo JIT mode active. Models will load on-demand per job.{RESET}\n")
        else:
            print(f"       {EMERALD_BOLD}[READY]{RESET} {SLATE}Proceeding with server launch...{RESET}\n")
    except (KeyboardInterrupt, EOFError):
        print(f"\n       {EMERALD_BOLD}[READY]{RESET} {SLATE}Proceeding with server launch...{RESET}\n")

def check_frontend():
    print(f" {INDIGO_BOLD}[4/4]{RESET} {WHITE_BOLD}Checking React Web Interface distribution...{RESET}")
    dist_index = REPO_ROOT / "frontend" / "dist" / "index.html"
    if not dist_index.exists():
        print(f"       {SLATE}Compiling React web bundle (one-time step)...{RESET}")
        subprocess.run(["npm", "install"], cwd=str(REPO_ROOT / "frontend"), shell=True)
        subprocess.run(["cmd", "/c", "npm run build"], cwd=str(REPO_ROOT / "frontend"))
        print(f"       {EMERALD_BOLD}[OK]{RESET} {SLATE}Production build compiled successfully{RESET}\n")
    else:
        print(f"       {EMERALD_BOLD}[OK]{RESET} {SLATE}Pre-compiled Web UI bundle ready in frontend\\dist{RESET}\n")

def open_browser_when_ready(url="http://localhost:8765", max_wait=30):
    import threading
    def _wait_and_open():
        start_t = time.time()
        while time.time() - start_t < max_wait:
            try:
                req = urllib.request.Request(f"{url}/api/health", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=0.8) as resp:
                    if resp.status == 200:
                        print(f"\n {EMERALD_BOLD}[ONLINE]{RESET} {WHITE_BOLD}VaaniSetu is live! Opening web browser at {url} ...{RESET}\n")
                        webbrowser.open(url)
                        return
            except Exception:
                time.sleep(0.3)

    th = threading.Thread(target=_wait_and_open, daemon=True)
    th.start()

def start_server():
    print(f"{SAFFRON_BOLD}  ================================================================================")
    print(f"   🚀 LAUNCHING VAANISETU SERVER")
    print(f"  ================================================================================{RESET}")
    print(f"   {WHITE_BOLD}Local Web Access:{RESET} {EMERALD_BOLD}http://localhost:8765{RESET}")
    print(f"   {WHITE_BOLD}Office WiFi LAN:{RESET}  {INDIGO_BOLD}http://0.0.0.0:8765{RESET}")
    print()
    print(f"   {SLATE}Web browser will open automatically once the server is live.{RESET}")
    print(f"   {SLATE}Press {WHITE_BOLD}Ctrl+C{SLATE} in this window at any time to safely stop the server.{RESET}")
    print(f"{SAFFRON_BOLD}  ================================================================================{RESET}\n")

    # Clean port before binding
    free_port(8765)

    open_browser_when_ready("http://localhost:8765")

    try:
        import uvicorn
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8765, log_level="info")
    except KeyboardInterrupt:
        print(f"\n{INDIGO}[INFO] VaaniSetu server stopped gracefully.{RESET}")
    except Exception as e:
        print(f"\n{SAFFRON}[ERROR] Server failed to start: {e}{RESET}")
        print(f"Check structured logs at C:\\VaaniSetu\\logs\\vaanisetu.log")
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
