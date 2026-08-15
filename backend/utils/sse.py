"""
VaaniSetu — Server-Sent Events Manager
Pub/sub system for streaming pipeline progress to browser clients.

Event format (per spec):
    data: {"stage":"translating","pct":60,"message":"..."}\n\n

Stages (in order):
    queued → validating → extracting → transcribing →
    translating → generating → packaging → completed | failed
"""

import asyncio
import json
from collections import defaultdict
from typing import AsyncGenerator


STAGE_PCT: dict[str, int] = {
    "queued":       0,
    "validating":   5,
    "extracting":  15,
    "transcribing":35,
    "translating": 60,
    "generating":  80,
    "packaging":   92,
    "completed":  100,
    "failed":     100,
}


class SSEManager:
    """Manages per-job SSE subscriber queues."""

    def __init__(self):
        self._subs: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self._last_event: dict[str, dict] = {}

    async def subscribe(self, job_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subs[job_id].append(q)
        # Immediately push last known event so clients that connect mid-job catch up
        if job_id in self._last_event:
            await q.put(self._last_event[job_id])
        return q

    def unsubscribe(self, job_id: str, q: asyncio.Queue) -> None:
        subs = self._subs.get(job_id, [])
        try:
            subs.remove(q)
        except ValueError:
            pass

    async def publish(self, job_id: str, stage: str, message: str = "", extra: dict | None = None) -> None:
        pct = STAGE_PCT.get(stage, 0)
        event = {"stage": stage, "pct": pct, "message": message}
        if extra:
            event.update(extra)
        self._last_event[job_id] = event
        for q in list(self._subs.get(job_id, [])):
            await q.put(event)

    async def event_stream(self, job_id: str) -> AsyncGenerator[str, None]:
        """Async generator yielding SSE-formatted strings."""
        q = await self.subscribe(job_id)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=25.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    if event.get("stage") in ("completed", "failed"):
                        break
                except asyncio.TimeoutError:
                    # Heartbeat to keep connection alive
                    yield f"data: {json.dumps({'stage': 'heartbeat', 'pct': -1, 'message': 'alive'})}\n\n"
        finally:
            self.unsubscribe(job_id, q)


# Global singleton
sse_manager = SSEManager()


# ---------------------------------------------------------------------------
# Cross-thread publishing
# ---------------------------------------------------------------------------
# Subscriber queues are asyncio.Queues owned by the FastAPI event loop, but
# publishes originate in pipeline worker threads. Driving them from a fresh
# asyncio.run() loop puts items on a queue whose waiters live on a different
# loop, so the SSE consumer may never wake. Hand the coroutine to the loop
# that owns the queues instead.
_main_loop: asyncio.AbstractEventLoop | None = None


def bind_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Called once at startup with the loop serving the app."""
    global _main_loop
    _main_loop = loop


def publish_threadsafe(
    job_id: str,
    stage: str,
    message: str = "",
    extra: dict | None = None,
) -> None:
    """Publish from any thread. Never raises — SSE must not break a pipeline."""
    loop = _main_loop
    if loop is None or not loop.is_running():
        return
    try:
        asyncio.run_coroutine_threadsafe(
            sse_manager.publish(job_id, stage, message, extra), loop
        )
    except Exception:
        pass
