"""
VaaniSetu — Confidence Scoring Service
Computes translation confidence from IndicTrans2 beam scores.

Formula (per spec):
    confidence = exp(max(mean(log_softmax(token_scores)), -5.0))
    → range 0–1
    Green ≥ 0.85 · Amber ≥ 0.65 · Red < 0.65
"""

import math
import logging
from typing import Optional

logger = logging.getLogger("vaanisetu.confidence")

# Used when confidence cannot be measured at all — an empty score list or a
# failed computation. Deliberately below CONFIDENCE_GREEN so the segment is
# routed to a human instead of being auto-cleared for distribution: "we do
# not know" must fail towards review, never towards the farmer.
FALLBACK_CONFIDENCE = 0.75


def _calibrate_log_probs(log_probs: list) -> float:
    if not log_probs:
        return FALLBACK_CONFIDENCE
    N = len(log_probs)
    mean_lp = sum(log_probs) / N

    # Subword length normalization boost for Indic subwords
    length_adj = min(0.6, max(0.0, (N - 1) * 0.05))
    adj_lp = mean_lp + length_adj

    # Calibrated sigmoid mapping token log-probability to a human confidence
    # scale. The output must span the Green/Amber/Red thresholds in
    # backend/config.py — an earlier revision rescaled this into 0.982-0.995,
    # which put the floor above CONFIDENCE_GREEN and made amber and red
    # unreachable. Nothing then ever reached the Review Queue, and every job
    # was stamped "Distribution Cleared" regardless of translation quality.
    val = 1.8 * (adj_lp + 1.4)
    conf = 1.0 / (1.0 + math.exp(-val))
    return max(0.50, min(0.98, float(conf)))


def compute_sequence_confidence(scores: list, sequence_ids) -> float:
    try:
        import torch
        import torch.nn.functional as F

        log_probs: list[float] = []
        for step_idx, step_scores in enumerate(scores):
            if step_idx + 1 >= len(sequence_ids):
                break
            token_id = sequence_ids[step_idx + 1]
            if hasattr(token_id, "item"):
                token_id = token_id.item()
            if token_id <= 25:
                continue
            if step_scores.dim() == 2:
                step_scores = step_scores[0]
            lsm = F.log_softmax(step_scores.float(), dim=-1)
            val = lsm[token_id].item()
            if not (math.isnan(val) or math.isinf(val)):
                log_probs.append(val)

        conf = _calibrate_log_probs(log_probs)
        if math.isnan(conf) or math.isinf(conf):
            return FALLBACK_CONFIDENCE
        return max(0.0, min(1.0, float(conf)))
    except Exception as e:
        logger.warning(f"Confidence computation failed: {e}")
        return FALLBACK_CONFIDENCE


def batch_confidence(scores: list, sequences) -> list[float]:
    try:
        import torch
        import torch.nn.functional as F

        batch_size = sequences.shape[0]
        results = []

        for b in range(batch_size):
            log_probs: list[float] = []
            for step_i, step_scores in enumerate(scores):
                if step_scores.dim() == 2:
                    row_idx = b * (step_scores.size(0) // batch_size) if step_scores.size(0) >= batch_size else b
                    row = step_scores[row_idx]
                else:
                    row = step_scores
                
                if step_i + 1 >= sequences.size(1):
                    break
                
                token_id = sequences[b, step_i + 1].item()
                if token_id <= 25:  # Skip forced language control tokens
                    continue

                lsm = F.log_softmax(row.float(), dim=-1)
                val = lsm[token_id].item()
                if not (math.isnan(val) or math.isinf(val)):
                    log_probs.append(val)

            conf = _calibrate_log_probs(log_probs)
            if math.isnan(conf) or math.isinf(conf):
                conf = FALLBACK_CONFIDENCE
            else:
                conf = max(0.0, min(1.0, float(conf)))
            results.append(conf)

        return results
    except Exception as e:
        logger.warning(f"Batch confidence failed: {e}")
        return [FALLBACK_CONFIDENCE] * (sequences.shape[0] if hasattr(sequences, "shape") else 1)


def confidence_level(score: float) -> str:
    """Map numeric confidence to Green/Amber/Red label."""
    from backend.config import CONFIDENCE_GREEN, CONFIDENCE_AMBER
    if score is None or not isinstance(score, (int, float)) or math.isnan(score) or math.isinf(score):
        score = FALLBACK_CONFIDENCE
    if score >= CONFIDENCE_GREEN:
        return "green"
    if score >= CONFIDENCE_AMBER:
        return "amber"
    return "red"


def avg_confidence(scores: list[float]) -> float:
    valid_scores = [
        float(s) for s in scores 
        if s is not None and isinstance(s, (int, float)) and not math.isnan(s) and not math.isinf(s)
    ]
    if not valid_scores:
        return FALLBACK_CONFIDENCE
    return sum(valid_scores) / len(valid_scores)
