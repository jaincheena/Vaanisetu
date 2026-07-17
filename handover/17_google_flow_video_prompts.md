# VaaniSetu — Google Flow Video Generation Prompts

> **How to use:** Open [Google Vids](https://vids.google.com) or any AI video tool (Runway, Synthesia, Pika, HeyGen).  
> Paste the prompt from the appropriate section below into the "Script / Prompt" field.  
> Select the language/voice option for Marathi where available.  
> Export at **1080p**, **16:9** aspect ratio for projection screens.

---

## Video 1 — 60-Second Hackathon Pitch Video
*For the BAIF Pune presentation. Marathi voiceover preferred. English subtitles.*

### 🎬 Google Flow / Vids Prompt

```
Create a 60-second cinematic product pitch video for VaaniSetu — an offline AI translation platform built for BAIF Development Research Foundation in Pune, India.

STORY ARC (match each beat to visuals):

[0:00–0:08 — THE PROBLEM]
Visual: Close-up of a simple Nokia feature phone held by a farmer's weathered hand in a Maharashtra wheat field at golden hour. 
On-screen text overlay: "120 million Indian farmers speak only their local language."
Background audio: Soft rural ambient — birds, wind through crops. No music yet.
Voiceover (Marathi, subtitled in English): "शेतकऱ्यांपर्यंत ज्ञान पोहोचत नाही. कारण ते इंग्रजीत आहे."
English subtitle: "Knowledge doesn't reach farmers. Because it's in English."

[0:08–0:20 — THE SOLUTION REVEAL]
Visual: Smooth animated transition — the Nokia phone transforms into a laptop screen showing the VaaniSetu dashboard UI (dark green theme with three cards: Upload, Review Queue, Impact Ledger). 
Title text animates in with a green pulse glow: "VaaniSetu — Voice Bridge"
Background music starts: Modern electronic background, hopeful and energetic (similar to Coldplay's "A Sky Full of Stars" instrumental, but subtle).
Voiceover (Marathi): "वाणीसेतू — एक ऑफलाइन AI प्लॅटफॉर्म जो २२ भारतीय भाषांमध्ये अनुवाद करतो."
English subtitle: "VaaniSetu — An offline AI platform that translates into 22 Indian languages."

[0:20–0:35 — THE DEMO MOMENT]
Visual: Screen recording-style animation — a user uploads a 5-minute English crop advisory video. A progress bar moves through 7 stages (Validating → Extracting → Transcribing → Translating → Generating → Packaging → Done!). Show a Confidence Gate with Green/Amber/Red color coding on translation segments. 
Text overlay appears: "Whisper STT + IndicTrans2 + Coqui TTS — 100% offline."
Voiceover (English, clear and confident): "In under 45 minutes, VaaniSetu converts English agricultural training videos into Marathi, Hindi, or any of India's 22 official languages — with voice dubbing, subtitles, and a bilingual document — without using the internet."

[0:35–0:48 — THE IMPACT PROOF]
Visual: Animated Impact Ledger dashboard. Counter animates: "₹0 translation cost" spins up from ₹25,000. Timeline shrinks: "3 Weeks → 45 Minutes". Farmer reach counter: "3 million farmers reachable."
Voiceover (Marathi): "फक्त एका संगणकावर, इंटरनेटशिवाय, BAIF आता कोणत्याही शेतकऱ्यापर्यंत पोहोचू शकते."
English subtitle: "From a single computer, without internet, BAIF can now reach any farmer."

[0:48–1:00 — THE CALL TO ACTION]
Visual: Split screen — Left side: the Nokia feature phone receiving a WhatsApp video in Marathi. Right side: a farmer's face watching and smiling. Final frame: Large QR code appears with text "Scan to download a live demo translation."
Voiceover (English, powerful and slow): "VaaniSetu. We didn't just build a translator. We built a bridge."
Music swells and fades. Final logo animation: VaaniSetu leaf/bridge logo with tagline "22 Languages. Zero Internet. Real Impact."

STYLE GUIDE:
- Color palette: Deep forest green (#2F855A), clean white, warm amber (#F6AD55)
- Font: Clean sans-serif (Poppins or Inter), large and readable
- Mood: Hopeful, professional, impactful — NOT corporate or sterile
- Avoid: Stock photo clichés, generic "technology" imagery, overly fast cuts
- DO include: Real Marathi script on screen, actual UI screenshots, counters animating
```

---

## Video 2 — 3-Minute Live Demo Recording
*For screen recording during the actual pitch. Use OBS or Loom to record the real app. Then use this prompt to add voiceover and text overlays in Google Vids.*

### 🎬 Google Flow / Vids Prompt (Voiceover + Overlay Script)

```
Add professional voiceover, animated text overlays, and lower-third labels to an existing 3-minute screen recording of the VaaniSetu web application dashboard. The screen recording already shows the real UI — do not replace it.

SEGMENT 1 [0:00–0:30 — DASHBOARD OVERVIEW]
Lower-third label: "VaaniSetu Dashboard — Running Offline on Office LAN"
Callout annotation: Draw an animated arrow pointing to the health status bar at the top, label it: "Live system health: RAM, Disk, Review Queue — all visible at a glance"
Voiceover: "This is the VaaniSetu dashboard running live on a standard office PC. No cloud subscription. No internet. Any BAIF staff member can access this from any device connected to the office WiFi by simply opening their browser."

SEGMENT 2 [0:30–1:15 — UPLOAD FLOW]
Lower-third label: "Step 1: Upload an English Training Video"
Callout annotation: Highlight the file upload dropzone with a pulse animation. Label: "Drag & drop or browse — accepts MP4, MP3, PDF, DOCX"
Callout annotation: Highlight the language selector dropdown. Label: "Select 1 or more of 22 Indian languages"
Callout annotation: Highlight the Resource Saver toggle. Label: "Resource Saver Mode: reduces RAM usage on older PCs"
Voiceover: "The officer selects a training video in English, picks Marathi as the target language, and hits submit. The 7-stage AI pipeline starts immediately."

SEGMENT 3 [1:15–1:45 — PIPELINE IN PROGRESS]
Lower-third label: "7-Stage AI Pipeline — Real-Time Progress"
Callout annotation: Highlight each stage as it completes. Stage labels: "1-Validating → 2-Extracting → 3-Transcribing (Whisper) → 4-Translating (IndicTrans2) → 5-Generating Outputs → 6-Packaging ZIP → ✅ Done"
Voiceover: "Watch the pipeline run. Whisper converts speech to text. IndicTrans2 translates every sentence. The system then auto-generates a captioned MP4, an MP3 voiceover in Marathi, SRT subtitles, and a bilingual DOCX document — all in a single ZIP file."

SEGMENT 4 [1:45–2:15 — CONFIDENCE GATE / REVIEW QUEUE]
Lower-third label: "Confidence Gate — AI Quality Assurance"
Callout annotation: Highlight GREEN segments. Label: "Green > 85% — Safe to distribute immediately"
Callout annotation: Highlight AMBER segments. Label: "Amber 65–85% — Needs staff review before distribution"
Callout annotation: Highlight the Edit and Approve buttons. Label: "Staff can correct and approve in one click"
Text overlay: "Approved corrections are saved to Translation Memory — system learns and improves automatically!"
Voiceover: "Every translated sentence receives an AI confidence score. Green means distribute immediately. Amber means a BAIF staff member should review it first. The system enforces distribution clearance — so incorrect content never reaches farmers."

SEGMENT 5 [2:15–2:45 — IMPACT LEDGER]
Lower-third label: "Impact Ledger — Donor-Ready Reporting"
Callout annotation: Highlight the cost saved counter. Label: "₹ Translation cost saved vs. professional agency"
Callout annotation: Highlight the farmers reachable counter. Label: "Estimated farmer reach per language"
Text overlay: "Export to PDF for donor reports with one click."
Voiceover: "The Impact Ledger automatically calculates the money saved versus professional translation agencies, the hours of content translated, and the estimated number of farmers reached in each language — ready for donor and funder reports."

SEGMENT 6 [2:45–3:00 — DOWNLOAD AND DISTRIBUTION]
Lower-third label: "Last-Mile Delivery — WhatsApp & IVR Ready"
Callout annotation: Highlight the download ZIP button. Label: "Download complete translation package"
Text overlay: "ZIP contains: .srt subtitles, .mp3 voiceover, bilingual .docx, captioned .mp4, IVR .wav for feature phones"
Voiceover: "Every ZIP output is ready for WhatsApp broadcast, IVR telecom systems, or direct field officer distribution. VaaniSetu bridges the language gap — from the BAIF office to the last-mile farmer."

STYLE:
- Text overlays: White text on semi-transparent dark green background (#2F855A at 80% opacity)
- Callout arrows: Bright amber (#F6AD55), thick, animated pulse
- Voiceover: Clear, confident, moderately paced English. Professional tone.
- DO NOT hide the real application UI at any point
```

---

## Video 3 — BAIF Staff Training & Handover Video
*For the IT Admin and Training Officers at BAIF Pune HQ. This is a longer reference video (5–8 minutes) in simple language. Marathi preferred.*

### 🎬 Google Flow / Vids Prompt

```
Create a professional staff training video for BAIF Development Research Foundation staff members who are not technical experts. The video teaches them how to use the VaaniSetu translation platform in their daily work. Language: Marathi with English subtitles. Duration: 5–8 minutes.

TARGET AUDIENCE: BAIF field officers, training coordinators, and administrative staff in Pune. Average tech literacy: can use WhatsApp and Google Forms. They are not engineers.

TONE: Warm, encouraging, simple. Like a senior colleague showing you something helpful — not a lecture. Use a friendly voiceover voice, not robotic.

VIDEO STRUCTURE:

CHAPTER 1: "VaaniSetu म्हणजे काय?" [What is VaaniSetu?] (0:00–1:30)
Visual: Animated infographic showing the problem — an English video vs. a Marathi farmer.
Voiceover (Marathi): "BAIF च्या शेतकरी मित्रांसाठी एक आनंदाची बातमी! आता आपले इंग्रजी प्रशिक्षण व्हिडिओ कोणत्याही भारतीय भाषेत रूपांतरित होऊ शकतात — मोफत, इंटरनेटशिवाय, फक्त आपल्या ऑफिसमधून."
English subtitle: "Great news for BAIF's farmer friends! Our English training videos can now be converted into any Indian language — for free, without internet, right from our office."
Show: Simple flow diagram — Video file → VaaniSetu box → Marathi MP4 + Marathi Audio + Bilingual Document

CHAPTER 2: "पहिल्यांदा कसे करावे" [How to do it for the first time] (1:30–3:30)
Visual: Screen recording of the actual login page and upload page.
Step-by-step callouts with large text:
  Step 1: "ब्राउझर उघडा आणि http://vaanisetu.local टाइप करा" 
  Step 2: "आपले नाव आणि पासवर्ड टाका"
  Step 3: "Upload बटण दाबा, व्हिडिओ निवडा"
  Step 4: "मराठी भाषा निवडा आणि Submit करा"
  Step 5: "थांबा — AI आपोआप काम करतो. चहा प्या!"
Show a real progress bar animating.
Voiceover (Marathi): "जेव्हा जॉब पूर्ण होईल, तेव्हा हिरव्या रंगात 'Completed' दिसेल. आता Download बटण दाबा."

CHAPTER 3: "Review Queue — महत्त्वाचे!" [Review Queue — Important!] (3:30–5:00)
Visual: Screen recording of the Review Queue page showing Amber and Green segments.
Voiceover (Marathi): "काही वेळा AI ला खात्री नसते. अशा वेळी Translation पिवळ्या रंगात दिसते — याला 'Amber' म्हणतात."
English subtitle: "Sometimes the AI is not certain. These translations appear in yellow — called 'Amber'."
Show: Staff member clicks on an Amber translation, edits it in the text box, and clicks "Approve."
Voiceover (Marathi): "हे अनुवाद तपासा. चुकीचे असेल तर दुरुस्त करा आणि Approve दाबा. एकदा तुम्ही सुधारल्यावर, AI ते लक्षात ठेवतो आणि पुढच्या वेळी आपोआप बरोबर करतो."
English subtitle: "Check these translations. If wrong, correct and approve. Once corrected, the AI remembers and automatically gets it right next time."
Important callout box: "⚠️ Amber translations वितरित करण्यापूर्वी नेहमी तपासा" / "Always review Amber translations before distributing to farmers."

CHAPTER 4: "Impact Ledger — आपल्या कामाचे मोजमाप" [Measuring your impact] (5:00–6:00)
Visual: Impact Ledger page with animated counters.
Voiceover (Marathi): "Impact Ledger आपल्याला दाखवतो की आपण किती खर्च वाचवला, किती वेळ वाचवला, आणि किती शेतकऱ्यांपर्यंत पोहोचलो. हे donors आणि management ला दाखवण्यासाठी PDF म्हणून डाउनलोड करता येते."
English subtitle: "The Impact Ledger shows money saved, time saved, and how many farmers you reached. Download as PDF for donors and management."

CHAPTER 5: "समस्या आली तर काय करावे?" [What to do if something goes wrong?] (6:00–7:30)
Visual: Simple troubleshooting flowchart — friendly cartoon style.
Show 3 scenarios with icons:
  🔴 Red scenario: "Server बंद झाला" → "IT Admin ला सांगा. File पुन्हा submit करा."
  🟡 Yellow scenario: "Review Queue मध्ये 200+ items" → "टीम बरोबर review session organize करा."
  🟢 Green scenario: "New staff member" → "Browser उघडा, login करा, training video पाहा!"
Voiceover (Marathi): "कोणतीही समस्या असल्यास, घाबरू नका. IT Admin शी संपर्क करा. सर्व माहिती VaaniSetu Handover Document मध्ये आहे."

CHAPTER 6: "Quick Reference Card" (7:30–8:00)
Visual: Clean infographic summary card — like a fridge magnet.
Show: 4 key steps in large text with icons.
  📤 Upload → 🤖 AI translates → ✅ Review amber → 📥 Download ZIP
Voiceover (Marathi): "लक्षात ठेवा — Upload, Review, Download. बाकी सगळं VaaniSetu करतो."
English subtitle: "Remember — Upload, Review, Download. VaaniSetu does everything else."

FINAL FRAME:
VaaniSetu logo + BAIF logo side by side.
Text: "Made with ❤️ for BAIF Pune by Team VaaniSetu"
Support contact line: "IT Support: [BAIF IT Admin Name] | Ext: XXXX"

PRODUCTION NOTES:
- Marathi script on screen must use Devanagari Unicode (not transliteration)
- All chapter titles should be visible as chapter markers for easy navigation
- Keep individual sentences short — staff may pause and re-watch specific steps
- Use screen recordings of the real VaaniSetu app — do not use placeholder mockups
- Add chapter markers at each section start for YouTube / internal LMS navigation
```

---

## Quick Reference: Video Asset Checklist

| Video | Duration | Language | Priority | Where Used |
|-------|----------|----------|----------|-----------|
| Video 1: Pitch | 60 seconds | Marathi VO + English subs | 🔴 CRITICAL | Hackathon stage |
| Video 2: Demo Recording | 3 minutes | English VO + overlays | 🔴 CRITICAL | Embedded in pitch deck / fallback |
| Video 3: Staff Training | 5–8 minutes | Marathi VO + English subs | 🟡 HIGH | BAIF Handover Package |

## Tools Recommended for Video Generation

| Tool | Best For | Notes |
|------|----------|-------|
| **Google Vids** | AI-assisted video with script prompts | Direct integration with Google Workspace |
| **Synthesia** | AI avatar presenter speaking Marathi | Supports Indian languages and accents |
| **HeyGen** | Realistic AI presenters | Good for staff training format |
| **Runway Gen-3** | Cinematic shots (farmer, fields) | For pitch video B-roll |
| **OBS Studio** | Screen recording for demo video | Free, reliable, no watermark |
| **Loom** | Quick screen + face recording | Good for voiceover-over-screen style |
| **Canva Video** | Adding overlays, callouts, lower thirds | Easiest for non-technical team members |

---
*Document prepared for VaaniSetu Team | BAIF Hackathon July 2026 | Pune, Maharashtra*
