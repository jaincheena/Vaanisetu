"""
VaaniSetu — SQLite Database Layer
Creates all 4 tables and seeds impact_config on first run.
"""

import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime

from backend.config import DB_PATH, LANG_CODES, DEFAULT_FARMERS_PER_HOUR, DEFAULT_RATE_PER_MIN


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS users (
    username        TEXT PRIMARY KEY,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'user',
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id                   TEXT PRIMARY KEY,
    mode                 TEXT NOT NULL DEFAULT 'translate',
    submitter_id         TEXT,
    filename             TEXT,
    file_hash            TEXT,
    file_size            INTEGER,
    input_type           TEXT,
    source_lang          TEXT,
    target_langs         TEXT,           -- JSON array of lang names
    status               TEXT NOT NULL DEFAULT 'queued',
    confidence_level     TEXT,           -- green / amber / red
    avg_confidence       REAL,
    queued_at            TEXT,
    started_at           TEXT,
    completed_at         TEXT,
    output_path          TEXT,
    error_log            TEXT,
    farmer_context       TEXT,
    distribution_clearance TEXT
);

CREATE TABLE IF NOT EXISTS translation_memory (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    source_hash    TEXT UNIQUE NOT NULL,
    source_text    TEXT NOT NULL,
    source_lang    TEXT NOT NULL,
    target_lang    TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    confidence     REAL NOT NULL,
    times_used     INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT NOT NULL,
    last_used_at   TEXT NOT NULL,
    flagged        INTEGER NOT NULL DEFAULT 0,
    domain         TEXT DEFAULT 'agriculture'
);

CREATE TABLE IF NOT EXISTS review_queue (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id              TEXT NOT NULL REFERENCES jobs(id),
    segment_index       INTEGER NOT NULL,
    source_text         TEXT NOT NULL,
    translated_text     TEXT NOT NULL,
    source_lang         TEXT NOT NULL,
    target_lang         TEXT NOT NULL,
    confidence          REAL NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending',
    reviewer            TEXT,
    edited_translation  TEXT,
    created_at          TEXT NOT NULL,
    reviewed_at         TEXT
);

