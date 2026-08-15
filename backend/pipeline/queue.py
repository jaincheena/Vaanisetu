"""
VaaniSetu — Queue Module Alias
Forwarding alias to backend.pipeline.job_queue for backward compatibility.
"""

from backend.pipeline.job_queue import *  # noqa: F401, F403
from backend.pipeline.job_queue import (
    get_queue_depth,
    get_current_job,
    get_current_jobs,
    get_concurrency,
    enqueue,
    start_workers,
    worker,
)
