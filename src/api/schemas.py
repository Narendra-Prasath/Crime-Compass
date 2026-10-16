"""
CRIME DNA — Phase 11: Pydantic API Schemas

Strict data validation and typing models for all incoming requests,
outgoing responses, and nested data structures across all 10 API capabilities.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


# ============================================================================
# 1. Health & System Status
# ============================================================================

class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    api_version: str = Field(..., examples=["1.0.0"])
    uptime_seconds: float = Field(..., examples=[120.45])
    components_status: Dict[str, str] = Field(
        ...,
        examples=[{
            "similarity_engine": "online",
            "clustering": "online",
            "cross_crime": "online",
            "evolution": "online",
            "anomaly_detection": "online",
            "explainability": "online",
            "incident_registry": "online"
        }]
    )
    indexed_incidents: int = Field(..., examples=[220663])
    vector_dimension: int = Field(..., examples=[70])


# ============================================================================
# 2. Dataset Statistics
# ============================================================================

class DatasetStatsResponse(BaseModel):
    dataset_name: str = Field(..., examples=["Crime Compass Master Behavioral Corpus"])
    reference_dataset_source: Optional[str] = Field(
        "Historical reference dataset: Alabama, USA, 2024 (FBI NIBRS)",
        description="Verified source of historical reference corpus"
    )
    total_incidents: int = Field(..., examples=[220663])
    raw_columns_count: int = Field(..., examples=[210])
    cleaned_features_count: int = Field(..., examples=[196])
    behavioral_dna_features_count: int = Field(..., examples=[70])
    feature_taxonomy_counts: Dict[str, int] = Field(
        ...,
        examples=[{
            "temporal_features": 7,
            "behavioral_offense_features": 15,
            "victimology_demographics": 11,
            "offender_demographics": 11,
            "weapon_violence_features": 3,
            "property_contraband_features": 13,
            "environmental_geographic_features": 128,
            "post_incident_outcomes": 6
        }]
    )
    behavioral_groups_count: int = Field(..., examples=[7])
    clusters_count: int = Field(..., examples=[8])
    cross_crime_patterns_count: int = Field(..., examples=[8])
    novelty_tier_counts: Dict[str, int] = Field(
        ...,
        examples=[{
            "Standard Behavioral Pattern": 209630,
            "Moderate Novelty": 8826,
            "High Novelty": 1986,
            "Extreme Outlier": 221
        }]
    )


# ============================================================================
# 3. Incident Lookup
# ============================================================================

class IncidentContext(BaseModel):
    incident_hour: int = Field(..., ge=0, le=23, examples=[22])
    incident_month: int = Field(..., ge=1, le=12, examples=[7])
    incident_weekday: int = Field(..., ge=0, le=6, examples=[5])
    is_weekend: bool = Field(..., examples=[True])
    is_night: bool = Field(..., examples=[True])
    population: float = Field(..., examples=[120000.0])
    offense_count: int = Field(..., examples=[1])
    victim_count: int = Field(..., examples=[1])
    offender_count: int = Field(..., examples=[1])
    property_value: float = Field(..., examples=[250.0])
    has_weapon: bool = Field(..., examples=[True])
    has_injury: bool = Field(..., examples=[False])
    has_property: bool = Field(..., examples=[True])
    has_drug: bool = Field(..., examples=[False])
    has_arrest: bool = Field(..., examples=[True])
    has_relationship: bool = Field(..., examples=[False])
    crime_against_person: bool = Field(..., examples=[False])
    crime_against_property: bool = Field(..., examples=[True])
    crime_against_society: bool = Field(..., examples=[False])
    primary_crime_category: str = Field(..., examples=["Property Crime"])


class IncidentClusterAssignment(BaseModel):
    cluster_id: int = Field(..., examples=[3])
    cluster_name: str = Field(..., examples=["Nocturnal & Weekend Residential/Commercial Burglary"])


class IncidentNoveltyInfo(BaseModel):
    novelty_score: float = Field(..., examples=[0.1824])
    novelty_tier: str = Field(..., examples=["Standard Behavioral Pattern"])
    nearest_cluster_id: int = Field(..., examples=[3])
    nearest_cluster_name: str = Field(..., examples=["Nocturnal & Weekend Residential/Commercial Burglary"])
    distance_to_nearest_cluster: float = Field(..., examples=[0.2941])


class IncidentProfileResponse(BaseModel):
    incident_id: str = Field(..., examples=["INC_136975"])
    cluster: IncidentClusterAssignment
    novelty: IncidentNoveltyInfo
    context: IncidentContext


# ============================================================================
# 4. Behavioral DNA
# ============================================================================

class FeatureTrait(BaseModel):
    feature: str = Field(..., examples=["time_hour_sin"])
    value: float = Field(..., examples=[0.3812])


class BehavioralDNAResponse(BaseModel):
    incident_id: str = Field(..., examples=["INC_136975"])
    vector_dimension: int = Field(..., examples=[70])
    feature_vector: Dict[str, float]
    group_energies: Dict[str, float] = Field(
        ...,
        examples=[{
            "temporal_dynamics": 0.4521,
            "crime_characteristics": 0.5891,
            "location_and_environment": 0.3120,
            "method_and_activity": 0.2541,
            "people_and_demographics": 0.3890,
            "property_and_economics": 0.1205,
            "context_and_harm": 0.1542
        }]
    )
    top_active_traits: List[FeatureTrait]


# ============================================================================
# 5. Similar Incidents
# ============================================================================

class SimilarityQueryRequest(BaseModel):
    incident_id: str = Field(..., examples=["INC_136975"])
    top_k: int = Field(5, ge=1, le=50, examples=[5])
    include_breakdown: bool = Field(True, examples=[True])


class VectorSimilarityQueryRequest(BaseModel):
    vector: List[float] = Field(..., min_length=70, max_length=70)
    top_k: int = Field(5, ge=1, le=50, examples=[5])


class SimilarIncidentMatch(BaseModel):
    rank: int = Field(..., examples=[1])
    incident_id: str = Field(..., examples=["INC_135749"])
    similarity_score_pct: float = Field(..., examples=[99.86])
    similarity: Optional[str] = Field(None, examples=["99.86%"])
    cosine_distance: float = Field(..., examples=[0.0014])
    subprofile_similarity_pct: Optional[Dict[str, float]] = None
    primary_crime_category: Optional[str] = Field(None, examples=["Property Crime (Theft/Burglary)"])
    crime_category: Optional[str] = Field(None, examples=["Property Crime (Theft/Burglary)"])
    cluster_name: Optional[str] = Field(None, examples=["Nocturnal & Weekend Residential/Commercial Burglary"])
    is_cross_crime_match: Optional[bool] = Field(False, description="True if match belongs to a different crime category than query")
    category_relationship: Optional[str] = Field("Same Crime Category", description="Same Crime Category or Different Crime Category")
    cross_crime_indicator: Optional[str] = Field(None, description="Clear indicator of cross-category modus operandi match")
    relevant_behavioral_characteristics: Optional[List[str]] = Field(default_factory=list, description="Key behavioral MO traits extracted from actual incident values")


class SimilarIncidentsResponse(BaseModel):
    query_incident_id: str = Field(..., examples=["INC_136975"])
    top_k_requested: int = Field(..., examples=[5])
    total_matches_returned: int = Field(..., examples=[5])
    cross_crime_indicator: Optional[str] = Field(None, examples=["Similar behavioral characteristics were found across different crime categories."])
    has_cross_crime_matches: Optional[bool] = False
    matches: List[SimilarIncidentMatch]
    grouped_by_category_relationship: Optional[Dict[str, List[SimilarIncidentMatch]]] = None
    ethical_advisory: str = (
        "Based on patterns learned from historical incidents. "
        "CRIME DNA analyzes behavioral patterns in historical incident data. "
        "Similarity or novelty does not establish offender identity, guilt, or causation. "
        "Behavioral similarity reflects shared modus operandi characteristics between incidents and does not identify offenders."
    )


class VectorSimilarIncidentsResponse(BaseModel):
    top_k_requested: int = Field(..., examples=[5])
    total_matches_returned: int = Field(..., examples=[5])
    cross_crime_indicator: Optional[str] = Field(None, examples=["Similar behavioral characteristics were found across different crime categories."])
    has_cross_crime_matches: Optional[bool] = False
    matches: List[SimilarIncidentMatch]
    grouped_by_category_relationship: Optional[Dict[str, List[SimilarIncidentMatch]]] = None
    ethical_advisory: str = (
        "Based on patterns learned from historical incidents. "
        "CRIME DNA analyzes behavioral patterns in historical incident data. "
        "Similarity or novelty does not establish offender identity, guilt, or causation. "
        "Behavioral similarity reflects shared modus operandi characteristics between incidents and does not identify offenders."
    )


# ============================================================================
# 6. Cluster Information
# ============================================================================

class ClusterDistinctiveFeature(BaseModel):
    feature: str = Field(..., examples=["is_night"])
    cluster_mean: float = Field(..., examples=[0.852])
    global_mean: float = Field(..., examples=[0.341])
    difference: float = Field(..., examples=[0.511])


class ClusterSummaryItem(BaseModel):
    cluster_id: int = Field(..., examples=[0])
    name: str = Field(..., examples=["Small-City Property & Structure Theft"])
    macro_category: str = Field(..., examples=["Property"])
    summary: str
    incident_count: int = Field(..., examples=[17725])
    percentage_of_total: float = Field(..., examples=[8.03])


class ClusterDetailResponse(BaseModel):
    cluster_id: int = Field(..., examples=[0])
    name: str = Field(..., examples=["Small-City Property & Structure Theft"])
    macro_category: str = Field(..., examples=["Property"])
    summary: str
    incident_count: int = Field(..., examples=[17725])
    percentage_of_total: float = Field(..., examples=[8.03])
    dominant_patterns: Dict[str, Any]
    top_distinctive_features: List[ClusterDistinctiveFeature]


class ClustersListResponse(BaseModel):
    total_clusters: int = Field(..., examples=[8])
    clusters: List[ClusterSummaryItem]


# ============================================================================
# 7. Cross-Crime Behavioral Patterns
# ============================================================================

class CategoryRepresentation(BaseModel):
    category_name: str = Field(..., examples=["Property"])
    incident_count: int = Field(..., examples=[17583])
    percentage: float = Field(..., examples=[99.2])


class ExemplarIncident(BaseModel):
    incident_id: str = Field(..., examples=["INC_171133"])
    crime_category: str = Field(..., examples=["Property"])
    category_description: str = Field(..., examples=["Property Offense"])
    behavioral_highlights: Dict[str, Any]


class CrossCrimePatternSummary(BaseModel):
    pattern_id: str = Field(..., examples=["CCP_00"])
    cluster_id: int = Field(..., examples=[0])
    pattern_name: str = Field(..., examples=["Cross-Crime: Small-City Property & Structure Theft"])
    total_incidents: int = Field(..., examples=[17725])
    categories_represented: List[CategoryRepresentation]


class CrossCrimePatternDetailResponse(BaseModel):
    pattern_id: str = Field(..., examples=["CCP_00"])
    cluster_id: int = Field(..., examples=[0])
    pattern_name: str = Field(..., examples=["Cross-Crime: Small-City Property & Structure Theft"])
    total_incidents: int = Field(..., examples=[17725])
    categories_represented: List[CategoryRepresentation]
    dominant_behavioral_characteristics: Dict[str, Any]
    inter_category_similarities: Dict[str, Any]
    exemplar_incidents: List[ExemplarIncident]
    exemplar_pairwise_similarities: Union[Dict[str, Any], List[Any]]
    cross_crime_evidence: Dict[str, Any]


class CrossCrimeListResponse(BaseModel):
    total_patterns: int = Field(..., examples=[8])
    patterns: List[CrossCrimePatternSummary]
    summary_metrics: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None


class AssociationStrengthDetail(BaseModel):
    association_score: float = Field(..., examples=[0.7286])
    confidence_score_pct: float = Field(..., examples=[72.9])
    confidence_tier: str = Field(..., examples=["Moderate Association"])
    distance_to_centroid: float = Field(..., examples=[0.2714])
    metric: str = Field(..., examples=["Cosine Similarity to Spherical Archetype Centroid"])


class AssociatedPatternItem(BaseModel):
    pattern_identifier: str = Field(..., examples=["CCP_03"])
    cluster_id: int = Field(..., examples=[3])
    pattern_name: str = Field(..., examples=["Cross-Crime: Nocturnal & Weekend Residential/Commercial Burglary"])
    association_score: float = Field(..., examples=[0.7286])
    confidence_score_pct: float = Field(..., examples=[72.9])
    confidence_tier: str = Field(..., examples=["Moderate Association"])
    supporting_historical_incidents: int = Field(..., examples=[33335])
    categories_represented_count: int = Field(..., examples=[3])
    is_primary: bool = Field(..., examples=[True])


class HiddenBehavioralPatternResult(BaseModel):
    pattern_detected: bool = Field(True, description="Indicates whether an associated behavioral pattern was found")
    pattern_identifier: str = Field(..., examples=["CCP_03"])
    pattern_name: str = Field(..., examples=["Cross-Crime: Nocturnal & Weekend Residential/Commercial Burglary"])
    archetype_name: str = Field(..., examples=["Nocturnal & Weekend Residential/Commercial Burglary"])
    behavioral_characteristics: List[str] = Field(..., examples=[["Night", "Residential", "Property involved", "No injury"]])
    behavioral_formula: str = Field(..., examples=["Night + Residential + Property involved + No injury"])
    number_of_supporting_historical_incidents: int = Field(..., examples=[33335])
    number_of_crime_categories_represented: int = Field(..., examples=[3])
    relevant_crime_categories: List[CategoryRepresentation]
    association_strength: AssociationStrengthDetail
    is_cross_crime_pattern: bool = Field(True)
    cross_crime_summary: str = Field("Found across multiple crime categories.")
    shared_profile_text: str = Field("These crime categories share a similar behavioral profile.")
    associated_patterns: Optional[List[AssociatedPatternItem]] = None
    inter_category_similarities: Optional[Dict[str, Any]] = None
    cross_crime_evidence: Optional[Dict[str, Any]] = None
    ethical_advisory: str
    cluster_id: int
    cluster_name: str
    macro_category: str
    distance_to_centroid: float
    cluster_summary: str
    archetype_details: Optional[Dict[str, Any]] = None


# ============================================================================
# 8. Behavioral Evolution
# ============================================================================

class SignificantShift(BaseModel):
    shift_id: str = Field(..., examples=["SHIFT_01"])
    domain: Optional[str] = Field(None, examples=["Temporal Dynamics"])
    title: Optional[str] = Field(None, examples=["Summer Nocturnal Behavioral Surge"])
    baseline_period: Optional[str] = Field(None, examples=["February (24.24%)"])
    peak_period: Optional[str] = Field(None, examples=["July (28.16%)"])
    delta_magnitude: Optional[str] = Field(None, examples=["+3.92%"])
    statistical_test: Optional[str] = Field(None, examples=["ANOVA F-Test across 12 months"])
    test_statistic: Optional[str] = Field(None, examples=["F=12.64"])
    p_value: Optional[float] = Field(None, examples=[2.54e-24])
    statistical_significance: str = Field(..., examples=["Extremely Significant (p < 0.001)"])
    behavioral_explanation: Optional[str] = None


class EvolutionTimelineResponse(BaseModel):
    metadata: Dict[str, Any]
    cluster_timeline: Dict[str, Any]
    feature_timeline: Dict[str, Any]
    significant_shifts: List[SignificantShift]


class ShiftsListResponse(BaseModel):
    total_shifts: int = Field(..., examples=[4])
    shifts: List[SignificantShift]


class TimelineStageMetrics(BaseModel):
    nighttime_pct: float = Field(..., examples=[46.8])
    weapon_presence_pct: float = Field(..., examples=[1.3])
    physical_injury_pct: float = Field(..., examples=[1.2])
    property_involvement_pct: float = Field(..., examples=[99.9])
    incident_volume: int = Field(..., examples=[10012])


class TimelineStage(BaseModel):
    stage_id: str = Field(..., examples=["early"])
    period_label: str = Field(..., examples=["EARLY PERIOD"])
    time_range: str = Field(..., examples=["January – April (Winter / Early Months)"])
    behavioral_formula: str = Field(..., examples=["Night + Residential + No Weapon"])
    behavioral_characteristics: List[str] = Field(..., examples=[["Night", "Residential", "No Weapon"]])
    summary: str = Field(..., examples=["Baseline nocturnal property break-ins concentrated in residential structures."])
    metrics: TimelineStageMetrics


class BehavioralEvolutionResult(BaseModel):
    timeline_title: str = Field(..., examples=["Historical Behavioral Evolution Timeline"])
    pattern_identifier: str = Field(..., examples=["CCP_03"])
    pattern_name: str = Field(..., examples=["Nocturnal & Weekend Residential/Commercial Burglary"])
    dataset_time_span: str = Field(..., examples=["12-Month Historical Observation Period (January – December)"])
    evolution_interpretation: str = Field(..., examples=["Behavioral characteristics changed over the observed historical period."])
    timeline_stages: List[TimelineStage]
    aligned_statistical_shifts: Optional[List[Dict[str, Any]]] = None
    ethical_advisory: str = Field(...)
    calendar_month: Optional[int] = None
    hour_of_day: Optional[int] = None
    baseline_alignment_note: Optional[str] = None
    historical_longitudinal_context: Optional[str] = None


# ============================================================================
# 9. Novel Behavioral Patterns (Anomaly Detection)
# ============================================================================

class ScoreStats(BaseModel):
    mean: float = Field(..., examples=[0.1824])
    std: float = Field(..., examples=[0.0812])
    median: float = Field(..., examples=[0.1712])
    min: float = Field(..., examples=[0.0210])
    max: float = Field(..., examples=[0.9854])


class AnomalySummaryResponse(BaseModel):
    version: str = Field(..., examples=["1.0"])
    total_incidents: int = Field(..., examples=[220663])
    algorithm: str = Field(..., examples=["Ensemble: Isolation Forest + Cluster Distance"])
    hyperparameters: Dict[str, Any]
    thresholds: Dict[str, float]
    tier_counts: Dict[str, int]
    tier_percentages: Dict[str, float]
    score_statistics: ScoreStats


class BehavioralOutlierItem(BaseModel):
    incident_id: str = Field(..., examples=["INC_082341"])
    novelty_score: float = Field(..., examples=[0.8912])
    novelty_tier: str = Field(..., examples=["Extreme Outlier"])
    nearest_cluster: Dict[str, Any]
    second_nearest_cluster: Dict[str, Any]
    unusual_features: List[Dict[str, Any]]
    behavioral_summary: str


class OutliersListResponse(BaseModel):
    total_outliers_returned: int = Field(..., examples=[50])
    total_extreme_outliers: int = Field(..., examples=[221])
    outliers: List[BehavioralOutlierItem]


class IncidentAnomalyResponse(BaseModel):
    incident_id: str = Field(..., examples=["INC_082341"])
    novelty_score: float = Field(..., examples=[0.8912])
    novelty_tier: str = Field(..., examples=["Extreme Outlier"])
    nearest_cluster_id: int = Field(..., examples=[1])
    nearest_cluster_name: str
    distance_to_nearest_cluster: float = Field(..., examples=[0.7412])
    unusual_features: Optional[List[Dict[str, Any]]] = None
    behavioral_summary: Optional[str] = None


class BehavioralPatternFit(BaseModel):
    fit_score: float = Field(..., examples=[0.7155])
    fit_percentage: float = Field(..., examples=[71.6])
    fit_level: str = Field(..., examples=["High Fit", "Moderate Fit", "Low Fit (Atypical Combination)"])
    fit_summary: str
    cosine_alignment_to_archetype_pct: float = Field(..., examples=[78.4])


class UnusualBehavioralFactor(BaseModel):
    feature_name: str = Field(..., examples=["has_weapon"])
    factor_name: str = Field(..., examples=["Weapon Utilization"])
    incident_value: float = Field(..., examples=[1.0])
    cluster_baseline_value: float = Field(..., examples=[0.02])
    deviation_delta: float = Field(..., examples=[0.98])
    direction: str = Field(..., examples=["Elevated", "Suppressed"])
    explanation: str


class BehavioralNoveltyResult(BaseModel):
    behavioral_pattern_fit: BehavioralPatternFit
    novelty_score: float = Field(..., examples=[0.2845])
    novelty_tier: str = Field(..., examples=["Standard Behavioral Pattern", "Moderate Behavioral Novelty", "High Behavioral Outlier", "Extreme Behavioral Outlier"])
    percentile_description: str = Field(..., examples=["Baseline Typical Profile (Bottom 95%)"])
    is_novel: bool = Field(..., examples=[False])
    is_unusual: bool = Field(..., examples=[False])
    banner_title: str = Field(..., examples=["STANDARD BEHAVIORAL PATTERN", "⚠️ NOVEL BEHAVIORAL PATTERN"])
    banner_message: str = Field(..., examples=["This incident contains a behavioral combination that does not closely match the major patterns learned from the historical dataset."])
    unusual_behavioral_factors: List[UnusualBehavioralFactor]
    nearest_cluster_id: int = Field(..., examples=[3])
    nearest_cluster_name: str = Field(..., examples=["Residential Property Infiltration"])
    distance_to_nearest_cluster: float = Field(..., examples=[0.2156])
    isolation_forest_raw_score: Optional[float] = None
    thresholds: Dict[str, float]
    ethical_advisory: str
    unusual_features: Optional[List[Dict[str, Any]]] = None


# ============================================================================
# 10. Similarity Explanation
# ============================================================================

class ExplainRequest(BaseModel):
    incident_id_1: str = Field(..., examples=["INC_136975"])
    incident_id_2: str = Field(..., examples=["INC_145291"])


class GroupContributionItem(BaseModel):
    group_key: str = Field(..., examples=["temporal_dynamics"])
    display_name: str = Field(..., examples=["Time Pattern"])
    absolute_contribution: float = Field(..., examples=[0.2498])
    percentage_of_similarity: float = Field(..., examples=[29.1])


class FeatureContributionItem(BaseModel):
    feature_name: str = Field(..., examples=["has_relationship"])
    contribution: float = Field(..., examples=[0.0753])
    incident_1_value: float = Field(..., examples=[0.283])
    incident_2_value: float = Field(..., examples=[0.266])
    description: Optional[str] = None


class BehavioralGroupComparisonItem(BaseModel):
    group_key: str = Field(..., examples=["temporal_dynamics"])
    group_name: str = Field(..., examples=["Time"])
    status: str = Field(..., examples=["match"])
    indicator: str = Field(..., examples=["✓"])
    label: str = Field(..., examples=["✓ Same time pattern"])
    raw_label: Optional[str] = Field(None, examples=["Same time pattern"])
    match_tier: str = Field(..., examples=["Strong match"])
    similarity_score: float = Field(..., examples=[0.952])
    contribution_score: float = Field(..., examples=[0.2498])
    share_percentage: float = Field(..., examples=[29.1])
    details: Optional[str] = None


class SimilarityExplanationResponse(BaseModel):
    incident_pair: List[str] = Field(..., examples=[["INC_136975", "INC_145291"]])
    similarity_score_pct: float = Field(..., examples=[85.7])
    cosine_similarity_raw: float = Field(..., examples=[0.857])
    plain_english_explanation: Optional[str] = Field(
        None,
        examples=["The strongest behavioral similarities are the time pattern, location context, and property involvement."]
    )
    behavioral_group_comparisons: Optional[List[BehavioralGroupComparisonItem]] = None
    main_contributing_similarities: List[str]
    differences: List[str]
    group_contributions: List[GroupContributionItem]
    top_contributing_features: List[FeatureContributionItem]
    formatted_text_summary: str
    disclaimer: str = (
        "Based on patterns learned from historical incidents. "
        "CRIME DNA analyzes behavioral patterns in historical incident data. "
        "Similarity or novelty does not establish offender identity, guilt, or causation. "
        "Explanations represent mathematical feature-space attribution without establishing causal relationships."
    )


# ============================================================================
# 11. Incident Input & Real-Time Behavioral Analysis
# ============================================================================

class IncidentInputRequest(BaseModel):
    """
    Scientifically validated incident input schema exposing ONLY behavioral
    dimensions grounded in the 70-dimensional Behavioral DNA taxonomy.
    """
    scenario_title: Optional[str] = Field("Simulated Incident Case", description="User-friendly scenario title or case identifier")
    incident_date: Optional[str] = Field(None, description="Calendar date of occurrence (YYYY-MM-DD)")
    incident_time: Optional[str] = Field(None, description="Time of occurrence (HH:MM)")
    incident_hour: Optional[int] = Field(None, ge=0, le=23, description="Hour of occurrence (0-23)")
    incident_month: Optional[int] = Field(None, ge=1, le=12, description="Month of occurrence (1-12)")
    incident_weekday: Optional[int] = Field(None, ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    is_weekend: Optional[bool] = Field(None, description="Explicit weekend indicator")
    
    # Crime Classification
    crime_category: str = Field(
        "property",
        description="Target domain: person, property, society, person_property, person_society, property_society, person_property_society"
    )
    is_attempted: bool = Field(False, description="Attempted rather than completed offense")
    offense_count: int = Field(1, ge=1, le=20, description="Total distinct offenses in this incident")
    offense_categories_count: int = Field(1, ge=1, le=10, description="Number of statutory categories involved")
    
    # Environmental & Jurisdiction Profile
    population_setting: str = Field(
        "mid_sized_city",
        description="Jurisdiction density: small_city, mid_sized_city, large_city, metropolitan_core, small_town, rural_community, state_police"
    )
    population: Optional[float] = Field(None, ge=0.0, description="Exact jurisdiction population if known")
    location_count: int = Field(1, ge=1, le=10, description="Number of distinct crime scenes or premises")
    
    # Weapon & Modus Operandi
    has_weapon: bool = Field(False, description="Weapon displayed, threatened, or deployed")
    weapon_count: int = Field(0, ge=0, le=10, description="Total weapons identified")
    weapon_types_count: int = Field(0, ge=0, le=5, description="Distinct types of weapons used")
    has_criminal_activity: bool = Field(False, description="Gang, syndicate, or organized activity present")
    criminal_activity_count: int = Field(0, ge=0, le=5, description="Count of secondary criminal activities")
    has_relationship: bool = Field(False, description="Known prior relationship between victim and offender")
    
    # People & Demographics
    victim_count: int = Field(1, ge=0, le=50, description="Total victim count")
    victim_avg_age: Optional[float] = Field(None, ge=0.0, le=120.0, description="Average estimated victim age in years")
    victim_sexes_count: int = Field(1, ge=0, le=3, description="Distinct victim genders represented")
    victim_types_count: int = Field(1, ge=0, le=5, description="Distinct victim entity types (individual, business, etc.)")
    offender_count: int = Field(1, ge=0, le=50, description="Total suspected offenders involved")
    offender_avg_age: Optional[float] = Field(None, ge=0.0, le=120.0, description="Average estimated offender age in years")
    offender_sexes_count: int = Field(1, ge=0, le=3, description="Distinct offender genders represented")
    
    # Property & Economics
    has_property: bool = Field(False, description="Physical property damaged, seized, or targeted")
    property_record_count: int = Field(0, ge=0, le=20, description="Number of documented property items")
    has_stolen_property: bool = Field(False, description="Property stolen/carried away")
    stolen_count: int = Field(0, ge=0, le=20, description="Number of stolen property items")
    property_value: float = Field(0.0, ge=0.0, description="Total estimated economic value of property in USD")
    is_cargo_theft: bool = Field(False, description="Commercial cargo/freight theft")
    
    # Context & Harm
    has_injury: bool = Field(False, description="Physical injury sustained by victim")
    injury_record_count: int = Field(0, ge=0, le=10, description="Documented injury records")
    has_drug: bool = Field(False, description="Narcotics or contraband seized or involved")
    suspected_drug_count: int = Field(0, ge=0, le=10, description="Types of suspected narcotics")
    estimated_drug_quantity: float = Field(0.0, ge=0.0, description="Estimated contraband metric quantity")
    has_bias_motivation: bool = Field(False, description="Suspected hate/bias motivation")
    has_arrest: bool = Field(False, description="Immediate arrest effected on scene")
    arrest_count: int = Field(0, ge=0, le=20, description="Number of subjects arrested on scene")
    user_id: Optional[str] = Field(None, description="Lightweight user or session identifier (e.g. User_A, User_B)")

    # India-Ready Location & Regional Metadata (Optional, fully backward-compatible)
    country: Optional[str] = Field("India", description="Country of incident occurrence (e.g. India)")
    state_ut: Optional[str] = Field(None, description="Indian State or Union Territory (e.g. Maharashtra)")
    district: Optional[str] = Field(None, description="District or Police Commissionerate jurisdiction")
    city_town: Optional[str] = Field(None, description="City, Town, or Village name")
    locality: Optional[str] = Field(None, description="Locality, Police Station Jurisdiction, or Landmark")
    pin_code: Optional[str] = Field(None, description="Optional 6-digit Indian Postal PIN code")
    currency: Optional[str] = Field("INR", description="Currency designation for property loss (INR or USD)")
    timezone: Optional[str] = Field("Asia/Kolkata", description="Timezone of incident recording (defaults to Asia/Kolkata for India)")


class ScenarioPreset(BaseModel):
    id: str
    title: str
    description: str
    category: str
    payload: Dict[str, Any]


class AnalysisInputSummary(BaseModel):
    scenario_title: str
    crime_category: str
    population_setting: str
    temporal_profile: Dict[str, Any]
    behavioral_flags: Dict[str, bool]
    incident_counts: Dict[str, int]


class AnalysisDnaSummary(BaseModel):
    vector_dimension: int = 70
    subprofile_energies: Dict[str, float]
    top_active_traits: List[Dict[str, Any]]
    human_readable_fingerprint: Optional[Dict[str, Any]] = None


class AnalysisSimilaritySummary(BaseModel):
    top_matched_incident_id: Optional[str]
    similarity_percentage: float
    distance_metric: str = "Cosine Similarity on Unit L2 Hyper-Sphere"
    category_relationship: str
    has_cross_crime_match: bool
    k_neighbors_searched: int


class AnalysisPatternSummary(BaseModel):
    pattern_id: str
    cluster_id: int
    pattern_name: str
    behavioral_formula: str
    supporting_incident_count: int
    crime_categories_represented_count: int
    association_strength_score: float
    association_tier: str


class AnalysisNoveltySummary(BaseModel):
    novelty_score: float
    novelty_tier: str
    is_novel: bool
    pattern_fit_score: float
    fit_description: str
    unusual_factors: List[str] = Field(default_factory=list)


class AnalysisRecord(BaseModel):
    analysis_id: str
    user_id: str
    timestamp: str
    input_summary: AnalysisInputSummary
    behavioral_dna: AnalysisDnaSummary
    similarity_summary: AnalysisSimilaritySummary
    pattern_summary: AnalysisPatternSummary
    novelty_summary: AnalysisNoveltySummary
    ethical_advisory: str
    full_result: Optional[Dict[str, Any]] = None


class AnalysisRecordListResponse(BaseModel):
    total_count: int
    user_id: Optional[str] = None
    limit: int = 50
    offset: int = 0
    records: List[AnalysisRecord]


class InputAnalysisResponse(BaseModel):
    # Canonical Engine Keys
    incident_summary: Optional[Dict[str, Any]] = None
    behavioral_dna: Dict[str, Any]
    dna_similarity: Optional[Dict[str, Any]] = None
    similar_historical_incidents: List[Dict[str, Any]]
    similar_behavioral_incidents: Optional[Dict[str, Any]] = None
    cross_crime_matches: Optional[Dict[str, Any]] = None
    hidden_behavioral_patterns: Optional[HiddenBehavioralPatternResult] = None
    why_similar: Optional[Dict[str, Any]] = None
    behavioral_evolution: Optional[BehavioralEvolutionResult] = None
    novelty: Optional[BehavioralNoveltyResult] = None
    technical_metadata: Optional[Dict[str, Any]] = None
    analysis_record: Optional[AnalysisRecord] = None

    # Core Identifiers & Backwards-Compatible Frontend Keys
    analysis_id: str
    timestamp: str
    scenario_title: str
    human_readable_dna: Optional[Dict[str, Any]] = None
    machine_readable_dna: Optional[Dict[str, Any]] = None
    cluster_assignment: Dict[str, Any]
    cross_crime_mapping: Dict[str, Any]
    novelty_assessment: Dict[str, Any]
    why_similar_explanation: Dict[str, Any]
    evolutionary_context: Dict[str, Any]
    dna_comparison: Dict[str, Any]
    ethical_advisory: str


# ============================================================================
# 11. CRIME DNA Comparison Feature
# ============================================================================

class IncidentComparisonSpec(BaseModel):
    incident_id: Optional[str] = Field(None, description="ID of historical incident (e.g. INC_000001)")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Custom incident payload or attributes")
    payload: Optional[Dict[str, Any]] = Field(None, description="Custom incident payload or attributes")
    label: Optional[str] = Field(None, description="Custom label for this incident")


class DnaComparisonRequest(BaseModel):
    incident_a: IncidentComparisonSpec
    incident_b: IncidentComparisonSpec


class DnaComparisonTableRow(BaseModel):
    feature: str
    incident_a: str
    incident_b: str
    result: str
    match_status: str
    details: Optional[str] = None


class DnaComparisonSimilarity(BaseModel):
    similarity_score_pct: float
    cosine_distance: float
    match_tier: str
    affinity_summary: str


class WhatChangedDetail(BaseModel):
    headline: str
    escalations: List[str]
    transitions: List[str]
    narrative: str
    match_count: int
    differ_count: int
    total_dimensions_compared: int
    summary_match_line: str = ""
    summary_differ_line: str = ""
    summary_text: str = ""
    match_items: List[str] = Field(default_factory=list)
    differ_items: List[str] = Field(default_factory=list)
    same_crime_category: bool = False
    crime_category_status: str = "Different Crime Category"
    crime_category_detail: str = ""
    strongest_similarities: List[str] = Field(default_factory=list)
    most_meaningful_differences: List[str] = Field(default_factory=list)


class DnaComparisonResponse(BaseModel):
    comparison_title: str
    incident_a: Dict[str, Any]
    incident_b: Dict[str, Any]
    dna_similarity: DnaComparisonSimilarity
    dna_comparison_table: List[DnaComparisonTableRow]
    matching_characteristics: List[str]
    differing_characteristics: List[str]
    what_changed: WhatChangedDetail
    subprofile_comparison: List[Dict[str, Any]]
    ethical_advisory: str


# ============================================================================
# 12. Explore Behavioral Patterns (Clean Cards & Detail View)
# ============================================================================

class PatternCardSummary(BaseModel):
    pattern_id: str = Field(..., examples=["PATTERN 01"])
    cluster_id: int = Field(..., examples=[0])
    pattern_code: str = Field(..., examples=["CCP_00"])
    pattern_name: str = Field(..., examples=["Small-City Property & Structure Theft"])
    behavioral_formula: str = Field(..., examples=["Day + Small Town + Property + No Weapon"])
    key_characteristics: List[str] = Field(default_factory=list)
    supporting_incident_count: int = Field(..., examples=[17725])
    percentage_of_total: float = Field(..., examples=[8.03])
    crime_categories_summary: str = Field(..., examples=["Multiple crime categories (3 categories)"])
    top_crime_categories: List[str] = Field(default_factory=list)
    time_information: str = Field(..., examples=["Primarily Daytime (85.2% daytime execution)"])
    similarity_strength_score: float = Field(..., examples=[74.7])
    similarity_strength_label: str = Field(..., examples=["High MO Convergence (0.747)"])
    summary: str


class PatternEvolutionStage(BaseModel):
    stage_id: str
    period_label: str
    time_range: str
    behavioral_formula: str
    summary: str
    metrics: Dict[str, Any] = Field(default_factory=dict)


class PatternDetailViewResponse(BaseModel):
    pattern_id: str
    cluster_id: int
    pattern_code: str
    pattern_name: str
    behavioral_formula: str
    key_characteristics: List[str]
    supporting_incident_count: int
    percentage_of_total: float
    crime_categories_summary: str
    top_crime_categories: List[str]
    time_information: str
    similarity_strength_score: float
    similarity_strength_label: str
    summary: str
    why_this_pattern_exists: str
    crime_categories_involved: List[Dict[str, Any]]
    behavioral_characteristics: Dict[str, Any]
    evolution_timeline: List[PatternEvolutionStage]
    supporting_evidence: Dict[str, Any]
    analysis_details: Dict[str, Any]
    ethical_advisory: str


class ExplorePatternsResponse(BaseModel):
    total_patterns: int
    corpus_incident_count: int
    patterns: List[PatternCardSummary]


# ============================================================================
# 13. Behavioral Connection Map
# ============================================================================

class SharedBehavioralDna(BaseModel):
    time: str = Field(..., examples=["Primarily Daytime (85.2% day, 26.5% weekend)"])
    location: str = Field(..., examples=["Small municipal jurisdictions (10k-25k population)"])
    property: str = Field(..., examples=["High property involvement (99.2%), mean value: $1,420"])
    weapon: str = Field(..., examples=["Unarmed execution (weapon presence: 0.91%)"])
    context_harm: str = Field(..., examples=["Physical injury: 0.82%, on-scene arrest: 17.2%"])
    key_shared_traits: List[str] = Field(default_factory=list)
    why_connected: str
    metrics: Dict[str, Any] = Field(default_factory=dict)


class GraphNode(BaseModel):
    id: str = Field(..., examples=["cat_property", "pattern_03"])
    label: str = Field(..., examples=["Property Crimes", "PATTERN 04"])
    title: str = Field(..., examples=["Property Offenses (Theft, Burglary, Larceny)", "Residential Property Infiltration"])
    type: str = Field(..., examples=["crime_category", "behavioral_pattern"])
    incident_count: int = Field(..., examples=[111244])
    percentage: float = Field(..., examples=[50.41])
    color: str = Field(..., examples=["#0ea5e9", "#a855f7"])
    details: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str = Field(..., examples=["edge_cat_property_pattern_03"])
    source: str = Field(..., examples=["cat_property"])
    target: str = Field(..., examples=["pattern_03"])
    source_label: str = Field(..., examples=["Property Crimes"])
    target_label: str = Field(..., examples=["PATTERN 04"])
    incident_count: int = Field(..., examples=[33065])
    percentage_of_pattern: float = Field(..., examples=[99.2])
    percentage_of_category: float = Field(..., examples=[29.7])
    similarity_score: float = Field(..., examples=[76.2])
    strength_label: str = Field(..., examples=["Strong Behavioral Connection"])
    shared_behavioral_dna: SharedBehavioralDna


class BehavioralConnectionMapResponse(BaseModel):
    title: str = "Behavioral Connection Map"
    corpus_incident_count: int = 220663
    total_nodes: int
    total_edges: int
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    ethical_advisory: str


# ============================================================================
# 14. Human-In-The-Loop Investigator Feedback
# ============================================================================

class InvestigatorFeedbackPayload(BaseModel):
    is_useful: bool = Field(..., description="Was this behavioral match useful? (True = Yes, False = No)")
    target_type: Optional[str] = Field("incident_analysis", description="Type of analysis evaluated, e.g. incident_analysis, similarity_match")
    target_id: Optional[str] = Field(None, description="Optional incident ID or pattern identifier evaluated")
    useful_aspects: List[str] = Field(
        default_factory=list,
        description="Aspects identified as useful: similar_time, similar_location, similar_property, similar_method, other"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Optional operational notes (no PII)")


class InvestigatorFeedbackResponse(BaseModel):
    feedback_id: str
    status: str = "received"
    recorded_at: str
    is_useful: bool
    useful_aspects: List[str]
    disclaimer: str = (
        "Feedback is recorded strictly for human-in-the-loop evaluation and system validation. "
        "It is not currently utilized for automatic model retraining."
    )


class FeedbackSummaryResponse(BaseModel):
    total_feedback_count: int
    useful_count: int
    not_useful_count: int
    useful_percentage: float
    aspects_breakdown: Dict[str, int]
    recent_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    disclaimer: str = (
        "Feedback is recorded strictly for human-in-the-loop evaluation and system validation. "
        "It is not currently utilized for automatic model retraining."
    )


# ============================================================================
# 11. User Dataset Upload & Behavioral Analysis Schemas
# ============================================================================

class ColumnMappingDetail(BaseModel):
    standard_field: str
    label: str
    description: str
    category: str
    required: bool
    suggested_column: Optional[str] = None
    confidence: str


class ColumnSummary(BaseModel):
    name: str
    inferred_type: str
    non_null_count: int
    null_count: int
    sample_values: List[str]


class DatasetValidationResponse(BaseModel):
    file_token: str
    filename: str
    file_size_bytes: int
    total_records: int
    total_columns: int
    columns: List[str]
    column_summaries: List[ColumnSummary]
    preview_rows: List[Dict[str, Any]]
    suggested_mapping: Dict[str, str]
    mapping_details: List[ColumnMappingDetail]
    unmapped_user_columns: List[str]
    missing_cells: int
    missing_percentage: float
    duplicate_rows: int
    available_locations: Dict[str, List[str]]
    date_range: Dict[str, Optional[str]]
    warnings: List[str]
    is_valid: bool
    validation_time_ms: float


class DatasetAnalyzeRequest(BaseModel):
    file_token: Optional[str] = None
    csv_text: Optional[str] = None
    filename: str = "dataset.csv"
    column_mapping: Dict[str, str] = Field(default_factory=dict)
    scope: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None


class DatasetPattern(BaseModel):
    pattern_id: str
    title: str
    description: str
    incident_count: int
    percentage_of_dataset: float
    defining_traits: List[str]
    represented_categories: List[str]
    category_breakdown: Dict[str, float]
    sample_incident_ids: List[str]


class DatasetSimilarIncident(BaseModel):
    source_id: str
    target_id: str
    similarity_score: float
    source_category: str
    target_category: str
    source_cluster: str
    target_cluster: str
    matching_characteristics: List[str]
    differing_characteristics: List[str]


class CrossCrimePatternItem(BaseModel):
    category_a: str
    category_b: str
    behavioral_similarity: float
    shared_observed_traits: List[str]
    explanation: str
    non_offender_disclaimer: str


class LocationAreaSummary(BaseModel):
    area_name: str
    incident_count: int
    proportion_of_dataset: float
    primary_observed_category: str
    category_proportions: Dict[str, float]
    pattern_proportions: Dict[str, float]


class LocationInsightsResponse(BaseModel):
    is_available: bool
    granularity: str
    areas: List[LocationAreaSummary]
    disclaimer: str


class TemporalPeriodSummary(BaseModel):
    period: str
    incident_count: int
    proportion: float


class TemporalEvolutionResponse(BaseModel):
    is_available: bool
    period_breakdown: List[TemporalPeriodSummary]
    hourly_distribution: Dict[str, int]
    disclaimer: str


class UnusualCombinationItem(BaseModel):
    incident_id: str
    novelty_score: float
    novelty_label: str
    assigned_pattern: str
    crime_category: str
    contributing_features: List[str]
    explanation: str


class DatasetSummaryResponse(BaseModel):
    dataset_name: str
    total_records: int
    initial_records_count: int
    excluded_by_scope: int
    number_of_categories: int
    date_range: str
    geographic_scope: str
    fields_used: List[str]


class DatasetAnalysisResultResponse(BaseModel):
    analysis_id: str
    user_id: str
    created_at: str
    filename: str
    dataset_summary: DatasetSummaryResponse
    behavioral_patterns: List[DatasetPattern]
    similar_incidents: List[DatasetSimilarIncident]
    cross_crime_patterns: List[CrossCrimePatternItem]
    location_insights: LocationInsightsResponse
    temporal_evolution: TemporalEvolutionResponse
    unusual_combinations: List[UnusualCombinationItem]
    reference_comparison: Optional[Dict[str, Any]] = None
    why_these_results: Dict[str, List[str]]
    technical_details: Dict[str, Any]


class DatasetDeleteResponse(BaseModel):
    status: str
    analysis_id: str
    deleted: bool
    message: str





