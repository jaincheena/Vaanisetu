"""
VaaniSetu — Pydantic Schemas
Request / response models for all API endpoints.
"""

from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------
class JobStatus(BaseModel):
    id: str
    mode: str
    filename: Optional[str]
    source_lang: Optional[str]
    target_langs: Optional[list[str]]
    status: str
    confidence_level: Optional[str]
    avg_confidence: Optional[float]
    queued_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    output_path: Optional[str]
    error_log: Optional[str]
    distribution_clearance: Optional[str]
    quality_mode: Optional[str]


class JobSubmitResponse(BaseModel):
    job_id: str
    message: str


# ---------------------------------------------------------------------------
# Review Queue
# ---------------------------------------------------------------------------
class ReviewAction(BaseModel):
    action: str  # approve | edit | reject
    edited_text: Optional[str] = None
    reviewer: Optional[str] = "reviewer"


class ReviewItem(BaseModel):
    id: int
    job_id: str
    segment_index: int
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: float
    status: str
    reviewer: Optional[str]
    edited_translation: Optional[str]
    created_at: str
    reviewed_at: Optional[str]


class ReviewStats(BaseModel):
    pending: int
    approved: int
    edited: int
    rejected: int
    total: int


# ---------------------------------------------------------------------------
# Impact
# ---------------------------------------------------------------------------
class ImpactConfigUpdate(BaseModel):
    language: str
    farmers_per_hour: int = Field(ge=1)
    translation_rate_per_min: int = Field(ge=1)


class LanguageImpact(BaseModel):
    language: str
    job_count: int
    total_minutes: float
    cost_saved: float
    farmers_reachable: int


class ImpactSummary(BaseModel):
    total_hours: float
    total_cost_saved: float
    total_farmers_reachable: int
    job_count: int
    # Completed jobs finished before media_duration_s existed. They cannot be
    # costed honestly, so they are excluded from every figure and counted here.
    unmeasured_job_count: int = 0
    language_breakdown: list[LanguageImpact]


# ---------------------------------------------------------------------------
# Glossary
# ---------------------------------------------------------------------------
class GlossaryTerm(BaseModel):
    source_text: str
    source_lang: str
    translations: dict[str, str]   # lang_name → translated_text
    times_used: int
    confidence: float


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    ram_gb: float
    ram_free_gb: float
    disk_gb: float
    disk_free_gb: float
    queue_depth: int
    review_pending: int
    models_loaded: dict[str, bool]
    status: str
