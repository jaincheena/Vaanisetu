"""
VaaniSetu — Translation Memory Service
SQLite-backed cache keyed by SHA-256("src_lang|tgt_lang|" + text.strip().lower())
"""

import math
import logging
from datetime import datetime
from typing import Optional

from backend.database import get_db
from backend.utils.file_utils import tm_cache_key
from backend.config import TM_CACHE_HIT_MIN, TM_STORE_MIN, GLOSSARY_MIN_USES, GLOSSARY_MIN_CONF

logger = logging.getLogger("vaanisetu.tm")


def lookup(src_lang: str, tgt_lang: str, text: str) -> Optional[str]:
    """
    Check TM cache. Returns translated text if hit, else None.
    Hit criteria: confidence ≥ TM_CACHE_HIT_MIN and not flagged.
    Also increments times_used on hit.
    """
    key = tm_cache_key(src_lang, tgt_lang, text)
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT id, translated_text, confidence, flagged
            FROM translation_memory
            WHERE source_hash = ?
            """,
            (key,),
        ).fetchone()

        if not row:
            return None
        if row["flagged"] or row["confidence"] < TM_CACHE_HIT_MIN:
            return None

        # Update usage stats
        now = datetime.utcnow().isoformat()
        conn.execute(
            "UPDATE translation_memory SET times_used = times_used + 1, last_used_at = ? WHERE id = ?",
            (now, row["id"]),
        )
        logger.debug(f"TM hit for {src_lang}→{tgt_lang}: '{text[:40]}…'")
        return row["translated_text"]


def store(
    src_lang: str,
    tgt_lang: str,
    source_text: str,
    translated_text: str,
    confidence: Optional[float] = None,
    domain: str = "agriculture",
) -> None:
    """Store a translation in TM if confidence ≥ TM_STORE_MIN."""
    
    # 1. Force confidence to a valid float immediately (handling None, NaN, Inf, or invalid types)
    import math
    if confidence is None or not isinstance(confidence, (int, float)) or math.isnan(confidence) or math.isinf(confidence):
        confidence = 0.85
    else:
        confidence = max(0.0, min(1.0, float(confidence)))

    # 2. Now safe to compare
    if confidence < TM_STORE_MIN:
        return

    key = tm_cache_key(src_lang, tgt_lang, source_text)
    now = datetime.utcnow().isoformat()

    with get_db() as conn:
        existing = conn.execute(
            "SELECT id, confidence, times_used FROM translation_memory WHERE source_hash = ?",
            (key,),
        ).fetchone()

        if existing:
            # Update if new confidence is higher
            if confidence > existing["confidence"]:
                conn.execute(
                    """
                    UPDATE translation_memory
                    SET translated_text=?, confidence=?, last_used_at=?
                    WHERE id=?
                    """,
                    (translated_text, confidence, now, existing["id"]),
                )
        else:
            conn.execute(
                """
                INSERT INTO translation_memory
                (source_hash, source_text, source_lang, target_lang, translated_text,
                 confidence, times_used, created_at, last_used_at, flagged, domain)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, 0, ?)
                """,
                (key, source_text, src_lang, tgt_lang, translated_text,
                 confidence, now, now, domain),
            )

def store_approved(
    src_lang: str,
    tgt_lang: str,
    source_text: str,
    translated_text: str,
) -> None:
    """Store human-approved translation with high confidence=0.99 (>98%)."""
    store(src_lang, tgt_lang, source_text, translated_text, 0.99)


def get_glossary(limit: int = 500) -> list[dict]:
    """
    Return terms used ≥ GLOSSARY_MIN_USES with confidence ≥ GLOSSARY_MIN_CONF.
    Groups by source_text + source_lang, collecting all target languages.
    """
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, source_text, source_lang, target_lang, translated_text,
                   times_used, confidence
            FROM translation_memory
            WHERE times_used >= ? AND confidence >= ? AND flagged = 0
            ORDER BY times_used DESC, source_text
            LIMIT ?
            """,
            (GLOSSARY_MIN_USES, GLOSSARY_MIN_CONF, limit),
        ).fetchall()

    # Group by (source_text, source_lang)
    glossary: dict[tuple, dict] = {}
    for r in rows:
        key = (r["source_text"], r["source_lang"])
        if key not in glossary:
            glossary[key] = {
                "id": r["id"],
                "source_text": r["source_text"],
                "source_lang": r["source_lang"],
                "times_used":  r["times_used"],
                "confidence":  r["confidence"],
                "translations": {},
            }
        from backend.config import LANG_NAMES_BY_CODE
        lang_name = LANG_NAMES_BY_CODE.get(r["target_lang"], r["target_lang"])
        glossary[key]["translations"][lang_name] = r["translated_text"]

    return list(glossary.values())