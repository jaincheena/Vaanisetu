"""
VaaniSetu — RAM-Aware Concurrency Planner

Decides how many units of work may run at once, so a 4 GB field laptop
degrades to serial processing while a 32 GB desk machine uses its headroom.

Sizing is deliberately conservative: we subtract a fixed OS headroom first,
then divide what's left by a measured per-task cost, then clamp to the CPU
budget and a hard ceiling. Anything that would return 0 returns 1 — the
pipeline must always make forward progress, however slowly.
"""

import logging
import os

import psutil

from backend.config import (
    CONCURRENCY_HEADROOM_GB,
    CONCURRENCY_MAX,
    CONCURRENCY_TASK_COST_GB,
)

logger = logging.getLogger("vaanisetu.resources")


def available_ram_gb() -> float:
    """Free RAM the OS can hand out right now, in GB."""
    return psutil.virtual_memory().available / 1e9


def cpu_budget() -> int:
    """Leave one core for the event loop and the UI."""
    return max(1, (os.cpu_count() or 2) - 1)


def physical_cores() -> int:
    """
    Real cores, not hyperthreads.

    The right bound for model inference: two threads sharing one physical
    core contend for the same arithmetic units, so a second replica there
    costs full memory for a fraction of the throughput.
    """
    try:
        n = psutil.cpu_count(logical=False)
    except Exception:
        n = None
    return max(1, n or (os.cpu_count() or 2))


def preflight() -> tuple[bool, str]:
    """
    Will the models this deployment loads actually fit in RAM?

    Called before loading, so a 4 GB machine gets a clear message instead of
    ten minutes of swapping followed by an opaque MemoryError. Returns
    (fits, human-readable message).
    """
    from backend.config import (
        EAGER_LOAD_REVERSE_BRIDGE, MODEL_FOOTPRINT_GB, RUNTIME_OVERHEAD_GB,
    )

    needed = RUNTIME_OVERHEAD_GB
    needed += MODEL_FOOTPRINT_GB["whisper"]
    needed += MODEL_FOOTPRINT_GB["en_indic"]
    needed += MODEL_FOOTPRINT_GB["tts"]
    if EAGER_LOAD_REVERSE_BRIDGE:
        needed += MODEL_FOOTPRINT_GB["indic_en"]

    free = available_ram_gb()
    fits = free >= needed + CONCURRENCY_HEADROOM_GB

    if fits:
        return True, (
            f"RAM check OK — need ~{needed:.1f}GB, {free:.1f}GB free"
        )

    short = (needed + CONCURRENCY_HEADROOM_GB) - free
    return False, (
        f"LOW RAM — models need ~{needed:.1f}GB plus {CONCURRENCY_HEADROOM_GB:.1f}GB "
        f"headroom, but only {free:.1f}GB is free (short by ~{short:.1f}GB). "
        f"Everything will run serially and may swap. To fit this machine, set "
        f"WHISPER_MODEL=small (saves ~4GB) or close other applications."
    )


def plan(kind: str, resource_saver: bool = False, share: int = 1) -> int:
    """
    How many `kind` tasks may run concurrently right now.

    kind:
        "job"      — whole pipelines running side by side
        "generate" — per-language output sets within one job

    share: how many callers will each run their own pool of this size. Pass
    the job concurrency when planning "generate", so N jobs × M languages
    cannot multiply into thousands of threads on a large server. Without it
    each planner is sane alone but the product is not.

    Resource Saver Mode always collapses to 1, matching the promise the
    Upload page makes to the user ("won't freeze while doing background work").
    """
    if resource_saver:
        return 1

    cost = CONCURRENCY_TASK_COST_GB.get(kind)
    if cost is None:
        raise ValueError(f"Unknown concurrency kind: {kind}")

    free = available_ram_gb()
    usable = free - CONCURRENCY_HEADROOM_GB
    by_ram = int(usable // cost) if usable > 0 else 0

    # Both bounds are read from the machine, not fixed in code: how much RAM
    # is free right now, and how many cores there are to run on. Threads past
    # the core count only thrash, so the smaller of the two wins.
    # Core budget depends on what the work actually does. Generation is mostly
    # ffmpeg subprocesses that spend much of their life blocked on disk, so
    # running more of them than there are cores genuinely helps. A job holds
    # model locks and does real compute, so it is bounded by real cores.
    budget = physical_cores() * 2 if kind == "generate" else physical_cores()

    share = max(1, share)
    if share > 1:
        # Split the machine between the concurrent callers rather than giving
        # each the whole thing.
        by_ram = by_ram // share
        budget = budget // share

    n = max(1, min(by_ram, budget))

    cap = CONCURRENCY_MAX.get(kind)
    if cap is not None:
        n = max(1, min(n, cap))

    logger.info(
        f"Concurrency plan [{kind}]: {n} "
        f"(free={free:.1f}GB, by_ram={by_ram}, cpu={budget}"
        + (f", share={share}" if share > 1 else "")
        + (f", cap={cap}" if cap is not None else "") + ")"
    )
    return n


def snapshot() -> dict:
    """Current sizing, for /api/health."""
    return {
        "ram_free_gb":      round(available_ram_gb(), 1),
        "cpu_budget":       cpu_budget(),
        "job_concurrency":  plan("job"),
        "generate_concurrency": plan("generate"),
    }
