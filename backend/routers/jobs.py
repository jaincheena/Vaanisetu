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

# Languages currently supported end-to-end (Piper + IndicTrans2 verified)
ACTIVE_LANGS = {"Hindi", "Marathi", "English", "Gujarati", "Bengali", "Kannada"}

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
    quality_mode: str = Form("full"),  # 'draft' | 'full'
    output_formats: str = Form(default=None),  # JSON array e.g. '["txt","srt","mp3"]'
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

    # Validate all requested target languages are in the active set
    invalid = [l for l in langs if l not in ACTIVE_LANGS]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Languages not yet supported: {', '.join(invalid)}. Active languages: {', '.join(sorted(ACTIVE_LANGS))}"
        )

    parsed_output_formats = None
    if output_formats:
        try:
            import json as _json
            parsed_output_formats = _json.loads(output_formats)
        except Exception:
            pass

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
             source_lang, target_langs, status, queued_at, farmer_context, quality_mode, output_formats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?, ?, ?)
            """,
            (job_id, mode, current_user["username"], file.filename, file_hash, file_size, input_type,
             source_lang, json.dumps(langs), now, farmer_context, quality_mode,
             json.dumps(parsed_output_formats) if parsed_output_formats else None),
        )

    await enqueue(job_id)
    return {"job_id": job_id, "message": "Job queued"}


@router.get("/scenarios")
async def get_demo_scenarios():
    """Return pre-configured realistic agricultural demonstration scenarios for 1-click test runs."""
    return [
        {
            "id": "scenario_wheat_rust",
            "title": "🌾 Maharashtra & National Crop Disease Advisory",
            "subtitle": "Wheat Yellow Rust Fungicide Protocol (Maharashtra & Central India)",
            "source_lang": "English",
            "target_langs": ["Marathi", "Hindi", "Gujarati", "Telugu", "Kannada"],
            "mode": "translate",
            "quality_mode": "draft",
            "output_formats": ["txt", "docx", "srt", "vtt", "mp3", "ivr_wav", "dubbed_mp4", "whatsapp"],
            "farmer_context": "Immediate advisory for wheat farmers across Maharashtra and Vidarbha. Yellow Rust spores detected in field blocks. Recommend Propiconazole 25% EC spray.",
            "sample_text": "Immediate advisory for wheat farmers across Maharashtra and Gujarat: Yellow Rust fungal spores have been detected in regional field blocks. For rapid containment, spray Propiconazole 25% EC at 1 ml per liter of water immediately across the entire canopy. Avoid excessive urea fertilizer application during early vegetative stages. Contact your nearest Krishi Vigyan Kendra (KVK) or BAIF field extension officer for door-step guidance.",
        },
        {
            "id": "scenario_dairy_care",
            "title": "🐄 Livestock Veterinary & Dairy Advisory",
            "subtitle": "Lumpy Skin Disease (LSD) Prevention for Indigenous Gir & Sahiwal Breeds",
            "source_lang": "English",
            "target_langs": ["Marathi", "Hindi", "Gujarati", "Bengali", "Kannada"],
            "mode": "translate",
            "quality_mode": "draft",
            "output_formats": ["txt", "docx", "srt", "vtt", "mp3", "ivr_wav", "dubbed_mp4", "whatsapp"],
            "farmer_context": "BAIF Livestock Development Programme. Prevention, goat pox vaccination, and isolation protocols for dairy cattle showing fever and nodular skin eruptions.",
            "sample_text": "Urgent advisory for dairy farmers: To protect your Gir and Sahiwal cattle from Lumpy Skin Disease (LSD), administer goat pox vaccine immediately. If cattle exhibit high fever, watery eyes, or cutaneous nodules, isolate them into quarantine sheds. Apply organic neem oil formulation on open skin lesions to prevent secondary bacterial infection and fly bites. Provide mineral mixture and fresh water daily. Contact BAIF veterinary field team for doorstep emergency care.",
        },
        {
            "id": "scenario_reverse_bridge",
            "title": "🎙️ Farmer Voice Query → Pune HQ Agronomists",
            "subtitle": "Bundelkhand Chickpea Farmer Query forwarded to Central Agronomists",
            "source_lang": "Hindi",
            "target_langs": ["Marathi", "English"],
            "mode": "reverse_bridge",
            "quality_mode": "draft",
            "output_formats": ["txt", "docx", "mp3", "ivr_wav", "dubbed_mp4"],
            "farmer_context": "Field query from Bundelkhand region: Drip irrigation emitter clogging due to hard water salt accumulation in chickpea fields.",
            "sample_text": "नमस्ते साहब, हमारे ड्रिप इरिगेशन (Drip Irrigation) की नलियों में खारे पानी की वजह से सफेद नमक जम गया है और पानी बहुत धीमा टपक रहा है। क्या हम इसमें हाइड्रोक्लोरिक एसिड का एसिड ट्रीटमेंट कर सकते हैं? कृपया चना फसल के लिए सही घोल की मात्रा, पीएच स्तर और सुरक्षा सावधानियां तुरंत बताएं।",
        }
    ]


@router.get("/{job_id}/preview")
async def preview_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Return in-browser preview data (transcripts, audio availability, and manifest) for completed jobs."""
    import zipfile
    with get_db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found")
    
    data = dict(row)
    if data.get("target_langs"):
        try:
            data["target_langs"] = json.loads(data["target_langs"])
        except Exception:
            pass

    zip_p = data.get("output_path") or str(job_zip_path(job_id))
    files_list = []
    translations = {}
    subtitles = {}
    transcript = ""
    manifest = {}

    if os.path.exists(zip_p):
        try:
            with zipfile.ZipFile(zip_p, 'r') as z:
                files_list = z.namelist()
                if "manifest.json" in files_list:
                    manifest = json.loads(z.read("manifest.json").decode("utf-8"))
                if "transcript.txt" in files_list:
                    transcript = z.read("transcript.txt").decode("utf-8")
                for fn in files_list:
                    if fn.startswith("translation_") and fn.endswith(".txt"):
                        lang = fn.replace("translation_", "").replace(".txt", "")
                        translations[lang] = z.read(fn).decode("utf-8")
                    elif fn.startswith("subtitles_") and fn.endswith(".srt"):
                        lang = fn.replace("subtitles_", "").replace(".srt", "")
                        subtitles[lang] = z.read(fn).decode("utf-8")
        except Exception as e:
            logger.warning(f"Error reading zip for preview: {e}")

    return {
        "job": data,
        "files": files_list,
        "manifest": manifest,
        "transcript": transcript,
        "translations": translations,
        "subtitles": subtitles,
    }


