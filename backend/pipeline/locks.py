"""
VaaniSetu — Shared Model Locks

The registry holds ONE instance of each model (see backend/models/registry.py).
A torch module is not safe to drive from several threads at once, and cloning
one per worker would cost ~1 GB each — the opposite of what a field laptop
needs. So the models stay single, and every call site takes the matching lock.

Everything that is *not* a shared model — ffmpeg subprocesses, file writers,
ZIP packaging — runs fully parallel and needs none of this.
"""

import threading

# IndicTrans2: guards registry.{en_indic,indic_en}_model.generate()
TRANSLATE_LOCK = threading.Lock()

# Coqui XTTS: guards registry.tts_model.tts_to_file()
TTS_LOCK = threading.Lock()

# Whisper: guards registry.whisper_model.transcribe()
TRANSCRIBE_LOCK = threading.Lock()
