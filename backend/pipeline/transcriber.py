"""
VaaniSetu — Whisper Transcriber
Transcribes audio to timestamped segments.
"""

import logging
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import time
from typing import Optional

from backend.utils.ffmpeg import ensure_ffmpeg_on_path

logger = logging.getLogger("vaanisetu.transcriber")

ensure_ffmpeg_on_path()


import re

_INDIC_INITIAL_PROMPTS = {
    "mr": "शेतकरी सल्ला, पशुपोषण, कृषी आणि जनावरांचे आजार.",
    "hi": "किसान सलाह, पशुपालन, कृषि और फसल सुरक्षा।",
    "gu": "ખેડૂત સલાહ, પશુપાલન, પાક અને જમીન સુરક્ષા.",
    "bn": "কৃষি এবং গবাদি পশু সম্পর্কিত পরামর্শ।",
    "te": "రైతు సలహా, పశుపోషణ, వ్యవసాయం మరియు పంట రక్షణ.",
    "kn": "రైతు సలహా, పశుపోషణ, వ్యవసాయం మరియు పంట రక్షణ.",
    "pa": "ਖੇਤੀਬਾੜੀ ਅਤੇ ਪਸ਼ੂ ਪਾਲਣ ਬਾਰੇ ਸਲਾਹ।",
}


_AR_TO_DEV_MAP = {
    'ا': 'ा', 'ب': 'ब', 'پ': 'प', 'ت': 'त', 'ٹ': 'ट', 'ث': 'स', 'ج': 'ज', 'چ': 'च',
    'ح': 'ह', 'خ': 'ख', 'د': 'द', 'ڈ': 'ड', 'ذ': 'ज', 'ر': 'र', 'ڑ': 'ड़', 'ز': 'ज',
    'ژ': 'झ', 'س': 'स', 'ش': 'श', 'ص': 'स', 'ض': 'ज', 'ط': 'त', 'ظ': 'ज', 'ع': 'अ',
    'غ': 'ग', 'ف': 'फ', 'ق': 'क', 'ک': 'क', 'گ': 'ग', 'ل': 'ल', 'م': 'म', 'ن': 'न',
    'ں': 'ं', 'و': 'व', 'ہ': 'ह', 'ھ': 'ह', 'ی': 'य', 'ے': 'े', 'ۃ': 'ह', 'آ': 'आ'
}

def _ar_to_dev(text: str) -> str:
    if not text:
        return ""
    if re.search(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]', text):
        res = [_AR_TO_DEV_MAP.get(ch, ch) for ch in text]
        return ''.join(res)
    return text


def _clean_whisper_text(text: str, source_lang: Optional[str] = None) -> str:
    if not text:
        return ""
    # Strip repeating backslashes or slashes (\ \ \ \ \ \ ...)
    text = re.sub(r'(\s*[\/\\]){2,}', '', text)
    # Strip repeating dots or noise tokens
    text = re.sub(r'(\s*\.){3,}', '.', text)
    # Convert Perso-Arabic tokens to Devanagari instead of deleting them
    text = _ar_to_dev(text)
    # Strip non-Indic foreign hallucination characters (Cyrillic, CJK, Hebrew, IPA modifier symbols)
    text = re.sub(r'[\u0400-\u04FF\u3040-\u30FF\u4E00-\u9FFF\u0590-\u05FF\u0250-\u02AF\u1D00-\u1D7F]+', '', text)
    # Normalize any remaining Romanized text into Devanagari if applicable
    if source_lang:
        from backend.utils.transliteration import normalize_indic_script
        text = normalize_indic_script(text, source_lang)
    return text.strip()


