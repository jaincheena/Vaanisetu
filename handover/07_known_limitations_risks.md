# VaaniSetu — Known Limitations & Risk Register

---

## Known Limitations

| Limitation | Detail | Workaround |
|-----------|--------|-----------|
| **Speed on long files** | A 60-minute video takes ~25–40 min on CPU | Schedule jobs overnight; shorter clips translate faster |
| **One job at a time** | Only one file processes at a time; others queue | Plan submissions in advance; check queue depth in top banner |
| **No image/PDF translation** | Cannot read text from scanned PDFs or images | Export text from PDF first, upload as .txt |
| **Dialect support** | AI doesn't distinguish between dialects (e.g. Dakhni Urdu vs. standard Urdu) | Use standard form of language; reviewers can adjust |
| **TTS quality varies** | AI voice sounds robotic for some languages (Manipuri, Dogri, Santhali) | Use TTS output as reference only; produce human voice-over for final content |
| **RAM ceiling** | Cannot run on <16 GB RAM | Use **Resource Saver Mode** or close other applications during processing |
| **No internet recovery** | Models cannot update automatically offline | Re-run `download_models.bat` on an internet-connected day if model quality is needed |
| **SQLite concurrency** | Database has WAL mode enabled but single-writer bottleneck | Not an issue at NGO scale (<100 jobs/day); upgrade DB if volume increases |

---

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|-----------|
| R1 | Server hard disk failure | Medium | High | Weekly backup to external drive; keep copy offsite |
| R2 | Model weights deleted or corrupted | Low | High | Backup models directory monthly; USB copy stored separately |
| R3 | Staff turnover — institutional knowledge lost | Medium | Medium | This document + training plan; two staff trained per role |
| R4 | Translation quality below acceptable threshold | Low | Medium | Confidence Gate + Review Queue catches issues before distribution |
| R5 | Computer RAM insufficient (upgraded to 32 languages) | Low | Low | Current design supports 22 languages within 16 GB |
| R6 | Large video file (>2 GB) submitted | Medium | Low | File size limit enforced; error message guides user to compress |
| R7 | Network connectivity drops during job | Low | Low | Jobs run server-side; browser disconnect doesn't stop processing |
| R8 | Power cut during job | Medium | Medium | UPS recommended for server; incomplete job marked as failed; re-submit |
| R9 | Amber Reviews ignored → wrong content distributed | Medium | High | **Policy**: make distribution clearance a mandatory step in SOP |

---

## Scenario Action Cards

### 🔴 Scenario 1: Server Crashed During a Job
1. Run `stop_vaanisetu.bat`
2. Run `start_vaanisetu.bat` and wait for "Models: Ready"
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
