"""
VaaniSetu — Impact Ledger Service
Aggregates job metrics into hours saved, ₹ cost saved, farmers reachable.
"""

import logging
from datetime import datetime

from backend.database import get_db

logger = logging.getLogger("vaanisetu.impact")


def get_impact_summary() -> dict:
    with get_db() as conn:
        # Completed jobs with duration
        jobs = conn.execute(
            """
            SELECT id, target_langs, started_at, completed_at
            FROM jobs
            WHERE status = 'completed'
              AND started_at IS NOT NULL
              AND completed_at IS NOT NULL
            """
        ).fetchall()

        config = {
            row["language"]: dict(row)
            for row in conn.execute("SELECT * FROM impact_config").fetchall()
        }

    import json as _json

    total_minutes = 0.0
    total_cost = 0.0
    total_farmers = 0.0
    lang_stats: dict[str, dict] = {}

    for job in jobs:
        try:
            start = datetime.fromisoformat(job["started_at"])
            end   = datetime.fromisoformat(job["completed_at"])
            duration_min = max((end - start).total_seconds() / 60, 0)
        except Exception:
            duration_min = 0.0

        target_langs = _json.loads(job["target_langs"] or "[]")
        for lang in target_langs:
            cfg = config.get(lang, {})
            fph  = cfg.get("farmers_per_hour", 120)
            rate = cfg.get("translation_rate_per_min", 850)

            cost    = duration_min * rate
            farmers = (duration_min / 60) * fph

            total_minutes += duration_min
            total_cost    += cost
            total_farmers += farmers

            if lang not in lang_stats:
                lang_stats[lang] = {
                    "language": lang,
                    "job_count": 0,
                    "total_minutes": 0.0,
                    "cost_saved": 0.0,
                    "farmers_reachable": 0.0,
                }
            lang_stats[lang]["job_count"]        += 1
            lang_stats[lang]["total_minutes"]    += duration_min
            lang_stats[lang]["cost_saved"]       += cost
            lang_stats[lang]["farmers_reachable"] += farmers

    return {
        "total_hours":            round(total_minutes / 60, 2),
        "total_cost_saved":       round(total_cost, 2),
        "total_farmers_reachable": round(total_farmers, 0),
        "job_count":               len(jobs),
        "language_breakdown":      list(lang_stats.values()),
    }


def update_impact_config(language: str, farmers_per_hour: int, rate_per_min: int) -> None:
    now = datetime.utcnow().isoformat()
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
