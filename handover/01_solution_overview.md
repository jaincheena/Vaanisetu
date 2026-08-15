# VaaniSetu — Solution Overview

![VaaniSetu Dashboard UI Mockup](assets/vaanisetu_app_ui.png)

## What Is VaaniSetu?

**VaaniSetu** (meaning "voice bridge" in Sanskrit) is a fully offline AI-powered translation platform built specifically for BAIF Development Research Foundation. It translates agricultural training videos, audio recordings, and text documents into 22 official Indian languages — covering over 1.3 billion speakers — without requiring an internet connection after the one-time setup.

The platform runs on a standard office computer (Windows 11, i5 or Ryzen 5 processor, 16 GB RAM) and serves the entire office network from a single machine, making it accessible from any device connected to the office WiFi.

---

## Why Was It Built?

BAIF's field officers distribute training content in English and a few regional languages, but many farming communities across Maharashtra, Bihar, Assam, Odisha, and other states speak primarily their local dialect. The gap between content creation and community reach costs real impact. Professional translation is expensive (₹850+ per minute), slow (weeks per project), and unavailable off-hours in rural areas with poor connectivity.

VaaniSetu eliminates this barrier by bringing AI translation directly into the BAIF office — offline, instant, and free to operate after setup.

---

## Who Uses It?

| Role | How They Use VaaniSetu |
|------|------------------------|
| **Training Officers** | Upload training videos and get translations in multiple languages within minutes |
| **Field Coordinators** | Use Reverse Bridge mode to upload farmer audio and get English summaries for HQ |
| **Content Reviewers** | Approve or edit amber-confidence translations before distribution |
| **IT Admin** | Manage server startup, backups, model updates |
| **Programme Managers** | View Impact Ledger to report social impact to funders |

---

## Core Innovations (What Makes VaaniSetu Unique)

| # | Innovation | What It Does |
|---|-----------|--------------|
| 1 | **Pipelined Job Engine** | Automatically processes files through 7 stages. Translates target languages concurrently and caches the English pivot for Indic-to-Indic jobs. Overlaps Stage 4 (translation) & Stage 5 (generation) so audio/video rendering begins the moment a language finishes translating |
| 2 | **RAM-Aware Resource Planner** | Dynamically sizes concurrent jobs and generation workers based on available RAM and physical CPU cores; includes single-worker Resource Saver Mode |
| 3 | **AgriShield™ Domain Dictionary & TM** | Guards 120+ mission-critical agricultural schemes (PM-KISAN, PMFBY), pests (Yellow Rust, Fall Armyworm), fertilizer formulas (DAP, NPK 19:19:19), and BAIF livestock breeds (Gir, Sahiwal, Murrah) from translation corruption |
| 4 | **Confidence Gate & Review Queue** | AI computes token log-probability confidence (Green/Amber/Red) and routes uncertain translations to reviewers before distribution |
| 5 | **Reverse Bridge & Multilingual Pivot** | Transcribes regional farmer audio to English for HQ, and enables Indic $\rightarrow$ Indic translation (e.g., Marathi $\rightarrow$ Telugu) via a cached English pivot |
| 6 | **Gender-Aware Voice Matching & Cloning** | Analyzes speaker pitch via librosa ($F_0 > 165\text{Hz}$) to select male/female Piper voices or extract a 15-second reference clip for high-fidelity Coqui XTTS voice cloning |
| 7 | **Interactive In-Browser Result Studio** | Listen to translated audio directly in the browser, compare source vs target transcripts side-by-side, and inspect subtitle timings without unzipping |
| 8 | **1-Click Realistic Agricultural Presets** | Instant demo scenarios (Wheat Yellow Rust, Dairy Veterinary Alert, Farmer Irrigation Query) pre-configured for live presentations |
| 9 | **WhatsApp & 8kHz Feature Phone Simulators** | Visual interactive mockups showing exactly how advisory notes reach smartphones on WhatsApp and ₹1,000 basic phones over IVR telecom audio |
| 10 | **WhatsApp Auto-Splitter** | Slices translated videos into <15MB chunks to bypass WhatsApp media size limits |
| 11 | **GPU Auto-Detection & Draft/Full Mode** | Automatically uses CUDA GPU when available (10-30x speedup); Draft mode delivers text+SRT+audio in minutes; Full Quality mode renders all outputs overnight-ready |
| 12 | **Interactive Financial ROI Ledger** | Live dynamic economic model calculating ₹ Lakhs in agency translation savings and farmer reach metrics across BAIF's 12 regional state centers |

![Last Mile Delivery via WhatsApp and IVR Feature Phones](assets/whatsapp_farmers.png)

---

## Production-Ready Edge Case Handling
Built to survive BAIF's actual IT constraints:
- **RAM Spike Protection:** Uploads are chunk-streamed to disk in 64KB blocks, preventing memory crashes even if a 2GB video is uploaded to a 16GB laptop.
- **Hardware-Aware Concurrency:** Automatically runs serially on low-memory 4GB laptops and scales to multi-worker pools on 16GB–32GB machines.
- **Smart Target Deduplication:** The cache intelligently checks both the file hash and the requested target languages.
- **AI Hallucination Guards:** Real Silero VAD filters silence before IndicTrans2 — prevents hallucinations on quiet segments.
- **Auto-Disk Recovery:** Intermediate gigabyte-heavy workspace files are purged after every run to prevent server disk exhaustion.
- **Force Re-run (Bypass Cache):** Re-translates with updated human review corrections in under 1 minute.

---

## Key Metrics (Design Targets)

| Metric | Target |
|--------|--------|
| Languages supported | 22 official Indian languages |
| Formats accepted | Video (.mp4, .mkv, .avi, .mov), Audio (.mp3, .wav, .m4a, .flac), Documents (.txt, .pdf, .docx, .csv) |
| Output formats per job | .txt, bilingual .docx, .srt, .vtt, TTS .mp3, dubbed .mp4, captioned .mp4, IVR .wav, WhatsApp chunks, .zip (Draft mode: text, SRT, MP3 only; Full mode: all formats) |
| Internet required at runtime | **None (100% Offline)** |
| Maximum file size | 2 GB |
| Concurrent jobs | Dynamically planned by available RAM & CPU cores (e.g. 1 on 4GB, up to 4+ on 16GB/32GB) |
| LAN accessibility | All devices on office WiFi / Ethernet |
| Data storage | Local SQLite WAL with 30s timeout — never leaves the building |
