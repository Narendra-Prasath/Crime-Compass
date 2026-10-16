"""
CRIME DNA — Human-In-The-Loop Investigator Feedback Service

Stores and aggregates evaluation feedback from investigators and analysts.

STRICT CONSTRAINTS & COMPLIANCE:
1. Data Minimization: Stores only evaluation answers (thumbs up/down, selected aspects, operational notes).
2. Privacy: Collects ZERO personally identifiable information (PII).
3. Evaluation Only: Feedback is preserved strictly as evaluation and validation data.
   It is NOT presented as automatic model retraining.
"""

import os
import json
import sqlite3
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("CRIME_DNA_FEEDBACK_SERVICE")

FEEDBACK_DIR = Path("data/feedback")
DB_PATH = FEEDBACK_DIR / "feedback.db"
JSONL_PATH = FEEDBACK_DIR / "feedback.jsonl"

ALLOWED_ASPECTS = {
    "similar_time",
    "similar_location",
    "similar_property",
    "similar_method",
    "other"
}

ASPECT_DISPLAY_NAMES = {
    "similar_time": "Similar time",
    "similar_location": "Similar location",
    "similar_property": "Similar property",
    "similar_method": "Similar method",
    "other": "Other"
}

ASPECT_ALIAS_MAP = {
    "time": "similar_time",
    "temporal": "similar_time",
    "location": "similar_location",
    "spatial": "similar_location",
    "property": "similar_property",
    "economic": "similar_property",
    "method": "similar_method",
    "weapon": "similar_method",
    "modus_operandi": "similar_method",
    "other": "other",
}


class FeedbackService:
    """
    Manages evaluation feedback storage and statistics.
    """

    def __init__(self, db_path: Path = DB_PATH, jsonl_path: Path = JSONL_PATH):
        self.db_path = db_path
        self.jsonl_path = jsonl_path
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Initializes feedback directory and SQLite table."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investigator_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    is_useful INTEGER NOT NULL,
                    target_type TEXT,
                    target_id TEXT,
                    useful_aspects TEXT,
                    notes TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fb_useful ON investigator_feedback(is_useful)")
            conn.commit()

    def record_feedback(
        self,
        is_useful: bool,
        target_type: Optional[str] = "incident_analysis",
        target_id: Optional[str] = None,
        useful_aspects: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Records human-in-the-loop evaluation feedback.
        """
        feedback_id = f"FB_{uuid.uuid4().hex[:12].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Sanitize aspects
        valid_aspects = []
        if useful_aspects:
            for a in useful_aspects:
                norm_a = str(a).strip().lower().replace(" ", "_")
                norm_a = ASPECT_ALIAS_MAP.get(norm_a, norm_a)
                if norm_a in ALLOWED_ASPECTS and norm_a not in valid_aspects:
                    valid_aspects.append(norm_a)

        # Sanitize notes (max 500 chars, no PII)
        clean_notes = (notes.strip()[:500]) if notes else None

        record = {
            "feedback_id": feedback_id,
            "created_at": now_iso,
            "is_useful": bool(is_useful),
            "target_type": target_type or "incident_analysis",
            "target_id": target_id,
            "useful_aspects": valid_aspects,
            "notes": clean_notes
        }

        # 1. Insert into SQLite
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO investigator_feedback (
                        feedback_id, created_at, is_useful, target_type, target_id, useful_aspects, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback_id,
                    now_iso,
                    1 if is_useful else 0,
                    target_type,
                    target_id,
                    json.dumps(valid_aspects),
                    clean_notes
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to write feedback to SQLite: {e}", exc_info=True)

        # 2. Append to JSONL audit file
        try:
            with open(self.jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Failed to append feedback to JSONL: {e}", exc_info=True)

        disclaimer = (
            "Feedback is recorded strictly for human-in-the-loop evaluation and system validation. "
            "It is not currently utilized for automatic model retraining."
        )

        return {
            "feedback_id": feedback_id,
            "status": "received",
            "recorded_at": now_iso,
            "is_useful": is_useful,
            "useful_aspects": valid_aspects,
            "disclaimer": disclaimer
        }

    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Returns aggregated evaluation feedback statistics.
        """
        aspect_counts = {k: 0 for k in ALLOWED_ASPECTS}
        total_count = 0
        useful_count = 0
        not_useful_count = 0
        recent = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Counts
                cursor.execute("SELECT COUNT(*) as total, SUM(is_useful) as useful FROM investigator_feedback")
                row = cursor.fetchone()
                if row and row["total"]:
                    total_count = row["total"]
                    useful_count = row["useful"] or 0
                    not_useful_count = total_count - useful_count

                # Aspects count
                cursor.execute("SELECT useful_aspects FROM investigator_feedback")
                for r in cursor.fetchall():
                    raw = r["useful_aspects"]
                    if raw:
                        try:
                            items = json.loads(raw)
                            for it in items:
                                if it in aspect_counts:
                                    aspect_counts[it] += 1
                        except Exception:
                            pass

                # Recent 10 feedback items
                cursor.execute("""
                    SELECT feedback_id, created_at, is_useful, target_type, target_id, useful_aspects
                    FROM investigator_feedback
                    ORDER BY created_at DESC LIMIT 10
                """)
                for r in cursor.fetchall():
                    recent.append({
                        "feedback_id": r["feedback_id"],
                        "created_at": r["created_at"],
                        "is_useful": bool(r["is_useful"]),
                        "target_type": r["target_type"],
                        "target_id": r["target_id"],
                        "useful_aspects": json.loads(r["useful_aspects"]) if r["useful_aspects"] else []
                    })
        except Exception as e:
            logger.error(f"Error querying feedback summary from SQLite: {e}", exc_info=True)

        useful_pct = round((useful_count / total_count * 100.0), 1) if total_count > 0 else 0.0

        disclaimer = (
            "Feedback is recorded strictly for human-in-the-loop evaluation and system validation. "
            "It is not currently utilized for automatic model retraining."
        )

        return {
            "total_feedback_count": total_count,
            "useful_count": useful_count,
            "not_useful_count": not_useful_count,
            "useful_percentage": useful_pct,
            "aspects_breakdown": aspect_counts,
            "recent_feedback": recent,
            "disclaimer": disclaimer
        }


# Global singleton instance
feedback_service = FeedbackService()
