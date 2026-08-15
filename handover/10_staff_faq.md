# VaaniSetu — Staff FAQ
## Frequently Asked Questions for BAIF Staff

This document answers the most common questions from training officers, field coordinators, content reviewers, and IT admins using VaaniSetu day-to-day. No technical knowledge needed to read this.

---

## PART A — Getting Started

---

**Q: How do I open VaaniSetu? Do I need to install anything on my laptop?**

No installation needed on your laptop, tablet, or phone. VaaniSetu is a website that opens in any browser (Chrome, Edge, Firefox).

Just open your browser and type the office server address — it looks like:
```
http://192.168.1.100:8765
```
(Your IT admin will give you the exact address. Save it as a bookmark.)

As long as you are connected to the **office WiFi**, it will work. You cannot access it from home unless your IT admin sets up remote access separately.

---

**Q: Can I use VaaniSetu on my mobile phone?**

Yes. Open the same address in your phone's browser (Chrome recommended). The interface works on phones and tablets — though uploading large video files from a phone can be slow. For video uploads, a laptop or desktop is more convenient.

---

**Q: Do I need an account or password?**

No. VaaniSetu does not have a login. Anyone connected to the office WiFi can open it. Physical security of the office network is sufficient.

---

**Q1: What files can I upload?**
- **Videos:** .mp4, .mkv, .avi, .mov, .webm
- **Audio:** .mp3, .wav, .ogg, .m4a, .flac
- **Documents:** .pdf, .docx, .txt, .csv

*Note: For scanned PDFs or images, the system does not support direct OCR to keep the application lightweight for field laptops. As a fallback workflow, please use Google Keep, Microsoft Lens, or a similar offline/mobile OCR app to extract the text first, then upload it as a plain .txt file into VaaniSetu.*

---

**Q: The server address doesn't open in my browser. What should I do?**

Check the following, in order:
1. Is your device connected to the **office WiFi** (not mobile data)?
2. Is the VaaniSetu server computer **switched on**?
3. Has the IT admin started the server? (They need to run `start_vaanisetu.bat` each morning.)
4. Try refreshing the page (press F5).
5. If still not working, contact your IT admin.

---

## PART B — Submitting a Translation Job

---

**Q: How do I submit a file for translation?**

1. Click **Upload** in the sidebar
2. Choose your mode (see below)
3. Select the **source language** (what language your file is in)
4. Click the **language chips** to choose which languages to translate into
5. **(New) Choose Quality Mode:**
   - ⚡ **Draft** — generates text + subtitles + MP3 audio only, in minutes. Perfect for quick previews and internal review.
   - 🎬 **Full Quality** (default) — generates all outputs including dubbed video, captioned video, WhatsApp chunks, and IVR audio. Takes longer but is distribution-ready.
6. Drag your file into the upload box (or click to browse)
7. Click **Start Translation**
8. Watch the progress bar — it completes automatically

---

**Q: What is "Translate Content" mode vs "Reverse Bridge" mode?**

| Mode | Use when... |
|------|------------|
| **Translate Content** | You have BAIF training material in English/Hindi and want to translate it into regional languages for farmers |
| **Reverse Bridge** | A farmer has recorded a query in their local language (Marathi, Odia, Assamese) and you want to understand it in English for HQ experts |

---

**Q: Can I select all 22 languages at once?**

Yes — click the **All** button above the language chips. Be aware: translating into all 22 languages for a long video will take significantly more time than translating into 3–4 languages. Only select the languages you actually need.

---

**Q: How long does translation take?**

| Content Length | ⚡ Draft Mode (3–4 languages) | 🎬 Full Quality Mode (3–4 languages) |
|---------------|-------------------------------|-----------------------------------|
| Short clip (5 min) | 1–3 minutes | 8–12 minutes |
| Training video (20 min) | 5–8 minutes | 30–45 minutes |
| Long session (60 min) | 15–25 minutes | 90–120 minutes |

> **Tip:** Use ⚡ **Draft mode** to get a quick preview in minutes. Switch to 🎬 **Full Quality** when you need dubbed video, WhatsApp-ready clips, and IVR audio. Submit Full Quality jobs at the end of the day or during lunch — they process in the background.

