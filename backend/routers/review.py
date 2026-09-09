"""
VaaniSetu — Review Queue Router
GET /api/review/queue | /stats | POST /api/review/{id}
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from backend.database import get_db
from backend.models.schemas import ReviewAction
from backend.services.translation_memory import store_approved
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/api/review", tags=["review"])
logger = logging.getLogger("vaanisetu.router.review")


@router.get("/queue")
async def get_queue(status: str = "pending", limit: int = 100, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        if status == "all":
            rows = conn.execute(
                "SELECT * FROM review_queue ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM review_queue WHERE status=? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
    return [dict(r) for r in rows]


@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM review_queue").fetchone()["c"]
        by_status = conn.execute(
            "SELECT status, COUNT(*) as c FROM review_queue GROUP BY status"
        ).fetchall()

    counts = {r["status"]: r["c"] for r in by_status}
    return {
        "pending":  counts.get("pending", 0),
        "approved": counts.get("approved", 0),
        "edited":   counts.get("edited", 0),
        "rejected": counts.get("rejected", 0),
        "total":    total,
    }


@router.post("/{item_id}")
async def review_item(item_id: int, body: ReviewAction, current_user: dict = Depends(get_current_user)):
    if body.action not in ("approve", "edit", "reject"):
        raise HTTPException(400, "action must be approve | edit | reject")

    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM review_queue WHERE id=?", (item_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Review item not found")

        now = datetime.utcnow().isoformat()
        new_status = {"approve": "approved", "edit": "edited", "reject": "rejected"}[body.action]
        edited_text = body.edited_text or row["translated_text"]
        reviewer_name = body.reviewer or current_user.get("username", "Field Officer")

        conn.execute(
            """
            UPDATE review_queue
            SET status=?, reviewer=?, edited_translation=?, reviewed_at=?
            WHERE id=?
            """,
            (new_status, reviewer_name, edited_text, now, item_id),
        )

        # Store to TM directly in the same connection to avoid nested connection deadlocks
        if body.action in ("approve", "edit"):
            from backend.utils.file_utils import tm_cache_key
            key = tm_cache_key(row["source_lang"], row["target_lang"], row["source_text"])
            conn.execute(
                """
                INSERT OR REPLACE INTO translation_memory
                (source_hash, source_text, source_lang, target_lang, translated_text,
                 confidence, times_used, created_at, last_used_at, flagged, domain)
                VALUES (?, ?, ?, ?, ?, 0.98, 1, ?, ?, 0, 'agriculture')
                """,
                (key, row["source_text"], row["source_lang"], row["target_lang"], edited_text, now, now),
            )
            # Synchronize corrections directly into the job's output ZIP archive
            _sync_review_to_zip(
                job_id=row["job_id"],
                target_lang=row["target_lang"],
                old_text=row["translated_text"],
                new_text=edited_text,
                reviewer=reviewer_name,
            )

        # Check if all items for this job are now resolved
        job_id = row["job_id"]
        pending_row = conn.execute(
            "SELECT COUNT(*) as c FROM review_queue WHERE job_id=? AND status='pending'",
            (job_id,),
        ).fetchone()
        pending = pending_row["c"] if pending_row else 0

        if pending == 0:
            conn.execute(
                "UPDATE jobs SET distribution_clearance='cleared' WHERE id=?",
                (job_id,),
            )
            logger.info(f"Job {job_id} cleared for distribution")

    return {"success": True, "new_status": new_status, "item_id": item_id}


def _sync_review_to_zip(job_id: str, target_lang: str, old_text: str, new_text: str, reviewer: str) -> None:
    """Update outputs ZIP archive with human review corrections so downloads always match."""
    import os
    import zipfile
    import tempfile
    import json
    from pathlib import Path
    from backend.utils.file_utils import job_zip_path

    zip_path = job_zip_path(job_id)
    if not zip_path.exists():
        return

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            with zipfile.ZipFile(str(zip_path), "r") as z_in:
                z_in.extractall(tmp_path)

            modified = False
            # 1. Update text file
            txt_file = tmp_path / f"translation_{target_lang}.txt"
            if txt_file.exists():
                content = txt_file.read_text(encoding="utf-8")
                if old_text and old_text in content:
                    content = content.replace(old_text, new_text)
                    txt_file.write_text(content, encoding="utf-8")
                    modified = True

            # 2. Update subtitle files
            for sub_ext in ("srt", "vtt"):
                sub_file = tmp_path / f"subtitles_{target_lang}.{sub_ext}"
                if sub_file.exists():
                    sub_content = sub_file.read_text(encoding="utf-8")
                    if old_text and old_text in sub_content:
                        sub_content = sub_content.replace(old_text, new_text)
                        sub_file.write_text(sub_content, encoding="utf-8")
                        modified = True

            # 3. Update manifest
            manifest_file = tmp_path / "manifest.json"
            if manifest_file.exists():
                try:
                    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                    manifest["last_reviewed"] = datetime.utcnow().isoformat()
                    manifest["reviewer"] = reviewer
                    manifest["verified"] = True
                    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
                    modified = True
                except Exception:
                    pass

            if modified:
                temp_zip = tmp_path / "updated.zip"
                with zipfile.ZipFile(str(temp_zip), "w", zipfile.ZIP_DEFLATED) as z_out:
                    for f in tmp_path.iterdir():
                        if f.is_file() and f.name != "updated.zip":
                            z_out.write(str(f), f.name)
                import shutil
                shutil.move(str(temp_zip), str(zip_path))
                logger.info(f"Updated ZIP package for job {job_id} with human review corrections")
    except Exception as e:
        logger.warning(f"Could not update ZIP for job {job_id} after review: {e}")


@router.delete("/clear-all")
async def clear_review_queue(current_user: dict = Depends(get_current_user)):
    """Clear test items from review queue."""
    with get_db() as conn:
        conn.execute("DELETE FROM review_queue WHERE translated_text LIKE 'FAKE TRANSLATION%'")
    return {"success": True, "message": "Test items cleaned up"}
