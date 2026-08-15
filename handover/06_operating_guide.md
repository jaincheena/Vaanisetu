# VaaniSetu — Operating Guide

---

## Daily Operations

| Task | Who | When | How |
|------|-----|------|-----|
| Start the server | IT Admin / Senior Staff | Start of work day | Double-click `start_vaanisetu.bat` |
| Check system health | Any user | Anytime | Look at the top banner in the browser |
| Submit a translation job | Training Officer | As needed | Upload page |
| Review amber segments | Content Reviewer | Daily (before distributing) | Review Queue page |
| Export impact report | Programme Manager | Monthly | Impact Ledger → Export PDF |
| Backup database | IT Admin | Weekly | `backup.bat` → external drive |
| Stop the server | IT Admin | End of work day | `stop_vaanisetu.bat` |

---

## Submitting a Job — Step by Step

1. **Open** `http://localhost:8765` in any browser
2. **Login** with the provided office credentials
3. Click **Upload** in the sidebar
4. **Choose mode:**
   - *Translate Content* — for BAIF training videos/audio
   - *Reverse Bridge* — for farmer audio recordings
4. **Select source language** (what language the file is in)
5. **Click language chips** to select target languages (you can pick multiple)
6. **(Optional) Toggle Resource Saver Mode** if your PC is slow
7. **Drag your file** into the upload zone (or click to browse)
8. Click **Start Translation**
8. Watch the **progress bar** — 7 stages take 2–60 minutes depending on file length
9. When done, **download the ZIP** which contains all output files

---

## Understanding Confidence Badges

| Badge | Colour | Meaning | Action Required |
|-------|--------|---------|-----------------|
| ✓ High Confidence | 🟢 Green | AI is ≥ 85% confident | Ready to distribute |
| ⚠ Review Needed | 🟡 Amber | AI is 65–84% confident | Go to Review Queue and approve |
| ✗ Low Confidence | 🔴 Red | AI is < 65% confident | Manual review + possible re-translation |

> **Rule:** Never distribute a job with amber segments until the Review Queue shows 0 pending items for that job.

---

## Using the Review Queue

1. Click **Review Queue** in the sidebar
2. Enter your name in the "Reviewer Name" field
3. For each card:
   - **Read** the source text (left pane)
   - **Read** the AI translation (right pane, editable)
   - If translation looks correct → click **✓ Approve**
   - If it needs fixing → edit the text box → click **✏️ Save Edit**
   - If completely wrong → click **✗ Reject** and retranslate manually
4. When a job has zero pending items, it automatically gets **distribution clearance**

---

## Understanding Outputs (ZIP Contents)

Each ZIP download contains:
| File | What It Is |
|------|------------|
| `translation_Hindi.txt` | Plain text translation |
| `bilingual_Hindi.docx` | Word document with source + translation side by side |
| `subtitles_Hindi.srt` | Subtitle file (for video players) |
| `subtitles_Hindi.vtt` | Web subtitle file (for online players) |
| `audio_Hindi.mp3` | AI-spoken version in the target language (Coqui XTTS v2) |
| `ivr_audio_Hindi.wav` | 8kHz mono audio for feature phones & IVR broadcasts |
| `dubbed_Hindi.mp4` | Video with translated audio replacing the original audio track |
| `captioned_Hindi.mp4` | Video with burned-in subtitles and synchronized translated audio |
| `translated_Hindi.csv` | Translated CSV document (for structured data uploads) |
| `whatsapp_part00_Hindi.mp4` | Video chunked for WhatsApp (<15MB each) |
| `manifest.json` | Job metadata, timestamp (IST), confidence, and file list |

---

## Maintenance Tasks

### Weekly
- Run `backup.bat` and store external drive offsite
- Check disk space in top banner — should stay above 50 GB free
- Clear old uploads: delete files in `C:\VaaniSetu\uploads\` older than 30 days

### Monthly
- Review Impact Ledger and export PDF for management reporting
- Check Review Queue stats — if pending > 100, schedule a review session

### As Needed
- If the server becomes unresponsive: run `stop_vaanisetu.bat` then restart
- If model outputs seem worse than usual: check if Translation Memory has flagged entries

---

## Quick Reference Card

```
START SERVER:    scripts\start_vaanisetu.bat
STOP SERVER:     scripts\stop_vaanisetu.bat
BACKUP:          scripts\backup.bat
BROWSER URL:     http://localhost:8765

CONFIDENCE:  🟢 ≥85% ready  🟡 65-84% review first  🔴 <65% manual check

SUPPORT:     IT Admin → [fill in contact]
             Developer → [fill in contact]
```
