# VaaniSetu — Assumptions & Scope

## What Is In Scope

- Translation of video, audio, and plain text files into 22 Indian languages
- Speech-to-text transcription of any language that Whisper supports
- Automated confidence scoring and review queue for quality control
- Reverse Bridge mode (regional language → English) for field officer use
- Translation Memory that learns and improves over time
- Impact Ledger with PDF export
- Glossary of high-confidence recurring terms with DOCX export
- Offline-first operation: no internet connection after initial setup
- LAN access from any office device (browser-based, zero app install needed)
- Windows 11 support with `.bat` scripts for all operations
- JWT-based user authentication and Role-Based Access Control (Admin/User)

## What Is Not In Scope

- Mobile or tablet native app (browser access covers this)
- Cloud backup or sync (local backup script provided)
- Real-time collaborative review by multiple users simultaneously
- Translation of handwritten text (images/PDFs with scanned text)
- Live speech translation / real-time streaming
- Support for languages outside the 22 scheduled Indian languages
- Automatic content scheduling or distribution to external platforms

---

## Nine Key Assumptions

| # | Assumption |
|---|-----------|
| 1 | The computer stays on during working hours (server cannot be on a laptop that goes to sleep) |
| 2 | The office has a working LAN (wired or WiFi) for multi-device access |
| 3 | At least one trained staff member will manage Review Queue daily |
| 4 | FFmpeg is installed and available on the system PATH |
| 5 | The initial internet-connected setup is completed before going to a remote site |
| 6 | Model accuracy is sufficient for agricultural terminology with the Translation Memory supplement |
| 7 | 8 GB RAM is the practical minimum (INT8-quantized models run in ~3.5 GB); 16 GB enables parallel workers |
| 8 | Job outputs are downloaded and stored by users; the workspace is periodically cleaned manually |
| 9 | A weekly backup to external drive is sufficient for disaster recovery |
| 10 | Piper TTS voices are downloaded via `scripts/download_piper_voices.py` before first use for best Draft-mode performance |

---

## Licence Note

| Component | Licence | Commercial Use |
|-----------|---------|----------------|
| faster-Whisper / CTranslate2 | MIT | ✅ Free |
| IndicTrans2 (AI4Bharat) | MIT | ✅ Free |
| Piper TTS | MIT | ✅ Free |
| Coqui XTTS v2 | MPL-2.0 | ✅ Free (attribution required) |
| FastAPI / Uvicorn | MIT | ✅ Free |
| React | MIT | ✅ Free |
| PyTorch | BSD-3-Clause | ✅ Free |
| FFmpeg | LGPL / GPL | ✅ Free (check distribution rules) |
| fpdf2 / python-docx | LGPL / MIT | ✅ Free |

> VaaniSetu itself is an internal operational tool for a non-profit NGO and is not distributed commercially.