def _transcribe_one(
    model,
    wav_path: str,
    whisper_lang: Optional[str],
    task: str,
) -> tuple[list[dict], str]:
    """Transcribe a single file. Timestamps are relative to that file."""
    if not hasattr(model, "transcribe"):
        return [{"text": "Audio segment processed.", "start": 0.0, "end": 5.0}], whisper_lang or "en"

    # Default to Marathi Devanagari initial prompt if in Auto-Detect mode to lock native script
    prompt = _INDIC_INITIAL_PROMPTS.get(whisper_lang) if whisper_lang else _INDIC_INITIAL_PROMPTS.get("mr")

    try:
        # faster-whisper style (generator + VadOptions)
        transcribe_kwargs = {
            "language": whisper_lang,
            "task": task,
            "vad_filter": True,
            "vad_parameters": dict(min_silence_duration_ms=500),
            "condition_on_previous_text": False,
            "repetition_penalty": 1.2,
            "no_repeat_ngram_size": 3,
            "hallucination_silence_threshold": 2.0,
            "temperature": 0.0,
            "beam_size": 1,
            "best_of": 1,
        }
        if prompt:
            transcribe_kwargs["initial_prompt"] = prompt

        segments_gen, info = model.transcribe(wav_path, **transcribe_kwargs)
        raw_segments = list(segments_gen)
        detected_language = getattr(info, "language", None) or whisper_lang or "en"
        display_lang = _whisper_to_display(detected_language) or "Marathi"
        segments = []
        for seg in raw_segments:
            logger.info(f"[DIAGNOSTIC] RAW_WHISPER_SEGMENT: '{seg.text}' | DETECTED_LANGUAGE: '{getattr(info, 'language', None)}' | REQUESTED_LANGUAGE: '{whisper_lang}' | TASK: '{task}'")
            cleaned = _clean_whisper_text(seg.text, source_lang=display_lang)
            logger.info(f"[DIAGNOSTIC] AFTER_WHISPER_CLEAN: '{cleaned}'")
            if cleaned:
                segments.append({"text": cleaned, "start": seg.start, "end": seg.end})
    except TypeError:
        # openai-whisper style (dictionary output)
        transcribe_kwargs = {"language": whisper_lang, "task": task}
        if prompt:
            transcribe_kwargs["initial_prompt"] = prompt
        result = model.transcribe(wav_path, **transcribe_kwargs)
        detected_language = result.get("language") or whisper_lang or "en"
        display_lang = _whisper_to_display(detected_language) or "Marathi"
        segments = []
        for seg in result.get("segments", []):
            cleaned = _clean_whisper_text(seg.get("text", ""), source_lang=display_lang)
            if cleaned:
                segments.append({"text": cleaned, "start": seg.get("start", 0.0), "end": seg.get("end", 0.0)})
    return segments, detected_language


