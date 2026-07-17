# VaaniSetu — Architecture & Data Flow

## System Architecture (4 Layers)

```
┌─────────────────────────────────────────────────────┐
│  LAYER 4: USER INTERFACE                            │
│  React 18 + Vite · Runs in any office browser       │
│  5 Pages: Upload · History · Review · Impact · Glossary │
│  Polls /api/health every 30s · SSE for live progress │
└────────────────────┬────────────────────────────────┘
                     │ HTTP / SSE on port 8765
┌────────────────────▼────────────────────────────────┐
│  API LAYER (FastAPI + JWT Authentication)           │
│  REST endpoints + SSE stream                        │
│  Role-Based Access Control (Admin vs User)          │
└────────────────────┬────────────────────────────────┘
                     │ Python function calls
┌────────────────────▼────────────────────────────────┐
│  LAYER 2: PIPELINE ENGINE                           │
│  7-Stage Processor → FIFO Async Queue               │
│  FFmpeg · Whisper · IndicTrans2 · Coqui TTS         │
│  Translation Memory · Confidence Scorer             │
└────────────────────┬────────────────────────────────┘
                     │ SQLite reads/writes · File I/O
┌────────────────────▼────────────────────────────────┐
│  LAYER 1: DATA LAYER                                │
│  SQLite (4 tables) · C:\VaaniSetu\                  │
│  workspace/{job_id}/ · outputs/{job_id}.zip         │
│  models/ (Whisper, IndicTrans2, Coqui TTS)          │
└─────────────────────────────────────────────────────┘
```

---

## 6-Stage Processing Pipeline

### 2. The 7-Stage Pipeline

Located in `backend/pipeline/processor.py`. Only **one job processes at a time** using an async FIFO queue (`asyncio.Queue`) to prevent memory exhaustion (Whisper + IndicTrans2 uses ~12GB RAM combined).

#### Stage 0: Upload & Deduplication (Edge Case Optimized)
- File is received via `multipart/form-data`.
- **Edge Case Protection:** It is *chunk-streamed* to disk (64KB at a time), ensuring RAM doesn't spike when a 2GB video is uploaded.
- **Smart Deduplication:** The SHA-256 hash of the file is checked against the database. If it matches a completed job, the backend verifies if the *requested target languages* are a subset of the cached job's languages. If yes, it returns the cached ZIP instantly, bypassing the pipeline.
- **Force Re-run (Bypass Cache):** If the user checks "Force Re-run" in the UI, the deduplication cache check is bypassed. The file goes through the pipeline again. Since any manual corrections are stored in the Translation Memory, the engine pulls them on the second run, generating a corrected ZIP (new audio/video captions) in less than a minute.

```
User uploads file
       │
       ▼
[1] VALIDATING ──── Check file type, size, SHA-256 dedup
       │
       ▼
[2] EXTRACTING ──── FFmpeg: any format → 16 kHz mono WAV
       │
       ▼
[3] TRANSCRIBING ── Whisper large-v3-turbo → text segments
       │               with timestamps {text, start_s, end_s}
       │               + Empty segment sanitization (filters out silence/noise)
       ▼
[4] TRANSLATING ──── For each target language:
       │               1. Check Translation Memory (SHA-256 key)
       │               2. Cache hit? → use cached (confidence=1.0)
       │               3. Miss? → IndicTrans2 batch(8) → score
       │               4. Confidence < 0.65 → Review Queue
       │               5. Store to TM if confidence ≥ 0.70
       ▼
[5] GENERATING ───── Per language: .txt, bilingual .docx,
       │               .srt, .vtt, TTS .mp3, captioned .mp4
       ▼
[6] PACKAGING ────── manifest.json + all files → .zip
       │            - All outputs are bundled into a standard `.zip` file stored in `C:\VaaniSetu\outputs\`.
       │            - **Auto-Disk Recovery:** The 1GB+ original upload and all heavy intermediate `workspace/` files (like the uncompressed `.wav`) are immediately permanently deleted from the disk. This edge-case optimization prevents the NGO server from running out of hard drive space.
       │
       ▼
COMPLETE — distribution_clearance = cleared | pending_review
```

---

## Input / Output Matrix

| Input Format | Audio Extraction | Transcription | Translation | Outputs |
|---|---|---|---|---|
| `.mp4`, `.mkv` (video) | ✅ FFmpeg | ✅ Whisper | ✅ IndicTrans2 | TXT, DOCX, SRT, VTT, MP3, captioned MP4, ZIP |
| `.mp3`, `.wav` (audio) | ✅ FFmpeg (normalize) | ✅ Whisper | ✅ IndicTrans2 | TXT, DOCX, SRT, VTT, MP3, ZIP |
| `.pdf`, `.docx`, `.csv`, `.txt` | ❌ N/A | ❌ (direct read) | ✅ IndicTrans2 | TXT, DOCX, CSV, ZIP |

---

## Confidence Flow

![Confidence Gate Review UI](assets/confidence_gate_ui.png)

```
IndicTrans2 generates token scores
         │
         ▼
 mean(log_softmax(scores))
         │
         ▼
 exp( max( mean, -5.0 ) ) = confidence in [0, 1]
         │
    ┌────┴──────┬──────────┐
    │           │          │
  ≥ 0.85      0.65–0.84   < 0.65
    │           │          │
  GREEN       AMBER       RED
  ready    →  Review    manual
  to dist     Queue    retranslate
```

---

## Port & Network

| Service | Port | Protocol | Notes |
|---------|------|----------|-------|
| FastAPI | 8765 | HTTP | LAN-accessible, no auth |
| React Dev | 5173 | HTTP | Development only |
| SQLite | local file | — | Never exposed on network |
