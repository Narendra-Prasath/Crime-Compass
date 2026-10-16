"""
CRIME DNA — Unified Analysis Coordinator (Re-exporting Central Analysis Engine)

Maintains backwards compatibility for src.models.analysis_coordinator
while delegating analysis orchestration to src.services.analysis_engine.
"""

from typing import Dict, Any
from src.services.analysis_engine import CrimeDnaAnalysisEngine, analysis_engine


class AnalysisCoordinator:
    """
    Coordinates multi-perspective behavioral intelligence analysis
    by delegating to the central CrimeDnaAnalysisEngine service.
    """

    def __init__(self):
        self.engine = analysis_engine

    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Delegates analysis to the central CrimeDnaAnalysisEngine."""
        return self.engine.analyze(input_data)


# Global singleton instance
analysis_coordinator = AnalysisCoordinator()

__all__ = ["AnalysisCoordinator", "analysis_coordinator"]
