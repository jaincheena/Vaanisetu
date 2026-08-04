from backend.models.registry import registry
from backend.pipeline.translator import translate_segments

registry.load_all()

segments = [
    {
        "text": "नमस्ते, आप कैसे हैं?",
        "start": 0,
        "end": 2,
    }
]

try:
    result = translate_segments(
        segments=segments,
        source_lang="Hindi",
        target_lang_name="English",
        target_lang_code="eng_Latn",
        job_id="test",
    )
    print(result)
except Exception:
    import traceback
    traceback.print_exc()