# VaaniSetu Comprehensive Testing Guide & Scenarios

As VaaniSetu is deployed to BAIF centers, thorough testing is critical. This guide provides a structured QA checklist, recommended agricultural test data, and instructions for testing the system's edge cases in field scenarios.

**Note for Field Validation:** Always select the primary regional language of the local BAIF center during testing to ensure the translated agricultural terminology resonates with the local staff.

---

## 1. Recommended Test Data (Agricultural Content)

To prove the system works for BAIF's actual use case, do not test with generic videos (like movie trailers). Use real Indian agricultural content.

### Video Test Files (Download via YouTube)
You can use free tools like `yt-dlp` or any online YouTube downloader to grab these short clips for testing:
1. **Drip Irrigation Basics (English):** Search *"Introduction to Drip Irrigation for Farmers"* (Find a 2-5 minute clip).
2. **Pest Management:** Search *"Integrated Pest Management Fall Armyworm"* (Great for testing technical terminology translation).
3. **SRI Rice Cultivation:** Search *"System of Rice Intensification Training"* (Tests specific agricultural acronyms).

### Audio & Document Test Files
- **Farmer Query (Audio):** Record a 15-second voice memo on your phone speaking in Marathi: *"माझ्या टोमॅटोच्या पिकावर पांढरे डाग पडले आहेत, मी काय करू?"* (My tomato crop has white spots, what should I do?). Use this to test the **Reverse Bridge**.
- **Handout (DOCX):** Create a 1-page Word document with a bulleted list of fertilizer mixing instructions in English.

---

## 2. Manual QA Test Scenarios (The "Happy Path")

Run these tests to ensure the core pipeline is functioning perfectly before production rollout.

| Test ID | Scenario | Steps to Execute | Expected Result | Pass/Fail |
|---------|----------|------------------|-----------------|-----------|
| **QA-01** | Standard Video Translation | 1. Upload a 2-minute English agriculture video.<br>2. Select **Marathi** and **Hindi**.<br>3. Click Start. | Progress bar completes. ZIP downloads containing: `.mp4` (captioned), `.docx` (bilingual), `.mp3` (voiced), and `whatsapp_part01.mp4`. | [ ] |
| **QA-02** | Document Translation | 1. Upload a `.docx` file (English).<br>2. Select **Marathi**.<br>3. Click Start. | Extremely fast processing (< 1 min). Returns a translated bilingual `.docx` file. | [ ] |
| **QA-03** | Reverse Bridge (Farmer Audio) | 1. Toggle "Reverse Bridge" in UI.<br>2. Upload Marathi farmer voice memo (`.m4a` or `.mp3`).<br>3. Select **English**.<br>4. Click Start. | Audio is transcribed from Marathi and translated into English text for HQ experts to read. | [ ] |
| **QA-04** | Translation Memory Cache Hit | 1. Upload the EXACT same video from QA-01.<br>2. Select **Marathi** and **Hindi** again.<br>3. Click Start. | The system skips Whisper/IndicTrans2 and instantly returns the ZIP file (Smart Dedup). | [ ] |

---

## 3. Edge Case & Stress Testing

Production readiness means proving the system doesn't break when users do unexpected things. Test these edge cases to verify the robust optimizations we implemented.

| Test ID | Scenario | Steps to Execute | Expected Result | Pass/Fail |
|---------|----------|------------------|-----------------|-----------|
| **EDGE-01** | RAM Limit / Chunked Upload Test | 1. Find a massive file (e.g., a 1.5GB movie or `.iso` file).<br>2. Attempt to upload it to VaaniSetu. | The UI immediately rejects the file showing "File exceeds maximum allowed size (200MB)" **without** crashing the server or spiking laptop RAM. | [ ] |
| **EDGE-02** | Smart Dedup (Language Mismatch) | 1. Upload `drip_irrigation.mp4` and translate to **Marathi** (Wait for completion).<br>2. Upload `drip_irrigation.mp4` again, but this time select **Odia**.<br>3. Click Start. | The system does *not* instantly return the cached ZIP. It correctly re-runs the pipeline to generate the newly requested Odia translation. | [ ] |
| **EDGE-03** | Confidence Gate & Review Queue | 1. Upload a video with extreme background noise or heavy technical jargon.<br>2. Go to the "Review" tab while it translates. | Segments with low AI confidence appear flagged in Amber/Red. The job status shows "Pending Review - Hold Distribution". | [ ] |
| **EDGE-04** | Whisper Empty Segment Guard | 1. Upload an audio file that is 60 seconds of pure silence.<br>2. Select **Marathi**. | The system processes it without crashing IndicTrans2 (the sanitization layer skips the empty strings) and returns an empty/blank output. | [ ] |
| **EDGE-05** | Auto-Disk Recovery Cleanup | 1. Note the free space on your `C:\` drive.<br>2. Run a 50MB video translation.<br>3. Check `C:\VaaniSetu\workspace\` and `uploads\`. | The massive intermediate `.wav` files and original uploads are gone. Only the final `.zip` remains in `outputs\`. Free space is recovered. | [ ] |
| **EDGE-06** | Hardware Resource Saver | 1. Check the "Resource Saver" toggle in the UI.<br>2. Upload a video and start translation.<br>3. Open Windows Task Manager (Ctrl+Shift+Esc). | CPU usage is throttled. The PC remains usable for other tasks (browsing, email) while the AI runs in the background. | [ ] |

---

## 4. Built-in Automated Test Suites

VaaniSetu includes production-grade test suites that validate orchestration, memory scaling, pipeline execution, and model fallbacks without requiring GPU execution:

### C. Translation Model Fallback Unit Test
```cmd
python tests/test_translator_fallback.py
```
**Validates graceful fallback** to source text with red confidence flag when models are temporarily unavailable or loading.

---

## 5. Automated API Integration Script

For end-to-end integration testing against a running FastAPI backend:

```python
import requests
import time
import os

BASE_URL = "http://localhost:8765/api/jobs"

def test_pipeline():
    print("--- Starting VaaniSetu Automated API Test ---")
    
    # 1. Create a dummy text file to test document translation
    with open("test_agri.txt", "w", encoding="utf-8") as f:
        f.write("Drip irrigation saves up to 50% of water usage for tomato crops.")
    
    # 2. Submit the job targeting Marathi
    print("Submitting job targeting Marathi...")
    with open("test_agri.txt", "rb") as f:
        files = {"file": f}
        data = {
            "target_langs": '["Marathi"]',
            "source_lang": "English",
            "mode": "translate",
            "resource_saver": "false"
        }
        response = requests.post(f"{BASE_URL}/submit", files=files, data=data)
        
    assert response.status_code == 200, f"Submit failed: {response.text}"
    job_id = response.json()["job_id"]
    print(f"Job queued successfully. ID: {job_id}")
    
    # 3. Poll for status
    while True:
        status_resp = requests.get(f"{BASE_URL}/{job_id}/status")
        status_data = status_resp.json()
        current_status = status_data["status"]
        
        print(f"Current Status: {current_status}")
        if current_status in ["completed", "failed"]:
            break
        time.sleep(2)
        
    assert current_status == "completed", "Job did not complete successfully."
    
    # 4. Cleanup
    os.remove("test_agri.txt")
    print("--- Test Passed Successfully! ---")

if __name__ == "__main__":
    test_pipeline()
```
