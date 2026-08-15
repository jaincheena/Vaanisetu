import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.pipeline import translator


def test_translate_segments_falls_back_when_model_unavailable(monkeypatch=None):
    import backend.models.registry as registry_module

    orig_get = registry_module.registry.get_indic_pair
    try:
        registry_module.registry.get_indic_pair = lambda source_lang: (None, None)
        segments = [{"text": "Hello world", "start": 0.0, "end": 1.0}]

        result = translator.translate_segments(
            segments=segments,
            source_lang="English",
            target_lang_name="Hindi",
            target_lang_code="hin_Deva",
            job_id="job-1",
        )

        assert len(result) == 1
        assert result[0]["translated"] == "Hello world"
        assert result[0]["confidence"] >= 0.98
        assert result[0]["level"] == "green"
        assert result[0]["from_cache"] is True
    finally:
        registry_module.registry.get_indic_pair = orig_get


if __name__ == "__main__":
    test_translate_segments_falls_back_when_model_unavailable()
    print("test_translator_fallback passed!")
