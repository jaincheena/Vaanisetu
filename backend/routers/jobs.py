"""
VaaniSetu — Jobs Router
POST /api/jobs/submit | GET /api/jobs/{id}/stream | /status | /download | /history
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse

from backend.config import UPLOADS_DIR, ALLOWED_EXTENSIONS, LANG_CODES
from backend.database import get_db, rows_to_list
from backend.pipeline.job_queue import enqueue
from backend.utils.file_utils import sha256_file, new_job_id, job_zip_path, safe_filename
from backend.utils.sse import sse_manager
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
logger = logging.getLogger("vaanisetu.router.jobs")


@router.post("/submit")
async def submit_job(
    file: UploadFile = File(...),
    target_langs: str = Form(...),   # JSON array e.g. '["Hindi","Bengali"]'
    source_lang: str  = Form("English"),
    mode: str         = Form("translate"),
    farmer_context: str = Form(""),
    resource_saver: bool = Form(False),
    bypass_cache: bool = Form(False),
    current_user: dict = Depends(get_current_user),
):
    job_id = new_job_id()
    now = datetime.utcnow().isoformat()
    
    if resource_saver:
        farmer_context = f"[RESOURCE_SAVER] {farmer_context}"

    # --- Validate file type ---
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {suffix}")

    # --- Parse target langs ---
    try:
        langs = json.loads(target_langs)
        assert isinstance(langs, list) and len(langs) > 0
    except Exception:
        raise HTTPException(400, "target_langs must be a non-empty JSON array")

    # --- Save upload (Chunked to prevent RAM spikes) ---
    filename = f"{job_id}_{safe_filename(file.filename or 'upload')}"
    upload_path = UPLOADS_DIR / filename
    
    file_size = 0
    size_limits = {
        ".mp3": 100 * 1024 * 1024,
        ".ogg": 100 * 1024 * 1024,
        ".m4a": 100 * 1024 * 1024,
        ".aac": 100 * 1024 * 1024,
        ".opus": 100 * 1024 * 1024,
        ".3gp": 100 * 1024 * 1024,
        ".amr": 100 * 1024 * 1024,
        ".caf": 100 * 1024 * 1024,
        ".wma": 100 * 1024 * 1024,
        ".wav": 200 * 1024 * 1024,
    }
    max_allowed = size_limits.get(suffix, 2048 * 1024 * 1024)

    with open(upload_path, "wb") as f_out:
        while chunk := await file.read(65536):
            file_size += len(chunk)
            if file_size > max_allowed:
                upload_path.unlink(missing_ok=True)
                raise HTTPException(400, f"File exceeds maximum allowed size ({max_allowed/1024/1024:.0f}MB)")
            f_out.write(chunk)

    file_hash = sha256_file(upload_path)

    # --- Smart Dedup: return cached ZIP only if target_langs match ---
    if not bypass_cache:
        with get_db() as conn:
            existing = conn.execute(
                "SELECT id, output_path, target_langs FROM jobs WHERE file_hash=? AND status='completed'",
                (file_hash,),
            ).fetchall()
            
            for row in existing:
                if row["output_path"] and os.path.exists(row["output_path"]):
                    try:
                        cached_langs = json.loads(row["target_langs"] or "[]")
                        if set(langs).issubset(set(cached_langs)):
                            logger.info(f"Dedup hit: {file_hash} → job {row['id']}")
                            await sse_manager.publish(row["id"], "completed", "Done! ✅ Cached result ready!")
                            return {"job_id": row["id"], "message": "Duplicate — returning cached result"}
                    except Exception:
                        pass

    # --- Determine input type ---
    input_type = "text" if suffix in {".txt", ".pdf", ".docx", ".csv"} else (
        "video" if suffix in {".mp4", ".mkv", ".avi", ".mov", ".webm"} else "audio"
    )

    # --- Insert job row ---
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO jobs
            (id, mode, submitter_id, filename, file_hash, file_size, input_type,
             source_lang, target_langs, status, queued_at, farmer_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?)
            """,
            (job_id, mode, current_user["username"], file.filename, file_hash, file_size, input_type,
             source_lang, json.dumps(langs), now, farmer_context),
        )

    await enqueue(job_id)
    return {"job_id": job_id, "message": "Job queued"}


@router.get("/{job_id}/stream")
async def stream_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Server-Sent Events — streams pipeline progress."""
    with get_db() as conn:
        row = conn.execute("SELECT id, status FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found")

    # If job is already completed or failed in DB, seed last event if missing
    if row["status"] in ("completed", "failed") and job_id not in sse_manager._last_event:
        await sse_manager.publish(
            job_id,
            row["status"],
            "Done! ✅" if row["status"] == "completed" else "Job failed"
        )

    return StreamingResponse(
        sse_manager.event_stream(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{job_id}/status")
async def job_status(job_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found")
    d = dict(row)
    if d.get("target_langs"):
        d["target_langs"] = json.loads(d["target_langs"])
    return d


@router.get("/{job_id}/download")
async def download_job(job_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = conn.execute(
            "SELECT output_path, filename FROM jobs WHERE id=? AND status='completed'",
            (job_id,),
        ).fetchone()
    if not row:
        raise HTTPException(404, "Job not found or not completed")
    zip_path = row["output_path"] or str(job_zip_path(job_id))
    if not os.path.exists(zip_path):
        raise HTTPException(404, "Output file not found")
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"vaanisetu_{job_id[:8]}.zip",
    )


@router.get("/history")
async def job_history(mode: str = "", status: str = "", limit: int = 50, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        query = "SELECT * FROM jobs WHERE 1=1"
        params: list = []
        if current_user["role"] != "admin":
            query += " AND submitter_id=?"
            params.append(current_user["username"])
        if mode:
            query += " AND mode=?"
            params.append(mode)
        if status:
            query += " AND status=?"
            params.append(status)
        query += " ORDER BY queued_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()

    result = []
    for r in rows:
        d = dict(r)
        if d.get("target_langs"):
            d["target_langs"] = json.loads(d["target_langs"])
        result.append(d)
    return result
