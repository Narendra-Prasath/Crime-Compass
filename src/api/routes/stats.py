"""
CRIME DNA — Dataset Statistics Endpoints
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from src.api.schemas import DatasetStatsResponse
from src.api.state import state

router = APIRouter(tags=["Dataset Statistics"])


@router.get(
    "/stats",
    response_model=DatasetStatsResponse,
    summary="Corpus & Pipeline Statistics",
    description="Returns aggregate dataset statistics, dimensionality reductions, feature taxonomy breakdown, and cluster counts."
)
@router.get(
    "/dataset-stats",
    response_model=DatasetStatsResponse,
    summary="Corpus & Pipeline Statistics (Alias)",
    include_in_schema=False
)
async def get_dataset_stats() -> DatasetStatsResponse:
    cm = state.cleaning_metadata
    an = state.anomaly_metadata

    raw_cols = cm.get("initial_dimensions", {}).get("columns", 210)
    cleaned_cols = cm.get("final_dimensions", {}).get("columns", 196)
    taxonomy = cm.get("feature_taxonomy_counts", {
        "temporal_features": 7,
        "behavioral_offense_features": 15,
        "victimology_demographics": 11,
        "offender_demographics": 11,
        "weapon_violence_features": 3,
        "property_contraband_features": 13,
        "environmental_geographic_features": 128,
        "post_incident_outcomes": 6
    })

    tier_counts = an.get("tier_counts", {
        "Standard Behavioral Pattern": 209629,
        "Moderate Behavioral Novelty": 8827,
        "High Behavioral Outlier": 2207
    })

    return DatasetStatsResponse(
        dataset_name="Crime Compass Master Behavioral Corpus",
        reference_dataset_source="Historical reference dataset: Alabama, USA, 2024 (FBI NIBRS)",
        total_incidents=len(state.incident_ids),
        raw_columns_count=raw_cols,
        cleaned_features_count=cleaned_cols,
        behavioral_dna_features_count=len(state.feature_names),
        feature_taxonomy_counts=taxonomy,
        behavioral_groups_count=len(state.feature_groups),
        clusters_count=len(state.cluster_profiles),
        cross_crime_patterns_count=len(state.cross_crime_patterns),
        novelty_tier_counts=tier_counts
    )
