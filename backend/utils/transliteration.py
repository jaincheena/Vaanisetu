"""
VaaniSetu — Indic Script Transliteration & Normalization Utility
Converts Romanized Latin Indic text (Hinglish / Minglish) to authentic Devanagari script
so IndicTrans2 receives proper native script for English and regional translations.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger("vaanisetu.transliteration")

# Comprehensive dictionary for verified BAIF, agricultural, and veterinary terms
DEV_DICT: dict[str, str] = {
    # BAIF Field Programs & Roles
    "pashisaki": "पशुसखी",
    "pashusakhi": "पशुसखी",
    "pasheha": "पशुसखी",
    "muha": "मुखी",
    "mukhi": "मुखी",
    "mugh": "मुख",
    "muhaki": "मुखी",
    "feehlgaid": "फील्ड गाइड",
    "fieldguide": "फील्ड गाइड",
    "philha": "फील्ड",
    "kilha": "गाइड",
    "ki": "की",
    "ka": "का",
    "ke": "के",
    "chya": "च्या",
    
    # Common Disease & Livestock Terms
    "sirens": "सायरेन्स",
    "samanne": "सामान्य",
    "azar": "आजार",
    "roganche": "रोगांचे",
    "zanavaran": "जनावरांमध्ये",
    "zanavaranche": "जनावरांचे",
    "nirogi": "निरोगी",
    "anirogi": "अनिरोगी",
    "duda": "दूध",
    "chara": "चारा",
    "shushka": "शुष्क",
    "ravantakriya": "रवंथक्रिया",
    "nadi": "नाडी",
    "shvesun": "श्वसन",
    "takman": "तापमान",
    "vagnu": "वागणूक",
    "prani": "प्राणी",
    "badaal": "बद्दल",
    "samjun": "समजून",
    "furak": "फरक",
    "upchaar": "उपचार",
    "heora": "हेमोराजिक",
    "septisimiya": "सेप्टिसेमिया",
}

VOWEL_MAP = {
    "aa": "ा", "ai": "ै", "au": "ौ", "ee": "ी", "oo": "ू",
    "a": "", "i": "ि", "u": "ु", "e": "े", "o": "ो",
}

INDEPENDENT_VOWELS = {
    "aa": "आ", "ai": "ऐ", "au": "औ", "ee": "ई", "oo": "ऊ",
    "a": "अ", "i": "इ", "u": "उ", "e": "ए", "o": "ओ",
}

CONSONANTS = [
    ("ksh", "क्ष"), ("dny", "ज्ञ"), ("gy", "ज्ञ"), ("chh", "छ"), ("kh", "ख"), ("gh", "घ"),
    ("jh", "झ"), ("th", "थ"), ("dh", "ध"), ("ph", "फ"), ("bh", "भ"), ("sh", "श"),
    ("k", "क"), ("g", "ग"), ("ch", "च"), ("j", "ज"), ("t", "त"), ("d", "द"),
    ("n", "न"), ("p", "प"), ("b", "ब"), ("m", "म"), ("y", "य"), ("r", "र"),
    ("l", "ल"), ("v", "व"), ("w", "व"), ("s", "स"), ("h", "ह"), ("z", "ज़"),
    ("f", "फ़"), ("c", "क"),
]


def phonetic_roman_to_devanagari(word: str) -> str:
    """Generic phonetic transliterator for Romanized Indic words."""
    w = word.lower()
    i = 0
    n = len(w)
    out = []
    prev_was_consonant = False

    while i < n:
        # Match consonant
        matched_c = None
        for pattern, dev in CONSONANTS:
            if w.startswith(pattern, i):
                matched_c = (pattern, dev)
                break

        if matched_c:
            pattern, dev = matched_c
            out.append(dev)
            i += len(pattern)
            prev_was_consonant = True
            continue

        # Match vowel
        matched_v = None
        for pattern in ("aa", "ai", "au", "ee", "oo", "a", "i", "u", "e", "o"):
            if w.startswith(pattern, i):
                matched_v = pattern
                break

        if matched_v:
            if prev_was_consonant:
                matra = VOWEL_MAP.get(matched_v, "")
                out.append(matra)
            else:
                out.append(INDEPENDENT_VOWELS.get(matched_v, ""))
            i += len(matched_v)
            prev_was_consonant = False
            continue

        # Fallback for non-alphabetic characters
        out.append(w[i])
        i += 1
        prev_was_consonant = False

    return "".join(out)


def normalize_indic_script(text: str, source_lang: Optional[str]) -> str:
    """
    If source_lang is an Indic language (e.g. Marathi, Hindi) and text is in Romanized Latin script,
    normalizes Romanized words to authentic Devanagari script so IndicTrans2 receives proper native script.
    """
    if not text or not source_lang:
        return text

    source_lang_clean = source_lang.strip()
    if source_lang_clean not in ("Marathi", "Hindi", "Gujarati", "Bengali", "Telugu", "Kannada"):
        return text

    # Check if text contains Latin characters and zero Devanagari/Indic characters
    has_indic = bool(re.search(r"[\u0900-\u0D7F]", text))
    has_latin = bool(re.search(r"[a-zA-Z]", text))

    if not (has_latin and not has_indic):
        return text

    words = text.split()
    converted = []
    for w in words:
        clean_w = re.sub(r"[^\w]", "", w.lower())
        if clean_w in DEV_DICT:
            converted.append(DEV_DICT[clean_w])
        elif clean_w and not clean_w.isdigit():
            # Apply generic phonetic transliteration for any un-mapped Romanized Indic word
            p_dev = phonetic_roman_to_devanagari(clean_w)
            converted.append(p_dev if p_dev else w)
        else:
            converted.append(w)

    result = " ".join(converted)
    logger.info(f"Normalized Romanized Indic: '{text}' → '{result}'")
    return result
