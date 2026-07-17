"""
VaaniSetu — Mock Server (Demo / Presentation Mode)

Simulates the full 7-stage pipeline in ~8 seconds with realistic SSE events
and a working download ZIP, so the frontend looks 100% live during a demo.

Usage:
    python mock_server.py
"""

import asyncio
import json
import logging
import time
import zipfile
import os
from pathlib import Path
from unittest.mock import MagicMock

import uvicorn
from backend.main import app
from backend.models.registry import registry
from backend.pipeline import processor
from backend.config import OUTPUTS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mock_server")

# ── Patch model loader so startup finishes instantly ─────────────────────────
registry.load_all = MagicMock()
registry.models_status = {"whisper": "mock", "indictrans2": "mock", "tts": "mock"}

# ── Realistic 7-stage mock pipeline ──────────────────────────────────────────
STAGES = [
    ("validating",   "Checking file …",                       0.5),
    ("extracting",   "Extracting audio …",                    1.0),
    ("transcribing", "Transcribing speech (Whisper) …",       1.5),
    ("translating",  "Translating → Marathi (IndicTrans2) …", 2.0),
    ("generating",   "Generating SRT, DOCX, TTS MP3 …",       1.5),
    ("packaging",    "Packaging output ZIP …",                0.5),
    ("completed",    "Done! ✅ Distribution Clearance: Green", 0.0),
]


def _make_demo_zip(job_id: str) -> str:
    """Create a minimal but real ZIP so the Download button works."""
    zip_path = str(OUTPUTS_DIR / f"{job_id}.zip")
    manifest = {
        "job_id": job_id,
        "generated": "2026-07-17T00:00:00",
        "source_lang": "English",
        "target_langs": ["Marathi"],
        "files": [
            "translation_Marathi.txt",
            "subtitles_Marathi.srt",
            "bilingual_Marathi.docx",
            "audio_Marathi.mp3",
            "manifest.json",
        ],
    }
    sample_txt = (
        "# VaaniSetu Demo Translation — Marathi\n"
        "शेतकऱ्यांसाठी आधुनिक शेतीच्या पद्धती महत्त्वाच्या आहेत.\n"
        "माती परीक्षण दर तीन वर्षांनी करणे आवश्यक आहे.\n"
        "जैविक खते वापरल्याने जमिनीचा दर्जा सुधारतो.\n"
    )
    sample_srt = (
        "1\n00:00:00,000 --> 00:00:03,500\n"
        "शेतकऱ्यांसाठी आधुनिक शेतीच्या पद्धती महत्त्वाच्या आहेत.\n\n"
        "2\n00:00:03,500 --> 00:00:07,000\n"
        "माती परीक्षण दर तीन वर्षांनी करणे आवश्यक आहे.\n\n"
    )
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json",           json.dumps(manifest, indent=2, ensure_ascii=False))
        zf.writestr("translation_Marathi.txt", sample_txt)
        zf.writestr("subtitles_Marathi.srt",   sample_srt)
        zf.writestr("bilingual_Marathi.docx",  b"(demo placeholder)".decode("latin-1"))
        zf.writestr("audio_Marathi.mp3",        b"(demo placeholder)".decode("latin-1"))
    logger.info(f"Demo ZIP created: {zip_path}")
    return zip_path


def mock_run_pipeline(job_id: str) -> None:
    """Simulates pipeline: publishes SSE events for every stage."""
    from backend.database import get_db
    from backend.utils.sse import sse_manager

    logger.info(f"MOCK PIPELINE ▶ job={job_id}")

    for stage, msg, delay in STAGES:
        # Update DB status
        with get_db() as conn:
            conn.execute("UPDATE jobs SET status=? WHERE id=?", (stage, job_id))

        # Publish SSE event (asyncio.run is safe from a thread)
        try:
            asyncio.run(sse_manager.publish(job_id, stage, msg))
        except Exception:
            pass

        logger.info(f"  [{stage}] {msg}")
        if delay:
            time.sleep(delay)

    # Finalise DB row
    zip_path = _make_demo_zip(job_id)
    with get_db() as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status='completed', avg_confidence=0.92, confidence_level='green',
                distribution_clearance='cleared', output_path=?, completed_at=datetime('now')
            WHERE id=?
            """,
            (zip_path, job_id),
        )
    logger.info(f"MOCK PIPELINE ✅ job={job_id} — ZIP ready at {zip_path}")


processor.run_pipeline = mock_run_pipeline

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("  VaaniSetu MOCK SERVER  (Demo / Presentation Mode)")
    logger.info("  Pipeline completes in ~8 s with live SSE progress")
    logger.info("  Download button will serve a real demo ZIP")
    logger.info("  → http://localhost:8765")
    logger.info("="*60)
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
