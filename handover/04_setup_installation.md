# VaaniSetu — Setup & Installation Guide

---

## ⚡ 1-Click Interactive Onboarding Wizard (Recommended for All Users)

**For all users, field officers, and hackathon evaluators:**
1. Simply double-click **`Launch_VaaniSetu.bat`** (or `quick_start.bat`) in the main project folder.
2. The interactive assistant automatically:
   - **Prerequisite Detection:** Checks for Python 3.10+; if missing, offers automated 1-click installer download and setup instructions.
   - **Environment Setup:** Creates all required storage directories on `C:\VaaniSetu\` (`models`, `workspace`, `outputs`, `uploads`, `logs`).
   - **Dependency Auto-Install:** Verifies dependencies and auto-prompts `pip install -r requirements.txt` if needed.
   - **Low-RAM Sizing & JIT Models:** Automatically inspects available RAM and selects the optimal Whisper model (`tiny`/`base`/`small`/`large-v3-turbo`) with lazy loading (<60MB idle RAM).
   - **Web UI Verification:** Ensures the pre-compiled React distribution bundle is ready.
   - **Health-Polled Launch:** Starts the FastAPI server, monitors `/api/health`, and **only opens your web browser to `http://localhost:8765` after all prerequisites, dependencies, and models are verified and the server is live**.
3. Pick any of the **1-Click Agricultural Scenarios** on the home screen and start localizing immediately!

---

## Hardware Compatibility & Memory Profiles

VaaniSetu automatically adapts its pipeline to the host PC's available memory:

| Hardware Tier | Target Device | Whisper Model | Peak RAM | Mode & Worker Sizing |
| :--- | :--- | :--- | :--- | :--- |
| **Low-Memory Tier** | Basic Field Laptop (4–8 GB RAM) | `tiny` or `base` | **< 650 MB** | JIT Lazy Loading + Auto Resource Saver |
| **Standard Tier** | Office Desktop (8–16 GB RAM) | `small` or `base` | **~1.2 GB** | Balanced Pipelined Execution |
| **High-Performance Tier** | Workstation / Dedicated Server (16+ GB RAM / GPU) | `large-v3-turbo` | **~3.5 GB** | Full Precision + XTTS Voice Cloning |

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
Double-click `scripts\download_models.bat` (or use `python scripts/download_helper.py` with your HF Token if using gated checkpoints).

This downloads approximately **5–6 GB**:
- faster-Whisper large-v3-turbo (~1.5 GB, CTranslate2 INT8 format)
- IndicTrans2 en-indic (~0.8 GB, INT8 quantized at load)
- IndicTrans2 indic-en (~0.8 GB, loaded on-demand during Reverse Bridge)
- Coqui XTTS v2 (~2.5 GB)

*Keep internet connected until this completes. Do not close the window.*

### Step 3.5 — Validate Installation (Optional)
Run the automated validation suites:
```cmd
python tests_concurrency.py
python tests_mock.py
```
Both should report `RESULT: PASS`.

### Step 3.5 — Download Piper TTS Voices (Recommended)
Run: `python scripts/download_piper_voices.py`
Downloads lightweight ONNX voice models (~50–150 MB total) for 9 Indic languages into `C:\VaaniSetu\models\piper\`.
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
