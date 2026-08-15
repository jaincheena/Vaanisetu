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


@router.delete("/clear-all")
async def clear_review_queue(current_user: dict = Depends(get_current_user)):
    """Clear test items from review queue."""
    with get_db() as conn:
        conn.execute("DELETE FROM review_queue WHERE translated_text LIKE 'FAKE TRANSLATION%'")
    return {"success": True, "message": "Test items cleaned up"}
