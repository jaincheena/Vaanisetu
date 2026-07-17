# VaaniSetu Video Production Guide

Because the hackathon requires high-quality video submissions (and judges often grade heavily based on the video), this guide provides the exact step-by-step instructions, shot lists, and scripts you need to produce **two** professional videos yourself.

---

## 🛠️ Recommended Free Tools for Production
- **Screen Recording:** OBS Studio (Free, no watermarks) or Windows Game Bar (Win + G)
- **Video Editing:** CapCut (PC/Mac) or DaVinci Resolve (Professional, free)
- **AI Voiceover (Optional):** ElevenLabs (free tier) if you don't want to record your own voice, though a passionate human voice is highly recommended for the Pitch video!

---

## Video 1: The 1-Minute Pitch & Demo Video (For Presentation/Judges)
**Goal:** Hook the judges in 10 seconds, prove the offline capability, and show the physical outputs.
**Vibe:** High energy, fast-paced, documentary style.

### Shot List & Script (60 Seconds)

| Time | Visual / Screen Recording | Voiceover Script (Read with energy!) |
|------|---------------------------|--------------------------------------|
| **0:00 - 0:08** | **Camera:** Speaker holding a basic feature phone in one hand and a smartphone in the other, looking directly at the camera. | "BAIF creates world-class agricultural training content. But professional translation costs ₹850 a minute and takes weeks. By the time it reaches the farmer, the crops are dead." |
| **0:08 - 0:15** | **Camera:** Quick cut to the speaker aggressively unplugging the Wi-Fi router or turning off the laptop's Wi-Fi. | "We built VaaniSetu. A 100% offline, AI-powered translation bridge that runs right on a standard office laptop." |
| **0:15 - 0:25** | **Screen Record:** Show the VaaniSetu dashboard. Cursor drags an English `.mp4` file into the upload zone, clicks "Hindi", "Marathi", and "Odia", and hits Start. | "A field officer simply drops an English video into the app, selects up to 22 Indian languages, and clicks start. Zero internet required." |
| **0:25 - 0:38** | **Screen Record:** Fast-forward (speed up 10x) the progress bars filling up. Show the "Confidence Gate" UI (Red/Amber/Green). | "Under the hood, Whisper transcribes and IndicTrans2 translates. Our unique Confidence Gate mathematically scores the AI's accuracy, holding unsure translations in a Review Queue." |
| **0:38 - 0:50** | **Screen Record:** Open the downloaded `.zip` file. Show the `whatsapp_part01.mp4` video playing, then show the bilingual `.docx`. | "Within 45 minutes, it generates a bilingual Word document for printed handouts, and an MP4 video automatically chunked below 15 megabytes to bypass WhatsApp limits." |
| **0:50 - 1:00** | **Camera:** Speaker holding the physical printed bilingual document, smiling at the camera. Text overlay: *Cost: ₹0. Time: 45 Mins.* | "VaaniSetu drops the cost from one lakh rupees to zero, and the time from a month to 45 minutes. Knowledge shouldn't be a privilege. Thank you." |

---

## Video 2: The Technical Handover Video (For Documentation/Developers)
**Goal:** A slower, methodical "How-To" video meant for BAIF IT staff or future developers who need to install, maintain, or use the system after the hackathon. 
**Vibe:** Professional, educational, clear.
**Target Length:** 2-3 Minutes.

### Shot List & Script

| Time | Visual / Screen Recording | Voiceover Script (Calm & Clear) |
|------|---------------------------|---------------------------------|
| **0:00 - 0:20** | **Screen Record:** Show the Windows desktop. Open the folder, double-click `check_hardware.bat`, then `setup.bat`. | "Welcome to the VaaniSetu technical handover. Deployment is designed for non-technical staff. Simply double-click `check_hardware.bat` to verify your RAM and disk space, followed by `setup.bat` to install dependencies." |
| **0:20 - 0:40** | **Screen Record:** Show `download_models.bat` running. (Fast forward the download bars). Then double-click `start_vaanisetu.bat`. | "Next, run `download_models.bat` while connected to the internet. This permanently downloads the Whisper and IndicTrans2 AI models. Once complete, you never need the internet again. Double-click `start` to boot the server." |
| **0:40 - 1:10** | **Screen Record:** Navigate the UI. Upload a video. Show the "Hardware Resource Saver" toggle being clicked. | "The React interface runs on port 8765. For older hardware, users can check the 'Resource Saver' toggle, which throttles the AI threads to prevent the computer from freezing during heavy translation jobs." |
| **1:10 - 1:50** | **Screen Record:** Show the Review Queue page. Click an Amber segment, edit the text, and click "Approve". | "A critical feature is the Review Queue. Segments with a confidence score below 0.65 are flagged Amber or Red. Bilingual staff can edit the translation here. Upon approval, this correction is permanently saved to the local SQLite Translation Memory." |
| **1:50 - 2:30** | **Screen Record:** Open the `backend/config.py` file in VS Code or Notepad. Highlight the `BATCH_SIZE` and `CONFIDENCE_AMBER` thresholds. | "For developers, all core logic is modular. You can adjust the AI batch size or confidence thresholds in `backend/config.py`. The system requires no proprietary cloud APIs and is 100% open-source." |
| **2:30 - 2:45** | **Screen Record:** Show the Impact Ledger PDF report generation. | "Finally, the Impact Ledger automatically calculates money and time saved, exporting directly to PDF for BAIF donor reports. Thank you for reviewing the VaaniSetu architecture." |

---

## 🎬 Tips for a Winning Video
1. **Audio is 80% of the video:** Use a good microphone or a quiet room. If there is background noise, use Adobe Podcast AI (free online tool) to clean up your voice recording.
2. **Fast Forwarding:** Nobody wants to watch a progress bar fill up in real-time. Record the translation process, then in CapCut, speed that section up 10x or 20x and add a text overlay saying *"Processing sped up for demo"*.
3. **Zoom In:** When showing code or the UI (like the Confidence Gate), zoom in heavily so judges watching on small laptop screens can actually read the text.