---

**Q: Can I close the browser while a job is processing?**

Yes. The translation continues on the server even if you close your browser tab. Come back later, go to **History**, find your job, and download the ZIP when it shows "Completed."

---

**Q: I submitted a job but the progress bar isn't moving. Is it stuck?**

It may be queued behind another job. Check the **top banner** — if it shows "Queue: 1 job(s)", your job is waiting. It will start automatically when the current job finishes.

If the progress bar has been stuck on the same stage for more than 30 minutes, contact your IT admin — the server may need to be restarted.

---

**Q: How does the system match the speaker's voice gender?**

VaaniSetu uses pitch analysis (`librosa`) to detect the speaker's vocal frequency in the original recording:
- **Male Speaker** (fundamental frequency < 165Hz) → Synthesizes speech using a natural male voice profile.
- **Female Speaker** (fundamental frequency ≥ 165Hz) → Synthesizes speech using a female voice profile.
In **Full Quality Mode**, the system extracts a 15-second audio reference clip to clone the speaker's tone using Coqui XTTS.

---

**Q: Can I record voice directly into the application without uploading a file?**

Yes! On the **Upload** page, click the **"🎙️ Record Mic"** tab. Click **"Start Recording"**, speak your advisory or query, and click **"Stop"**. The audio clip will be automatically processed by the pipeline.

---

**Q: Can I choose which output files to generate so it runs faster?**

Yes! Click **"Output Formats"** on the Upload page. You can uncheck heavy video files (like dubbed MP4s) and generate only Text (.txt), Subtitles (.srt), and Audio (.mp3). This saves disk space and finishes much faster on basic laptops.

---

**Q: Can I listen to the translated audio and check WhatsApp previews directly in the browser?**

Yes! When a job completes, the **Interactive Result Studio** appears on the screen. You can:
1. **🎧 In-Browser Audio Player**: Click play to hear the translated audio immediately without extracting any ZIP files.
2. **📄 Bilingual Transcript**: Read the original vs translated text side-by-side.
3. **💬 WhatsApp Simulator**: See how the bulletin message and voice note look on a farmer's phone.
4. **📞 Feature Phone IVR Simulator**: Test how the 8kHz audio sounds on a basic keypad phone.

---

## PART C — Understanding the Results

---

**Q: What does 🟢 Green / 🟡 Amber / 🔴 Red mean?**

These are **confidence badges** — how confident the AI is in its translation:

| Badge | Meaning | What to do |
|-------|---------|-----------|
| 🟢 **Green** (≥85%) | AI is very confident | Safe to use and distribute |
| 🟡 **Amber** (65–84%) | AI is somewhat uncertain | Check the Review Queue before distributing |
| 🔴 **Red** (<65%) | AI is not confident | A bilingual person must review before use |

A job shows the **overall** badge based on the average across all sentences.

---

**Q: Can I share an Amber-confidence translation immediately?**

**Not yet.** When a job has Amber segments, you will see:
> ⚠ Pending Review — hold distribution

Go to the **Review Queue**, check the flagged sentences, approve or correct them, and then the job will be automatically marked **Cleared for Distribution**.

> **Important rule:** Never share content with farmers until it shows "Cleared for Distribution." A wrong translation of agricultural advice (fertiliser dosage, pesticide safety) could cause real harm.

---

**Q: What's inside the ZIP file I download?**

When you download the ZIP for a job, it contains a comprehensive set of files for each target language:

