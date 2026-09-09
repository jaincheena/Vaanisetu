"""
VaaniSetu — IndicTrans2 Translator
Batch translation with TM cache, confidence scoring, and amber routing.
"""

import math
import logging
import re
import time
from typing import Optional

logger = logging.getLogger("vaanisetu.translator")


# Using purely numeric boundaries to prevent IndicTrans2 from transliterating English letters (like VSP -> व्ही एस पी)
_PLACEHOLDER_TAG = "9999"  
_PLACEHOLDER_RE = re.compile(r'<\s*' + _PLACEHOLDER_TAG + r'\s*(\d+)[^>]*>', re.IGNORECASE)

# Patterns for entities that should not be translated.
_PROTECT_PATTERNS = [
    # URLs
    re.compile(r'https?://\S+'),
    # Email addresses
    re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    # Alphanumeric codes like "E20", "H1N1", "Type2" that mix letters and numbers.
    re.compile(r'\b([A-Za-z]+[0-9]+[A-Za-z0-9]*|[0-9]+[A-Za-z]+[A-Za-z0-9]*)\b'),
]

# AgriShield™ — Specialized BAIF Agricultural & Rural Development Entity Dictionary
# Protects mission-critical domain entities, government schemes, chemical formulas,
# crop varieties, pest names, and livestock breeds from literal translation errors.
_GLOSSARY_TERMS = [
    # Technology & General Platforms
    "WhatsApp", "YouTube", "Facebook", "Instagram", "Twitter", "Google", "Microsoft", "Android", "iOS",
    
    # Government Agricultural Schemes & Portals
    "PM-KISAN", "PMFBY", "PMKSY", "e-NAM", "KCC", "Kisan Credit Card", "Soil Health Card",
    "MGNREGA", "NABARD", "ATMA", "KVK", "ICAR", "RKVY", "NFSM", "MIDH", "APMC", "Mandi",
    "BAIF", "Bharatiya Agro Industries Foundation", "Vaani Setu", "VaaniSetu",
    
    # Agricultural Practices & Methods
    "SRI", "System of Rice Intensification", "DSR", "Direct Seeded Rice", "Zero Tillage",
    "Mulching", "Vermicompost", "Vermicomposting", "Jeevamrut", "Beejamrut", "Panchagavya",
    "Drip Irrigation", "Micro-irrigation", "Fertigation", "Integrated Pest Management", "IPM",
    "Crop Rotation", "Hydroponics", "Polyhouse", "Shade Net",
    
    # Pests, Plant Pathogens & Crop Diseases
    "Fall Armyworm", "Spodoptera frugiperda", "Yellow Rust", "Puccinia striiformis",
    "Stem Borer", "Leaf Miner", "Whitefly", "Aphids", "Thrips", "Bollworm", "Pink Bollworm",
    "Blast Disease", "Sheath Blight", "Downy Mildew", "Powdery Mildew", "Root Rot",
    "Wilt", "Anthracnose", "Dieback", "Bacterial Leaf Blight",
    
    # Livestock & Veterinary Diseases
    "Lumpy Skin Disease", "LSD", "Foot and Mouth Disease", "FMD", "Mastitis",
    "Brucellosis", "Anthrax", "Black Quarter", "BQ", "Hemorrhagic Septicemia", "HS",
    "Theileriosis", "Babesiosis", "Deworming",
    
    # Indigenous & Improved Livestock Breeds (BAIF Cattle/Goat programs)
    "Gir", "Sahiwal", "Red Sindhi", "Tharparkar", "Kankrej", "Rathi", "Ongole", "Hallikar",
    "Murrah", "Surti", "Jaffrabadi", "Nili-Ravi", "Osmanabadi", "Sirohi", "Barbari", "Jamnapari",
    "Black Bengal", "Boer", "Kadaknath",
    
    # Fertilizers, Nutrients & Bio-inoculants
    "DAP", "Di-Ammonium Phosphate", "Urea", "MOP", "Muriate of Potash", "SSP", "Single Super Phosphate",
    "NPK 19:19:19", "NPK 12:32:16", "NPK 10:26:26", "NPK 20:20:0:13", "Zinc Sulphate",
    "Ferrous Sulphate", "Borax", "Gypsum", "Trichoderma", "Trichoderma viride",
    "Pseudomonas fluorescens", "Azotobacter", "Rhizobium", "PSB", "Phosphate Solubilizing Bacteria",
    "Mycorrhiza", "VAM", "Neem Cake", "Neem Oil",
    
    # Crop Types & Agro-Ecological Seasons
    "Kharif", "Rabi", "Zaid", "BT Cotton", "Desi Cotton", "Basmati", "Hybrid Napier", "Lucerne",
    "Berseem", "Stylosanthes", "Azolla", "Silage",
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
        try:
            index = int(match.group(1))
            if 0 <= index < len(protected_items):
                return f" {protected_items[index]} "
        except Exception:
            pass
        return ""

    processed_text = _PLACEHOLDER_RE.sub(replacer, text)
    # Strip any remaining unhandled < 9999... > tags
    processed_text = re.sub(r'<\s*9999[^\s>]*>?', '', processed_text, flags=re.IGNORECASE)
    # Normalize all whitespace (multiple spaces, newlines, etc.) into single spaces.
    return " ".join(processed_text.split()).strip()


def _run_inference(tokenizer, model, pending_texts: list[str], src_code: str, target_lang_code: str, max_length: int = 256, num_beams: int = 4):
    """
    Tokenise → generate → decode on ONE model instance.
    Caller owns exclusivity: holds replica from pool or holds TRANSLATE_LOCK.
    """
    import torch
    from backend.services.confidence import batch_confidence

    all_decoded = []
    all_confs = []
    BATCH_SIZE = 1  # Force single-item batching to prevent past_key_values AttributeError and OOM

    for i in range(0, len(pending_texts), BATCH_SIZE):
        batch_texts = pending_texts[i:i+BATCH_SIZE]
        
        formatted_texts = [
            f"{src_code} {target_lang_code} {text}"
            for text in batch_texts
        ]

        inputs = tokenizer(
            formatted_texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        )

        input_tokens_len = inputs["input_ids"].shape[1] if "input_ids" in inputs else 32
        effective_max_length = min(max_length, max(48, int(input_tokens_len * 2.2)))

        bos_id = getattr(tokenizer, "lang_code_to_id", {}).get(target_lang_code)
        gen_kwargs = {
            "num_beams": num_beams,
            "max_length": effective_max_length,
            "early_stopping": True if num_beams > 1 else False,
            "output_scores": True,
            "return_dict_in_generate": True,
            "use_cache": True,
        }
        if bos_id is not None:
            gen_kwargs["forced_bos_token_id"] = bos_id

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                **gen_kwargs,
            )

        if hasattr(tokenizer, "_switch_to_target_mode"):
            tokenizer._switch_to_target_mode()

        decoded = tokenizer.batch_decode(
            outputs.sequences,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )

        if hasattr(tokenizer, "_switch_to_input_mode"):
            tokenizer._switch_to_input_mode()
            
        scores_list = list(outputs.scores) if outputs.scores else []
        confs = batch_confidence(scores_list, outputs.sequences)
        
        all_decoded.extend(decoded)
        all_confs.extend(confs)

    return all_decoded, all_confs


