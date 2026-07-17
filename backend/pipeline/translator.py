"""
VaaniSetu — IndicTrans2 Translator
Batch translation with TM cache, confidence scoring, and amber routing.
"""

import logging
import math
from typing import Optional

logger = logging.getLogger("vaanisetu.translator")


def translate_segments(
    segments: list[dict],
    source_lang: str,
    target_lang_name: str,
    target_lang_code: str,
    job_id: str,
) -> list[dict]:
    """
    Translate a list of segments for ONE target language.

    Args:
        segments: list of {text, start, end}
        source_lang: display name e.g. "English" / "Hindi"
        target_lang_name: display name e.g. "Hindi"
        target_lang_code: FLORES code e.g. "hin_Deva"
        job_id: for TM + review queue

    Returns:
        list of dicts: {text, start, end, translated, confidence, level, from_cache}
    """
    import torch
    from backend.models.registry import registry
    from backend.services.translation_memory import lookup, store
    from backend.services.confidence import batch_confidence, confidence_level
    from backend.config import (
        BATCH_SIZE, ENGLISH_CODE, LANG_CODES, CONFIDENCE_AMBER
    )

    tokenizer, model = registry.get_indic_pair(source_lang)
    if tokenizer is None or model is None:
        raise RuntimeError("IndicTrans2 model not loaded for direction")

    src_code = ENGLISH_CODE if source_lang == "English" else LANG_CODES.get(source_lang, "hin_Deva")

    results = []
    batch_indices = range(0, len(segments), BATCH_SIZE)

    for batch_start in batch_indices:
        batch = segments[batch_start: batch_start + BATCH_SIZE]
        texts = [s["text"] for s in batch]
        translations: list[Optional[str]] = [None] * len(texts)
        confidences:  list[Optional[float]] = [None] * len(texts)
        from_cache   = [False] * len(texts)

        # ---------------------------------------------------------------
        # TM cache lookup
        # ---------------------------------------------------------------
        pending_idx: list[int] = []
        for i, text in enumerate(texts):
            if not text.strip():
                # Edge Case Optimization: Skip empty Whisper segments to prevent IndicTrans2 tensor crashes
                translations[i] = ""
                confidences[i]  = 1.0
                from_cache[i]   = True
                continue
                
            cached = lookup(source_lang, target_lang_name, text)
            if cached is not None:
                translations[i] = cached
                confidences[i]  = 1.0   # from TM → treat as high confidence
                from_cache[i]   = True
            else:
                pending_idx.append(i)

        # ---------------------------------------------------------------
        # IndicTrans2 inference for uncached segments
        # ---------------------------------------------------------------
        if pending_idx:
            pending_texts = [texts[i] for i in pending_idx]
            inputs = tokenizer(
                pending_texts,
                src_lang=src_code,
                tgt_lang=target_lang_code,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256,
            )

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    num_beams=4,
                    max_length=256,
                    output_scores=True,
                    return_dict_in_generate=True,
                )

            decoded = tokenizer.batch_decode(
                outputs.sequences, skip_special_tokens=True
            )

            scores_list = list(outputs.scores) if outputs.scores else []
            confs = batch_confidence(scores_list, outputs.sequences)

            for local_i, global_i in enumerate(pending_idx):
                t = decoded[local_i].strip()
                c = confs[local_i] if local_i < len(confs) else 0.5
                translations[global_i] = t
                confidences[global_i]  = c

                # Store to TM
                store(source_lang, target_lang_name, texts[global_i], t, c)

        # ---------------------------------------------------------------
        # Build results + route amber to review queue
        # ---------------------------------------------------------------
        for i, seg in enumerate(batch):
            trans = translations[i] or ""
            conf  = confidences[i] or 0.0
            level = confidence_level(conf)

            result_seg = {
                **seg,
                "translated":  trans,
                "confidence":  conf,
                "level":       level,
                "target_lang": target_lang_name,
                "from_cache":  from_cache[i],
            }
            results.append(result_seg)

            # Route amber/red to review queue
            if level in ("amber", "red") and not from_cache[i]:
                _add_to_review_queue(
                    job_id=job_id,
                    segment_index=batch_start + i,
                    source_text=seg["text"],
                    translated_text=trans,
                    source_lang=source_lang,
                    target_lang=target_lang_name,
                    confidence=conf,
                )

    return results


def _add_to_review_queue(
    job_id: str,
    segment_index: int,
    source_text: str,
    translated_text: str,
    source_lang: str,
    target_lang: str,
    confidence: float,
) -> None:
    from datetime import datetime
    from backend.database import get_db

    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO review_queue
            (job_id, segment_index, source_text, translated_text,
             source_lang, target_lang, confidence, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (job_id, segment_index, source_text, translated_text,
             source_lang, target_lang, confidence, now),
        )
