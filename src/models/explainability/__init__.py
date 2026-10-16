"""
CRIME DNA — Explainable AI (XAI) & Behavioral Attribution Package
"""

from src.models.explainability.config import (
    EXPLAINABILITY_CONFIG,
    GROUP_DISPLAY_NAMES,
    GROUP_NOUN_PHRASES
)
from src.models.explainability.explainer import (
    BehavioralSimilarityExplainer,
    decompose_behavioral_similarity,
    synthesize_plain_english_explanation
)

__all__ = [
    "EXPLAINABILITY_CONFIG",
    "GROUP_DISPLAY_NAMES",
    "GROUP_NOUN_PHRASES",
    "BehavioralSimilarityExplainer",
    "decompose_behavioral_similarity",
    "synthesize_plain_english_explanation"
]
