"""
CRIME DNA — Analysis Record Repository Service

Manages immutable, structured analysis records for multi-user / multi-incident analyses.

STRICT CONSTRAINTS & COMPLIANCE:
1. Data Minimization: Stores ONLY behavioral attributes, DNA vectors, and analytical summaries.
2. Privacy & Zero PII: Strictly excludes personal identifiable information (no names, phones,
   email addresses, personal street addresses, or individual identifiers).
3. Collision-Resistant Unique Analysis IDs: Each analysis record possesses a unique Analysis ID.
4. Independent User Scoping: Multi-user support allowing User A, User B, User C to maintain
   independent, queryable incident analysis histories while sharing the same historical ML models.
5. No Model Retraining: Analysis records are purely analytical audit records and never trigger
   model retraining.
"""

import json
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("CRIME_DNA_ANALYSIS_RECORD_SERVICE")

RECORDS_DIR = Path("data/analysis_records")
DB_PATH = RECORDS_DIR / "analysis_records.db"


class AnalysisRecordService:
    """
    Persistent repository for clean, privacy-preserving incident analysis records.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Initializes records directory and SQLite table."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_records (
                    analysis_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    scenario_title TEXT,
                    input_summary TEXT NOT NULL,
                    behavioral_dna TEXT NOT NULL,
                    similarity_summary TEXT NOT NULL,
                    pattern_summary TEXT NOT NULL,
                    novelty_summary TEXT NOT NULL,
                    record_json TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rec_user ON analysis_records(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rec_created ON analysis_records(created_at)")
            conn.commit()

    def save_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves a clean analysis record to persistent storage.
        """
        analysis_id = str(record["analysis_id"]).strip()
        user_id = str(record.get("user_id", "user_anon")).strip()
        created_at = str(record.get("timestamp") or datetime.now(timezone.utc).isoformat())
        
        input_summary = record.get("input_summary", {})
        scenario_title = str(input_summary.get("scenario_title", "Simulated Incident Case"))
        
        behavioral_dna = record.get("behavioral_dna", {})
        similarity_summary = record.get("similarity_summary", {})
        pattern_summary = record.get("pattern_summary", {})
        novelty_summary = record.get("novelty_summary", {})

        record_json = json.dumps(record, ensure_ascii=False)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_records (
                    analysis_id,
                    user_id,
                    created_at,
                    scenario_title,
                    input_summary,
                    behavioral_dna,
                    similarity_summary,
                    pattern_summary,
                    novelty_summary,
                    record_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                user_id,
                created_at,
                scenario_title,
                json.dumps(input_summary, ensure_ascii=False),
                json.dumps(behavioral_dna, ensure_ascii=False),
                json.dumps(similarity_summary, ensure_ascii=False),
                json.dumps(pattern_summary, ensure_ascii=False),
                json.dumps(novelty_summary, ensure_ascii=False),
                record_json
            ))
            conn.commit()

        logger.debug(f"Persisted clean analysis record {analysis_id} for user {user_id}")
        return record

    def get_record(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a clean analysis record by its unique Analysis ID.
        """
        clean_id = str(analysis_id).strip()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT record_json FROM analysis_records WHERE analysis_id = ?",
                (clean_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            try:
                return json.loads(row["record_json"])
            except Exception as e:
                logger.error(f"Failed to parse record_json for {clean_id}: {e}")
                return None

    def list_records(
        self,
        user_id: Optional[str] = None,
        search: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Lists analysis records, optionally filtered by user_id, search query, or crime category, with pagination.
        """
        limit = max(1, min(limit, 200))
        offset = max(0, offset)

        conditions = []
        params = []

        if user_id:
            clean_uid = str(user_id).strip()
            conditions.append("user_id = ?")
            params.append(clean_uid)

        if category and category.strip() and category.strip().lower() != "all":
            clean_cat = category.strip().lower()
            conditions.append("(LOWER(input_summary) LIKE ? OR LOWER(scenario_title) LIKE ?)")
            params.append(f"%{clean_cat}%")
            params.append(f"%{clean_cat}%")

        if search and search.strip():
            clean_search = f"%{search.strip().lower()}%"
            conditions.append("""
                (LOWER(analysis_id) LIKE ?
                 OR LOWER(scenario_title) LIKE ?
                 OR LOWER(input_summary) LIKE ?
                 OR LOWER(pattern_summary) LIKE ?)
            """)
            params.extend([clean_search, clean_search, clean_search, clean_search])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Count total matching
            count_sql = f"SELECT COUNT(*) as total FROM analysis_records {where_clause}"
            cursor.execute(count_sql, tuple(params))
            total = cursor.fetchone()["total"]

            # Fetch page records
            select_sql = f"""
                SELECT record_json FROM analysis_records
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(select_sql, tuple(params + [limit, offset]))
            rows = cursor.fetchall()

        records = []
        for r in rows:
            try:
                records.append(json.loads(r["record_json"]))
            except Exception:
                continue

        return {
            "total_count": total,
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
            "records": records
        }

    def delete_record(self, analysis_id: str, user_id: Optional[str] = None) -> bool:
        """
        Deletes a clean analysis record by Analysis ID, with optional user scoping.
        """
        clean_id = str(analysis_id).strip()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute(
                    "DELETE FROM analysis_records WHERE analysis_id = ? AND user_id = ?",
                    (clean_id, str(user_id).strip())
                )
            else:
                cursor.execute(
                    "DELETE FROM analysis_records WHERE analysis_id = ?",
                    (clean_id,)
                )
            conn.commit()
            deleted = cursor.rowcount > 0

        if deleted:
            logger.info(f"Deleted analysis record {clean_id}")
        return deleted

    def count_records(self, user_id: Optional[str] = None) -> int:
        """Returns total records count, optionally filtered by user_id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM analysis_records WHERE user_id = ?",
                    (str(user_id).strip(),)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM analysis_records")
            return cursor.fetchone()[0]

    def clear_records(self) -> None:
        """Purges all records (used primarily for test isolation)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM analysis_records")
            conn.commit()


# Global singleton instance
analysis_record_service = AnalysisRecordService()
