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

## Eight Core Innovations

| # | Innovation | What It Does |
|---|-----------|--------------|
| 1 | **Pipelined Job Engine** | Automatically processes files through 7 stages. Overlaps Stage 4 (translation) & Stage 5 (generation) so audio/video rendering begins the moment a language finishes translating |
| 2 | **RAM-Aware Resource Planner** | Dynamically sizes concurrent jobs and generation workers based on available RAM and physical CPU cores; includes single-worker Resource Saver Mode |
| 3 | **Translation Memory & Entity Shield** | Caches verified translations and shields agricultural acronyms, URLs, and brand names with protected placeholder tokens |
| 4 | **Confidence Gate & Review Queue** | AI computes token log-probability confidence (Green/Amber/Red) and routes uncertain translations to reviewers before distribution |
| 5 | **Reverse Bridge & Multilingual Pivot** | Transcribes regional farmer audio to English for HQ, and enables Indic $\rightarrow$ Indic translation (e.g., Marathi $\rightarrow$ Telugu) via an English pivot |
| 6 | **Video Dubbing & Subtitling** | Generates dubbed MP4s (voice replacement), captioned MP4s, WebVTT, and SRT subtitles synced to sentence boundaries |
| 7 | **IVR / Feature Phone Export** | Auto-generates 8kHz mono audio for direct telecom broadcast to basic phones |
| 8 | **WhatsApp Auto-Splitter** | Slices translated videos into <15MB chunks to bypass WhatsApp media size limits |

![Last Mile Delivery via WhatsApp and IVR Feature Phones](assets/whatsapp_farmers.png)

---

## Production-Ready Edge Case Handling
Built to survive BAIF's actual IT constraints:
- **RAM Spike Protection:** Uploads are chunk-streamed to disk in 64KB blocks, preventing memory crashes even if a 2GB video is uploaded to a 16GB laptop.
- **Hardware-Aware Concurrency:** Automatically runs serially on low-memory 4GB laptops and scales to multi-worker pools on 16GB–32GB machines.
- **Smart Target Deduplication:** The cache intelligently checks both the file hash and the requested target languages.
- **AI Hallucination Guards:** Whisper silence/noise segments are sanitized before hitting IndicTrans2 to prevent tensor crashes and loops.
- **Auto-Disk Recovery:** Intermediate gigabyte-heavy workspace files are purged after every run to prevent server disk exhaustion.
- **Force Re-run (Bypass Cache):** Re-translates with updated human review corrections in under 1 minute.

---

## Key Metrics (Design Targets)

| Metric | Target |
|--------|--------|
| Languages supported | 22 official Indian languages |
| Formats accepted | Video (.mp4, .mkv, .avi, .mov), Audio (.mp3, .wav, .m4a, .flac), Documents (.txt, .pdf, .docx, .csv) |
| Output formats per job | .txt, bilingual .docx, .srt, .vtt, TTS .mp3, dubbed .mp4, captioned .mp4, IVR .wav, WhatsApp chunks, .zip |
| Internet required at runtime | **None (100% Offline)** |
| Maximum file size | 2 GB |
| Concurrent jobs | Dynamically planned by available RAM & CPU cores (e.g. 1 on 4GB, up to 4+ on 16GB/32GB) |
| LAN accessibility | All devices on office WiFi / Ethernet |
| Data storage | Local SQLite WAL with 30s timeout — never leaves the building |