@router.get("/{job_id}/audio/{lang_name}")
async def stream_audio_file(job_id: str, lang_name: str):
    """Stream translated MP3 audio directly with proper HTTP range support."""
    import zipfile
    from fastapi import Response
    from backend.utils.file_utils import job_workspace
    ws_dir = job_workspace(job_id)
    target_name = f"audio_{lang_name}.mp3"
    
    # 1. Direct workspace check
    ws_audio = ws_dir / target_name
    if ws_audio.exists():
        return FileResponse(str(ws_audio), media_type="audio/mpeg", headers={"Accept-Ranges": "bytes"})
        
    # 2. Check ZIP archive
    zip_p = str(job_zip_path(job_id))
    if os.path.exists(zip_p):
        try:
            with zipfile.ZipFile(zip_p, 'r') as z:
                if target_name in z.namelist():
                    audio_bytes = z.read(target_name)
                    return Response(
                        content=audio_bytes,
                        media_type="audio/mpeg",
                        headers={
                            "Accept-Ranges": "bytes",
                            "Content-Length": str(len(audio_bytes)),
                            "Content-Disposition": f"inline; filename={target_name}",
                            "Cache-Control": "public, max-age=3600"
                        }
                    )
        except Exception as e:
            logger.warning(f"Error reading audio from ZIP: {e}")

    raise HTTPException(404, f"Audio for {lang_name} not found")


