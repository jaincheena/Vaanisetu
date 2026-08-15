# VaaniSetu — Access, Dependencies & Hardware

---

## Accessing the Application

VaaniSetu is a web application that runs in your browser. No installation needed on client devices.

| Access Type | Address | Who Can Use |
|------------|---------|-------------|
| On the server machine | `http://localhost:8765` | Person sitting at the server PC |
| From any office device | `http://[SERVER-IP]:8765` | Any device on the office WiFi |

**How to find the server IP:**
- Look at the top banner of VaaniSetu — it shows the LAN address
- Or ask the IT admin: run `ipconfig` in Command Prompt, look for the IPv4 address

**Note on Security:** VaaniSetu operates with JWT Authentication. Default administrative seating is provided out of the box (Username: `admin`, Password: `baif2026`). Non-admin accounts will have read-only or restricted access to specific impact ledgers and translation glossaries.

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Intel i5 / Ryzen 5 (8th gen+) | Intel i7 / Ryzen 7 (10th gen+) |
| RAM | 16 GB | 32 GB |
| Storage | 250 GB free | 500 GB SSD |
| OS | Windows 11 64-bit | Windows 11 64-bit |
| GPU | Not required (CPU-optimised INT8) | NVIDIA GPU (any CUDA-capable) — 10-30x speedup if present |
| Network | 100 Mbps LAN | Gigabit LAN |
| Internet at runtime | ❌ Not needed | ❌ Not needed |

---

## Software Dependencies

| Package | Version | Purpose | Licence |
|---------|---------|---------|---------|
| Python | 3.11+ | Backend runtime | PSF |
| FastAPI | 0.111+ | REST API framework | MIT |
| Uvicorn | 0.30+ | ASGI web server | BSD |
| faster-Whisper | 1.1+ | Speech-to-text (CTranslate2 INT8, 4-8x faster) | MIT |
| IndicTrans2 (AI4Bharat) | dist-200M | Translation | MIT |
| Piper TTS | 2023.11+ | Text-to-speech (ONNX, default, near-realtime) | MIT |
| Coqui XTTS | 0.27+ | High-quality voice cloning (Full Quality mode) | MPL-2.0 |
| CTranslate2 | 4.5+ | INT8 inference engine for Whisper & IndicTrans2 | MIT |
| PyTorch | 2.3+ | ML framework | BSD |
| Transformers (HuggingFace) | 4.40+ | Model loading | Apache 2.0 |
| FFmpeg | 6+ | Audio/video extraction | LGPL/GPL |
| fpdf2 | 2.7+ | PDF generation | LGPL |
| python-docx | 1.1+ | DOCX generation | MIT |
| React | 18.3 | Frontend framework | MIT |
| Node.js | 18+ | Build tooling | MIT |

---

## Port Configuration

| Port | Service | Firewall Rule Needed |
|------|---------|---------------------|
| 8765 | VaaniSetu API + UI | Allow inbound TCP 8765 on LAN |
| 5173 | Vite dev server (dev only) | Block on production |

**Windows Firewall Setup** (run once as Administrator):
```
netsh advfirewall firewall add rule name="VaaniSetu" dir=in action=allow protocol=TCP localport=8765
```

---

## Model Files (Do Not Delete)

| Directory | Size | Contents |
|-----------|------|---------|
| `C:\VaaniSetu\models\whisper\` | ~1.5 GB | Whisper large-v3-turbo |
| `C:\VaaniSetu\models\indictrans2-en-indic\` | ~0.8 GB | Translation English→Indian |
| `C:\VaaniSetu\models\indictrans2-indic-en\` | ~0.8 GB | Translation Indian→English |
| `C:\VaaniSetu\models\coqui_xtts\` | ~2 GB | Text-to-speech (optional) |
| `C:\VaaniSetu\models\piper\` | ~50–150 MB | Piper TTS ONNX voice models (9 Indic languages) |

> ⚠️ Deleting model files will require re-downloading them. Always have a backup copy on an external drive.