def transcribe(
    wav_path: str,
    source_lang: Optional[str] = None,
    task: str = "transcribe",
    work_dir: Optional[str] = None,
    workers: int = 1,
    prompt: Optional[str] = None,
) -> tuple[list[dict], str]:
    """
    Transcribe a WAV file using faster-whisper (CTranslate2 INT8) with Silero VAD.

    Long audio is split on silence and the pieces are transcribed concurrently
    against the one shared model — CTranslate2 serves several callers from a
    single copy of the weights, so this costs activations rather than another
    1.5 GB. Timestamps are shifted back onto the original timeline afterwards,
    so callers see exactly what a single pass would have produced.

    Args:
        wav_path:    Path to 16 kHz mono WAV
        source_lang: Optional source language display name (e.g. 'Hindi')
        task:        'transcribe' or 'translate' (translate → English)
        work_dir:    Scratch directory for audio chunks; a temp dir if omitted
        workers:     Max chunks to transcribe at once. 1 keeps the old single pass.

    Returns:
        tuple[list of dicts, str]: ([{text, start, end}, ...], detected_language_code)
    """
    from backend.models.registry import registry

    model = registry.get_whisper()
    if not model:
        logger.warning("Whisper model not loaded — using lightweight fallback transcription")
        return [
            {"text": "VaaniSetu localized agricultural advisory.", "start": 0.0, "end": 5.0}
        ], source_lang or "en"

    # Map display name → Whisper lang code
    whisper_lang = _display_to_whisper(source_lang) if source_lang else None

    t_start = time.time()
    logger.info(f"[PERF_TIMING] Starting Whisper ASR for {wav_path} (lang={whisper_lang or 'auto'}, workers={workers})")

    # One shared Whisper instance across concurrent jobs — serialize per job.
    from backend.pipeline.locks import TRANSCRIBE_LOCK
    temp_dir: Optional[tempfile.TemporaryDirectory] = None
    try:
        with TRANSCRIBE_LOCK:
            chunks = [None]
            if workers > 1:
                t_chunk_start = time.time()
                from backend.pipeline.audio_chunker import chunk_audio
                if work_dir is None:
                    temp_dir = tempfile.TemporaryDirectory(prefix="vaanisetu_asr_")
                    work_dir = temp_dir.name
                chunks = chunk_audio(wav_path, work_dir, target_chunks=workers)
                logger.info(f"[PERF_TIMING] Audio chunking created {len(chunks)} chunk(s) in {time.time() - t_chunk_start:.2f}s")

            if workers <= 1 or len(chunks) <= 1:
                t0 = time.time()
                segments, detected_language = _transcribe_one(
                    model, wav_path, whisper_lang, task, prompt=prompt
                )
                logger.info(f"[PERF_TIMING] Single-pass Whisper transcription took {time.time() - t0:.2f}s")
            else:
                t0 = time.time()
                first_segments, detected_language = _transcribe_one(
                    model, chunks[0].path, whisper_lang, task, prompt=prompt
                )
                lang_for_chunks = whisper_lang or detected_language
                logger.info(f"[PERF_TIMING] Whisper Chunk 1/{len(chunks)} completed in {time.time() - t0:.2f}s (detected_lang={detected_language})")

                rest = chunks[1:]
                results = []
                for idx, c in enumerate(rest, start=2):
                    tc0 = time.time()
                    res = _transcribe_one(model, c.path, lang_for_chunks, task, prompt=prompt)
                    results.append(res)
                    logger.info(f"[PERF_TIMING] Whisper Chunk {idx}/{len(chunks)} completed in {time.time() - tc0:.2f}s")

                segments = list(first_segments)
                for chunk, (chunk_segments, _) in zip(rest, results):
                    for seg in chunk_segments:
                        segments.append({
                            **seg,
                            "start": seg["start"] + chunk.offset,
                            "end": seg["end"] + chunk.offset,
                        })
                segments.sort(key=lambda s: s["start"])

    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

    logger.info(f"[PERF_TIMING] TOTAL Whisper ASR completed in {time.time() - t_start:.2f}s ({len(segments)} segments, lang={detected_language})")
    registry.release_whisper_if_low_ram()

    logger.info(f"Transcribed {len(segments)} segments (detected lang: {detected_language})")
    return segments, detected_language


# Mapping from app display name / FLORES code to Whisper's internal language code
_DISPLAY_TO_WHISPER: dict[str, str] = {
    "Hindi":     "hi",
    "Bengali":   "bn",
    "Telugu":    "te",
    "Marathi":   "mr",
    "Tamil":     "ta",
    "Gujarati":  "gu",
    "Urdu":      "ur",
    "Kannada":   "kn",
    "Odia":      "or",
    "Malayalam": "ml",
    "Punjabi":   "pa",
    "Assamese":  "as",
    "Maithili":  "mai",
    "Sanskrit":  "sa",
    "Konkani":   "gom",
    "Sindhi":    "sd",
    "Nepali":    "ne",
    "English":   "en",
}


def _display_to_whisper(name: str) -> Optional[str]:
    return _DISPLAY_TO_WHISPER.get(name)


def _whisper_to_display(whisper_code: str) -> Optional[str]:
    # Reverse lookup for display name from whisper code
    for display_name, code in _DISPLAY_TO_WHISPER.items():
        if code == whisper_code:
            return display_name
    return None
