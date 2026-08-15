"""
VaaniSetu — Model Replica Pools

A pool holds N copies of a model. Workers check one out, use it, and return
it, so N jobs can run that stage at once instead of queueing on a single
instance. With N=1 a pool behaves exactly like the lock it replaces — which
is what a small field laptop gets, automatically.

Replica count is sized from free RAM at startup (backend/utils/resources.py
does the same job for thread counts). Replica 0 is always the instance the
registry already loaded; extras are loaded on top, and only if they fit.

Whisper has no pool on purpose: ~5 GB a copy, and it runs once per job rather
than once per language, so duplicating it buys little for a lot of memory.
"""

import logging
import queue
import threading
from contextlib import contextmanager

from backend.config import MODEL_POOL_MAX, MODEL_REPLICA_COST_GB

logger = logging.getLogger("vaanisetu.pool")


class ModelPool:
    """Fixed set of interchangeable model instances, checked out by threads."""

    def __init__(self, name: str, primary, factory=None, size: int = 1):
        """
        name:    label for logs and /api/health
        primary: the already-loaded instance (never re-created)
        factory: callable returning a fresh replica, or None for no extras
        size:    total instances wanted, including the primary
        """
        self.name = name
        self._slots: queue.Queue = queue.Queue()
        self._size = 0

        if primary is not None:
            self._slots.put(primary)
            self._size = 1

        if factory is not None:
            for i in range(1, max(1, size)):
                try:
                    replica = factory()
                except Exception as e:
                    logger.warning(
                        f"[{name}] replica {i} failed to load, "
                        f"continuing with {self._size}: {e}"
                    )
                    break
                if replica is None:
                    break
                self._slots.put(replica)
                self._size += 1

        logger.info(f"[{name}] pool ready with {self._size} instance(s)")

    @property
    def size(self) -> int:
        return self._size

    @contextmanager
    def acquire(self):
        """
        Block until an instance is free, then yield it.

        Always returns the instance, even if the caller raises — a leaked slot
        would shrink the pool permanently and eventually deadlock the stage.
        """
        if self._size == 0:
            raise RuntimeError(f"{self.name} pool is empty — model not loaded")
        item = self._slots.get()
        try:
            yield item
        finally:
            self._slots.put(item)


# ---------------------------------------------------------------------------
# Sizing
# ---------------------------------------------------------------------------
def plan_replicas(kind: str, consumers: int | None = None) -> int:
    """
    How many copies of `kind` to load, including the primary.

    Three bounds, all read from the machine rather than fixed in code:

      1. RAM      — what actually fits after the OS reserve
      2. cores    — physical cores; a replica with no core to run on is
                    memory spent for nothing
      3. consumers— how many callers can even ask at once. Translation runs
                    once per job, so job concurrency bounds it; TTS runs once
                    per language being generated, so generate concurrency does.

    The smallest wins. Stricter than the thread planner on purpose: an
    over-committed thread merely waits, but an over-committed model copy
    pushes the machine into swap — slower than no parallelism at all.

    Call order matters. Pools are built one at a time and each reads free RAM
    *after* the previous one has loaded, so budgets never double-count.
    """
    from backend.utils.resources import available_ram_gb, physical_cores
    from backend.config import CONCURRENCY_HEADROOM_GB

    cost = MODEL_REPLICA_COST_GB[kind]
    cap = MODEL_POOL_MAX.get(kind)

    # Keep the OS headroom, and a second reserve so ffmpeg and job buffers
    # still have somewhere to live once the replicas are resident.
    free = available_ram_gb()
    spare = free - (CONCURRENCY_HEADROOM_GB * 2)
    by_ram = 1 + (int(spare // cost) if spare > 0 else 0)

    limit = physical_cores()
    if consumers is not None:
        limit = min(limit, max(1, consumers))

    n = max(1, min(by_ram, limit))
    if cap is not None:
        n = max(1, min(n, cap))

    logger.info(
        f"Replica plan [{kind}]: {n} "
        f"(free={free:.1f}GB, cost={cost}GB/copy, by_ram={by_ram}, "
        f"cores={physical_cores()}, consumers={consumers}"
        + (f", cap={cap}" if cap is not None else "")
        + f") ≈ {n * cost:.1f}GB"
    )
    return n


# ---------------------------------------------------------------------------
# Global pools — built by init_pools() at startup
# ---------------------------------------------------------------------------
_pools: dict[str, ModelPool] = {}
_init_lock = threading.Lock()


def get_pool(name: str) -> ModelPool | None:
    return _pools.get(name)


def init_pools() -> None:
    """Build the pools. Safe to call once models are loaded."""
    from backend.models.registry import registry
    from backend.utils.resources import plan

    with _init_lock:
        _pools.clear()

        # TTS first: it is the slowest per-language stage and the one most
        # worth parallelizing, so it gets first claim on spare RAM. Building
        # translation first would let it eat the budget and starve this.
        if registry.tts_model is not None:
            _pools["tts"] = ModelPool(
                "tts",
                primary=registry.tts_model,
                factory=registry.make_tts_replica,
                size=plan_replicas("tts", consumers=plan("generate")),
            )

        # en→indic translation: the direction every English-source job uses.
        # Only one translation runs per job, so job concurrency bounds it.
        if registry.en_indic_model is not None:
            _pools["translate_en_indic"] = ModelPool(
                "translate_en_indic",
                primary=(registry.en_indic_tokenizer, registry.en_indic_model),
                factory=registry.make_en_indic_replica,
                size=plan_replicas("translate", consumers=plan("job")),
            )


def snapshot() -> dict:
    """Pool sizes, for /api/health."""
    return {name: p.size for name, p in _pools.items()}
