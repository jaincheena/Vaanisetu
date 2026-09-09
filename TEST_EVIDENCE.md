# VaaniSetu: System Integration Test (SIT) Evidence Document

**Client / Stakeholder:** BAIF Development Research Foundation  
**Environment:** Local Field Simulation (16GB RAM Standard Laptop, Offline Processing)  

---

## 1. Requirement Traceability & Execution Results

| Requirement ID | Test Objective | Success Criteria | Status | Evidence / Remarks |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-001** | End-to-End Pipeline Execution | System must process video from upload ➔ transcription ➔ translation ➔ dubbing automatically. | **PASS** ✅ | Zero manual intervention required post-upload. |
| **REQ-002** | Processing Speed Threshold | Total processing time for a standard field video must be `< 30 Minutes`. | **PASS** ✅ | 5-7 min video processed under 20 mins. |
| **REQ-003** | Hardware Portability | Must run locally on a standard 16GB office laptop without cloud GPUs. | **PASS** ✅ | Pipeline dynamically throttled RAM to prevent crashes. |
| **REQ-004** | Multi-Format Deliverables | Must produce MP4 (WhatsApp), Subtitles (VTT/SRT), and Audio Voice Note (WAV). | **PASS** ✅ | Verified ZIP output generation. |
| **REQ-005** | Real-Time Process Monitoring | System must display live, step-by-step progress to the user during long operations. | **PASS** ✅ | Verified SSE real-time progress bar UI. |

---

## 2. Evidence Logs & Visual Proofs

### Test Case 1: Real-Time Pipeline Progress Monitoring
- **Test Condition:** Observe the UI during a long-running transcription and translation job.
- **Expected:** A progress bar showing active stages (Queue ➔ Validate ➔ Extract ➔ Transcribe ➔ Translate ➔ Generate ➔ Package) with real-time percentages via SSE.
- **Actual:** Success.
> <img width="1528" height="747" alt="image" src="https://github.com/user-attachments/assets/b2158720-63e2-441b-bbf1-dbb990e643c9" />

### Test Case 2: Automated Pipeline Completion
- **Test Condition:** Upload a source video and wait for final completion.
- **Expected:** "Localization Complete & Ready" status badge appears.
- **Actual:** Success.
> <img width="1545" height="846" alt="image" src="https://github.com/user-attachments/assets/64c63f49-5483-41b0-bdbb-af823992f50b" />

### Test Case 3: Multi-Channel Output Generation (ZIP Kit)
- **Test Condition:** Download the processed artifacts.
- **Expected:** Availability of Video, Audio, Subtitles, and Bilingual Print Document.
- **Actual:** Success.
> <img width="1172" height="310" alt="image" src="https://github.com/user-attachments/assets/f79790f1-bcbf-4aa0-b266-4d10cafa2ee6" />

### Test Case 4: History & Audit
- **Test Condition:** Access the History & Audit dashboard to review completed, cancelled, or failed jobs.
- **Expected:** Users can review past jobs, verify processing time and check confidence scores.
- **Actual:** Success.
> <img width="1532" height="175" alt="image" src="https://github.com/user-attachments/assets/15c70ca9-01af-43ed-86af-a074e9a04b13" />

### Test Case 5: 100% Offline Capability (Air-Gapped Execution)
- **Test Condition:** Disconnect the system from the internet and process a video.
- **Expected:** The entire pipeline (transcription, translation, TTS) runs successfully using purely local models, proving viability in remote field locations.
- **Actual:** Success.

### Test Case 6: Intelligent Resource Throttling (Low-RAM Handling)
- **Test Condition:** Run the system on a standard 16GB office laptop under memory constraints.
- **Expected:** Instead of crashing, the system detects low memory and automatically throttles to "Serial Mode" (Processing 1 job at a time) to ensure successful completion.
- **Actual:** Success.
> <img width="1447" height="162" alt="image" src="https://github.com/user-attachments/assets/38725706-7eff-4ee2-a6f6-1787e4b222b3" />

### Test Case 7: Automatic Gender Detection & Voice Matching
- **Test Condition:** Upload a video with a distinct male or female speaker.
- **Expected:** The system analyzes the source audio, automatically detects the gender, and assigns a matching synthesized voice for the final dub.
- **Actual:** Success.
> <img width="1472" height="146" alt="image" src="https://github.com/user-attachments/assets/e17dd1d6-80ff-4bb4-a2b8-80dba7733cff" />

