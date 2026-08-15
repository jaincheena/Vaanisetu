"""
VaaniSetu — Async Job Queue
FIFO queue drained by a RAM-sized pool of workers. Jobs beyond the pool's
width wait their turn, so a batch of N runs together and the rest follow.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("vaanisetu.queue")

_queue: asyncio.Queue = asyncio.Queue()

# job_id → worker index, for /api/health. Dict ops are atomic under the GIL
# and only the event loop mutates this, so no extra lock is needed.
_running: dict[str, int] = {}

_workers: list[asyncio.Task] = []
_executor: ThreadPoolExecutor | None = None
_concurrency: int = 1


def get_queue_depth() -> int:
    return _queue.qsize()


def get_current_job() -> str | None:
    """First running job — kept for backwards compatibility."""
    return next(iter(_running), None)


def get_current_jobs() -> list[str]:
    return list(_running)


def get_concurrency() -> int:
    return _concurrency


async def enqueue(job_id: str) -> None:
    await _queue.put(job_id)
    logger.info(f"Job {job_id} enqueued. Queue depth: {_queue.qsize()}")


async def _worker(index: int) -> None:
    """Consume job IDs forever. One of `_concurrency` such tasks."""
    loop = asyncio.get_running_loop()

    while True:
        job_id = await _queue.get()
        _running[job_id] = index
        logger.info(f"[worker {index}] processing job {job_id}")
        try:
            from backend.pipeline.processor import run_pipeline
            await loop.run_in_executor(_executor, run_pipeline, job_id)
        except Exception as e:
            logger.error(
                f"[worker {index}] job {job_id} failed with unhandled error: {e}",
                exc_info=True,
            )
        finally:
            _running.pop(job_id, None)
            _queue.task_done()


async def start_workers() -> None:
    """
    Size the pool against free RAM and spawn the workers.

    Called once at FastAPI startup. Sizing happens here — before any job has
    allocated anything — so the reading reflects a genuinely idle machine.
    """
    global _executor, _concurrency

    from backend.utils.resources import plan

    _concurrency = plan("job")
    _executor = ThreadPoolExecutor(
        max_workers=_concurrency, thread_name_prefix="vaani-job"
    )

    for i in range(_concurrency):
        _workers.append(asyncio.create_task(_worker(i)))

    logger.info(f"Job queue started with {_concurrency} concurrent worker(s)")


async def worker() -> None:
    """Deprecated single-worker entry point — retained for older callers."""
    await start_workers()
