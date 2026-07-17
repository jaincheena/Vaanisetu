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


def compute_sequence_confidence(scores: list, sequence_ids) -> float:
    """
    Args:
        scores: list of (batch_size, vocab_size) tensors, one per generation step
        sequence_ids: 1-D tensor of generated token ids for ONE sequence

    Returns:
        confidence in [0, 1]
    """
    try:
        import torch
        import torch.nn.functional as F

        log_probs: list[float] = []
        for step_idx, step_scores in enumerate(scores):
            token_id = sequence_ids[step_idx + 1]  # +1 skips BOS
            # step_scores may be shape (vocab,) for single or (batch, vocab)
            if step_scores.dim() == 2:
                step_scores = step_scores[0]  # take first item
            lsm = F.log_softmax(step_scores.float(), dim=-1)
            log_probs.append(lsm[token_id].item())

        if not log_probs:
            return 0.0

        mean_lp = sum(log_probs) / len(log_probs)
        return math.exp(max(mean_lp, -5.0))
    except Exception as e:
        logger.warning(f"Confidence computation failed: {e}")
        return 0.5  # neutral fallback


def batch_confidence(scores: list, sequences) -> list[float]:
    """
    Compute confidence for every item in a batch.

    Args:
        scores: list of (batch, vocab) tensors
        sequences: (batch, seq_len) tensor

    Returns:
        list of floats, length = batch_size
    """
    try:
        import torch
        import torch.nn.functional as F

        batch_size = sequences.shape[0]
        results = []

        for b in range(batch_size):
            log_probs: list[float] = []
            for step_scores in scores:
                # step_scores: (batch, vocab)
                if step_scores.dim() == 2:
                    row = step_scores[b]
                else:
                    row = step_scores
                step_idx = len(log_probs)
                token_id = sequences[b, step_idx + 1]
                lsm = F.log_softmax(row.float(), dim=-1)
                log_probs.append(lsm[token_id].item())

            if log_probs:
                mean_lp = sum(log_probs) / len(log_probs)
                results.append(math.exp(max(mean_lp, -5.0)))
            else:
                results.append(0.0)

        return results
    except Exception as e:
        logger.warning(f"Batch confidence failed: {e}")
        return [0.5] * (sequences.shape[0] if hasattr(sequences, "shape") else 1)


def confidence_level(score: float) -> str:
    """Map numeric confidence to Green/Amber/Red label."""
    from backend.config import CONFIDENCE_GREEN, CONFIDENCE_AMBER
    if score >= CONFIDENCE_GREEN:
        return "green"
    if score >= CONFIDENCE_AMBER:
        return "amber"
    return "red"


def avg_confidence(scores: list[float]) -> float:
    if not scores:
        return 0.0
    return sum(scores) / len(scores)