| File | What it is | How to use it |
|------|-----------|--------------|
| `translation_Hindi.txt` | Plain Hindi text | SMS, feature phone messaging, BAIF mobile app |
| `bilingual_Hindi.docx` | Word document with original + Hindi side-by-side | Print as handout for field officers & local trainers |
| `subtitles_Hindi.srt` | Subtitle file | Add to video in VLC, YouTube, or editing software |
| `subtitles_Hindi.vtt` | Web subtitle file | Upload with video to BAIF website or web portal |
| `audio_Hindi.mp3` | AI-spoken Hindi audio | Community radio, WhatsApp voice broadcast |
|  | (⚡ Draft: Piper TTS, near-realtime; 🎬 Full: Coqui XTTS v2 high-quality) | |
| `ivr_audio_Hindi.wav` | 8kHz mono telephone audio (🎬 Full Quality only) | Interactive Voice Response (IVR) phone calls to farmers |
| `dubbed_Hindi.mp4` | Video with translated audio voice-over (🎬 Full Quality only) | Gram panchayat video screenings, farmer workshops |
| `captioned_Hindi.mp4` | Video with burned-in subtitles (🎬 Full Quality only) | Social media, WhatsApp groups, TV displays |
| `translated_Hindi.csv` | Translated spreadsheet table | Tabular survey data & field reporting |
| `whatsapp_part00_Hindi.mp4` | Video auto-split into <15MB parts (🎬 Full Quality only) | Direct delivery to rural farmers on low-bandwidth WhatsApp |
| `manifest.json` | Job details and IST timestamp | System and audit record |

---

**Q: The translation in the Word document looks wrong for some sentences. What do I do?**

1. Go to the **Review Queue** page
2. Find the sentences that look wrong (they will be flagged as Amber or Red)
3. You can **edit** the translation directly in the text box, then click **Save Edit**
4. Once you save your correction, the system remembers it permanently — it won't make the same mistake again in future jobs

You can also open the `.docx` file in Word and manually edit it there, but corrections made in the Review Queue are saved for future jobs whereas manual edits in Word are not.

---

**Q: Where are my old translations saved? Can I download them again?**

All completed jobs are saved in the **History** page. Click **History** in the sidebar, find your job, and click **⬇ ZIP** to download it again at any time.

---

## PART D — The Review Queue

---

**Q: Who should be doing the reviews in the Review Queue?**

The Review Queue is for **bilingual staff or volunteers** who speak both the source language and the target language. They don't need to understand the technology — they just need to read the translation and judge whether it sounds correct and natural.

Suggested reviewers:
- BAIF state office staff who speak regional languages
- Community liaisons or panchayat workers
- Language teachers from the local area (as volunteers)

---

**Q: How do I use the Review Queue?**

1. Click **Review Queue** in the sidebar
2. Enter your name in the "Reviewer Name" box (for the audit record)
3. For each card shown:
   - **Left pane**: original sentence in the source language
   - **Right pane**: AI's translation (you can edit this text box)
4. Choose one action:
   - **✓ Approve** — translation is correct, use it as-is
   - **✏ Save Edit** — you changed the translation text, save your version
   - **✗ Reject** — translation is too wrong to use; the sentence will be flagged for manual retranslation
5. Move to the next card

---

**Q: Do I have to review every single sentence of every job?**

No. Only **Amber and Red** sentences appear in the Review Queue. Green sentences (the majority for common languages like Hindi and Marathi) do not need review. Typically, 70–80% of sentences will be Green — only 20–30% will appear for review.

---

**Q: I approved a translation but it was actually wrong. Can I undo it?**

Contact your IT admin. They can open the database with a tool called "DB Browser for SQLite," find the entry, and change its status back to "pending." This is a rare situation — most approvals are final.

---

## PART E — Privacy & Safety

---

**Q: If I upload a farmer's audio recording, does it get sent to Google or any server on the internet?**

**No.** Every recording, every piece of text, every translation stays on the BAIF office computer. Nothing is sent to any outside server. There is no internet connection used during translation.

This means:
- No farmer's name, voice, or query leaves your building
- No agricultural data is stored on any cloud service
- If the internet goes down, VaaniSetu still works perfectly

---

**Q: Who in the office can see the files I upload?**

Anyone connected to the office WiFi can open VaaniSetu and see the History page, including filenames and download ZIPs. There is no login or role separation by default.

If your office handles sensitive content, ask your IT admin about enabling access control.

---

**Q: Is it safe to translate content about pesticides, medicines, or chemical dosages?**

The system will translate it, but **the Confidence Gate and Review Queue are especially important for safety-critical content.**

Our strong recommendation: for any content involving dosages, chemical usage, or medical advice, **always require a qualified bilingual reviewer to check the translation in the Review Queue before distributing**, regardless of whether the badge is Green.