class TranslationUnavailableError(RuntimeError):
    """The translation model could not be loaded and no cache covers the text."""


def _fallback_translate_segments(segments: list[dict], target_lang_name: str) -> list[dict]:
    """
    Serve from translation memory when IndicTrans2 is not loaded.

    Anything the cache does not cover raises. This used to return the SOURCE
    TEXT as the translation, marked confidence 0.985 / green / cleared — so a
    Marathi farmer received an English audio file, an English video and an
    English printed handout, all stamped as verified. A job that cannot be
    translated must fail loudly; there is no safe way to ship the original
    text under a target-language label.
    """
    from backend.services.translation_memory import lookup

    res = []
    untranslatable = 0
    for seg in segments:
        text = seg.get("text", "").strip()
        cached = (
            lookup("Marathi", target_lang_name, text)
            or lookup("English", target_lang_name, text)
            or lookup("Hindi", target_lang_name, text)
        )
        if not cached:
            untranslatable += 1
            continue
        res.append({
            **seg,
            "translated": cached,
            "confidence": 0.99,
            "level": "green",
            "target_lang": target_lang_name,
            "from_cache": True,
        })

    if untranslatable:
        raise TranslationUnavailableError(
            f"Cannot translate into {target_lang_name}: the IndicTrans2 model is "
            f"not loaded and {untranslatable} of {len(segments)} segment(s) are "
            f"not in translation memory. Check the server log for the model load "
            f"error — the advisory has NOT been translated and must not be sent."
        )
    return res


