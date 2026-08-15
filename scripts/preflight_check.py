"""
VaaniSetu — Operational Readiness & Pre-Flight Verification Tool
Validates all system prerequisites, hardware headroom, dependencies, and model assets.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

def check_item(category, name, condition, details, is_warning=False):
    status = "[PASS]" if condition else ("[WARN]" if is_warning else "[FAIL]")
    print(f"{status:<7} {category:<16} | {name:<32} | {details}")
    return condition or is_warning

def run_preflight():
    print("=" * 80)
    print("VAANISETU — OPERATIONAL READINESS & PRE-FLIGHT VERIFICATION")
    print("=" * 80)
    print(f"{'STATUS':<7} {'CATEGORY':<16} | {'CHECK ITEM':<32} | {'DETAILS'}")
    print("-" * 80)

    all_passed = True

    # 1. Environment & Runtime
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 10)
    all_passed &= check_item("Runtime", "Python Version (>= 3.10)", py_ok, f"Python {py_ver}")

    node_path = shutil.which("node")
    node_ok = node_path is not None
    node_ver = "Not Found"
    if node_ok:
        try:
            node_ver = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
        except Exception:
            pass
    all_passed &= check_item("Runtime", "Node.js (for UI build)", node_ok, f"{node_ver}", is_warning=True)

    # 2. Multimedia Tools (FFmpeg)
    from backend.utils.ffmpeg import ffmpeg_executable, ffprobe_executable
    ff_path = ffmpeg_executable()
    ff_ok = Path(ff_path).exists() or shutil.which(ff_path) is not None
    all_passed &= check_item("Multimedia", "FFmpeg Binary", ff_ok, f"Path: {ff_path}")

    # 3. Hardware & Memory
    import psutil
    vm = psutil.virtual_memory()
    ram_gb = vm.total / (1024 ** 3)
    free_ram_gb = vm.available / (1024 ** 3)
    ram_ok = ram_gb >= 7.5
    all_passed &= check_item("Hardware", "System RAM (>= 8 GB)", ram_ok, f"Total: {ram_gb:.1f} GB, Available: {free_ram_gb:.1f} GB")

    base_dir = Path("C:/VaaniSetu")
    base_dir.mkdir(parents=True, exist_ok=True)
    disk = psutil.disk_usage(str(base_dir))
    disk_free_gb = disk.free / (1024 ** 3)
    disk_ok = disk_free_gb >= 10.0
    all_passed &= check_item("Storage", "Disk Free Space (>= 10 GB)", disk_ok, f"Free: {disk_free_gb:.1f} GB on {base_dir}")

    # 4. Device Acceleration (GPU / CPU)
    from backend.config import DEVICE
    has_cuda = DEVICE == "cuda"
    gpu_desc = "CUDA GPU Accelerated (10-30x speedup)" if has_cuda else "CPU Mode (INT8 Quantized, basic laptop ready)"
    check_item("Acceleration", "Hardware Compute Target", True, f"Target: {DEVICE.upper()} - {gpu_desc}")

    # 5. Core AI Libraries
    try:
        import transformers
        import torch
        ai_details = f"Torch {torch.__version__}, Transformers {transformers.__version__}"
        try:
            import faster_whisper
            ai_details += ", faster-whisper OK"
        except ImportError:
            ai_details += ", faster-whisper (optional offline STT engine)"
        ai_libs_ok = True
    except Exception as e:
        ai_libs_ok = False
        ai_details = f"Missing AI package: {e}"
    all_passed &= check_item("Dependencies", "AI Model Frameworks", ai_libs_ok, ai_details, is_warning=not ai_libs_ok)

    # 6. Database & Storage Architecture
    from backend.config import DB_PATH, LOGS_DIR, OUTPUTS_DIR, WORKSPACE_DIR
    from backend.database import init_db, get_db
    try:
        init_db()
        with get_db() as conn:
            cnt = conn.execute("SELECT count(*) FROM jobs").fetchone()[0]
        db_ok = True
        db_details = f"SQLite WAL Connected ({cnt} existing jobs)"
    except Exception as e:
        db_ok = False
        db_details = f"DB Connection Failed: {e}"
    all_passed &= check_item("Database", "SQLite WAL Storage", db_ok, db_details)

    # 7. Model Asset Readiness
    from backend.config import INDIC_EN_INDIC_PATH, WHISPER_MODEL_DIR, PIPER_VOICES_DIR
    whisper_ready = WHISPER_MODEL_DIR.exists() and any(WHISPER_MODEL_DIR.iterdir())
    check_item("AI Assets", "Whisper Offline Weights", whisper_ready, f"{WHISPER_MODEL_DIR} (Ready: {whisper_ready})", is_warning=True)

    indic_ready = Path(INDIC_EN_INDIC_PATH).exists() and any(Path(INDIC_EN_INDIC_PATH).iterdir())
    check_item("AI Assets", "IndicTrans2 Weights", indic_ready, f"{INDIC_EN_INDIC_PATH} (Ready: {indic_ready})", is_warning=True)

    piper_ready = PIPER_VOICES_DIR.exists() and any(PIPER_VOICES_DIR.iterdir())
    check_item("AI Assets", "Piper TTS Voices", piper_ready, f"{PIPER_VOICES_DIR} (Ready: {piper_ready})", is_warning=True)

    # 8. Web Distribution Bundle
    dist_dir = REPO_ROOT / "frontend" / "dist"
    ui_ready = dist_dir.exists() and (dist_dir / "index.html").exists()
    all_passed &= check_item("Frontend", "Compiled UI Bundle", ui_ready, f"{dist_dir} (Built: {ui_ready})")

    print("-" * 80)
    print("OPERATIONAL READINESS SUMMARY:")
    if all_passed:
        print(">> ALL CORE OPERATIONAL CRITERIA PASSED - READY FOR DEPLOYMENT <<")
    else:
        print(">> SOME CRITICAL CRITERIA FAILED - RESOLVE BEFORE STARTING SERVER <<")
    print("=" * 80)

if __name__ == "__main__":
    run_preflight()
