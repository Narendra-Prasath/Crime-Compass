"""
CRIME DNA — Behavioral Anomaly & Novelty Detection Package
"""

from src.models.anomaly.config import ANOMALY_CONFIG, ANOMALY_TIER_LABELS
from src.models.anomaly.detector import BehavioralAnomalyDetector

__all__ = ["ANOMALY_CONFIG", "ANOMALY_TIER_LABELS", "BehavioralAnomalyDetector"]
