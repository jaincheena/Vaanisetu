# VaaniSetu 🌱 — Developer Guide

> **100% Offline AI Translation Platform for BAIF Agricultural NGO**  
> Translates video / audio / text into **22 Indian languages** — zero internet at runtime.

---

## Table of Contents

1. [Project Purpose](#1-project-purpose)
2. [How It Works — Big Picture](#2-how-it-works--big-picture)
3. [Tech Stack — Why Each Tool Was Chosen](#3-tech-stack--why-each-tool-was-chosen)
4. [Repository Layout](#4-repository-layout)
5. [Architecture — 4 Layers Explained](#5-architecture--4-layers-explained)
6. [The 7-Stage Pipeline — Step-by-Step](#6-the-7-stage-pipeline--step-by-step)
7. [Database Schema](#7-database-schema)
8. [Backend — Module-by-Module](#8-backend--module-by-module)
9. [Frontend — Component Map](#9-frontend--component-map)
10. [Key Concepts for New Developers](#10-key-concepts-for-new-developers)
11. [Getting the App Running Locally](#11-getting-the-app-running-locally)
12. [API Reference](#12-api-reference)
13. [Known Bugs Fixed & Code Improvements](#13-known-bugs-fixed--code-improvements)
14. [Suggested Future Improvements](#14-suggested-future-improvements)
15. [Common Pitfalls / FAQ](#15-common-pitfalls--faq)

---

## 1. Project Purpose

**BAIF** (Bharatiya Agro Industries Foundation) is an agricultural NGO. They produce training content in English and a few regional languages, but farmers they serve often speak only their local language (Hindi, Tamil, Odia, Assamese, etc.).

**VaaniSetu** solves this by:
- Accepting uploaded **videos / audio recordings / text** from BAIF staff
- **Transcribing** them using OpenAI Whisper (speech-to-text)
- **Translating** them into up to **22 Indian languages** using AI4Bharat's IndicTrans2
- Generating **multiple output formats**: subtitles (.srt, .vtt), bilingual Word docs (.docx), plain text, AI-spoken audio (.mp3), legacy IVR audio (.wav), captioned video (.mp4), and auto-split WhatsApp video chunks
- Throttling hardware via **Resource Saver Mode** so low-end NGO computers don't freeze during heavy AI workloads
- Providing a **Review Queue** so staff can check low-confidence translations before distributing

Everything runs **100% offline** — after a one-time internet-connected setup, the PC never needs internet again.

---

## 2. How It Works — Big Picture

```
BAIF Staff                 VaaniSetu Server              Output
──────────                 ─────────────────              ──────
Opens browser   ────────►  React UI (port 8765)
Uploads file    ────────►  FastAPI validates it
                           ↓
                           FIFO Queue (one job at a time)
                           ↓
                     ┌─────────────────────┐
                     │  7-Stage Pipeline   │
                     │  1. Validate file   │
                     │  2. FFmpeg → WAV    │
                     │  3. Whisper → text  │
                     │  4. IndicTrans2     │──── Review Queue
                     │  5. Generate files  │     (amber segs)
                     │  6. Package ZIP     │
                     └─────────────────────┘
                           ↓
                     SSE progress pushed    ────► Browser progress bar
                           ↓
Staff downloads ZIP ◄──── Output: .txt .docx .srt .vtt .mp3 .mp4
```

---

## 3. Tech Stack — Why Each Tool Was Chosen

| Tool | Role | Why this tool? |
|------|------|----------------|
| **FastAPI** | Backend API framework | Async-native, auto-generates docs at `/docs`, very fast |
| **Uvicorn** | ASGI web server | Production-grade, handles async perfectly, simple to start |
| **SQLite** | Database | Zero-config, no separate DB server, perfect for single-machine deployment |
| **OpenAI Whisper** | Speech-to-text | Best open-source STT in existence, supports 100+ languages, runs CPU-only |
| **AI4Bharat IndicTrans2** | Translation | Best open-source model for Indian languages, 22-language support |
| **Coqui TTS** | Text-to-speech | Open-source multilingual TTS, can generate Indian language audio |
| **FFmpeg** | Audio/video processing | Industry standard, handles every media format, free |
| **React 18** | Frontend framework | Component-based UI, excellent for real-time updates (SSE) |
| **Vite** | Build tool | Lightning-fast dev server + optimised production builds |
| **PyJWT & passlib** | Authentication | Lightweight JWT token generation and password hashing |
| **pypdf** | PDF Extraction | Standard library for reading PDF documents |
| **langdetect** | Language Detection | Offline heuristic-based language sniffing |
| **fpdf2** | PDF generation | Pure Python, no external dependencies, good for reports |
| **python-docx** | Word doc generation | Native DOCX creation, tables, formatting |
| **Server-Sent Events (SSE)** | Progress streaming | One-way server→browser stream, simpler than WebSockets for this use case |

---

## 4. Repository Layout

```
Vaanisetu/
│
├── backend/                    ← Python backend (FastAPI)
│   ├── __init__.py
│   ├── main.py                 ← App entry point (start here!)
│   ├── config.py               ← ALL paths, constants, language codes
│   ├── database.py             ← SQLite table creation + helper functions
│   │
│   ├── models/                 ← AI model management
│   │   ├── registry.py         ← Singleton: loads Whisper + IndicTrans2 + TTS once
│   │   └── schemas.py          ← Pydantic data models (request/response shapes)
│   │
│   ├── pipeline/               ← The core translation engine
│   │   ├── queue.py            ← Async FIFO job queue (one job at a time)
│   │   ├── processor.py        ← 7-stage orchestrator (the "main loop")
│   │   ├── audio_extractor.py  ← FFmpeg wrapper (any format → 16kHz WAV)
│   │   ├── transcriber.py      ← Whisper wrapper (WAV → text segments)
│   │   ├── translator.py       ← IndicTrans2 wrapper + TM cache + confidence
│   │   ├── tts.py              ← Coqui TTS wrapper (text → MP3)
│   │   └── packager.py         ← Writes .txt .docx .srt .vtt .mp3 .mp4 .zip
│   │
│   ├── services/               ← Business logic (no HTTP knowledge here)
│   │   ├── translation_memory.py ← TM cache: lookup, store, glossary
│   │   ├── confidence.py         ← Confidence score formula
│   │   ├── impact_ledger.py      ← Impact metric calculations
│   │   └── export.py             ← PDF + DOCX export generation
│   │
│   ├── routers/                ← HTTP endpoint handlers (one file per feature)
│   │   ├── jobs.py             ← POST /api/jobs/submit, GET /api/jobs/...
│   │   ├── review.py           ← GET/POST /api/review/...
│   │   ├── impact.py           ← GET /api/impact, POST /api/impact/config
│   │   ├── glossary.py         ← GET /api/glossary, GET /api/glossary/export/docx
│   │   └── health.py           ← GET /api/health
│   │
│   └── utils/                  ← Shared utilities (no business logic)
│       ├── file_utils.py       ← SHA-256 hashing, file paths, job IDs
│       └── sse.py              ← Server-Sent Events pub/sub manager
│
├── frontend/                   ← React 18 + Vite frontend
│   ├── package.json
│   ├── vite.config.js          ← Dev proxy to port 8765
│   ├── index.html
│   └── src/
│       ├── main.jsx            ← React app bootstrap
│       ├── App.jsx             ← Router + layout shell
│       ├── index.css           ← ENTIRE design system (tokens, components, utilities)
│       ├── components/         ← Reusable UI pieces
│       │   ├── Sidebar.jsx         ← Navigation + review badge count
│       │   ├── TopBanner.jsx       ← LAN IP, RAM, disk, model status
│       │   ├── ProgressBar.jsx     ← 7-stage animated progress bar
│       │   ├── ConfidenceBadge.jsx ← 🟢🟡🔴 confidence label
│       │   ├── LangChipGrid.jsx    ← 22-language multi-select chip grid
│       │   └── DragDropZone.jsx    ← File drag-drop + browse
│       └── pages/              ← Full pages (one per sidebar item)
│           ├── Upload.jsx          ← Main job submission form + SSE progress
│           ├── History.jsx         ← Job table with filters
│           ├── ReviewQueue.jsx     ← Bilingual review cards
│           ├── ImpactLedger.jsx    ← Stat tiles + bar chart + config table
│           └── Glossary.jsx        ← Term table + DOCX export
│
├── scripts/                    ← Windows batch scripts
│   ├── check_hardware.bat      ← Verify prerequisites before setup
│   ├── setup.bat               ← Install deps + build frontend
│   ├── download_models.bat     ← Download AI models (~6-8 GB)
│   ├── start_vaanisetu.bat     ← Launch server + open browser
│   ├── stop_vaanisetu.bat      ← Graceful shutdown
│   ├── backup.bat              ← DB + outputs to external drive
│   └── install_from_usb.bat    ← Full offline install from USB
│
├── handover/                   ← Non-technical documentation for NGO staff
│   ├── 01_solution_overview.md
│   ├── 02_assumptions_scope.md
│   ├── 03_architecture_flow.md
│   ├── 04_setup_installation.md
│   ├── 05_access_dependencies.md
│   ├── 06_operating_guide.md
│   ├── 07_known_limitations_risks.md
│   ├── 08_training_plan.md
│   └── vaanisetu_documentation.html  ← All 8 docs in one offline HTML file
│
├── requirements.txt            ← Python dependencies
├── .gitignore
└── README.md                   ← You are here
```

---

## 5. Architecture — 4 Layers Explained

### Layer 1: Data Layer
**Location:** `C:\VaaniSetu\` (configured in `backend/config.py`)

Everything persists here — the SQLite database, uploaded files, generated outputs, and AI model weights. The `BASE_DIR` environment variable can override the default location.

```
C:\VaaniSetu\
├── vaanisetu.db          ← SQLite (4 tables)
├── models/               ← Whisper, IndicTrans2, Coqui TTS (~8 GB total)
├── uploads/              ← Incoming files (named {job_id}_{original_name})
├── workspace/{job_id}/   ← Intermediate files per job (WAV, transcript, etc.)
└── outputs/{job_id}.zip  ← Final packaged ZIP
```

### Layer 2: Pipeline Engine
**Location:** `backend/pipeline/` and `backend/services/`

This is the brain. It processes one job at a time through 7 stages. The `processor.py` orchestrator calls each stage module in sequence. Stage results are communicated back to the browser via SSE events.

### Layer 3: API Layer
**Location:** `backend/routers/` and `backend/main.py`

FastAPI handles HTTP. Each router file owns one feature area. FastAPI's automatic OpenAPI docs are available at `http://localhost:8765/docs` (great for testing endpoints).

### Layer 4: User Interface
**Location:** `frontend/src/`

React 18 SPA served from `frontend/dist/` by FastAPI's `StaticFiles`. In development, Vite's dev server proxies `/api/*` to port 8765. In production (after `npm run build`), all files are static HTML/JS/CSS — no separate frontend server needed.

---

## 6. The 7-Stage Pipeline — Step-by-Step

When a job is submitted, it goes through these stages. Each stage emits an SSE event — the browser's progress bar advances as these arrive.

### Stage 0: Submission (router)
File arrives at `POST /api/jobs/submit`. The router:
1. Validates file type (extension in `ALLOWED_EXTENSIONS`)
2. Saves the file to `uploads/{job_id}_{filename}`
3. **Deduplication check**: SHA-256 hashes the file. If an identical file was already completed → return the cached ZIP immediately, no reprocessing
4. Inserts a row into the `jobs` table with `status='queued'`
5. Calls `enqueue(job_id)` — adds to the asyncio FIFO queue
6. Returns `{job_id}` to the UI (UI then opens an SSE stream on `/api/jobs/{id}/stream`)

### Stage 1: Validating
```python
# processor.py: _stage_validating()
```
Re-confirms the file exists on disk, extension is valid. Updates DB: `status='validating'`.

### Stage 2: Extracting
```python
# processor.py: _stage_extracting()
# Calls: audio_extractor.py: extract_audio()
```
Uses FFmpeg to convert the input to **16 kHz mono WAV** — which is the format Whisper requires. For `.txt` files, this stage is skipped (file is copied to `workspace/original.txt` instead).

**Why 16 kHz?** Whisper was trained on 16 kHz audio. Other sample rates waste computation or reduce accuracy.

### Stage 3: Transcribing
```python
# processor.py: _stage_transcribing()
# Calls: transcriber.py: transcribe()
```
Whisper processes the WAV and returns a list of **segments**:
```python
[
  {"text": "Hello farmers", "start": 0.0, "end": 2.5},
  {"text": "Today we discuss irrigation", "start": 2.5, "end": 5.8},
  ...
]
```
For `.txt` inputs, lines are converted to fake segments (5-second intervals).

### Stage 4: Translating
```python
# processor.py: _stage_translating()
# Calls: translator.py: translate_segments()
```
This is the most complex stage. For **each target language**:

1. **TM Cache Check** (Translation Memory): For every segment, compute `SHA-256("src_lang|tgt_lang|" + text.lower())` and look up in the `translation_memory` table. If found with confidence ≥ 0.85 and not flagged → use cached translation (score = 1.0).

2. **IndicTrans2 Inference** (for uncached segments):
   - Group into batches of 8 (controlled by `BATCH_SIZE` in config)
   - Tokenize with the model's tokenizer (specifying source + target FLORES codes)
   - Run `model.generate(output_scores=True, return_dict_in_generate=True)` — the `output_scores=True` flag is critical for confidence computation
   - Decode output sequences back to text

3. **Confidence Scoring**: Uses the raw token probability scores from the generator:
   ```
   confidence = exp( max( mean(log_softmax(token_scores)), -5.0 ) )
   ```
   Result is 0–1. The `-5.0` floor prevents extreme low-probability tokens from crashing the exponential.

4. **Routing**: 
   - Confidence ≥ 0.85 → Green → store to TM (if ≥ 0.70)
   - Confidence 0.65–0.84 → Amber → store to TM + add to `review_queue`
   - Confidence < 0.65 → Red → add to `review_queue`

5. **Direction logic**: English as source → use `en-indic` model. Any other language as source → use `indic-en` model. This is why we have two separate IndicTrans2 checkpoints.

### Stage 5: Generating
```python
# processor.py: _stage_generating()
# Calls: packager.py
```
For each target language, generates all output formats in `workspace/{job_id}/`:

| File | Function |
|------|----------|
| `translation_Hindi.txt` | `write_txt()` — plain concatenation |
| `bilingual_Hindi.docx` | `write_bilingual_docx()` — python-docx table |
| `subtitles_Hindi.srt` | `write_srt()` — SRT format with `HH:MM:SS,ms` timestamps |
| `subtitles_Hindi.vtt` | `write_vtt()` — WebVTT format (same but `.` not `,`) |
| `audio_Hindi.mp3` | `write_tts_mp3()` → `tts.py: generate_tts_for_segments()` |
| `ivr_audio_Hindi.wav` | `write_ivr_wav()` → FFmpeg downsamples to 8kHz mono |
| `captioned_Hindi.mp4` | `write_captioned_mp4()` → FFmpeg subtitle burn |
| `whatsapp_part00_Hindi.mp4` | `write_whatsapp_chunks()` → FFmpeg slices video into <15MB chunks |

### Stage 6: Packaging
```python
# processor.py: _stage_packaging()
# Calls: packager.py: create_zip()
```
Creates a ZIP at `outputs/{job_id}.zip` containing all generated files + `manifest.json`.

### Finish
Updates `jobs` row: `status='completed'`, stores `avg_confidence`, `confidence_level`, and sets `distribution_clearance` to either `'cleared'` (no pending review items) or `'pending_review'`.

---

## 7. Database Schema

**Location:** `backend/database.py`

The DB lives at `C:\VaaniSetu\vaanisetu.db`. There are 4 tables:

### `jobs` — One row per submitted file
| Column | Type | Purpose |
|--------|------|---------|
| `id` | TEXT PK | UUID for the job |
| `mode` | TEXT | `translate` or `reverse_bridge` |
| `filename` | TEXT | Original uploaded filename |
| `file_hash` | TEXT | SHA-256 of file bytes (used for dedup) |
| `input_type` | TEXT | `video`, `audio`, or `text` |
| `source_lang` | TEXT | Display name e.g. `"English"` |
| `target_langs` | TEXT | JSON array e.g. `["Hindi","Bengali"]` |
| `status` | TEXT | `queued` → `validating` → ... → `completed` \| `failed` |
| `confidence_level` | TEXT | `green`, `amber`, or `red` |
| `avg_confidence` | REAL | Average confidence across all translated segments |
| `distribution_clearance` | TEXT | `cleared` or `pending_review` |

### `translation_memory` — Cached translations (the learning layer)
| Column | Type | Purpose |
|--------|------|---------|
| `source_hash` | TEXT UNIQUE | SHA-256 cache key |
| `source_text` | TEXT | Original sentence |
| `translated_text` | TEXT | AI translation |
| `confidence` | REAL | How confident the AI was |
| `times_used` | INT | Incremented on each cache hit |
| `flagged` | INT | 0/1 — flagged entries are excluded from cache hits |

**Glossary rule**: Terms with `times_used >= 3` AND `confidence >= 0.85` AND `flagged = 0` auto-appear in the Glossary page.

### `review_queue` — Amber/red segments awaiting human review
| Column | Type | Purpose |
|--------|------|---------|
| `job_id` | TEXT FK | Which job this segment belongs to |
| `segment_index` | INT | Position in the original transcript |
| `status` | TEXT | `pending` → `approved` \| `edited` \| `rejected` |
| `edited_translation` | TEXT | Human's improved translation (if edited) |

When a human approves or edits a segment, the approved translation is stored in `translation_memory` with `confidence=0.92` — bypassing the AI next time this exact sentence appears.

### `impact_config` — Per-language rate settings
| Column | Type | Purpose |
|--------|------|---------|
| `language` | TEXT PK | Language display name |
| `farmers_per_hour` | INT | How many farmers one hour of content reaches |
| `translation_rate_per_min` | INT | ₹ equivalent cost per minute of translation |

Seeded with all 22 languages at defaults (120 farmers/hr, ₹850/min) on first run.

---

## 8. Backend — Module-by-Module

### `backend/config.py`
**The single source of truth for constants.** If you ever need to change a path, threshold, or language code, this is the only file you touch.

```python
BASE_DIR = Path(os.getenv("VAANISETU_BASE", r"C:\VaaniSetu"))
CONFIDENCE_GREEN = 0.85   # ≥ this → green badge
CONFIDENCE_AMBER = 0.65   # ≥ this → amber badge (else red)
TM_CACHE_HIT_MIN = 0.85   # min confidence to serve from TM cache
TM_STORE_MIN     = 0.70   # min confidence to store in TM
BATCH_SIZE       = 8      # segments per IndicTrans2 call
```

---

### `backend/database.py`
Contains:
- `init_db()` — called at startup in `main.py`. Creates all tables (`CREATE TABLE IF NOT EXISTS`) and seeds `impact_config`
- `get_db()` — a **context manager** yielding an SQLite connection. Always use this pattern:

```python
with get_db() as conn:
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    # conn.commit() is called automatically on exit
    # conn.rollback() is called if an exception occurs
```

---

### `backend/models/registry.py`
The `ModelRegistry` is a **singleton** — only one instance is ever created, no matter how many times you call `ModelRegistry()`. This prevents the catastrophic scenario of loading 8 GB of models twice.

```python
registry = ModelRegistry()  # global instance (bottom of file)
```

Called once at startup via `await loop.run_in_executor(None, registry.load_all)` — this runs model loading in a background thread so the event loop isn't blocked.

The registry gracefully handles missing models:
- If Coqui TTS model dir doesn't exist → TTS disabled, everything else still works
- If IndicTrans2 local weights not found → tries downloading from HuggingFace Hub

---

### `backend/utils/sse.py`
The SSE manager handles streaming progress to the browser. When the pipeline publishes a stage event, all browser connections subscribed to that job receive it.

```python
# Publishing (from pipeline thread):
await sse_manager.publish(job_id, "translating", "Translating → Hindi …", {"pct": 65})

# SSE format sent to browser:
data: {"stage": "translating", "pct": 65, "message": "Translating → Hindi …"}
```

The manager also stores the last event per job so if a browser connects *after* a stage has already completed, it immediately receives the current state.

---

### `backend/pipeline/queue.py`
The worker is an `async` infinite loop that runs as a background task:

```python
async def worker():
    while True:
        job_id = await _queue.get()         # blocks here until a job arrives
        await loop.run_in_executor(None, run_pipeline, job_id)  # runs in thread
        _queue.task_done()
```

`run_pipeline()` is synchronous (blocking — Whisper/torch operations can't be async). So it runs in the thread-pool executor to avoid blocking the FastAPI event loop.

---

### `backend/services/confidence.py`
The key formula explained:

```python
# scores: list of (batch_size, vocab_size) tensors — one tensor per generated token
# sequences: (batch_size, seq_len) tensor of output token IDs

for each token:
    log_prob = log_softmax(step_scores)[token_id]
    # log_softmax converts raw logits to log-probabilities
    # Selecting the generated token's log-prob = "how likely was this choice?"

mean_log_prob = mean(all_log_probs)
# Average log-probability across all tokens in the translation

confidence = exp(max(mean_log_prob, -5.0))
# exp() converts from log-space back to probability space
# max(..., -5.0) prevents extreme negative values from making confidence ≈ 0
# Result: a number between 0 and 1
```

---

## 9. Frontend — Component Map

### Data Flow Pattern
All pages follow the same pattern:
```
Page component
  └── useEffect() → fetch('/api/...')  ← load data on mount
  └── state variables                  ← hold data, loading flags
  └── JSX                              ← render data
      └── child components             ← receive data as props
```

### Upload Page — SSE Flow
The Upload page is the most complex. When a job is submitted:
```
submit() 
  → POST /api/jobs/submit         ← get job_id
  → new EventSource('/api/jobs/{id}/stream')   ← SSE connection
  → es.onmessage = (evt) => {
      parse JSON event
      setProgress(event)           ← triggers ProgressBar re-render
      if (event.stage === 'completed') → setResult(event)
    }
  → on error: fallback to polling every 3s
```

### LangChipGrid Component
Renders all 22 language chips. State is managed by the **parent** (Upload page) and passed down via:
- `selected` — array of currently selected language names
- `onChange` — callback when user clicks a chip

This is the **"lifting state up"** React pattern.

### Design System (index.css)
All visual design lives in CSS custom properties (CSS variables):
```css
:root {
  --green-dark:   #1B4332;   /* sidebar, headers */
  --green-accent: #52B788;   /* buttons, active states, highlights */
  --amber:        #F59E0B;   /* warnings, review needed */
  --red:          #EF4444;   /* errors, low confidence */
  --bg:           #0D1F16;   /* page background (very dark green) */
}
```
No Tailwind, no Material UI — pure vanilla CSS. This keeps the bundle small and works 100% offline.

---

## 10. Key Concepts for New Developers

### What is a FLORES code?
IndicTrans2 uses the FLORES-200 language code system. Each language has a code in the format `script_Script`:
```
"hin_Deva" = Hindi (Devanagari script)
"ben_Beng" = Bengali (Bengali script)
"eng_Latn" = English (Latin script)
```
These codes tell the model exactly which language to translate from/to. They're defined in `LANG_CODES` in `config.py`.

### What is Translation Memory (TM)?
Instead of translating identical sentences repeatedly (wasting GPU time), we cache translations in SQLite. Before every IndicTrans2 call, we compute a hash of the source sentence and look it up. If found with sufficient confidence → return the cached translation immediately. Over time, this makes the system faster and more consistent.

### Why is SSE used instead of WebSockets?
Server-Sent Events are **one-way** (server → browser only). Since we only need to push progress updates from the pipeline to the browser (never the reverse), SSE is simpler:
- No handshake protocol
- Built-in reconnect handling in the browser
- Works over plain HTTP (no upgrade needed)
- Fewer moving parts → easier to debug

### Why one job at a time?
Whisper large-v3-turbo uses ~4-6 GB RAM. IndicTrans2 uses ~2 GB. On 16 GB RAM, running two jobs simultaneously would cause memory swapping → 10× slowdown or crash. The FIFO queue ensures predictable performance.

### What is the Reverse Bridge mode?
Normal mode: `source = English` → translate to Indian languages (for BAIF content)  
Reverse Bridge mode: `source = Indian language` → translate to English (for farmer queries)  
The pipeline is identical. Only the model direction flips (`en-indic` ↔ `indic-en`).

---

## 11. Getting the App Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- FFmpeg (add to PATH)
- **Microsoft C++ Build Tools**: Required for compiling a dependency of the `TTS` package.
  - **Recommended Fix**: To avoid a large download, you can often install a pre-compiled version first by running `pip install monotonic-align` before running `setup.bat`.
- 16 GB RAM
- 200 GB free disk (for models)

### Step 1: Install backend dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install frontend dependencies and build
```bash
cd frontend
npm install
npm run build
```

### Step 3: Download AI models (needs internet, ~6-8 GB)
```
scripts\download_models.bat
```

### Step 4: Start the server
```bash
# From the project root (Vaanisetu/)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765
```

### Step 5: Open browser
`http://localhost:8765`

### Development tip — frontend hot-reload
You can run Vite's dev server while the FastAPI backend is running:
```bash
cd frontend && npm run dev
# Opens http://localhost:5173
# API calls are proxied to http://localhost:8765 (configured in vite.config.js)
```

### Interactive API docs
FastAPI auto-generates an API explorer at: **`http://localhost:8765/docs`**  
Great for testing endpoints without building the frontend.

---

## 11.5. How to Deploy to Production

Because VaaniSetu is designed for remote, offline NGO field offices, "Deployment" doesn't mean AWS or Heroku. It means deploying to a physical Windows PC inside a local office.

**To Deploy (Simple English Guide):**
1. Pick a dedicated Windows 11 PC (i5+ processor, 16GB RAM) in the office.
2. Run `scripts\setup.bat` (needs internet once to install software).
3. Run `scripts\download_models.bat` (needs internet once to pull AI models).
4. Run `scripts\start_vaanisetu.bat`. The server is now running!
5. **Network Access**: The app runs on `http://0.0.0.0:8765`. Find the PC's IPv4 address (e.g., `192.168.1.100`) and share the link `http://192.168.1.100:8765` with all staff in the office. They can use the app from their own laptops/phones via the local WiFi.
6. **No internet is required** after step 3! You can disconnect the router from the internet and the app will continue to work flawlessly across the local LAN.

---

## 12. API Reference

| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| `POST` | `/api/jobs/submit` | Submit a file for translation | `{job_id, message}` |
| `GET` | `/api/jobs/{id}/stream` | SSE progress stream | Event stream |
| `GET` | `/api/jobs/{id}/status` | Check job status | Job object |
| `GET` | `/api/jobs/{id}/download` | Download output ZIP | ZIP file |
| `GET` | `/api/jobs/history` | List all jobs | Array of jobs |
| `GET` | `/api/review/queue` | List review items | Array of items |
| `GET` | `/api/review/stats` | Counts by status | `{pending, approved, ...}` |
| `POST` | `/api/review/{id}` | Approve/edit/reject | `{success, new_status}` |
| `GET` | `/api/impact` | Impact summary | Summary object |
| `POST` | `/api/impact/config` | Update language rates | `{success}` |
| `GET` | `/api/impact/export/pdf` | Download PDF report | PDF file |
| `GET` | `/api/glossary` | List glossary terms | Array of terms |
| `GET` | `/api/glossary/export/docx` | Download glossary | DOCX file |
| `GET` | `/api/health` | System health | `{ram_gb, disk_gb, models_loaded, ...}` |

### Submit Job — Form Fields
```
POST /api/jobs/submit  (multipart/form-data)

file          : <file>           — the media file
target_langs  : '["Hindi","Tamil"]'  — JSON array as string
source_lang   : "English"        — source language display name
mode          : "translate"      — or "reverse_bridge"
farmer_context: ""               — optional context for Reverse Bridge
resource_saver: "true"           — optional flag to throttle CPU threads
```

### SSE Event Format
```json
data: {"stage":"translating","pct":65,"message":"Translating → Hindi …"}

// On completion:
data: {"stage":"completed","pct":100,"message":"Done!","avg_confidence":0.89,"confidence_level":"green"}

// On failure:
data: {"stage":"failed","pct":100,"message":"FFmpeg not found in PATH"}
```

---

## 13. Known Bugs Fixed & Code Improvements

Two bugs were identified during code review and have been fixed:

### Bug 1: Path concatenation crash (processor.py line ~131)
**Problem:** `str(ws / "audio_raw" + suffix)` — In Python, `Path / str` returns a Path, but `Path + str` is not defined and raises `TypeError` on Windows.

```python
# ❌ Before (broken):
target = str(ws / "audio_raw" + suffix)

# ✅ After (fixed):
target = str(ws / f"audio_raw{suffix}")
```

### Bug 2: Event loop anti-pattern (processor.py `_publish()`)
**Problem:** `asyncio.new_event_loop()` / `loop.run_until_complete()` / `loop.close()` created a new event loop for every SSE publish call. This is heavyweight and can cause `RuntimeError: This event loop is already running` warnings on some OSes.

```python
# ❌ Before:
loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(sse_manager.publish(...))
finally:
    loop.close()

# ✅ After:
asyncio.run(sse_manager.publish(...))
# asyncio.run() handles loop lifecycle cleanly
```

---

## 14. Suggested Future Improvements

These are code quality improvements suggested after reviewing the codebase. None are blockers but they would make the code more robust as the project grows.

### High Priority

**1. Stream large file uploads (memory spike prevention)**  
Currently `await file.read()` loads the entire file into RAM before saving it. For a 2 GB video, this doubles peak RAM usage.
```python
# Current (risky for large files):
content = await file.read()
with open(upload_path, "wb") as f:
    f.write(content)

# Better — stream in chunks:
async with aiofiles.open(upload_path, "wb") as f: h
    while chunk := await file.read(65536):  # 64 KB chunks
        await f.write(chunk)
file_hash = sha256_file(upload_path)  # hash after writing
```

**2. Add a `dedup` check against different target langs**  
The current dedup only returns a cached result if the *same file* with *any* completed job exists. It doesn't check whether the target languages match — a user who previously translated to Hindi+Bengali and now wants only Tamil would get the cached ZIP (which has no Tamil in it).

**3. Clean up the `uploads/` directory automatically**  
Uploaded files are never deleted. After a job completes, the original upload is no longer needed. Consider deleting it (or moving to an archive folder) to conserve disk space.

### Medium Priority

**4. Add pagination to the History API**  
`GET /api/jobs/history` currently just returns the latest 50 jobs. As the job count grows, a proper `?page=&per_page=` pattern would be better.

**5. Expose a `/api/jobs/{id}/retry` endpoint**  
When a job fails, the user must re-upload the file. A retry endpoint would re-add the existing job to the queue without needing a re-upload.

**6. Validate that `source_lang` is in the known language list**  
Currently any string is accepted as `source_lang`. If a user types a typo, the pipeline will try to translate from an unrecognized language and fail with a confusing error.

```python
if source_lang != "English" and source_lang not in LANG_CODES:
    raise HTTPException(400, f"Unknown source language: {source_lang}")
```

**7. Add a `pytest` test suite**  
At minimum, add unit tests for:
- `confidence.py` — test the formula with known inputs
- `translation_memory.py` — test cache hit/miss/store logic  
- `file_utils.py` — test SHA-256, TM key generation
- API routes — test with `httpx.AsyncClient` and `TestClient`

### Low Priority / Nice-to-Have

**8. Job progress persistence** — If the server restarts mid-job, the browser SSE stream dies. A polling fallback exists but the job status in DB should reflect mid-stage states so the UI can show accurate progress on reconnect.

**9. Translate text files paragraph-by-paragraph** — Currently `.txt` files create 5-second fake timestamps. Preserving paragraph structure would produce better bilingual DOCX output.

**10. Per-language confidence badge** — Currently one average confidence badge covers all languages. Per-language badges in the History page would let reviewers see which specific language translation needs review.

---

## 15. Common Pitfalls / FAQ

**Q: I get "Models: Loading…" forever — what's wrong?**  
A: The model weights aren't downloaded yet. Run `scripts\download_models.bat`. Check that `C:\VaaniSetu\models\` has subdirectories with `.safetensors` or `.pt` files inside.

**Q: Jobs stay in `queued` status and never process.**  
A: The background worker may have crashed at startup. Check the server terminal for errors. Usually means a missing Python package — run `pip install -r requirements.txt` again.

**Q: I see `FileNotFoundError: Upload file not found`.**  
A: The `uploads/` directory doesn't exist. Run `scripts\setup.bat` which creates all required directories, or manually create `C:\VaaniSetu\uploads\`.

**Q: SSE stream connects but never receives events.**  
A: Check browser DevTools → Network → click the `/stream` request → "EventStream" tab. If the connection is established but empty, the SSE manager may not have any subscribers yet. Try refreshing after submitting the job.

**Q: IDE shows "Cannot find module `fastapi`" errors everywhere.**  
A: These are false positives — the IDE's Python environment doesn't have the packages installed, but they will be present when you run `pip install -r requirements.txt` in your virtual environment. Create a venv and install packages to fix IDE errors: `python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`.

**Q: The bilingual DOCX has garbled text for Devanagari/Arabic scripts.**  
A: Ensure MS Word has the relevant language packs installed. The DOCX files are correctly encoded in UTF-8; the display issue is a font rendering question on the viewer's machine.

**Q: Confidence is always 0 or 0.5 for all translations.**  
A: `output_scores=True` may not be supported by the specific IndicTrans2 checkpoint used. Check `backend/services/confidence.py` — the fallback returns `0.5`. This is a model compatibility issue, not a bug in the code.

**Q: How do I add a new Indian language?**  
A: Add it to `LANG_CODES` in `config.py` with its FLORES code. Re-seed the `impact_config` table (or add the row manually via SQLite). Check IndicTrans2 docs for whether that language is in the 200M distilled model or needs the 1B model.

---

## Quick Start (TL;DR for Experienced Devs)

```bash
# 1. Install
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..

# 2. Download models (internet, ~6-8 GB)
scripts\download_models.bat

# 3. Run
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765

# 4. Dev mode (hot-reload frontend separately)
cd frontend && npm run dev   # → http://localhost:5173
# backend stays at 8765; vite proxies /api/* to 8765

# 5. API explorer
open http://localhost:8765/docs
```

---

*Built with ❤️ for Indian farming communities. Reach 1 billion people — one language at a time.*
