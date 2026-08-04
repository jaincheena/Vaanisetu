from backend.pipeline import translator


def test_translate_segments_falls_back_when_model_unavailable(monkeypatch):
    import backend.models.registry as registry_module

    monkeypatch.setattr(
        registry_module.registry,
        "get_indic_pair",
        lambda source_lang: (None, None),
    )

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
    assert result[0]["confidence"] == 0.50
    assert result[0]["level"] == "red"
    assert result[0]["from_cache"] is True
