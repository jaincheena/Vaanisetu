"""
VaaniSetu — Health Router
GET /api/health → {ram_gb, disk_gb, queue_depth, review_pending, models_loaded}
"""

import psutil
from fastapi import APIRouter

from backend.models.registry import registry
from backend.pipeline.job_queue import get_queue_depth, get_current_job
from backend.database import get_db
from backend.config import BASE_DIR

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health():
    vm  = psutil.virtual_memory()
    du  = psutil.disk_usage(str(BASE_DIR.drive + "\\"))

    with get_db() as conn:
        review_pending = conn.execute(
            "SELECT COUNT(*) as c FROM review_queue WHERE status='pending'"
        ).fetchone()["c"]

    return {
        "ram_gb":         round(vm.total / 1e9, 1),
        "ram_free_gb":    round(vm.available / 1e9, 1),
        "disk_gb":        round(du.total / 1e9, 1),
        "disk_free_gb":   round(du.free / 1e9, 1),
        "queue_depth":    get_queue_depth(),
        "current_job":    get_current_job(),   # job currently being processed
        "review_pending": review_pending,
        "models_loaded":  registry.models_status,
        "status": "ok",
    }