def translate_segments(
    segments: list[dict],
    source_lang: str,
    target_lang_name: str,
    target_lang_code: str,
    job_id: str,
    num_beams: int = 4,
    bypass_cache: bool = False,
    progress_callback = None,
) -> list[dict]:
    """
    Translate a list of segments for ONE target language.
    Prioritizes Translation Memory (TM) cache before querying heavy neural models unless bypass_cache=True.
    """
    from backend.models.registry import registry
    from backend.models.pool import get_pool
    from backend.services.translation_memory import lookup, store
    from backend.services.confidence import batch_confidence, confidence_level, FALLBACK_CONFIDENCE
    from backend.config import BATCH_SIZE, ENGLISH_CODE, LANG_CODES, TRANSLATION_MAX_LENGTH

    # 1. Fast-path TM cache check
    all_cached = True
    cached_results = []
    if bypass_cache:
        logger.info(f"[DIAGNOSTIC] TM_BYPASSED=True (bypassing TM cache lookup for job {job_id})")
        all_cached = False
    else:
        for seg in segments:
            text = seg.get("text", "").strip()
            if not text:
                cached_results.append({**seg, "translated": "", "confidence": 1.0, "level": "green", "from_cache": True, "target_lang": target_lang_name})
                continue
            cached = lookup(source_lang, target_lang_name, text)
            if cached is not None:
                logger.info(f"[DIAGNOSTIC] TM_HIT=True | src='{text}' | cached='{cached}'")
                cached_results.append({**seg, "translated": cached, "confidence": 0.99, "level": "green", "from_cache": True, "target_lang": target_lang_name})
            else:
                logger.info(f"[DIAGNOSTIC] TM_HIT=False | src='{text}'")
                all_cached = False
                break

    if all_cached and len(cached_results) == len(segments):
        logger.info(f"100% TM hit for {len(segments)} segment(s) [{source_lang} -> {target_lang_name}]")
        return cached_results

    pool = get_pool("translate_en_indic") if source_lang == "English" else None
    if pool is None:
        tokenizer, model = registry.get_indic_pair(source_lang)
        if tokenizer is None or model is None:
            logger.info(
                "IndicTrans2 model not in RAM for %s -> %s; using TM cache & domain translation",
                source_lang,
                target_lang_name,
            )
            return _fallback_translate_segments(segments, target_lang_name)
    else:
        tokenizer, model = None, None

    src_code = ENGLISH_CODE if source_lang == "English" else LANG_CODES.get(source_lang, "hin_Deva")

    t_trans_start = time.time()
    logger.info(f"[PERF_TIMING] IndicTrans2 starting translation [{source_lang} -> {target_lang_name}] for {len(segments)} segment(s)")

    results = []
    batch_indices = range(0, len(segments), BATCH_SIZE)

    for batch_start in batch_indices:
        from backend.pipeline.processor import check_cancelled
        check_cancelled(job_id)

        from backend.utils.transliteration import normalize_indic_script
        batch = segments[batch_start: batch_start + BATCH_SIZE]
        texts = [normalize_indic_script(s.get("text", ""), source_lang) for s in batch]
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

            if pool is not None:
                with pool.acquire() as (tok, mdl):
                    decoded, confs = _run_inference(
                        tok, mdl, pending_texts, src_code, target_lang_code, TRANSLATION_MAX_LENGTH, num_beams=num_beams
                    )
            else:
                from backend.pipeline.locks import TRANSLATE_LOCK
                with TRANSLATE_LOCK:
                    decoded, confs = _run_inference(
                        tokenizer, model, pending_texts, src_code, target_lang_code, TRANSLATION_MAX_LENGTH, num_beams=num_beams
                    )

            for local_i, global_i in enumerate(pending_idx):
                # Post-process to restore placeholders and normalize whitespace
                raw_nmt_output = decoded[local_i]
                final_text = _postprocess_text(raw_nmt_output, replacements_map[global_i])
                logger.info(f"[DIAGNOSTIC] INDICTRANS_INPUT: '{pending_texts[local_i]}' | SRC_CODE: '{src_code}' | TGT_CODE: '{target_lang_code}'")
                logger.info(f"[DIAGNOSTIC] INDICTRANS_OUTPUT: '{raw_nmt_output}' | POSTPROCESSED_TTS_INPUT: '{final_text}'")
                
                c = confs[local_i] if local_i < len(confs) else 0.85
                if c is None or not isinstance(c, (int, float)) or math.isnan(c) or math.isinf(c):
                    c = 0.85
                else:
                    c = max(0.0, min(1.0, float(c)))
                translations[global_i] = final_text
                confidences[global_i]  = c

                # Store to TM unless bypass_cache is requested
                if not bypass_cache:
                    store(source_lang, target_lang_name, texts[global_i], final_text, c)

        # ---------------------------------------------------------------
        # Build results + route amber to review queue
        # ---------------------------------------------------------------
        for i, seg in enumerate(batch):
            trans = translations[i] or ""
            conf  = confidences[i] if confidences[i] is not None else FALLBACK_CONFIDENCE
            if not isinstance(conf, (int, float)) or math.isnan(conf) or math.isinf(conf):
                conf = FALLBACK_CONFIDENCE
            conf  = max(0.0, min(1.0, float(conf)))
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

        if progress_callback:
            batch_num = (batch_start // BATCH_SIZE) + 1
            total_batches = max(1, (len(segments) + BATCH_SIZE - 1) // BATCH_SIZE)
            try:
                progress_callback(batch_num, total_batches, target_lang_name)
            except Exception:
                pass

    logger.info(f"[PERF_TIMING] IndicTrans2 completed translation [{source_lang} -> {target_lang_name}] in {time.time() - t_trans_start:.2f}s")
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
    import math
    from datetime import datetime
    from backend.database import get_db

    if confidence is None or not isinstance(confidence, (int, float)) or math.isnan(confidence) or math.isinf(confidence):
        confidence = 0.50
    else:
        confidence = max(0.0, min(1.0, float(confidence)))

    now = datetime.utcnow().isoformat()
    try:
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
    except Exception as e:
        logger.warning(f"Could not insert segment into review queue for job {job_id}: {e}")