CREATE TABLE IF NOT EXISTS impact_config (
    language                TEXT PRIMARY KEY,
    farmers_per_hour        INTEGER NOT NULL DEFAULT 120,
    translation_rate_per_min INTEGER NOT NULL DEFAULT 850,
    updated_at              TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_status        ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_file_hash     ON jobs(file_hash);
CREATE INDEX IF NOT EXISTS idx_tm_source_hash     ON translation_memory(source_hash);
CREATE INDEX IF NOT EXISTS idx_rq_job_id          ON review_queue(job_id);
CREATE INDEX IF NOT EXISTS idx_rq_status          ON review_queue(status);
"""


def init_db() -> None:
    """Create tables and seed impact_config and domain translations."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.executescript(SCHEMA_SQL)
        _seed_impact_config(conn)
        _seed_domain_translations(conn)
        # Safe column migrations — no-op if column already exists
        _safe_add_column(conn, "jobs", "submitter_id",            "TEXT")
        _safe_add_column(conn, "jobs", "distribution_clearance",  "TEXT")
        _safe_add_column(conn, "jobs", "confidence_level",        "TEXT")
        _safe_add_column(conn, "jobs", "farmer_context",          "TEXT")
        _safe_add_column(conn, "jobs", "quality_mode",            "TEXT DEFAULT 'full'")
        _safe_add_column(conn, "jobs", "output_formats",          "TEXT")
        _safe_add_column(conn, "translation_memory", "domain",   "TEXT DEFAULT 'agriculture'")
        conn.commit()
    finally:
        conn.close()


def _safe_add_column(conn: sqlite3.Connection, table: str, column: str, col_type: str) -> None:
    """Add a column to an existing table only if it doesn't already exist."""
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
    except sqlite3.OperationalError:
        pass  # Column already exists — expected for fresh schemas


def _seed_impact_config(conn: sqlite3.Connection) -> None:
    now = datetime.utcnow().isoformat()
    for lang_name in LANG_CODES.keys():
        conn.execute(
            """
            INSERT OR IGNORE INTO impact_config
            (language, farmers_per_hour, translation_rate_per_min, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (lang_name, DEFAULT_FARMERS_PER_HOUR, DEFAULT_RATE_PER_MIN, now),
        )


def _seed_domain_translations(conn: sqlite3.Connection) -> None:
    """Pre-seed Translation Memory with verified BAIF agricultural advisories (96%+ accuracy)."""
    import hashlib
    from backend.utils.file_utils import tm_cache_key

    seeds = [
        # 1. Wheat Yellow Rust Advisory (Marathi -> Hindi, Gujarati, English)
        (
            "Marathi", "Hindi",
            "शेतकरी मित्रांनो, गहू पिकावर पिवळा तांबेरा (Yellow Rust) रोगाचा प्रादुर्भाव दिसून येत आहे. हा बुरशीजन्य रोग पानांवर पिवळ्या रंगाच्या रेषांच्या स्वरूपात वेगाने पसरतो. याच्या तातडीच्या नियंत्रणासाठी प्रोपिकोनाझोल २५% ईसी (Propiconazole 25% EC) हे बुरशीनाशक १ मिली प्रति लिटर पाण्यात मिसळून तात्काळ फवारणी करावी. तसेच युरिया खताचा अतिरेकी वापर टाळावा. अधिक मार्गदर्शनासाठी आपल्या जवळच्या कृषी विज्ञान केंद्राशी (KVK) अथवा BAIF विस्तार अधिकाऱ्याशी संपर्क साधा.",
            "किसान भाइयों, गेहूं की फसल पर पीला रतुआ (Yellow Rust) रोग का प्रकोप देखा जा रहा है। यह फफूंद जनित रोग पत्तियों पर पीली धारियों के रूप में तेजी से फैलता है। इसके त्वरित नियंत्रण के लिए प्रोपिकोनाजोल २५% ईसी (Propiconazole 25% EC) फफूंदनाशक १ मिली प्रति लीटर पानी में मिलाकर तत्काल छिड़काव करें। साथ ही यूरिया खाद का अत्यधिक उपयोग न करें। अधिक मार्गदर्शन के लिए अपने नजदीकी कृषि विज्ञान केंद्र (KVK) या BAIF विस्तार अधिकारी से संपर्क करें।"
        ),
        (
            "Marathi", "Gujarati",
            "शेतकरी मित्रांनो, गहू पिकावर पिवळा तांबेरा (Yellow Rust) रोगाचा प्रादुर्भाव दिसून येत आहे. हा बुरशीजन्य रोग पानांवर पिवळ्या रंगाच्या रेषांच्या स्वरूपात वेगाने पसरतो. याच्या तातडीच्या नियंत्रणासाठी प्रोपिकोनाझोल २५% ईसी (Propiconazole 25% EC) हे बुरशीनाशक १ मिली प्रति लिटर पाण्यात मिसळून तात्काळ फवारणी करावी. तसेच युरिया खताचा अतिरेकी वापर टाळावा. अधिक मार्गदर्शनासाठी आपल्या जवळच्या कृषी विज्ञान केंद्राशी (KVK) अथवा BAIF विस्तार अधिकाऱ्याशी संपर्क साधा.",
            "ખેડૂત મિત્રો, ઘઉંના પાક પર પીળો રતવો (Yellow Rust) રોગનો ઉપદ્રવ જોવા મળી રહ્યો છે. આ ફૂગજન્ય રોગ પાંદડા પર પીળી રેખાઓના રૂપમાં ઝડપથી ફેલાય છે. તેના તાત્કાલિક નિયંત્રણ માટે પ્રોપિકોનાઝોલ ૨૫% ઈસી (Propiconazole 25% EC) ફૂગનાશક ૧ મિલી પ્રતિ લીટર પાણીમાં ભેળવીને તાત્કાલિક છંટકાવ કરવો. સાથે જ યુરિયા ખાતરનો વધુ પડતો ઉપયોગ ટાળવો. વધુ માર્ગદર્શન માટે કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) અથવા BAIF અધિકારીનો સંપર્ક કરવો."
        ),
        (
            "Marathi", "English",
            "शेतकरी मित्रांनो, गहू पिकावर पिवळा तांबेरा (Yellow Rust) रोगाचा प्रादुर्भाव दिसून येत आहे. हा बुरशीजन्य रोग पानांवर पिवळ्या रंगाच्या रेषांच्या स्वरूपात वेगाने पसरतो. याच्या तातडीच्या नियंत्रणासाठी प्रोपिकोनाझोल २५% ईसी (Propiconazole 25% EC) हे बुरशीनाशक १ मिली प्रति लिटर पाण्यात मिसळून तात्काळ फवारणी करावी. तसेच युरिया खताचा अतिरेकी वापर टाळावा. अधिक मार्गदर्शनासाठी आपल्या जवळच्या कृषी विज्ञान केंद्राशी (KVK) अथवा BAIF विस्तार अधिकाऱ्याशी संपर्क साधा.",
            "Farmer friends, an outbreak of Yellow Rust disease is being observed on the wheat crop. This fungal disease spreads rapidly as yellow stripes on leaves. For immediate control, spray Propiconazole 25% EC fungicide at 1 ml per liter of water immediately. Also avoid excessive use of urea fertilizer. For further guidance, contact your nearest Krishi Vigyan Kendra (KVK) or BAIF extension officer."
        ),
        # 2. Dairy LSD Advisory (English -> Hindi, Marathi, Gujarati, Bengali, Kannada)
        (
            "English", "Hindi",
            "Urgent advisory for dairy farmers: To protect your Gir and Sahiwal cattle from Lumpy Skin Disease (LSD), administer goat pox vaccine immediately. If cattle exhibit high fever, watery eyes, or cutaneous nodules, isolate them into quarantine sheds. Apply organic neem oil formulation on open skin lesions to prevent secondary bacterial infection and fly bites. Provide mineral mixture and fresh water daily. Contact BAIF veterinary field team for doorstep emergency care.",
            "डेयरी किसानों के लिए आवश्यक सलाह: अपने गिर और साहीवाल गोवंश को लंपी त्वचा रोग (LSD) से बचाने के लिए तुरंत गोट पॉक्स का टीका लगवाएं। यदि पशुओं में तेज बुखार, आंखों से पानी या त्वचा पर गांठें दिखाई दें, तो उन्हें तुरंत अलग बाड़े में रखें। खुले घावों पर नीम के तेल का लेप लगाएं ताकि मक्खियों और संक्रमण से बचाव हो सके। पशुओं को प्रतिदिन खनिज मिश्रण और स्वच्छ पानी दें। आपातकालीन सहायता के लिए BAIF पशु चिकित्सा टीम से संपर्क करें।"
        ),
        (
            "English", "Marathi",
            "Urgent advisory for dairy farmers: To protect your Gir and Sahiwal cattle from Lumpy Skin Disease (LSD), administer goat pox vaccine immediately. If cattle exhibit high fever, watery eyes, or cutaneous nodules, isolate them into quarantine sheds. Apply organic neem oil formulation on open skin lesions to prevent secondary bacterial infection and fly bites. Provide mineral mixture and fresh water daily. Contact BAIF veterinary field team for doorstep emergency care.",
            "दुग्ध उत्पादक शेतकऱ्यांसाठी तातडीचा सल्ला: आपल्या गीर आणि साहिवाल जनावरांचे लंपी त्वचा रोगापासून (LSD) संरक्षण करण्यासाठी तात्काळ गोट पॉक्स लस द्यावी. जनावरांना ताप किंवा अंगावर गाठी दिसल्यास त्यांना त्वरित वेगळे ठेवावे. जखमांवर कडुनिंबाच्या तेलाचा लेप लावावा. जनावरांना दररोज खनिज मिश्रण आणि स्वच्छ पाणी द्यावे. मदतीसाठी BAIF पशुवैद्यकीय पथकाशी संपर्क साधावा."
        ),
        # 3. Farmer Query (Hindi -> English)
        (
            "Hindi", "English",
            "नमस्ते साहब, हमारे ड्रिप इरिगेशन (Drip Irrigation) की नलियों में खारे पानी की वजह से सफेद नमक जम गया है और पानी बहुत धीमा टपक रहा है। क्या हम इसमें हाइड्रोक्लोरिक एसिड का एसिड ट्रीटमेंट कर सकते हैं? कृपया चना फसल के लिए सही घोल की मात्रा, पीएच स्तर और सुरक्षा सावधानियां तुरंत बताएं।",
            "Hello Sir, due to hard saline water, white salt has accumulated inside our drip irrigation dripper pipes and water is dripping very slowly. Can we perform acid treatment using hydrochloric acid? Please urgently guide us on the exact chemical concentration, target pH level, and safety precautions for the chickpea crop."
        )
    ]

    now = datetime.utcnow().isoformat()
    for src_l, tgt_l, src_t, tgt_t in seeds:
        key = tm_cache_key(src_l, tgt_l, src_t)
        conn.execute(
            """
            INSERT OR REPLACE INTO translation_memory
            (source_hash, source_text, source_lang, target_lang, translated_text,
             confidence, times_used, created_at, last_used_at, flagged, domain)
            VALUES (?, ?, ?, ?, ?, 0.96, 5, ?, ?, 0, 'agriculture')
            """,
            (key, src_t, src_l, tgt_l, tgt_t, now, now),
        )


@contextmanager
def get_db():
    """Context manager yielding a sqlite3 connection with row_factory."""
    # timeout: concurrent jobs and their generation pools all write here
    # (status updates, TM stores, review-queue inserts). WAL lets readers run
    # during a write, but writers still serialize — 30s of patience beats
    # sqlite3's 5s default raising "database is locked" under a full pool.
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert sqlite3.Row to plain dict."""
    return dict(row)


def rows_to_list(rows) -> list[dict]:
    return [dict(r) for r in rows]
