# VaaniSetu — Known Limitations & Risk Register

---

## Known Limitations

| Limitation | Detail | Workaround |
|-----------|--------|-----------|
| **Speed on long video files** | A 60-minute video takes ~5–15 min in Draft mode or ~20–35 min in Full Quality mode on CPU | Use Draft mode for quick turnaround; Full Quality mode for overnight batch runs. Translation now runs in parallel across target languages. |
| **Concurrency bounded by RAM** | Low-memory PCs (4GB–8GB) run jobs serially | System dynamically allocates workers; on 16GB+ multiple jobs/stages run in parallel |
| **Scanned/Image OCR** | Text-based PDFs, DOCX, CSV, TXT are supported; scanned image PDFs are not | For scanned documents, OCR into text/DOCX before uploading |
| **Dialect support** | AI translates standard forms rather than local sub-dialects | Use standard regional language; reviewers adjust dialect nuances in Review Queue |
| **TTS voice naturalness** | 3-engine cascade: Piper ONNX (draft) → Coqui XTTS v2 (full quality voice cloning) → gTTS (online fallback) | Use Draft TTS for rapid reference; Full Quality mode produces human-like voice clones |
| **Hardware ceiling on low RAM** | Concurrency is RAM-aware. Job: 1.5GB, Generate: 0.6GB, Translate: 0.3GB, OS headroom: 2.0GB. | Use Launcher Option 2 (SIT & Field Testing) for lightweight 350MB models on low RAM |
| **Offline model updates** | Models cannot update automatically without internet | Re-run `scripts\download_models.bat` during internet maintenance windows |
| **Database concurrency** | SQLite WAL mode with 30s timeout handles multi-worker traffic | Built-in WAL and 30s lock timeout prevents database lock issues |
| **GPU auto-detection** | CUDA GPUs (NVIDIA) auto-used when present for 10-30x speedup; CPU INT8 is the well-optimised fallback | Use any CUDA-capable NVIDIA GPU to dramatically accelerate all three model stages |

---

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|-----------|
| R1 | Server hard disk failure | Medium | High | Weekly backup to external drive; keep copy offsite |
| R2 | Model weights deleted or corrupted | Low | High | Backup models directory monthly; USB copy stored separately |
| R3 | Staff turnover — institutional knowledge lost | Medium | Medium | This document + training plan; two staff trained per role |
| R4 | Translation quality below acceptable threshold | Low | Medium | Confidence Gate + Review Queue catches issues before distribution |
| R5 | Computer RAM insufficient | Low | Low | RAM-aware dynamic worker sizing ensures stable execution within available RAM |
| R6 | Large video file (>2 GB) submitted | Medium | Low | File size limit enforced; error message guides user to compress |
| R7 | Network connectivity drops during job | Low | Low | Jobs run server-side; browser disconnect doesn't stop processing |
| R8 | Power cut during job | Medium | Medium | UPS recommended for server; incomplete job marked as failed; re-submit |
| R9 | Amber Reviews ignored → wrong content distributed | Medium | High | **Policy**: make distribution clearance a mandatory step in SOP |

---

## Scenario Action Cards

### 🔴 Scenario 1: Server Crashed During a Job
1. Run `stop_vaanisetu.bat`
2. Run `Launch_VaaniSetu.bat` (select Option 1) and wait for "Models: Ready"
3. Go to History page — find the failed job
4. Re-submit the same file
5. *Note: output ZIP not created for the failed job; original file is still in uploads/*

### 🔴 Scenario 2: Disk Space Under 10 GB
1. Open `C:\VaaniSetu\uploads\` — delete files older than 7 days
2. Open `C:\VaaniSetu\workspace\` — delete completed job folders
3. If still low: run `backup.bat` to external drive, then delete old outputs
4. Consider adding a second hard drive

### 🟡 Scenario 3: Review Queue Has 200+ Pending Items
1. Organise a team review session
2. Filter by highest confidence first (`status=pending`, sort by confidence)
3. Approve high-confidence items in bulk
4. Flag systematically wrong translations — use reject + manual correction

### 🟡 Scenario 4: Translation Memory Giving Wrong Results
1. Go to Review Queue and identify the bad segments
2. Reject them or edit with correct translation — this updates the TM
3. If a specific term is always wrong, find it in Glossary and note the incorrect translation
4. Contact IT admin to manually flag the TM entry in the database

### 🟢 Scenario 5: New Staff Member Needs Access
1. Tell them the LAN address (visible in top banner)
2. They open it in any browser and log in with the shared credentials
3. Enrol them in the 2-hour training session (see Training Plan)

### 🟢 Scenario 6: Adding More Languages in Future
1. IndicTrans2 supports additional languages via model update
2. Re-run `download_models.bat` with updated model IDs
3. Update `backend/config.py` — add language to `LANG_CODES`
4. Update `impact_config` table in database (or seed automatically)
