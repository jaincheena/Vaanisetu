"""
Regression tests for the defects found during the Advisory Studio / Impact
Ledger test pass.

Each test names the behaviour that was broken, so a future change that
reintroduces it fails here rather than in the field.

Run:  python -m pytest tests/test_regressions.py -v
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Confidence gate
# ---------------------------------------------------------------------------
class TestConfidenceGate:
    """The gate rescaled everything into 0.982-0.995, above CONFIDENCE_GREEN.
    Amber and red were unreachable and the Review Queue never received work."""

    def test_poor_translations_do_not_score_green(self):
        from backend.services.confidence import _calibrate_log_probs, confidence_level

        for name, log_probs in [
            ("shaky", [-2.0] * 20),
            ("bad", [-5.0] * 20),
            ("nonsense", [-30.0] * 20),
        ]:
            level = confidence_level(_calibrate_log_probs(log_probs))
            assert level in ("amber", "red"), f"{name} scored {level}, should need review"

    def test_good_translations_still_clear(self):
        from backend.services.confidence import _calibrate_log_probs, confidence_level

        assert confidence_level(_calibrate_log_probs([-0.01] * 20)) == "green"
        assert confidence_level(_calibrate_log_probs([-0.4] * 20)) == "green"

    def test_score_range_spans_the_thresholds(self):
        from backend.config import CONFIDENCE_AMBER, CONFIDENCE_GREEN
        from backend.services.confidence import _calibrate_log_probs

        scores = [_calibrate_log_probs([lp] * 20) for lp in (-0.01, -1.0, -3.0, -10.0, -40.0)]
        assert min(scores) < CONFIDENCE_AMBER < CONFIDENCE_GREEN < max(scores), (
            f"observed {min(scores):.3f}-{max(scores):.3f}; the gate cannot fire "
            f"unless the range straddles amber ({CONFIDENCE_AMBER}) and green ({CONFIDENCE_GREEN})"
        )

    def test_unmeasurable_confidence_fails_towards_review(self):
        """An empty or failed computation must not auto-clear for distribution."""
        from backend.config import CONFIDENCE_GREEN
        from backend.services.confidence import (
            FALLBACK_CONFIDENCE, _calibrate_log_probs, avg_confidence, confidence_level,
        )

        assert FALLBACK_CONFIDENCE < CONFIDENCE_GREEN
        assert confidence_level(FALLBACK_CONFIDENCE) == "amber"
        assert _calibrate_log_probs([]) == FALLBACK_CONFIDENCE
        assert avg_confidence([]) == FALLBACK_CONFIDENCE


# ---------------------------------------------------------------------------
# Resource planning
# ---------------------------------------------------------------------------
class TestResourcePlanning:
    """is_low_ram_device() returned True for any CPU deployment, so every
    install ran pinned to one worker and two threads regardless of hardware."""

    def test_cpu_alone_does_not_mean_low_ram(self, monkeypatch):
        import psutil
        from backend import config

        class BigMachine:
            total = 32 * 1024 ** 3
            available = 20 * 1024 ** 3

        monkeypatch.setattr(psutil, "virtual_memory", lambda: BigMachine)
        monkeypatch.setattr(config, "DEVICE", "cpu")
        assert config.is_low_ram_device() is False

    def test_small_machine_is_still_low_ram(self, monkeypatch):
        import psutil
        from backend import config

        class FieldLaptop:
            total = 8 * 1024 ** 3
            available = 3 * 1024 ** 3

        monkeypatch.setattr(psutil, "virtual_memory", lambda: FieldLaptop)
        assert config.is_low_ram_device() is True

    def test_saver_mode_throttles_and_normal_mode_does_not(self):
        from backend.config import inference_threads

        assert inference_threads(resource_saver=True) == 2
        assert inference_threads(resource_saver=False) >= 2

    def test_asr_plan_does_not_oversubscribe_cores(self):
        from backend.config import asr_worker_plan, inference_threads

        num_workers, cpu_threads = asr_worker_plan()
        assert num_workers >= 1 and cpu_threads >= 1
        assert num_workers * cpu_threads <= inference_threads(), (
            "more concurrent chunks than cores makes each slower without "
            "finishing any sooner"
        )


# ---------------------------------------------------------------------------
# Audio chunking
# ---------------------------------------------------------------------------
class TestAudioChunker:
    """Chunks must only ever be cut inside a silence, and must never leave a
    fragment too short for Whisper to have sentence context."""

    def test_cuts_land_inside_detected_silences(self):
        from backend.pipeline.audio_chunker import plan_cut_points

        silences = [(t, t + 0.6) for t in range(30, 600, 30)]
        cuts = plan_cut_points(600, silences, target_chunks=4)
        assert len(cuts) == 3
        for cut in cuts:
            assert any(start <= cut <= end for start, end in silences), (
                f"cut at {cut}s is not inside any silence — it would slice a word"
            )

    def test_no_silence_means_no_split(self):
        from backend.pipeline.audio_chunker import plan_cut_points

        assert plan_cut_points(600, [], target_chunks=4) == []
        assert plan_cut_points(600, [(5.0, 5.6)], target_chunks=4) == []

    def test_every_chunk_meets_the_minimum_length(self):
        from backend.pipeline.audio_chunker import MIN_CHUNK_S, plan_cut_points

        silences = [(t, t + 0.5) for t in range(10, 600, 10)]
        cuts = plan_cut_points(600, silences, target_chunks=8)
        bounds = [0.0, *cuts, 600.0]
        for a, b in zip(bounds, bounds[1:]):
            assert b - a >= MIN_CHUNK_S

    def test_short_audio_is_left_alone(self):
        from backend.pipeline.audio_chunker import MIN_SPLIT_DURATION_S, chunk_audio

        with tempfile.TemporaryDirectory() as td:
            fake = os.path.join(td, "short.wav")
            Path(fake).write_bytes(b"RIFF")  # never read; duration probe returns 0
            chunks = chunk_audio(fake, td, target_chunks=4)
        assert len(chunks) == 1
        assert MIN_SPLIT_DURATION_S > 0


# ---------------------------------------------------------------------------
# Impact ledger
# ---------------------------------------------------------------------------
@pytest.fixture
def impact_db(tmp_path, monkeypatch):
    """A fresh database with three completed jobs of known content length."""
    monkeypatch.setenv("VAANISETU_BASE", str(tmp_path))
    for mod in [m for m in list(sys.modules) if m.startswith("backend")]:
        del sys.modules[mod]

    from backend.database import get_db, init_db

    init_db()
    with get_db() as conn:
        conn.execute("DELETE FROM review_queue")
        conn.execute("DELETE FROM jobs")
        for job_id, langs, seconds in [
            ("j1", ["Marathi", "Hindi", "Gujarati", "Telugu", "Kannada"], 600.0),
            ("j2", ["Marathi", "Hindi"], 270.0),
            ("j3", ["Marathi"], 120.0),
        ]:
            conn.execute(
                "INSERT INTO jobs (id, status, target_langs, media_duration_s,"
                " started_at, completed_at) VALUES (?,'completed',?,?,?,?)",
                (job_id, json.dumps(langs), seconds,
                 "2026-08-20T10:00:00", "2026-08-20T12:00:00"),
            )
        # predates duration tracking
        conn.execute(
            "INSERT INTO jobs (id, status, target_langs) VALUES ('legacy','completed',?)",
            (json.dumps(["Marathi"]),),
        )
    yield


class TestImpactLedger:
    def test_fresh_database_initialises(self, tmp_path, monkeypatch):
        """Seeds referenced jobs.quality_mode before the migration that adds
        it, so init_db() raised OperationalError on any clean install."""
        monkeypatch.setenv("VAANISETU_BASE", str(tmp_path / "brand_new"))
        for mod in [m for m in list(sys.modules) if m.startswith("backend")]:
            del sys.modules[mod]
        from backend.database import init_db

        init_db()  # must not raise

    def test_hours_counted_once_per_job(self, impact_db):
        """Hours were summed inside the per-language loop, so one advisory into
        five languages reported five times its runtime."""
        from backend.services.impact_ledger import get_impact_summary

        summary = get_impact_summary()
        expected_hours = (600 + 270 + 120) / 3600
        # total_hours is stored to 2dp, so half of the last digit is the
        # tightest meaningful tolerance.
        assert summary["total_hours"] == pytest.approx(expected_hours, abs=0.01)
        # The bug this guards against inflated the figure by the language
        # count, which is far outside any rounding tolerance.
        inflated = (600 * 5 + 270 * 2 + 120 * 1) / 3600
        assert summary["total_hours"] < inflated / 2

    def test_cost_is_per_language(self, impact_db):
        from backend.services.impact_ledger import get_impact_summary

        summary = get_impact_summary()
        expected = ((600 / 60) * 5 + (270 / 60) * 2 + (120 / 60) * 1) * 850
        assert summary["total_cost_saved"] == pytest.approx(expected)

    def test_farmer_counts_are_whole_numbers(self, impact_db):
        """The bar chart rendered "Marathi 7.6 farmers"."""
        from backend.services.impact_ledger import get_impact_summary

        summary = get_impact_summary()
        assert isinstance(summary["total_farmers_reachable"], int)
        for row in summary["language_breakdown"]:
            assert isinstance(row["farmers_reachable"], int)

    def test_jobs_without_a_measured_duration_are_excluded_and_counted(self, impact_db):
        from backend.services.impact_ledger import get_impact_summary

        summary = get_impact_summary()
        assert summary["job_count"] == 3
        assert summary["unmeasured_job_count"] == 1

    def test_processing_time_does_not_affect_the_figures(self, impact_db):
        """A slower laptop must not report more impact. Every job here ran for
        two wall-clock hours; the totals must depend only on content length."""
        from backend.database import get_db
        from backend.services.impact_ledger import get_impact_summary

        before = get_impact_summary()
        with get_db() as conn:
            conn.execute("UPDATE jobs SET completed_at='2026-08-21T04:00:00'")  # 18h
        assert get_impact_summary() == before

    def test_summary_matches_its_schema(self, impact_db):
        from backend.models.schemas import ImpactSummary
        from backend.services.impact_ledger import get_impact_summary

        ImpactSummary(**get_impact_summary())


# ---------------------------------------------------------------------------
# PDF export
# ---------------------------------------------------------------------------
class TestPdfExport:
    """Helvetica is latin-1; the report contains an em dash and ₹, so every
    click raised FPDFUnicodeEncodingException."""

    SUMMARY = {
        "total_hours": 3.2,
        "total_cost_saved": 163200.0,
        "total_farmers_reachable": 384,
        "job_count": 4,
        "unmeasured_job_count": 2,
        "language_breakdown": [
            {"language": "Marathi", "job_count": 4, "total_minutes": 192.0,
             "cost_saved": 163200.0, "farmers_reachable": 384},
        ],
    }

    def test_export_succeeds_with_a_unicode_font(self, tmp_path):
        from backend.services import export

        out = tmp_path / "impact.pdf"
        export.export_impact_pdf(self.SUMMARY, str(out))
        assert out.stat().st_size > 0

    def test_export_succeeds_with_no_unicode_font_available(self, tmp_path, monkeypatch):
        from backend.services import export

        monkeypatch.setattr(export, "_UNICODE_FONT_CANDIDATES", [Path("/nonexistent.ttf")])
        out = tmp_path / "impact_fallback.pdf"
        export.export_impact_pdf(self.SUMMARY, str(out))
        assert out.stat().st_size > 0

    def test_transliteration_keeps_the_meaning(self):
        from backend.services.export import _pdf_safe

        assert _pdf_safe("₹163,200", False) == "Rs.163,200"
        assert _pdf_safe("VaaniSetu — Report", False) == "VaaniSetu - Report"
        assert _pdf_safe("₹163,200", True) == "₹163,200"


# ---------------------------------------------------------------------------
# Translation availability
# ---------------------------------------------------------------------------
class TestTranslationFallback:
    """When IndicTrans2 could not be loaded, the fallback returned the SOURCE
    TEXT as the translation at confidence 0.985/green/cleared — so a Marathi
    farmer received English audio, video and a printed handout, all stamped
    verified."""

    def test_untranslatable_text_raises_instead_of_echoing_the_source(self, monkeypatch):
        from backend.pipeline import translator
        import backend.services.translation_memory as tm

        monkeypatch.setattr(tm, "lookup", lambda *a, **k: None)

        segments = [{"text": "Spray Propiconazole at 1 ml per litre.", "start": 0.0, "end": 3.0}]
        with pytest.raises(translator.TranslationUnavailableError) as excinfo:
            translator._fallback_translate_segments(segments, "Marathi")
        assert "NOT been translated" in str(excinfo.value)

    def test_cached_segments_still_serve(self, monkeypatch):
        from backend.pipeline import translator
        import backend.services.translation_memory as tm

        monkeypatch.setattr(tm, "lookup", lambda src, tgt, text: "फवारणी करा")
        segments = [{"text": "Spray it.", "start": 0.0, "end": 1.0}]
        out = translator._fallback_translate_segments(segments, "Marathi")
        assert out[0]["translated"] == "फवारणी करा"
        assert out[0]["from_cache"] is True

    def test_no_source_text_is_ever_returned_as_a_translation(self, monkeypatch):
        """Mixed case: one segment cached, one not. Must raise, not part-echo."""
        from backend.pipeline import translator
        import backend.services.translation_memory as tm

        def partial_lookup(src, tgt, text):
            return "फवारणी करा" if text == "Spray it." else None

        monkeypatch.setattr(tm, "lookup", partial_lookup)
        segments = [
            {"text": "Spray it.", "start": 0.0, "end": 1.0},
            {"text": "Something never seen before.", "start": 1.0, "end": 2.0},
        ]
        with pytest.raises(translator.TranslationUnavailableError):
            translator._fallback_translate_segments(segments, "Marathi")
