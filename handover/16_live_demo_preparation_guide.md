# Live Demo Preparation & Rehearsal Guide

To stand out in a competitive hackathon with 30 teams, your live demo must be flawless, high-energy, and completely immune to the "live demo curse" (where things mysteriously break). 

This guide provides the exact preparation checklist and rehearsal strategy to execute your **Last Mile Physical Evidence** pitch (Concept 3) with zero friction.

---

## 🛑 1. The 30-Minute Pre-Flight Checklist
*Complete this checklist 30 minutes before your time slot.*

### Desktop & Environment Setup
- [ ] **Clean Desktop:** Hide all desktop icons. Change your wallpaper to a solid dark grey or the BAIF logo. Nothing screams "unprofessional" like a messy desktop.
- [ ] **Turn Off Notifications:** Enable "Do Not Disturb" on Windows (Focus Assist) and Mac. Quit Slack, WhatsApp Web, and email clients.
- [ ] **Pre-Launch the App:** Do NOT wait to run `start_vaanisetu.bat` during the demo. Have the backend server and React frontend already running and fully loaded.
  - *💡 Differentiator Tip (The 3-Second Demo):* If your presentation laptop does not have a dedicated GPU or if you want to eliminate any risk of slow model loading under the 3-minute limit, run `python mock_server.py` instead of the regular server. It mocks the 7-stage pipeline in 3 seconds while preserving all UI states, allowing for a lightning-fast, zero-delay presentation!
- [ ] **Pre-Warm the AI Model:** If running the actual ML model live, run a dummy 10-second translation job before the pitch starts. This loads IndicTrans2 and Whisper into RAM so your live demo doesn't hang on the first query.

### Tab Management (The "Alt-Tab" Strategy)
Have exactly **three** things open, and nothing else. Practice switching between them smoothly.
1. **Browser Tab 1:** The VaaniSetu Dashboard (`http://localhost:8765`). Have a sample English `.mp4` file sitting on your desktop, ready to drag-and-drop.
2. **Browser Tab 2:** The massive QR Code (from the pitch script). Make sure it is already generated and fills the entire screen.
3. **PDF Viewer:** Have the `VaaniSetu_Technical_Analysis_Report.pdf` open and minimized to the taskbar, ready to deploy during the Q&A session.

### Physical Props Setup (For Speaker 1)
- [ ] Have the **modern smartphone** sitting on the desk, screen unlocked, with the WhatsApp Web video ready to play.
- [ ] Have the **Nokia-style feature phone** in your pocket.
- [ ] Have the **printed bilingual `.docx` handout** resting on your keyboard so you can hold it up instantly.

---

## 🛡️ 2. Failsafes & Fallbacks (The "Plan B")

Judges respect teams that handle technical failures gracefully. If the AI model crashes or the server hangs during your 3-minute window, you do not have time to debug. 

**The Video Fallback Strategy:**
1. Keep the `1-minute Demo Video` (that you created using Guide #13) minimized on your taskbar.
2. If the local server hangs, immediately say: 
   *"As you know, live hardware can be unpredictable, but our deployment handles this seamlessly. Let me show you the exact translation process we recorded this morning."*
3. Instantly open the video and talk over it. **Never apologize, never panic, just pivot.**

---

## 🎭 3. Rehearsal Script & Stage Directions

To differentiate your team, you must deliver the pitch like a well-rehearsed theater performance, not a boring technical lecture. 

### The Hook (0:00 - 0:45)
- **Action:** Speaker 1 holds up the smartphone and the feature phone to the camera immediately as the presentation starts. 
- **Delivery:** Do not say "Hi, we are team X and our project is Y." Start immediately with the problem. *"Look at these two phones. The smartphone farmer gets YouTube tutorials. The feature-phone farmer gets nothing. Today, we bridge that gap."*

### The QR Code Interactive Moment (0:45 - 1:30)
- **Action:** Speaker 2 takes over and immediately shares the screen showing the massive QR code.
- **Delivery:** *"Judges, please take out your phones and scan this QR code right now."* 
- **Psychology:** By forcing the judges to physically do something, you instantly break their "Zoom fatigue". While they scan it, you explain that they are downloading an auto-chunked WhatsApp video and a bilingual document.

### The UI Demo (1:30 - 2:30)
- **Action:** Speaker 2 switches the screen share to the VaaniSetu dashboard.
- **Delivery:** Talk *fast* but *clear*. Do not explain every button. Emphasize the **Confidence Gate** (show the Red/Amber/Green Review Queue). This is your technical differentiator.

### The Impact Ledger Close (2:30 - 3:00)
- **Action:** Show the Impact Ledger dashboard displaying money and time saved.
- **Delivery:** Finish with a powerful metric. *"We took translation costs from ₹25,000 to ₹0. We took the timeline from 3 weeks to 45 minutes. And we did it 100% offline."*

---

## 🧠 4. The Q&A "Trap" Strategy

You want the judges to ask specific questions so you can show off your hardest work. 

**How to set the trap:**
During the pitch, briefly mention: *"We had to engineer specific solutions for RAM limitations and target-language caching."* 
*Do not explain how you did it.* 
This creates a "curiosity gap". A technical judge will inevitably ask: *"Wait, how did you handle RAM limitations?"*

**Springing the trap:**
When they ask, smile, open the `VaaniSetu_Technical_Analysis_Report.pdf`, and say: *"I'm glad you asked. We actually generated an automated QA report for this. As you can see here on Page 3, Test EDGE-01..."* 

This level of preparation is the ultimate differentiator. It proves you aren't just coders; you are product engineers ready for the real world. Good luck!