@router.get("/{job_id}/ivr/{lang_name}")
async def stream_ivr_file(job_id: str, lang_name: str):
    """Stream 8kHz telephony WAV audio for IVR playback."""
    import zipfile
    from fastapi import Response
    from backend.utils.file_utils import job_workspace
    ws_dir = job_workspace(job_id)
    target_name = f"ivr_audio_{lang_name}.wav"
    ws_ivr = ws_dir / target_name
    if ws_ivr.exists():
        return FileResponse(str(ws_ivr), media_type="audio/wav", headers={"Accept-Ranges": "bytes"})
    
    # Check ZIP archive
    zip_p = str(job_zip_path(job_id))
    if os.path.exists(zip_p):
        try:
            with zipfile.ZipFile(zip_p, 'r') as z:
                if target_name in z.namelist():
                    ivr_bytes = z.read(target_name)
                    return Response(
                        content=ivr_bytes,
                        media_type="audio/wav",
                        headers={
                            "Accept-Ranges": "bytes",
                            "Content-Length": str(len(ivr_bytes)),
                            "Content-Disposition": f"inline; filename={target_name}",
                            "Cache-Control": "public, max-age=3600"
                        }
                    )
        except Exception:
            pass

    # Fallback to standard MP3 audio
    return await stream_audio_file(job_id, lang_name)


@router.get("/{job_id}/video/{lang_name}")
async def stream_video_file(job_id: str, lang_name: str):
    """Stream translated dubbed/advisory MP4 video for in-browser playback."""
    import zipfile
    from fastapi import Response
    from backend.utils.file_utils import job_workspace
    ws_dir = job_workspace(job_id)
    
    candidates = [
        f"video_dubbed_{lang_name}.mp4",
        f"dubbed_{lang_name}.mp4",
        f"video_advisory_{lang_name}.mp4",
        f"captioned_{lang_name}.mp4"
    ]

    for candidate in candidates:
        ws_vid = ws_dir / candidate
        if ws_vid.exists():
            return FileResponse(str(ws_vid), media_type="video/mp4", headers={"Accept-Ranges": "bytes"})
            
    zip_p = str(job_zip_path(job_id))
    if os.path.exists(zip_p):
        try:
            with zipfile.ZipFile(zip_p, 'r') as z:
                for candidate in candidates:
                    if candidate in z.namelist():
                        vid_bytes = z.read(candidate)
                        return Response(
                            content=vid_bytes,
                            media_type="video/mp4",
                            headers={
                                "Accept-Ranges": "bytes",
                                "Content-Length": str(len(vid_bytes)),
                                "Content-Disposition": f"inline; filename={candidate}",
                                "Cache-Control": "public, max-age=3600"
                            }
                        )
        except Exception as e:
            logger.warning(f"Error reading video from ZIP: {e}")

    raise HTTPException(404, f"Video for {lang_name} not found")


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
            try:
                d["target_langs"] = json.loads(d["target_langs"])
            except Exception:
                pass
        result.append(d)
    return result


@router.delete("/history/clear")
async def clear_history(current_user: dict = Depends(get_current_user)):
    """Purge synthetic/test runs and old failed jobs from history."""
    with get_db() as conn:
        conn.execute("DELETE FROM jobs WHERE id LIKE 'test_%' OR file_hash LIKE 'hash%' OR status='failed'")
    return {"success": True, "message": "Test runs cleared from history"}


@router.delete("/{job_id}")
async def delete_single_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a specific job and its outputs."""
    with get_db() as conn:
        conn.execute("DELETE FROM review_queue WHERE job_id=?", (job_id,))
        conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    return {"success": True, "job_id": job_id}
