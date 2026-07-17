"""
VaaniSetu — Async Job Queue
FIFO queue with a single background worker — one job at a time.
"""

import asyncio
import logging

logger = logging.getLogger("vaanisetu.queue")

_queue: asyncio.Queue = asyncio.Queue()
_current_job_id: str | None = None
_queue_lock = asyncio.Lock()


def get_queue_depth() -> int:
    return _queue.qsize()


def get_current_job() -> str | None:
    return _current_job_id


async def enqueue(job_id: str) -> None:
    await _queue.put(job_id)
    logger.info(f"Job {job_id} enqueued. Queue depth: {_queue.qsize()}")


async def worker() -> None:
    """
    Infinite loop consuming job IDs from the queue.
    Called once at FastAPI startup as an asyncio background task.
    """
    global _current_job_id
    logger.info("Job queue worker started")

    while True:
        job_id = await _queue.get()
        _current_job_id = job_id
        logger.info(f"Processing job {job_id}")
        try:
            from backend.pipeline.processor import run_pipeline
            await asyncio.get_event_loop().run_in_executor(None, run_pipeline, job_id)
        except Exception as e:
            logger.error(f"Job {job_id} failed with unhandled error: {e}", exc_info=True)
        finally:
            _current_job_id = None
            _queue.task_done()
