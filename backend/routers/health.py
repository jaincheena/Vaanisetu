"""
VaaniSetu — Health Router
GET /api/health → {ram_gb, disk_gb, queue_depth, review_pending, models_loaded}
"""

import psutil
from fastapi import APIRouter

from backend.models.registry import registry
from backend.pipeline.queue import get_queue_depth, get_current_job, get_current_jobs, get_concurrency
from backend.database import get_db
from backend.utils.resources import plan
from backend.models.pool import snapshot as pool_snapshot
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
        "current_job":    get_current_job(),    # first running job (legacy field)
        "current_jobs":   get_current_jobs(),   # all jobs running right now
        "review_pending": review_pending,
        "models_loaded":  registry.models_status,
        "concurrency": {
            "jobs":     get_concurrency(),      # fixed at startup
            "generate": plan("generate"),       # re-sized per job from free RAM
            "replicas": pool_snapshot(),        # model copies actually loaded
        },
        "status": "ok",
    }
