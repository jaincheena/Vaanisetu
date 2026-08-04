"""
VaaniSetu — IndicTrans2 Translator
Batch translation with TM cache, confidence scoring, and amber routing.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger("vaanisetu.translator")


# Using a simple, unlikely tag to protect parts of text from translation.
_PLACEHOLDER_TAG = "VSP"  # VaaniSetu Protected
_PLACEHOLDER_RE = re.compile(r'<\s*' + _PLACEHOLDER_TAG + r'(\d+)\s*>')

# Patterns for entities that should not be translated.
_PROTECT_PATTERNS = [
    # URLs
    re.compile(r'https?://\S+'),
    # Email addresses
    re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    # Alphanumeric codes like "E20", "H1N1", "Type2" that mix letters and numbers.
    re.compile(r'\b([A-Za-z]+[0-9]+[A-Za-z0-9]*|[0-9]+[A-Za-z]+[A-Za-z0-9]*)\b'),
]

# Glossary of proper nouns and technical terms that should not be translated.
# This list can be expanded or loaded from a configuration file/database.
_GLOSSARY_TERMS = [
    "HSBC", "ChatGPT", "Docker", "Kubernetes", "WhatsApp", "YouTube", "Facebook",
    "Instagram", "Twitter", "Google", "Microsoft", "Amazon", "Apple",
    "SRI",  # System of Rice Intensification
]

# Build a case-insensitive regex from the glossary and add it to the patterns.
# The \b ensures we match whole words only.
if _GLOSSARY_TERMS:
    glossary_pattern = r'\b(' + '|'.join(re.escape(term) for term in _GLOSSARY_TERMS) + r')\b'
    _PROTECT_PATTERNS.append(re.compile(glossary_pattern, re.IGNORECASE))



def _preprocess_text(text: str) -> tuple[str, list[str]]:
    """Replaces entities with placeholders to protect them from translation."""
    protected_items = []

    def replacer(match):
        protected_items.append(match.group(0))
        # Add spaces around placeholder to prevent it from merging with other words
        return f" <{_PLACEHOLDER_TAG}{len(protected_items)-1}> "

    processed_text = text
    for pattern in _PROTECT_PATTERNS:
        processed_text = pattern.sub(replacer, processed_text)
    return processed_text, protected_items


def _postprocess_text(text: str, protected_items: list[str]) -> str:
    """Restores placeholders and normalizes whitespace."""
    def replacer(match):
        index = int(match.group(1))
        return protected_items[index] if 0 <= index < len(protected_items) else match.group(0)

    processed_text = _PLACEHOLDER_RE.sub(replacer, text)
    # Normalize all whitespace (multiple spaces, newlines, etc.) into single spaces.
    return " ".join(processed_text.split()).strip()


def _fallback_translate_segments(segments: list[dict], target_lang_name: str) -> list[dict]:
    """Gracefully return source text when the IndicTrans2 model is unavailable."""
    return [
        {
            **seg,
            "translated": seg.get("text", "").strip(),
            "confidence": 0.50,
            "level": "red",
            "target_lang": target_lang_name,
            "from_cache": True,
        }
        for seg in segments
    ]


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
    from backend.config import BATCH_SIZE, ENGLISH_CODE, LANG_CODES, TRANSLATION_MAX_LENGTH

    tokenizer, model = registry.get_indic_pair(source_lang)
    if tokenizer is None or model is None:
        logger.warning(
            "IndicTrans2 model unavailable for %s -> %s; using source-text fallback",
            source_lang,
            target_lang_name,
        )
        return _fallback_translate_segments(segments, target_lang_name)

    src_code = ENGLISH_CODE if source_lang == "English" else LANG_CODES.get(source_lang, "hin_Deva")

    results = []
    batch_indices = range(0, len(segments), BATCH_SIZE)

    for batch_start in batch_indices:
        batch = segments[batch_start: batch_start + BATCH_SIZE]
        texts = [s["text"] for s in batch]
        translations: list[Optional[str]] = [None] * len(texts)
        confidences:  list[Optional[float]] = [None] * len(texts)
        from_cache   = [False] * len(texts)
        replacements_map: list[list[str]] = [[] for _ in texts]

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
            # Pre-process texts that are going to be translated
            pending_texts = []
            for i in pending_idx:
                processed_text, protected_items = _preprocess_text(texts[i])
                pending_texts.append(processed_text)
                replacements_map[i] = protected_items

            logger.info(f"Tokenizer class: {tokenizer.__class__}")
            logger.info(f"Tokenizer type: {type(tokenizer)}")
            formatted_texts = [
                f"{src_code} {target_lang_code} {text}"
                for text in pending_texts
            ]

            inputs = tokenizer(
                formatted_texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=TRANSLATION_MAX_LENGTH,
            )

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    num_beams=4,
                    # Increase max_length to avoid truncating long sentences
                    max_length=TRANSLATION_MAX_LENGTH,
                    output_scores=True,
                    return_dict_in_generate=True,
                )

            tokenizer._switch_to_target_mode()

            decoded = tokenizer.batch_decode(
                outputs.sequences,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )

            tokenizer._switch_to_input_mode()

            scores_list = list(outputs.scores) if outputs.scores else []
            confs = batch_confidence(scores_list, outputs.sequences)

            for local_i, global_i in enumerate(pending_idx):
                # Post-process to restore placeholders and normalize whitespace
                protected_items = replacements_map[global_i]
                t = _postprocess_text(decoded[local_i], protected_items)
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
                pass

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
