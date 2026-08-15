"""
VaaniSetu — Concurrency Tests

Covers the RAM-aware parallelism added in backend/utils/resources.py,
backend/models/pool.py and backend/pipeline/job_queue.py.

Run with:  python tests_concurrency.py

Model work is stubbed with timed sleeps — these tests check the orchestration
(pool widths, overlap, no leaked slots, sane sizing on machines of every size),
not real-world speed. The numbers a real job achieves depend on the models and
on ffmpeg, neither of which this file loads.
"""

import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.WARNING)

from backend.config import (
    CONCURRENCY_HEADROOM_GB, MODEL_REPLICA_COST_GB,
)
from backend.database import init_db
import backend.models.pool as pool_mod
import backend.utils.resources as res
from backend.models.pool import ModelPool, plan_replicas

PASS, FAIL = "PASS", "FAIL"
_results: list[tuple[str, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    _results.append((name, PASS if ok else FAIL))
    mark = "ok " if ok else "FAIL"
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))


# ---------------------------------------------------------------------------
# 1. Generation pool overlaps translation
# ---------------------------------------------------------------------------
TARGETS = ["Hindi", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati"]
SEGMENTS = [{"text": f"sentence {i}", "start": i * 2.0, "end": i * 2.0 + 1.9}
            for i in range(4)]
TRANSLATE_S, ENCODE_S = 0.30, 0.60


def test_translate_generate_overlap() -> None:
    print("\nGeneration overlaps translation")

    import backend.pipeline.packager as packager
    import backend.pipeline.processor as processor
    import backend.pipeline.translator as translator

    events, lock = [], threading.Lock()
    live = {"n": 0, "peak": 0}

    def fake_translate(segments, source_lang, target_lang_name, target_lang_code, job_id, *args, **kwargs):
        with lock:
            events.append((time.perf_counter(), "translate", "start"))
        time.sleep(TRANSLATE_S)
        with lock:
            events.append((time.perf_counter(), "translate", "end"))
        return [{**s, "translated": f"[{target_lang_name}] {s['text']}",
                 "confidence": 0.95, "level": "green",
                 "target_lang": target_lang_name, "from_cache": False}
                for s in segments]

    def make_writer(name, delay, is_encode=False, returns_path=True):
        def writer(*args, **kwargs):
            lang = next((a for a in args if isinstance(a, str) and a in TARGETS), "?")
            if is_encode:
                with lock:
                    live["n"] += 1
                    live["peak"] = max(live["peak"], live["n"])
                    events.append((time.perf_counter(), "encode", "start"))
            time.sleep(delay)
            if is_encode:
                with lock:
                    live["n"] -= 1
            if not returns_path:
                return []
            return str((kwargs.get("out_dir") or args[-1]) / f"{name}_{lang}.bin")
        return writer

    translator.translate_segments = fake_translate
    for fn in ("write_txt", "write_bilingual_docx", "write_srt", "write_vtt",
               "write_tts_mp3", "write_ivr_wav", "write_dubbed_mp4", "write_translated_csv"):
        setattr(packager, fn, make_writer(fn, 0.01))
    packager.write_captioned_mp4 = make_writer("burn", ENCODE_S, is_encode=True)
    packager.write_whatsapp_chunks = make_writer("wa", 0.01, returns_path=False)

    t0 = time.perf_counter()
    tmap, files = processor._stage_translate_and_generate(
        job_id="test-overlap",
        segments=SEGMENTS,
        source_lang="English",
        target_langs=TARGETS,
        whisper_detected_lang_code="en",
        upload_path="/fake/input.mp4",
        resource_saver=False,
    )
    elapsed = time.perf_counter() - t0

    serial = len(TARGETS) * (TRANSLATE_S + ENCODE_S)
    last_tr = max(t for t, k, p in events if k == "translate" and p == "end")
    first_enc = min(t for t, k, p in events if k == "encode" and p == "start")

    record("all languages translated", sorted(tmap) == sorted(TARGETS),
           f"{len(tmap)}/{len(TARGETS)}")
    record("outputs produced", len(files) > 0, f"{len(files)} files")
    record("encodes ran concurrently", live["peak"] >= 2,
           f"peak {live['peak']}")
    record("generation overlapped translation", first_enc < last_tr,
           f"by {last_tr - first_enc:.2f}s")
    record("faster than serial", elapsed < serial * 0.85,
           f"{elapsed:.2f}s vs {serial:.2f}s")


def test_resource_saver_is_serial() -> None:
    print("\nResource Saver forces serial")
    record("job width is 1", res.plan("job", resource_saver=True) == 1)
    record("generate width is 1", res.plan("generate", resource_saver=True) == 1)


# ---------------------------------------------------------------------------
# 2. Model replica pool
# ---------------------------------------------------------------------------
class _FakeModel:
    def __init__(self, i):
        self.i = i


def test_model_pool() -> None:
    print("\nModel replica pool")

    for size in (3, 1):
        lock = threading.Lock()
        live = {"n": 0, "peak": 0}
        seen = set()
        counter = {"n": 0}

        def factory():
            counter["n"] += 1
            return _FakeModel(counter["n"])

        pool = ModelPool("fake", primary=_FakeModel(0), factory=factory, size=size)

        def task(_):
            with pool.acquire() as m:
                with lock:
                    live["n"] += 1
                    live["peak"] = max(live["peak"], live["n"])
                    seen.add(m.i)
                time.sleep(0.15)
                with lock:
                    live["n"] -= 1

        n_tasks = size * 3
        with ThreadPoolExecutor(max_workers=n_tasks) as ex:
            list(ex.map(task, range(n_tasks)))

        record(f"pool of {size}: concurrency matches size",
               live["peak"] == pool.size, f"peak {live['peak']}")
        record(f"pool of {size}: never over-subscribed",
               live["peak"] <= pool.size)
        record(f"pool of {size}: all instances returned",
               pool._slots.qsize() == pool.size,
               f"{pool._slots.qsize()}/{pool.size}")
        record(f"pool of {size}: every replica used",
               len(seen) == pool.size, f"{len(seen)} distinct")

    # No factory — the small-machine path
    pool = ModelPool("single", primary=_FakeModel(0), factory=None, size=1)
    lock = threading.Lock()
    live = {"n": 0, "peak": 0}

    def task(_):
        with pool.acquire():
            with lock:
                live["n"] += 1
                live["peak"] = max(live["peak"], live["n"])
            time.sleep(0.05)
            with lock:
                live["n"] -= 1

    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(task, range(4)))
    record("no replicas available: stays serial", live["peak"] == 1)