---

## PART F — Troubleshooting Common Problems

---

**Q: The page says "Models: Loading…" in the top banner. What does that mean?**

The AI models take 2–5 minutes to load when the server first starts. This is normal. Wait a few minutes and refresh the page. When it changes to **"Models: Ready"** (in green), the system is ready to process jobs.

If it stays on "Loading…" for more than 10 minutes, contact the IT admin — the server may need to be restarted.

---

**Q: I uploaded a file but got an error "Unsupported file type."**

VaaniSetu explicitly supports videos, audio, plain text, and 3-4 MVP document formats. It does **not** accept:
- PowerPoint files (.pptx)
- Image files (.jpg, .png)
- Excel files (.xlsx)

**Solution:** For unsupported document types, use the new **"Short Text"** mode to simply copy and paste the text directly into the UI. Alternatively, copy the text into a `.txt` file and upload that.

---

**Q: My job shows "failed" in History. What happened?**

Common causes:
- The file was corrupted or empty
- The server ran out of memory (another large job was running)
- The file contained no spoken audio (a silent video)

**Solution:** Try re-uploading the same file. If it fails again, contact IT admin with the job ID (visible in the History page).

---

**Q: The top banner shows "Disk: low" in red. Should I be worried?**

Yes — tell your IT admin. The server is running low on storage space. Until they clear old files, new jobs may fail. IT admin can run the cleanup procedure — it takes less than 10 minutes.

---

**Q: The translation sounds/reads awkward in the regional language. Is this a bug?**

It's expected behaviour for first-time use. AI translation models are general-purpose — they don't know BAIF's specific vocabulary until they learn from corrections.

The solution is the **Review Queue + Translation Memory**: when your language reviewer corrects a mistranslation, the system saves that correction permanently. After 2–3 months of regular use and reviewing, the translation quality for your specific content will be noticeably better.

---

**Q: I downloaded the ZIP but the Hindi/Tamil text appears as boxes or question marks in Word.**

This is a font issue on the computer opening the file. The `.docx` file is correctly written in UTF-8 encoding. Solution:
1. Open Word → go to the paragraph with boxes
2. Select the text → change the font to **Mangal** (for Devanagari/Hindi) or **Nirmala UI** (for Tamil, Telugu, Bengali)
3. The text will display correctly

Alternatively, open the file on a computer that has Indian language font packs installed (Windows 11 includes them by default — go to Settings → Time & Language → Language & Region → Add a language).

---

## PART G — Impact Ledger

---

**Q: What is the Impact Ledger and who needs to use it?**

The Impact Ledger is for **Programme Managers and leadership** who need to report VaaniSetu's impact to donors and funders. It automatically counts:

- Total hours of content translated
- Estimated money saved (vs. hiring professional translators)
- Estimated number of farmers reached

Click **Impact Ledger** in the sidebar, then click **📄 Export PDF** to download a report you can attach to donor submissions or evaluation reports.

---

**Q: The "farmers reachable" number looks too high or too low. Can it be adjusted?**

Yes. At the bottom of the Impact Ledger page is a **Rate Configuration table**. Your programme manager can change the multipliers for each language:
- **Farmers per hour** — how many farmers one hour of content in this language typically reaches
- **Rate per minute** — the professional translation rate used for cost comparison

These are set to standard defaults initially. Adjust them to match your own field data for more accurate reporting.

---

## PART H — Glossary

---

**Q: What is the Glossary page?**

The Glossary automatically builds a database of **terms that have been translated at least 3 times with high confidence**. It shows each term in the source language alongside its translation in all target languages.

Over time, this becomes BAIF's own **agricultural terminology dictionary** across all Indian languages — completely customised to your content.

---

**Q: Can I export the Glossary to share with language reviewers?**

Yes — click **📄 Export DOCX** on the Glossary page. This downloads a Word document with the full glossary table, which you can print or share with external language reviewers or community volunteers.

---

*Last updated: July 2026 — For BAIF staff use*
*For technical issues, contact your IT Administrator*
*For translation quality issues, use the Review Queue*
