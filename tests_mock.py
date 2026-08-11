import asyncio
import json
import logging
import os
import shutil
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO)

# Run init DB
from backend.database import init_db, get_db
from backend.config import UPLOADS_DIR, WORKSPACE_DIR, OUTPUTS_DIR
from backend.utils.file_utils import sha256_file

init_db()

# Ensure directories
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Create a dummy upload file
job_id = str(uuid.uuid4())
filename = f"{job_id}_test_audio.wav"
upload_path = UPLOADS_DIR / filename
with open(upload_path, "wb") as f:
    f.write(b"dummy audio data")

file_hash = sha256_file(upload_path)
now = "2026-07-16T12:00:00Z"

with get_db() as conn:
    conn.execute(
        """
        INSERT INTO jobs
        (id, mode, submitter_id, filename, file_hash, file_size, input_type,
         source_lang, target_langs, status, queued_at, farmer_context)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?)
        """,
        (job_id, "translate", "admin", filename, file_hash, 16, "audio",
         "English", json.dumps(["Hindi", "Bengali"]), now, ""),
    )

print(f"Created mock job {job_id}")

# 2. Start testing the pipeline with mocks
from backend.pipeline import processor

# We mock all external ML and FFmpeg calls
@patch("backend.pipeline.audio_extractor.extract_audio")
@patch("backend.pipeline.transcriber.transcribe")
@patch("backend.pipeline.translator.translate_segments")
@patch("backend.pipeline.tts.generate_tts_for_segments")
@patch("subprocess.run") # for FFmpeg in packager
def test_pipeline_run(mock_subproc, mock_tts, mock_trans, mock_whisper, mock_extract):
    
    # Mock extract
    def fake_extract(upload_path, ws):
        # just create the audio.wav
        with open(ws / "audio.wav", "wb") as f:
            f.write(b"fake wav")
    mock_extract.side_effect = fake_extract
    
    # Mock whisper
    mock_whisper.return_value = (
        [
            {"text": "Hello farmers, this is a test.", "start": 0.0, "end": 2.0},
            {"text": "Irrigation is important.", "start": 2.0, "end": 4.0}
        ],
        "en"
    )
    
    # Mock indictrans2
    def fake_trans(segments, source_lang, target_lang_name, target_lang_code, job_id):
        res = []
        for s in segments:
            res.append({
                **s,
                "translated": f"FAKE TRANSLATION to {target_lang_name}: {s['text']}",
                "confidence": 0.90 if "test" in s["text"] else 0.60,
                "level": "green" if "test" in s["text"] else "amber",
                "target_lang": target_lang_name,
                "from_cache": False
            })
            
            # Check route amber
            if res[-1]["level"] == "amber":
                from backend.pipeline import translator
                translator._add_to_review_queue(
                    job_id=job_id,
                    segment_index=len(res)-1,
                    source_text=s["text"],
                    translated_text=res[-1]["translated"],
                    source_lang=source_lang,
                    target_lang=target_lang_name,
                    confidence=res[-1]["confidence"]
                )
        return res
    mock_trans.side_effect = fake_trans
    
    # Mock TTS
    def fake_tts(segments, lang, mp3_path):
        mp3 = Path(mp3_path)
        with open(mp3, "wb") as f:
            f.write(b"mp3 data")
        return str(mp3)
    mock_tts.side_effect = fake_tts
    
    # Run processor
    try:
        processor.run_pipeline(job_id)
        print("Pipeline execution completed without exceptions.")
    except Exception as e:
        print(f"Pipeline crashed: {e}")
        raise e
        
    # Validation
    with get_db() as conn:
        job = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        
    print(f"Job Status: {job['status']}")
    print(f"Avg Confidence: {job['avg_confidence']}")
    print(f"Clearance: {job['distribution_clearance']}")
    
    # Verify outputs exist
    import zipfile
    zip_path = job["output_path"]
    assert zip_path and os.path.exists(zip_path), "ZIP was not created"
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        files = z.namelist()
        print("Generated files in ZIP:")
        for f in files:
            print(" -", f)
            
    # Check review queue
    with get_db() as conn:
        revs = conn.execute("SELECT * FROM review_queue WHERE job_id=?", (job_id,)).fetchall()
        print(f"Found {len(revs)} amber review items in database.")
        for r in revs:
            print(f"   Review item: {r['source_text']} -> {r['translated_text']}")

if __name__ == "__main__":
    test_pipeline_run()
