# VaaniSetu — Deployment & Operational Readiness Guide

> **Target Audience:** BAIF IT Administrators, Field DevOps Engineers, and System Operators  
> **Architecture Goal:** 100% Offline, Deterministic, Repeatable Deployment across BAIF Regional Centers with Zero-Config Runtime, Low-RAM Adaptability, and Automated Disaster Recovery.

---

## 1. Deployment Time & Effort Summary

| Phase | Duration (Broadband Setup) | Duration (Air-Gapped USB Setup) | Frequency | Operator Skill Level |
| :--- | :---: | :---: | :---: | :---: |
| **⚡ Interactive Launcher Menu** | **< 10 Seconds** | **< 10 Seconds** | Daily / Anytime | **Zero-technical (`launcher.py`)** |
| **Prerequisites Validation** | 1 Minute | 1 Minute | Once per PC | Non-technical (runs script) |
| **Dependency Installation** | 3-5 Minutes | 0 Minutes (pre-bundled venv) | Once per PC | Automated (`setup.bat`) |
| **Model Weights Download** | 5-8 Minutes | 2 Minutes (USB copy) | Once per PC | Automated (`download_helper.py`) |
| **Cold Server Startup** | 0.2 Seconds | 0.2 Seconds | Daily / Auto-start | Interactive Menu (`launcher.py`) |
| **Total Time to Live Service** | **~10-15 Minutes** | **~3-5 Minutes** | — | **Zero configuration required** |

---

## 2. System Prerequisites & Hardware Tiers

### Minimum vs Recommended Hardware Matrix

| Hardware Component | Minimum Tier (Basic Field Laptop) | Recommended Tier (Office Server) |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11 (64-bit) or Linux | Windows 11 Pro / Windows Server 2022 |
| **Processor (CPU)** | Intel Core i3 / Ryzen 3 (Dual/Quad Core, 2.0 GHz) | Intel Core i7 / Ryzen 7 (8+ Cores, 3.5 GHz) |
| **System RAM** | **4 GB – 8 GB RAM** (Peak usage < 650 MB) | 16 GB – 32 GB DDR4/DDR5 |
| **Idle Memory Footprint** | **< 60 MB RAM** (JIT Lazy Model Loading) | ~1.5 GB RAM (Pre-warmed pools) |
| **Disk Storage** | 15 GB free space on `C:\` drive | 50 GB+ SSD free space on `C:\` drive |
| **GPU Compute** | None required (Runs INT8 CPU quantized) | NVIDIA RTX 3060 / 4060 (6GB+ VRAM) — *Auto-detected* |
| **Network** | Zero internet required at runtime (Offline LAN) | Office WiFi Router / 1 Gbps Ethernet Switch |

### Software & Toolchain Prerequisites

| Dependency | Required Version | Verification Command | Distribution Method |
| :--- | :---: | :--- | :--- |
| **Python** | 3.10 to 3.13 | `python --version` | Standard Python Windows installer |
| **Node.js** | 18+ (Dev build only) | `node --version` | Pre-compiled in `frontend/dist` for production |
| **FFmpeg** | 6.0+ | `ffmpeg -version` | Bundled in repository root (`ffmpeg-8.1.2...`) |
| **SQLite** | 3.35+ (Built into Python) | `python -c "import sqlite3; print(sqlite3.sqlite_version)"` | Zero external server installation needed |

---

## 3. Repeatable Deployment Workflows

### Method A: ⚡ Interactive Launcher Menu (`launcher.py` / `Launch_VaaniSetu.bat`)

Used for all new computers, non-technical field officers, or standard setups:

1. Double-click **`Launch_VaaniSetu.bat`** in the repository root.
2. The launcher automatically executes a 4-step verification: directories $\rightarrow$ dependencies $\rightarrow$ models $\rightarrow$ frontend.
3. The user is presented with a 4-option interactive menu:
   - **1. 🚀 Start Server Now (default)**
   - **2. 🧪 SIT & Field Testing (~350MB lightweight models)**
   - **3. 🏢 Production & HQ Deployment (~5.5GB full suite)**
   - **4. ⚡ Demo / JIT On-Demand (zero preload)**
4. Once the server is online and health is verified, the web browser opens automatically to `http://localhost:8765`.

*Note: For step 2 and 3 above, model downloads utilize `scripts/download_helper.py` which strictly uses `huggingface_hub.snapshot_download` to fetch optimized INT8 CPU models reliably (avoiding `AutoModelForSeq2SeqLM.from_pretrained`).*

---

### Method B: Air-Gapped / Zero-Internet USB Drive Deployment

Used for remote field stations (e.g., Nandurbar, Dantewada) with zero internet access:

