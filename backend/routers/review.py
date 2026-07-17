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

    with get_db() as conn:
        conn.execute(
            """
            UPDATE review_queue
            SET status=?, reviewer=?, edited_translation=?, reviewed_at=?
            WHERE id=?
            """,
            (new_status, body.reviewer, edited_text, now, item_id),
        )

        if body.action in ("approve", "edit"):
            # Store to TM with confidence=0.92
            store_approved(
                src_lang=row["source_lang"],
                tgt_lang=row["target_lang"],
                source_text=row["source_text"],
                translated_text=edited_text,
            )

        # Check if all items for this job are now resolved
        job_id = row["job_id"]
        pending = conn.execute(
            "SELECT COUNT(*) as c FROM review_queue WHERE job_id=? AND status='pending'",
            (job_id,),
        ).fetchone()["c"]

        if pending == 0:
            conn.execute(
                "UPDATE jobs SET distribution_clearance='cleared' WHERE id=?",
                (job_id,),
            )
            logger.info(f"Job {job_id} cleared for distribution")

    return {"success": True, "new_status": new_status}
