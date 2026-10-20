"""
CRIME DNA — Phase 11: Application State & Model Registry

Thread-safe in-memory cache and model registry loaded once during FastAPI lifespan.
Ensures zero retraining, zero repetitive disk reads, and sub-millisecond response times.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from src.api.config import (
    SIMILARITY_DIR,
    CLUSTERS_DIR,
    CROSS_CRIME_DIR,
    EVOLUTION_DIR,
    ANOMALY_DIR,
    EXPLAINABILITY_DIR,
    CLEANED_CSV_PATH,
    DNA_FEATURES_CSV_PATH,
    CLEANING_METADATA_PATH,
    DNA_METADATA_PATH
)
from src.features.config import (
    FEATURE_GROUPS,
    FEATURE_DESCRIPTIONS,
    FEATURE_FRIENDLY_NAMES,
    FEATURE_BEHAVIORAL_DOMAINS,
    DOMAIN_LABELS,
    FEATURE_SALIENCE_WEIGHTS
)
from src.models.similarity.engine import BehavioralSimilarityEngine
from src.models.explainability.explainer import BehavioralSimilarityExplainer
from src.models.clustering.engine import BehavioralClusterer

logger = logging.getLogger("CRIME_DNA_API")


class ApplicationState:
    """
    Singleton holding preloaded ML models, metadata, feature matrices,
    and fast in-memory incident lookup registries.
    """

    def __init__(self):
        self.is_ready: bool = False
        self.startup_timestamp: float = 0.0

        # Component readiness flags
        self.components_status: Dict[str, str] = {
            "similarity_engine": "offline",
            "clustering": "offline",
            "cross_crime": "offline",
            "evolution": "offline",
            "anomaly_detection": "offline",
            "explainability": "offline",
            "incident_registry": "offline"
        }

        # Core ML Engines
        self.similarity_engine: Optional[BehavioralSimilarityEngine] = None
        self.explainer: Optional[BehavioralSimilarityExplainer] = None
        self.clusterer: Optional[BehavioralClusterer] = None
        self.isolation_forest: Optional[Any] = None

        # Data and Model Artifacts
        self.cluster_profiles: Dict[str, Any] = {}
        self.cluster_metadata: Dict[str, Any] = {}
        self.cross_crime_patterns: Dict[str, Any] = {}
        self.cross_crime_summary: Dict[str, Any] = {}
        self.timeline_dashboard: Dict[str, Any] = {}
        self.significant_shifts: List[Dict[str, Any]] = []
        self.anomaly_metadata: Dict[str, Any] = {}
        self.top_outliers: List[Dict[str, Any]] = []
        self.outliers_by_id: Dict[str, Dict[str, Any]] = {}
        self.explanation_metadata: Dict[str, Any] = {}
        self.sample_explanations: List[Dict[str, Any]] = []
        self.cleaning_metadata: Dict[str, Any] = {}
        self.dna_metadata: Dict[str, Any] = {}

        # High-Speed Incident Registry
        self.incident_ids: List[str] = []
        self.id_to_idx: Dict[str, int] = {}
        self.feature_names: List[str] = []
        self.normalized_matrix: Optional[np.ndarray] = None
        self.feature_groups: Dict[str, List[str]] = FEATURE_GROUPS
        self.feature_group_indices: Dict[str, List[int]] = {}
        self.group_slices: Dict[str, Tuple[int, int]] = {}
        self.core_df: Optional[pd.DataFrame] = None
        self.clusters_df: Optional[pd.DataFrame] = None
        self.anomaly_df: Optional[pd.DataFrame] = None
        self.core_records: Optional[List[Dict[str, Any]]] = None
        self.clusters_records: Optional[List[Dict[str, Any]]] = None
        self.anomaly_records: Optional[List[Dict[str, Any]]] = None
        self._core_cols: Optional[Dict[str, np.ndarray]] = None
        self._cluster_cols: Optional[Dict[str, np.ndarray]] = None
        self._anomaly_cols: Optional[Dict[str, np.ndarray]] = None
        self._profile_cache: Dict[str, Dict[str, Any]] = {}

    def load_all(self) -> None:
        """
        Loads all required ML models and datasets into memory synchronously on application startup.
        """
        start_time = time.time()
        logger.info("Initializing CRIME DNA Application State & Model Registry...")

        # 1. Similarity Engine
        try:
            logger.info("Loading Similarity Engine...")
            self.similarity_engine = BehavioralSimilarityEngine().load(str(SIMILARITY_DIR))
            self.incident_ids = self.similarity_engine.incident_ids
            self.id_to_idx = self.similarity_engine.id_to_idx
            self.feature_names = self.similarity_engine.feature_names
            self.normalized_matrix = self.similarity_engine.features_norm

            # Precompute feature group indices and slices for fast subprofile access
            self.feature_group_indices = {
                grp_name: [self.feature_names.index(col) for col in cols if col in self.feature_names]
                for grp_name, cols in self.feature_groups.items()
            }
            self.group_slices = {
                grp_name: (min(idxs), max(idxs) + 1)
                for grp_name, idxs in self.feature_group_indices.items()
                if idxs
            }
            self.components_status["similarity_engine"] = "online"
        except Exception as e:
            logger.error(f"Failed to load Similarity Engine: {e}", exc_info=True)
            self.components_status["similarity_engine"] = f"error: {str(e)}"

        # 2. Clusters
        try:
            logger.info("Loading Cluster Profiles and Metadata...")
            profiles_path = CLUSTERS_DIR / "cluster_profiles.json"
            meta_path = CLUSTERS_DIR / "cluster_metadata.json"
            if profiles_path.exists():
                with open(profiles_path) as f:
                    self.cluster_profiles = json.load(f)
            if meta_path.exists():
                with open(meta_path) as f:
                    self.cluster_metadata = json.load(f)
            if (CLUSTERS_DIR / "kmeans_model.joblib").exists():
                self.clusterer = BehavioralClusterer().load(str(CLUSTERS_DIR))
            self.components_status["clustering"] = "online"
        except Exception as e:
            logger.error(f"Failed to load Clustering artifacts: {e}", exc_info=True)
            self.components_status["clustering"] = f"error: {str(e)}"

        # 3. Cross Crime Patterns
        try:
            logger.info("Loading Cross-Crime Patterns...")
            cc_path = CROSS_CRIME_DIR / "cross_crime_patterns.json"
            sum_path = CROSS_CRIME_DIR / "cross_crime_summary.json"
            if cc_path.exists():
                with open(cc_path) as f:
                    self.cross_crime_patterns = json.load(f)
            if sum_path.exists():
                with open(sum_path) as f:
                    self.cross_crime_summary = json.load(f)
            self.components_status["cross_crime"] = "online"
        except Exception as e:
            logger.error(f"Failed to load Cross-Crime artifacts: {e}", exc_info=True)
            self.components_status["cross_crime"] = f"error: {str(e)}"

        # 4. Evolution Timeline & Shifts
        try:
            logger.info("Loading Behavioral Evolution Timeline...")
            timeline_path = EVOLUTION_DIR / "timeline_dashboard.json"
            shifts_path = EVOLUTION_DIR / "significant_shifts.json"
            if timeline_path.exists():
                with open(timeline_path) as f:
                    self.timeline_dashboard = json.load(f)
            if shifts_path.exists():
                with open(shifts_path) as f:
                    self.significant_shifts = json.load(f)
            self.components_status["evolution"] = "online"
        except Exception as e:
            logger.error(f"Failed to load Evolution artifacts: {e}", exc_info=True)
            self.components_status["evolution"] = f"error: {str(e)}"

        # 5. Anomaly Detection
        try:
            logger.info("Loading Anomaly & Novelty Artifacts...")
            an_meta_path = ANOMALY_DIR / "anomaly_metadata.json"
            outliers_path = ANOMALY_DIR / "top_behavioral_outliers.json"
            if an_meta_path.exists():
                with open(an_meta_path) as f:
                    self.anomaly_metadata = json.load(f)
            if outliers_path.exists():
                with open(outliers_path) as f:
                    self.top_outliers = json.load(f)
                self.outliers_by_id = {item["incident_id"]: item for item in self.top_outliers}
            if (ANOMALY_DIR / "isolation_forest.joblib").exists():
                self.isolation_forest = joblib.load(ANOMALY_DIR / "isolation_forest.joblib")
            self.components_status["anomaly_detection"] = "online"
        except Exception as e:
            logger.error(f"Failed to load Anomaly artifacts: {e}", exc_info=True)
            self.components_status["anomaly_detection"] = f"error: {str(e)}"

        # 6. Metadata & High-Speed Incident Registries (Memory-Optimized Direct Arrays)
        try:
            logger.info("Loading Dataset Metadata & Incident Registries (compact dtypes)...")
            if CLEANING_METADATA_PATH.exists():
                with open(CLEANING_METADATA_PATH) as f:
                    self.cleaning_metadata = json.load(f)
            if DNA_METADATA_PATH.exists():
                with open(DNA_METADATA_PATH) as f:
                    self.dna_metadata = json.load(f)

            # Fast Incident Core Columns using compact C-native dtypes (int8/int16/float32)
            core_dtypes = {
                "incident_hour": "int8",
                "incident_month": "int8",
                "incident_weekday": "int8",
                "is_weekend": "int8",
                "is_night": "int8",
                "population": "float32",
                "offense_count": "int16",
                "victim_count": "int16",
                "offender_count": "int16",
                "property_value": "float32",
                "has_weapon": "int8",
                "has_injury": "int8",
                "has_property": "int8",
                "has_drug": "int8",
                "has_arrest": "int8",
                "has_relationship": "int8",
                "crime_against_person": "int8",
                "crime_against_property": "int8",
                "crime_against_society": "int8",
                "crime_against_person___property": "int8",
                "crime_against_person___society": "int8",
                "crime_against_property___society": "int8",
                "crime_against_person___property___society": "int8"
            }
            core_cols = list(core_dtypes.keys())
            if CLEANED_CSV_PATH.exists():
                self.core_df = pd.read_csv(CLEANED_CSV_PATH, usecols=core_cols, dtype=core_dtypes)
                self._core_cols = {col: self.core_df[col].values for col in core_cols}

            cl_labels_path = CLUSTERS_DIR / "incident_cluster_labels.csv"
            if cl_labels_path.exists():
                cl_dtypes = {"cluster_id": "int8", "cluster_name": "category"}
                self.clusters_df = pd.read_csv(cl_labels_path, usecols=["cluster_id", "cluster_name"], dtype=cl_dtypes)
                self._cluster_cols = {
                    "cluster_id": self.clusters_df["cluster_id"].values,
                    "cluster_name": self.clusters_df["cluster_name"].values
                }

            an_scores_path = ANOMALY_DIR / "incident_anomaly_scores.csv"
            if an_scores_path.exists():
                an_dtypes = {
                    "novelty_score": "float32",
                    "novelty_tier": "category",
                    "nearest_cluster_id": "int8",
                    "nearest_cluster_name": "category",
                    "distance_to_nearest_cluster": "float32"
                }
                self.anomaly_df = pd.read_csv(an_scores_path, usecols=list(an_dtypes.keys()), dtype=an_dtypes)
                self._anomaly_cols = {col: self.anomaly_df[col].values for col in an_dtypes}

            self.components_status["incident_registry"] = "online"
        except Exception as e:
            logger.error(f"Failed to load Incident Registries: {e}", exc_info=True)
            self.components_status["incident_registry"] = f"error: {str(e)}"

        # 7. Explainability Engine (re-using preloaded similarity matrix & shared core_df)
        try:
            logger.info("Loading Explainability Engine (shared memory)...")
            self.explainer = BehavioralSimilarityExplainer().load_data(
                features_path=str(DNA_FEATURES_CSV_PATH),
                cleaned_path=str(CLEANED_CSV_PATH),
                normalized_matrix=self.normalized_matrix,
                incident_ids=self.incident_ids,
                feature_names=self.feature_names,
                cleaned_df=self.core_df
            )
            exp_meta_path = EXPLAINABILITY_DIR / "explanation_metadata.json"
            sample_exp_path = EXPLAINABILITY_DIR / "sample_explanations.json"
            if exp_meta_path.exists():
                with open(exp_meta_path) as f:
                    self.explanation_metadata = json.load(f)
            if sample_exp_path.exists():
                with open(sample_exp_path) as f:
                    self.sample_explanations = json.load(f)
            self.components_status["explainability"] = "online"
        except Exception as e:
            logger.error(f"Failed to load Explainability Engine: {e}", exc_info=True)
            self.components_status["explainability"] = f"error: {str(e)}"

        self.startup_timestamp = time.time()
        self.is_ready = True
        elapsed = time.time() - start_time
        logger.info(f"CRIME DNA Application State successfully initialized in {elapsed:.3f}s.")

    def get_incident_index(self, incident_id: str) -> Optional[int]:
        """Returns row index for incident_id or None if not found."""
        return self.id_to_idx.get(incident_id)

    def get_incident_profile(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves unified incident context, cluster membership, and novelty tier.
        Fast in-memory cache and direct dictionary indexing.
        """
        if incident_id in self._profile_cache:
            return self._profile_cache[incident_id]

        idx = self.get_incident_index(incident_id)
        if idx is None:
            return None

        # Core context
        core_data = {}
        if self._core_cols is not None:
            core_data = {
                "incident_hour": int(self._core_cols["incident_hour"][idx]),
                "incident_month": int(self._core_cols["incident_month"][idx]),
                "incident_weekday": int(self._core_cols["incident_weekday"][idx]),
                "is_weekend": bool(self._core_cols["is_weekend"][idx]),
                "is_night": bool(self._core_cols["is_night"][idx]),
                "population": float(self._core_cols["population"][idx]),
                "offense_count": int(self._core_cols["offense_count"][idx]),
                "victim_count": int(self._core_cols["victim_count"][idx]),
                "offender_count": int(self._core_cols["offender_count"][idx]),
                "property_value": float(self._core_cols["property_value"][idx]),
                "has_weapon": bool(self._core_cols["has_weapon"][idx]),
                "has_injury": bool(self._core_cols["has_injury"][idx]),
                "has_property": bool(self._core_cols["has_property"][idx]),
                "has_drug": bool(self._core_cols["has_drug"][idx]),
                "has_arrest": bool(self._core_cols["has_arrest"][idx]),
                "has_relationship": bool(self._core_cols["has_relationship"][idx]),
                "crime_against_person": bool(self._core_cols["crime_against_person"][idx]),
                "crime_against_property": bool(self._core_cols["crime_against_property"][idx]),
                "crime_against_society": bool(self._core_cols["crime_against_society"][idx]),
                "crime_against_person_property": bool(self._core_cols["crime_against_person___property"][idx]),
                "crime_against_person_society": bool(self._core_cols["crime_against_person___society"][idx]),
                "crime_against_property_society": bool(self._core_cols["crime_against_property___society"][idx]),
                "crime_against_person_property_society": bool(self._core_cols["crime_against_person___property___society"][idx]),
            }
        elif self.core_records is not None and idx < len(self.core_records):
            core_row = self.core_records[idx]
            core_data = {
                "incident_hour": int(core_row.get("incident_hour", 0)),
                "incident_month": int(core_row.get("incident_month", 1)),
                "incident_weekday": int(core_row.get("incident_weekday", 1)),
                "is_weekend": bool(core_row.get("is_weekend", 0)),
                "is_night": bool(core_row.get("is_night", 0)),
                "population": float(core_row.get("population", 0.0)),
                "offense_count": int(core_row.get("offense_count", 1)),
                "victim_count": int(core_row.get("victim_count", 0)),
                "offender_count": int(core_row.get("offender_count", 0)),
                "property_value": float(core_row.get("property_value", 0.0)),
                "has_weapon": bool(core_row.get("has_weapon", 0)),
                "has_injury": bool(core_row.get("has_injury", 0)),
                "has_property": bool(core_row.get("has_property", 0)),
                "has_drug": bool(core_row.get("has_drug", 0)),
                "has_arrest": bool(core_row.get("has_arrest", 0)),
                "has_relationship": bool(core_row.get("has_relationship", 0)),
                "crime_against_person": bool(core_row.get("crime_against_person", 0)),
                "crime_against_property": bool(core_row.get("crime_against_property", 0)),
                "crime_against_society": bool(core_row.get("crime_against_society", 0)),
                "crime_against_person_property": bool(core_row.get("crime_against_person___property", 0)),
                "crime_against_person_society": bool(core_row.get("crime_against_person___society", 0)),
                "crime_against_property_society": bool(core_row.get("crime_against_property___society", 0)),
                "crime_against_person_property_society": bool(core_row.get("crime_against_person___property___society", 0)),
            }
        elif self.core_df is not None:
            core_row = self.core_df.iloc[idx].to_dict()
            core_data = {
                "incident_hour": int(core_row.get("incident_hour", 0)),
                "incident_month": int(core_row.get("incident_month", 1)),
                "incident_weekday": int(core_row.get("incident_weekday", 1)),
                "is_weekend": bool(core_row.get("is_weekend", 0)),
                "is_night": bool(core_row.get("is_night", 0)),
                "population": float(core_row.get("population", 0.0)),
                "offense_count": int(core_row.get("offense_count", 1)),
                "victim_count": int(core_row.get("victim_count", 0)),
                "offender_count": int(core_row.get("offender_count", 0)),
                "property_value": float(core_row.get("property_value", 0.0)),
                "has_weapon": bool(core_row.get("has_weapon", 0)),
                "has_injury": bool(core_row.get("has_injury", 0)),
                "has_property": bool(core_row.get("has_property", 0)),
                "has_drug": bool(core_row.get("has_drug", 0)),
                "has_arrest": bool(core_row.get("has_arrest", 0)),
                "has_relationship": bool(core_row.get("has_relationship", 0)),
                "crime_against_person": bool(core_row.get("crime_against_person", 0)),
                "crime_against_property": bool(core_row.get("crime_against_property", 0)),
                "crime_against_society": bool(core_row.get("crime_against_society", 0)),
                "crime_against_person_property": bool(core_row.get("crime_against_person___property", 0)),
                "crime_against_person_society": bool(core_row.get("crime_against_person___society", 0)),
                "crime_against_property_society": bool(core_row.get("crime_against_property___society", 0)),
                "crime_against_person_property_society": bool(core_row.get("crime_against_person___property___society", 0)),
            }

        # Primary crime macro category
        if core_data.get("crime_against_person_property"):
            macro_crime = "Person & Property Crime (Robbery/Extortion)"
        elif core_data.get("crime_against_person_society"):
            macro_crime = "Person & Society Crime"
        elif core_data.get("crime_against_property_society"):
            macro_crime = "Property & Society Crime"
        elif core_data.get("crime_against_person_property_society"):
            macro_crime = "Multi-Category Offense"
        elif core_data.get("crime_against_person"):
            macro_crime = "Crimes Against Persons (Assault/Violence)"
        elif core_data.get("crime_against_property"):
            macro_crime = "Property Crime (Theft/Burglary)"
        elif core_data.get("crime_against_society"):
            macro_crime = "Crimes Against Society (Narcotics/Weapons)"
        else:
            macro_crime = "Other Offense"
        core_data["primary_crime_category"] = macro_crime

        # Cluster assignment
        cluster_info = {}
        if self._cluster_cols is not None:
            cluster_info = {
                "cluster_id": int(self._cluster_cols["cluster_id"][idx]),
                "cluster_name": str(self._cluster_cols["cluster_name"][idx])
            }
        elif self.clusters_records is not None and idx < len(self.clusters_records):
            cl_row = self.clusters_records[idx]
            cluster_info = {
                "cluster_id": int(cl_row.get("cluster_id", -1)),
                "cluster_name": str(cl_row.get("cluster_name", "Unknown Cluster"))
            }
        elif self.clusters_df is not None:
            cl_row = self.clusters_df.iloc[idx].to_dict()
            cluster_info = {
                "cluster_id": int(cl_row.get("cluster_id", -1)),
                "cluster_name": str(cl_row.get("cluster_name", "Unknown Cluster"))
            }

        # Novelty / Anomaly assignment
        novelty_info = {}
        if self._anomaly_cols is not None:
            novelty_info = {
                "novelty_score": float(self._anomaly_cols["novelty_score"][idx]),
                "novelty_tier": str(self._anomaly_cols["novelty_tier"][idx]),
                "nearest_cluster_id": int(self._anomaly_cols["nearest_cluster_id"][idx]),
                "nearest_cluster_name": str(self._anomaly_cols["nearest_cluster_name"][idx]),
                "distance_to_nearest_cluster": float(self._anomaly_cols["distance_to_nearest_cluster"][idx])
            }
        elif self.anomaly_records is not None and idx < len(self.anomaly_records):
            an_row = self.anomaly_records[idx]
            novelty_info = {
                "novelty_score": float(an_row.get("novelty_score", 0.0)),
                "novelty_tier": str(an_row.get("novelty_tier", "Standard Behavioral Pattern")),
                "nearest_cluster_id": int(an_row.get("nearest_cluster_id", -1)),
                "nearest_cluster_name": str(an_row.get("nearest_cluster_name", "")),
                "distance_to_nearest_cluster": float(an_row.get("distance_to_nearest_cluster", 0.0))
            }
        elif self.anomaly_df is not None:
            an_row = self.anomaly_df.iloc[idx].to_dict()
            novelty_info = {
                "novelty_score": float(an_row.get("novelty_score", 0.0)),
                "novelty_tier": str(an_row.get("novelty_tier", "Standard Behavioral Pattern")),
                "nearest_cluster_id": int(an_row.get("nearest_cluster_id", -1)),
                "nearest_cluster_name": str(an_row.get("nearest_cluster_name", "")),
                "distance_to_nearest_cluster": float(an_row.get("distance_to_nearest_cluster", 0.0))
            }

        profile = {
            "incident_id": incident_id,
            "cluster": cluster_info,
            "novelty": novelty_info,
            "context": core_data
        }
        self._profile_cache[incident_id] = profile
        return profile

    def get_incident_dna_vector(self, incident_id: str) -> Optional[np.ndarray]:
        """Returns the raw normalized 70D numpy vector for incident_id or None."""
        idx = self.get_incident_index(incident_id)
        if idx is None or self.normalized_matrix is None:
            return None
        return self.normalized_matrix[idx]

    def get_incident_dna(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the 70-dimensional Behavioral DNA vector and subprofile group energies.
        """
        idx = self.get_incident_index(incident_id)
        if idx is None or self.normalized_matrix is None:
            return None

        vec = self.normalized_matrix[idx]
        vector_dict = {
            feat_name: float(vec[i])
            for i, feat_name in enumerate(self.feature_names)
        }

        # Group energies (L2 norm per group) via precomputed indices
        group_energies = {}
        for grp_name, indices in self.feature_group_indices.items():
            if indices:
                sub_vec = vec[indices]
                group_energies[grp_name] = round(float(np.linalg.norm(sub_vec)), 4)

        # Reverse mapping from feature to group
        feat_to_group = {
            col: grp for grp, cols in self.feature_groups.items() for col in cols
        }

        # Top active traits with domain awareness, salience, and balanced tie-breaking
        raw_candidates = []
        for f, v in vector_dict.items():
            if v > 0.001:
                grp = feat_to_group.get(f, "other")
                grp_energy = group_energies.get(grp, 0.0)
                salience = FEATURE_SALIENCE_WEIGHTS.get(f, 1.0)
                raw_candidates.append({
                    "feature": f,
                    "label": FEATURE_FRIENDLY_NAMES.get(f, f.replace("_", " ").title()),
                    "domain": grp,
                    "domain_label": DOMAIN_LABELS.get(grp, grp.replace("_", " ").title()),
                    "value": round(float(v), 4),
                    "energy_share_pct": round(float((v ** 2) * 100.0), 2),
                    "grp_energy": grp_energy,
                    "salience": salience,
                    "description": FEATURE_DESCRIPTIONS.get(f, f)
                })

        # Multi-criteria sort:
        # 1. Coordinate magnitude v (highest normalized components first)
        # 2. Domain energy of the trait's parent group (prioritizing high-activity behavioral domains)
        # 3. Behavioral salience (core MO actions over administrative flags)
        raw_candidates.sort(
            key=lambda x: (round(x["value"], 4), round(x["grp_energy"], 4), x["salience"]),
            reverse=True
        )

        # Balanced selection across domains (at most 3 traits per domain in top 10 if diverse options exist)
        domain_counts: Dict[str, int] = {}
        top_active = []
        overflow = []
        for cand in raw_candidates:
            grp = cand["domain"]
            if domain_counts.get(grp, 0) < 3:
                domain_counts[grp] = domain_counts.get(grp, 0) + 1
                top_active.append(cand)
            else:
                overflow.append(cand)
            if len(top_active) == 10:
                break

        if len(top_active) < 10 and overflow:
            for cand in overflow:
                top_active.append(cand)
                if len(top_active) == 10:
                    break

        for trait in top_active:
            trait.pop("grp_energy", None)
            trait.pop("salience", None)

        return {
            "incident_id": incident_id,
            "vector_dimension": len(self.feature_names),
            "feature_vector": vector_dict,
            "group_energies": group_energies,
            "top_active_traits": top_active
        }


# Global Singleton
state = ApplicationState()