# ---------------------------------------------------------------------------
# 3. Job queue drains through a RAM-sized pool
# ---------------------------------------------------------------------------
def test_job_queue() -> None:
    print("\nJob queue pool")

    import backend.pipeline.processor as processor
    import backend.pipeline.job_queue as q

    lock = threading.Lock()
    live = {"n": 0, "peak": 0}
    done = []
    JOB_S, N_JOBS = 0.4, 7

    def fake_pipeline(job_id):
        with lock:
            live["n"] += 1
            live["peak"] = max(live["peak"], live["n"])
        time.sleep(JOB_S)
        with lock:
            live["n"] -= 1
            done.append(job_id)

    processor.run_pipeline = fake_pipeline

    async def drive():
        await q.start_workers()
        width = q.get_concurrency()
        t0 = time.perf_counter()
        for i in range(N_JOBS):
            await q.enqueue(f"job-{i}")
        while q.get_queue_depth() > 0 or q.get_current_jobs():
            await asyncio.sleep(0.05)
        await asyncio.sleep(0.1)
        return width, time.perf_counter() - t0

    width, elapsed = asyncio.run(drive())

    record("pool width came from RAM", width >= 1, f"width {width}")
    record("ran at full width", live["peak"] == width, f"peak {live['peak']}")
    record("never exceeded width", live["peak"] <= width)
    record("all jobs completed", len(done) == N_JOBS, f"{len(done)}/{N_JOBS}")
    if width > 1:
        record("faster than serial", elapsed < N_JOBS * JOB_S * 0.85,
               f"{elapsed:.2f}s vs {N_JOBS * JOB_S:.2f}s")


# ---------------------------------------------------------------------------
# 4. Sizing behaves on machines of every size
# ---------------------------------------------------------------------------
BASE_MODELS_GB = 10.2   # Whisper large + en-indic + XTTS + runtime

MACHINES = [
    # name,               free GB, physical cores
    ("4 GB netbook",          2.6, 2),
    ("8 GB field laptop",     5.5, 4),
    ("16 GB laptop",         11.0, 4),
    ("32 GB laptop",         18.3, 4),
    ("64 GB workstation",    48.0, 8),
    ("128 GB server",       110.0, 32),
]


def test_scales_across_machines() -> None:
    print("\nSizing across machine sizes")

    real_ram, real_phys, real_cpu = (
        res.available_ram_gb, res.physical_cores, res.cpu_budget
    )
    try:
        for name, free, cores in MACHINES:
            res.available_ram_gb = lambda f=free: f
            res.physical_cores = lambda c=cores: c
            res.cpu_budget = lambda c=cores: max(1, c * 2 - 1)

            jobs = res.plan("job")
            gen_solo = res.plan("generate", share=1)
            gen_busy = res.plan("generate", share=jobs)

            remaining = free - BASE_MODELS_GB
            replicas, replica_gb = {}, 0.0
            for kind, consumers in (("tts", gen_solo), ("translate", jobs)):
                res.available_ram_gb = lambda r=remaining: r
                n = plan_replicas(kind, consumers=consumers)
                replicas[kind] = n
                extra = (n - 1) * MODEL_REPLICA_COST_GB[kind]
                replica_gb += extra
                remaining -= extra
            res.available_ram_gb = lambda f=free: f

            widths = [jobs, gen_solo, gen_busy, *replicas.values()]
            threads = jobs * gen_busy
            total = BASE_MODELS_GB + replica_gb

            record(f"{name}: no zero widths", min(widths) >= 1,
                   f"jobs={jobs} gen={gen_solo}/{gen_busy} "
                   f"tts={replicas['tts']} tr={replicas['translate']}")
            record(f"{name}: threads stay near core count",
                   threads <= cores * 4, f"{threads} threads on {cores} cores")
            if free >= BASE_MODELS_GB:
                record(f"{name}: replicas fit in RAM", total <= free,
                       f"{total:.1f}GB of {free:.1f}GB")
            else:
                fits, msg = res.preflight()
                record(f"{name}: preflight warns", not fits,
                       "reports low RAM")
    finally:
        res.available_ram_gb, res.physical_cores, res.cpu_budget = (
            real_ram, real_phys, real_cpu
        )


def test_preflight_on_this_machine() -> None:
    print("\nPreflight on this machine")
    fits, msg = res.preflight()
    print(f"       {msg}")
    record("preflight returns a verdict", isinstance(fits, bool))


# ---------------------------------------------------------------------------
def main() -> int:
    init_db()

    test_translate_generate_overlap()
    test_resource_saver_is_serial()
    test_model_pool()
    test_job_queue()
    test_scales_across_machines()
    test_preflight_on_this_machine()

    failed = [n for n, r in _results if r == FAIL]
    print(f"\n{len(_results) - len(failed)}/{len(_results)} checks passed")
    if failed:
        print("Failed:")
        for n in failed:
            print("  -", n)
    print("RESULT:", PASS if not failed else FAIL)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