1. **Prepare Master USB Drive (At HQ):**
   - Copy the pre-downloaded `C:\VaaniSetu\models\` directory onto a 32GB USB flash drive.
   - Copy the pre-built `Vaanisetu/` folder containing the compiled `frontend/dist/` bundle.
2. **Deploy on Field Machine:**
   - Plug the USB drive into the target laptop.
   - Run:
     ```cmd
     scripts\install_from_usb.bat
     ```
   - *Transfers models, registers bundled FFmpeg, initializes SQLite WAL database, and creates desktop shortcuts in under 3 minutes.*
3. **Ready to Operate:** Double-click the desktop shortcut `Start VaaniSetu`.

---

## 4. Operational Readiness, Logging & Health Monitoring

### A. Rotating Production Log Architecture

VaaniSetu automatically records structured logs to `C:\VaaniSetu\logs\vaanisetu.log` with a 10MB rotating limit (retaining 5 historical archives).

- **Log Path:** `C:\VaaniSetu\logs\vaanisetu.log`
- **Format:** `[TIMESTAMP] [LEVEL] [LOGGER_NAME] MESSAGE`
- **Sample Production Log Stream:**
  ```
  [2026-08-16 01:40:08,124] [INFO] [vaanisetu.config] Device detected: CPU — INT8 dynamic quantization enabled
  [2026-08-16 01:40:08,310] [INFO] [vaanisetu.registry] Loaded faster-whisper (large-v3-turbo, compute_type=int8)
  [2026-08-16 01:40:09,052] [INFO] [vaanisetu.processor] Job job_9a2f1: Processing video broadcast (Hindi, Marathi)
  [2026-08-16 01:40:11,402] [INFO] [vaanisetu.translator] AgriShield™: 14 agricultural entities protected
  [2026-08-16 01:40:14,891] [INFO] [vaanisetu.processor] Auto-Disk Recovery: Workspace purged, 48.2 MB reclaimed
  ```

### B. Automated Live Health API (`GET /api/health`)

The frontend and external monitoring tools poll the live health endpoint every 30 seconds:

```json
{
  "status": "healthy",
  "device": "cpu",
  "ram_total_gb": 15.7,
  "ram_available_gb": 3.7,
  "disk_free_gb": 129.9,
  "models_loaded": {
    "whisper": true,
    "indictrans2_en_indic": true,
    "indictrans2_indic_en": true,
    "piper_tts": true,
    "coqui_xtts": false
  },
  "active_jobs": 0,
  "queue_depth": 0,
  "resource_saver_active": false
}
```

---

## 5. Disaster Recovery, Backup & Rollback Mechanisms

### A. Automated Daily Backup (`scripts\backup.bat`)

IT administrators can schedule or manually execute a snapshot to an external hard drive or network share:

```cmd
scripts\backup.bat
```
- Creates a timestamped directory: `E:\VaaniSetu_Backup\backup_YYYY-MM-DD_HHMM\`
- Safely exports the SQLite database with WAL checkpointing.
- Backs up all completed job output ZIPs and user-approved Translation Memory terms.

### B. Instant Operational Rollback (`scripts\rollback.bat`)

If database corruption occurs or an admin needs to restore previous verified translation state:

1. Run the rollback tool:
   ```cmd
   scripts\rollback.bat
   ```
2. Enter the path of the backup snapshot (e.g., `E:\VaaniSetu_Backup\backup_2026-08-15_1800`).
3. **Safety Protection:** The tool automatically creates a pre-rollback snapshot (`C:\VaaniSetu\rollback_safety_...`) before modifying files.
4. Restores `vaanisetu.db`, verifies table schema integrity, and notifies the operator to restart the server.

---

## 6. Edge Case & Crash Recovery Guarantees

| Failure Scenario | Built-in Mitigation & Recovery Behavior |
| :--- | :--- |
| **Sudden Power Outage / Laptop Shutdown** | SQLite WAL mode ensures database transactions are atomic. In-progress jobs are safely flagged as `interrupted` upon restart without corrupting historical jobs. |
| **Disk Space Exhaustion** | After every job packaging step, `_cleanup_job()` purges multi-gigabyte intermediate WAV audio and frame buffers from `C:\VaaniSetu\workspace\`. |
| **Massive 2GB File Upload** | Multipart upload streams data to disk in 64KB chunks; never buffers the entire payload into RAM, preventing out-of-memory crashes. |
| **Model Load Failure** | If an AI engine is unavailable, the pipeline falls back gracefully (e.g. Coqui XTTS $\rightarrow$ Piper ONNX $\rightarrow$ gTTS fallback; IndicTrans2 fallback flags Red confidence). |
