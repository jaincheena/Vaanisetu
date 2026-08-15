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

1. **Open** `http://localhost:8765` in any browser on the office WiFi network
2. **Login** with the provided office credentials (default: `admin` / `baif2026`)
3. Click **Upload** in the sidebar
4. **(Optional) Select a 1-Click Preset:** Click any of the 3 built-in demo scenarios (Crop Disease Alert, Dairy Veterinary Advisory, Farmer Voice Query) to auto-fill text, languages, and settings instantly.
5. **Choose Mode:**
   - *HQ Advisory → Farmer Media* — for BAIF training videos/audio/documents
   - *Farmer Voice → HQ English Bridge* — for farmer field audio recordings
6. **Select Input Type:**
   - *📁 File Upload* — Drag & drop `.mp4`, `.mp3`, `.docx`, `.pdf`, or `.csv`
   - *📝 Text / Script* — Type or paste advisory text
   - *🎙️ Record Mic* — Record live farmer audio directly from your microphone
7. **Language Settings:**
   - Source: Auto-Detect (Whisper AI) or specific language
   - Target: Select from verified active Indic languages (Hindi, Marathi, Gujarati, Bengali, Kannada, English)
8. **Select Output Formats (Optional):** Expand "Output Formats" to select only the files you need (e.g. only Text & MP3 to skip heavy video rendering).
9. **Choose Quality Mode:** Select ⚡ Draft Mode for fast turnaround (30 sec–2 min) or 🎬 Full Quality Mode for video dubbing & WhatsApp chunking.
10. Click **🚀 Start AI Localization**
11. **Live Result Studio:** Once complete, use the interactive tabs to:
    - 🎧 Listen to translated voice playback in the browser
    - 📄 Compare source and translated transcripts side-by-side
    - 💬 Preview the WhatsApp advisory message
    - 📞 Test the 8kHz IVR phone broadcast
    - ⬇️ Download individual files or the complete ZIP package

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
| `audio_Hindi.mp3` | AI-spoken version (Piper TTS in Draft mode; Coqui XTTS v2 in Full Quality mode) |
| `ivr_audio_Hindi.wav` | 8kHz mono audio for feature phones & IVR broadcasts |
| `dubbed_Hindi.mp4` | Video with translated audio replacing the original audio track |
| `captioned_Hindi.mp4` | Video with burned-in subtitles and synchronized translated audio |
| `translated_Hindi.csv` | Translated CSV document (for structured data uploads) |
| `whatsapp_part00_Hindi.mp4` | Video chunked for WhatsApp (<15MB each) |
| `manifest.json` | Job metadata, timestamp (IST), confidence, and file list |

> **Draft vs Full Quality:** In Draft mode, only .txt, .srt, .vtt, .mp3, and .docx files are generated — dubbed/captioned MP4s and WhatsApp chunks are skipped for speed. Use Full Quality mode for all distribution-ready outputs.

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
