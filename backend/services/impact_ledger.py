"""
VaaniSetu — Impact Ledger Service

Aggregates completed jobs into hours localized, ₹ saved against agency rates,
and the reach those advisories make possible.

Two things this module is careful about, because the numbers end up in a PDF
that goes to donors and auditors:

  * Hours come from the length of the advisory (jobs.media_duration_s), not
    from completed_at - started_at. Wall-clock is how long the laptop took to
    think; billing an agency rate against it means a slower machine reports
    larger savings, which is backwards.

  * Content hours are counted once per job. Cost and reach are counted per
    target language, because translating one advisory into five languages
    genuinely is five deliverables — but it is still only one hour of source
    material, and reporting five would inflate the headline by the language
    count alone.

Reach is a capacity figure — how many farmers these advisories *can* serve at
the configured farmers-per-hour rate. VaaniSetu produces files; it does not
deliver them, and it has no way to know who listened. The field is named
`farmers_reachable` throughout for that reason, and the UI must not relabel it
as farmers reached.
"""

import logging
from datetime import datetime, timezone

from backend.database import get_db

logger = logging.getLogger("vaanisetu.impact")


def get_impact_summary() -> dict:
    with get_db() as conn:
        jobs = conn.execute(
            """
            SELECT id, target_langs, media_duration_s
            FROM jobs
            WHERE status = 'completed'
              AND media_duration_s IS NOT NULL
              AND media_duration_s > 0
            """
        ).fetchall()

        config = {
            row["language"]: dict(row)
            for row in conn.execute("SELECT * FROM impact_config").fetchall()
        }

        # Jobs finished before media_duration_s existed cannot be costed
        # honestly, so they are reported separately rather than guessed at.
        unmeasured = conn.execute(
            """
            SELECT COUNT(*) AS c FROM jobs
            WHERE status = 'completed'
              AND (media_duration_s IS NULL OR media_duration_s <= 0)
            """
        ).fetchone()["c"]

    import json as _json

    total_minutes = 0.0
    total_cost = 0.0
    total_farmers = 0.0
    lang_stats: dict[str, dict] = {}

    for job in jobs:
        duration_min = max(float(job["media_duration_s"] or 0.0) / 60.0, 0.0)

        try:
            target_langs = _json.loads(job["target_langs"] or "[]")
        except Exception:
            target_langs = []

        # Source material, counted once however many languages it went into.
        total_minutes += duration_min

        for lang in target_langs:
            cfg = config.get(lang, {})
            fph = cfg.get("farmers_per_hour", 120)
            rate = cfg.get("translation_rate_per_min", 850)

            cost = duration_min * rate
            farmers = (duration_min / 60) * fph

            total_cost += cost
            total_farmers += farmers

            if lang not in lang_stats:
                lang_stats[lang] = {
                    "language": lang,
                    "job_count": 0,
                    "total_minutes": 0.0,
                    "cost_saved": 0.0,
                    "farmers_reachable": 0.0,
                }
            lang_stats[lang]["job_count"] += 1
            lang_stats[lang]["total_minutes"] += duration_min
            lang_stats[lang]["cost_saved"] += cost
            lang_stats[lang]["farmers_reachable"] += farmers

    for row in lang_stats.values():
        row["total_minutes"] = round(row["total_minutes"], 2)
        row["cost_saved"] = round(row["cost_saved"], 2)
        # Whole people only — a bar reading "7.6 farmers" reads as a bug, and
        # in an audit report it reads as carelessness.
        row["farmers_reachable"] = int(round(row["farmers_reachable"]))

    return {
        "total_hours":             round(total_minutes / 60, 2),
        "total_cost_saved":        round(total_cost, 2),
        "total_farmers_reachable": int(round(total_farmers)),
        "job_count":               len(jobs),
        "unmeasured_job_count":    unmeasured,
        "language_breakdown":      sorted(
            lang_stats.values(), key=lambda r: r["farmers_reachable"], reverse=True
        ),
    }


def update_impact_config(language: str, farmers_per_hour: int, rate_per_min: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO impact_config (language, farmers_per_hour, translation_rate_per_min, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(language) DO UPDATE SET
                farmers_per_hour = excluded.farmers_per_hour,
                translation_rate_per_min = excluded.translation_rate_per_min,
                updated_at = excluded.updated_at
            """,
            (language, farmers_per_hour, rate_per_min, now),
        )


def get_impact_config() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM impact_config ORDER BY language"
        ).fetchall()
    return [dict(r) for r in rows]
