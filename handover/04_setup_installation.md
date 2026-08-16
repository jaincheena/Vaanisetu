# VaaniSetu — Setup & Installation Guide

---

## ⚡ 1-Click Interactive Onboarding Wizard (Recommended for All Users)

**For all users, field officers, and BAIF administrators:**
1. Simply double-click **`Launch_VaaniSetu.bat`** (or run `launcher.py`) in the main project folder.
2. The interactive assistant automatically performs a **4-step verification**:
   - **Directories:** Checks and creates `models`, `workspace`, `outputs`, `uploads`, `logs`, `vaanisetu.db`.
   - **Dependencies:** Verifies packages and environments.
   - **Models:** Checks for required models.
   - **Frontend:** Ensures the React SPA is built in `frontend/dist/`.
3. An interactive menu is **ALWAYS** shown with 4 options:
   1. 🚀 Start Server Now (default)
   2. 🧪 SIT & Field Testing (~350MB lightweight models)
   3. 🏢 Production & HQ Deployment (~5.5GB full suite)
   4. ⚡ Demo / JIT On-Demand (zero preload)
4. Select an option to start the FastAPI server on port 8765. The browser will open to `http://localhost:8765` once ready.

---

## Hardware Compatibility & AI Model Selection Guide

| Model Suite | Recommended Environment | Included Weights | Download Size | Peak RAM | Accuracy & Performance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **⚡ Lightweight Fast Suite** | **Recommended for SIT, Testing & Field Laptops** | Whisper Base (INT8) + Piper Indic ONNX Voices | **~350 MB** (1–2 min) | **< 650 MB** | 5×–10× real-time on CPU, native Indic voices |
| **🎬 Full High-Precision Suite** | **Recommended for Production & Regional HQ Servers** | Whisper Large-v3 + IndicTrans2 + Coqui XTTS | **~5.5 GB** (5–10 min) | **~3.5–5.0 GB** | Maximum translation accuracy + Zero-shot voice cloning |
| **🚀 Instant JIT Mode** | **Air-Gapped USB Pre-loads & On-Demand** | JIT on-demand fetching | **0 MB** upfront | **< 60 MB** idle | Instant start; compiles per job |

---

## Method A — Standard Automated Setup (First Time Staging)

**Time required:** ~10-15 minutes (mostly automated dependency downloads)

### Step 1 — Check Prerequisites
Double-click `scripts\health_check.bat` (or `scripts\check_hardware.bat`) to verify all prerequisites.

**Requirements:**
- Windows 10/11 (64-bit)
- Intel i3 / i5 / Ryzen 3 / 5 or better
- 4 GB RAM minimum (8 GB+ recommended)
- 15 GB free disk space (for offline models and workspace)
- Python 3.10+ ([python.org](https://python.org))
- Bundled FFmpeg included in repository root (or system PATH)

### Step 2 — Install Software & Build Frontend
Double-click `scripts\setup.bat`

This will:
1. Create `C:\VaaniSetu\` base directories (`models`, `workspace`, `outputs`, `uploads`)
2. Install all Python packages (`pip install -r requirements.txt`) including librosa/soundfile for voice detection and `bcrypt<4.1` pin
3. Install JS packages and build the optimized React interface (`frontend\dist`)

*Expected time: 15–30 minutes (PyTorch download is large)*

### Step 3 — Download AI Models
Run `python scripts/download_helper.py` which uses `huggingface_hub.snapshot_download` to fetch models. (Do not use `from_pretrained` directly to avoid `transformers.onnx` ModuleNotFoundError).

This downloads approximately **5.5 GB**:
- faster-whisper large-v3-turbo (~1.5 GB, CTranslate2 INT8 format)
- IndicTrans2 dist-200M (~1.6 GB, INT8 dynamic quantization on CPU)
- Coqui XTTS v2 (~2.5 GB)

*Keep internet connected until this completes. Do not close the window.*

### Step 3.5 — Download Piper TTS Voices (Recommended)
Run: `python scripts/download_piper_voices.py`
Downloads lightweight ONNX voice models (~50–150 MB total) for 22 Indic languages into `C:\VaaniSetu\models\piper\`.
This enables near-real-time Draft Mode TTS. If skipped, the system falls back to Coqui XTTS (slower) or gTTS (requires internet).

### Step 4 — First Launch
Double-click `scripts\start_vaanisetu.bat`

The server will take **1–3 minutes** on first launch while models load and replica pools are sized according to available RAM. When ready, your browser will open automatically to `http://localhost:8765`.

**Verify:** The top banner shows "Models: Ready" in green and display time is synchronized in IST.

---

## Method B — Offline USB Installation (No Internet)

**Use when:** Installing on a remote field office PC with no internet.

**Time required:** 1–2 hours

### Prepare the USB (on an internet-connected PC first)
1. Run Method A steps 1–3 on the connected PC
2. Copy this entire folder to USB:
   ```
   USB:\
     repo\          ← VaaniSetu application files
     packages\      ← pip download: pip download -r requirements.txt -d packages/
     models\        ← copy from C:\VaaniSetu\models\
     frontend_dist.zip  ← zip the frontend\dist\ folder
     installers\    ← Python installer, Node installer, FFmpeg zip
   ```

### Install on the Offline PC
1. Insert USB drive
2. Double-click `USB:\install_from_usb.bat`
3. Follow on-screen prompts
4. When done, double-click **VaaniSetu** shortcut on Desktop

---

## Troubleshooting Table

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Server doesn't start | Python not in PATH | Re-install Python with "Add to PATH" checked |
| "Models: Loading…" stays for >10 min | Low RAM / model file corrupt | Restart PC, check `C:\VaaniSetu\models\` not empty |
| Browser shows blank page | Frontend not built | Run `setup.bat` again or `cd frontend && npm run build` |
| FFmpeg error during upload | FFmpeg not in PATH | Download FFmpeg, add `C:\ffmpeg\bin` to System PATH |
| Job stays "queued" forever | Worker crashed | Restart the server with `stop_vaanisetu.bat` then `start_vaanisetu.bat` |
| "Disk free" shows red in banner | Less than 20 GB free | Delete old outputs or move backup to external drive |
| Port 8765 already in use | Another service using port | Run `netstat -ano \| findstr 8765` and kill that process |
| Translation is very slow | Whisper processing long video | Normal — CPU mode. A 30-min video takes ~5–8 min in Draft mode, ~15–25 min in Full Quality mode. Use Draft for quick previews. |
| Low confidence on all outputs | Unusual domain vocabulary | Add corrections via Review Queue to build Translation Memory |

---

## Directory Reference

| Path | Contents |
|------|----------|
| `C:\VaaniSetu\models\` | AI model weights |
| `C:\VaaniSetu\models\piper\` | Piper TTS ONNX voice models (15–50 MB each) |
| `C:\VaaniSetu\workspace\{job_id}\` | Per-job intermediate files |
| `C:\VaaniSetu\outputs\{job_id}.zip` | Final output ZIPs |
| `C:\VaaniSetu\vaanisetu.db` | All database tables |
| `C:\VaaniSetu\uploads\` | Uploaded files (can be cleaned periodically) |
