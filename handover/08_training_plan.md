# VaaniSetu — Employee Onboarding & Training Plan

> **Document Goal:** Provide an onboarding and training framework for BAIF Development Research Foundation employees.
> **Philosophy:** Learn by doing through interactive simulators, micro-learning video storyboards, and audio scenario exercises.

---

## 1. The 3-Tier Employee Onboarding Framework

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             VAANISETU EMPLOYEE ONBOARDING TRACKS                                 │
├────────────────────────────────┬────────────────────────────────┬────────────────────────────────┤
│ 🌾 LEVEL 1: ROOKIE LOCALIZER   │ 🛡️ LEVEL 2: QUALITY GATEKEEPER │ ⚙️ LEVEL 3: OPERATIONAL HERO   │
│ (Field & Extension Staff)      │ (Bilingual Content Reviewers)  │ (IT & Systems Administrators)  │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ • 1-Click Scenario Presets     │ • Spotting Mistranslations     │ • 100% Offline Air-Gapped USB  │
│ • Direct Mic Voice Recording   │ • Confidence Gate Scenarios    │ • RAM & Mutex Lock Sizing      │
│ • WhatsApp & IVR Simulators    │ • Approving Amber Alerts       │ • Rotating Production Logs     │
│ • Subtitle & Script Formats    │ • Translation Memory Training  │ • 1-Click Automated Rollback   │
└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
```

---

## 2. Interactive In-App Training Academy (`/training`)

BAIF staff can access the **Interactive Training Academy** directly within the web app at `http://localhost:8765/training`:

1. **Interactive Scenario Challenges:** Dynamic agricultural challenges testing AgriShield™ protection (70+ protected terms like PM-KISAN, Gir, Sahiwal, DAP), Confidence Gate approvals, and telecom dispatch.
2. **Instant Score & Explanations:** Explains *why* agricultural terms require protected token shields and why amber segments must never be distributed before review.
3. **Digital Certification Badge:** Generates an offline-verifiable certification diploma with printable timestamp.

---

## 3. Micro-Learning Video Scripts & Audio Guides (60-Second Bytes)

### 🎬 Video Byte 1: "Broadcast Localization in 3 Clicks"
- **Visual Scene:** Field officer opens browser at `http://localhost:8765`.
- **Action (0:00-0:20):** Clicks the green badge `"🌾 Scenario 1: Crop Disease Emergency Advisory"`.
- **Action (0:20-0:40):** Selects Marathi and Hindi, toggles ⚡ **Draft Mode**, and hits `"🚀 Start AI Localization"`.
- **Action (0:40-0:60):** Switches to the **In-Browser Audio Player**, hits play to verify the pitch-matched voice, and downloads the ready-to-share WhatsApp video clips.

### 🎬 Video Byte 2: "The Review Queue & The Amber Alert"
- **Visual Scene:** A yellow badge `"⚠ Review Needed"` pops up in the top navigation.
- **Action (0:00-0:25):** Officer clicks `"Review Queue"` in sidebar. Reads side-by-side: English original vs Hindi machine translation.
- **Action (0:25-0:45):** Corrects a local dialect word for "fertilizer mixture" directly in the inline textbox.
- **Action (0:45-0:60):** Clicks `"Approve"`. Shows how the job status changes to `"🟢 Cleared for Distribution"` and the correction is permanently saved into Translation Memory.

### 🎬 Video Byte 3: "Bridging the Digital Divide (8kHz Telecom IVR)"
- **Visual Scene:** Split screen showing a smartphone farmer vs a tribal farmer holding a ₹1,000 Nokia-style keypad phone.
- **Action (0:00-0:30):** Officer uploads an audio advisory and selects the `"IVR .wav"` format checkbox.
- **Action (0:30-0:60):** Tests the 8kHz audio on the interactive phone dialer simulator in the browser before exporting to BAIF's outbound voice broadcast service.

---

## 4. Hands-On Training Workshop Schedule (2-Hour Interactive Session)

| Time Slot | Module | Interactive Exercise Activity |
| :--- | :--- | :--- |
| **00:00 – 00:20** | **The Big Picture** | Live demonstration: Localizing a 5-minute English training video into Marathi, Hindi, and Gujarati in real-time. |
| **00:20 – 00:50** | **Hands-On Job Arena** | Every trainee opens `http://localhost:8765`, records a 15-second voice note using their laptop mic, and localizes it into their native language. |
| **00:50 – 01:20** | **The Gatekeeper Challenge** | Trainer injects intentional ambiguous terms (e.g. chemical dosages); trainees use the Review Queue to flag, correct, and approve them. |
| **01:20 – 01:45** | **Last-Mile Simulator Race** | Trainees test the WhatsApp message preview and the 8kHz IVR keypad dialer. |
| **01:45 – 02:00** | **Training Academy Review** | All trainees complete the modules at `/training` and print their completion certificates. |

---

## 5. Competency & Certification Checklist

### 🌾 Field Officers & Extension Staff
- [ ] Can connect to `http://localhost:8765` over office WiFi on laptop or smartphone.
- [ ] Can use the 1-Click Realistic Agricultural Presets for rapid demo/testing.
- [ ] Can record voice directly into the browser via the microphone recorder.
- [ ] Can selectively pick output formats (Text, Subtitles, Audio, Video) to save time and disk space.
- [ ] Understands the difference between ⚡ **Draft Mode** (2 min turnaround) and 🎬 **Full Quality Mode** (complete dubbed video).

### 🛡️ Bilingual Reviewers & Content Editors
- [ ] Understands confidence scoring: 🟢 Green ($\ge 85\%$), 🟡 Amber ($65-84\%$), 🔴 Red ($< 65\%$).
- [ ] Never clears amber content for distribution without human verification.
- [ ] Knows how to edit sentences directly in the Review Queue to continuously train the SQLite Translation Memory.
- [ ] Understands how AgriShield™ protects 120+ mission-critical agricultural schemes, pest names, and fertilizers.

### ⚙️ IT & Systems Administrators
- [ ] Can run automated pre-flight checks using `scripts\health_check.bat`.
- [ ] Knows how to execute a disaster recovery rollback using `scripts\rollback.bat`.
- [ ] Understands the 100% offline air-gapped USB deployment procedure (`scripts\install_from_usb.bat`).
- [ ] Knows how to monitor logs at `C:\VaaniSetu\logs\` and start the system using `Launch_VaaniSetu.bat` (4-option menu).
