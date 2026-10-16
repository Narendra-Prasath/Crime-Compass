/**
 * Crime Compass 🧭 — Frontend TypeScript Types & Interfaces
 * Matches backend Pydantic schemas in src/api/schemas.py
 */

export interface HealthResponse {
  status: string;
  api_version: string;
  uptime_seconds: number;
  components_status: Record<string, string>;
  indexed_incidents: number;
  vector_dimension: number;
}

export interface DatasetStats {
  dataset_name: string;
  total_incidents: number;
  raw_columns_count: number;
  cleaned_features_count: number;
  behavioral_dna_features_count: number;
  feature_taxonomy_counts: Record<string, number>;
  behavioral_groups_count: number;
  clusters_count: number;
  cross_crime_patterns_count: number;
  novelty_tier_counts: Record<string, number>;
  reference_dataset_source?: string;
}

export interface IncidentContext {
  incident_hour: number;
  incident_month: number;
  incident_weekday: number;
  is_weekend: boolean;
  is_night: boolean;
  population: number;
  offense_count: number;
  victim_count: number;
  offender_count: number;
  property_value: number;
  has_weapon: boolean;
  has_injury: boolean;
  has_property: boolean;
  has_drug: boolean;
  has_arrest: boolean;
  has_relationship: boolean;
  crime_against_person: boolean;
  crime_against_property: boolean;
  crime_against_society: boolean;
  primary_crime_category: string;
}

export interface IncidentClusterAssignment {
  cluster_id: number;
  cluster_name: string;
}

export interface IncidentNoveltyInfo {
  novelty_score: number;
  novelty_tier: string;
  nearest_cluster_id: number;
  nearest_cluster_name: string;
  distance_to_nearest_cluster: number;
}

export interface IncidentProfile {
  incident_id: string;
  cluster: IncidentClusterAssignment;
  novelty: IncidentNoveltyInfo;
  context: IncidentContext;
}

export interface FeatureTrait {
  feature: string;
  value: number;
}

export interface BehavioralDNA {
  incident_id: string;
  vector_dimension: number;
  feature_vector: Record<string, number>;
  group_energies: Record<string, number>;
  top_active_traits: FeatureTrait[];
}

export interface DomainCoverageItem {
  domain_id: string;
  name: string;
  coverage_pct: number;
  valid_fields_count: number;
  total_applicable_fields: number;
  unspecified_fields_count: number;
  description: string;
  available_fields: string[];
  unspecified_fields: string[];
}

export interface DataCoverage {
  domains: DomainCoverageItem[];
  overall_coverage_pct: number;
  total_valid_fields: number;
  total_applicable_fields: number;
  coverage_formula: string;
  coverage_caveat: string;
}

export interface CompactTrait {
  trait: string;
  value: string;
  status: 'Yes' | 'No' | 'Unknown' | 'Not applicable' | 'Applicable';
  domain: string;
}

export interface ObservedFeatureComparison {
  time_alignment: 'Similar' | 'Different' | 'Unknown';
  location_setting: 'Similar' | 'Different' | 'Unknown';
  crime_characteristics: 'Similar' | 'Different' | 'Unknown';
  method_and_activity: 'Similar' | 'Different' | 'Unknown';
  property_and_context: 'Similar' | 'Different' | 'Unknown';
  summary: string;
  matching_observed_fields: string[];
  differing_observed_fields: string[];
  unknown_observed_fields: string[];
  cross_crime_rationale?: string;
}

export interface SimilarMatch {
  rank: number;
  incident_id: string;
  similarity_score_pct: number;
  similarity?: string;
  cosine_distance: number;
  subprofile_similarity_pct?: Record<string, number>;
  primary_crime_category?: string;
  crime_category?: string;
  cluster_name?: string;
  is_cross_crime_match?: boolean;
  category_relationship?: string;
  cross_crime_indicator?: string;
  relevant_behavioral_characteristics?: string[];
  observed_feature_comparison?: ObservedFeatureComparison;
}

export interface SimilarIncidentsResponse {
  query_incident_id: string;
  top_k_requested: number;
  total_matches_returned: number;
  cross_crime_indicator?: string;
  has_cross_crime_matches?: boolean;
  matches: SimilarMatch[];
  grouped_by_category_relationship?: {
    same_crime_category: SimilarMatch[];
    different_crime_categories: SimilarMatch[];
  };
  ethical_advisory?: string;
}

export interface DistinctiveFeature {
  feature: string;
  cluster_mean: number;
  global_mean: number;
  difference: number;
}

export interface ClusterSummary {
  cluster_id: number;
  name: string;
  macro_category: string;
  summary: string;
  incident_count: number;
  percentage_of_total: number;
}

export interface ClusterDetail extends ClusterSummary {
  dominant_patterns: Record<string, string>;
  top_distinctive_features: DistinctiveFeature[];
}

export interface CategoryRepresentation {
  category_name: string;
  incident_count: number;
  percentage: number;
}

export interface ExemplarIncident {
  incident_id: string;
  crime_category: string;
  category_description: string;
  behavioral_highlights: Record<string, any>;
}

export interface CrossCrimePatternSummary {
  pattern_id: string;
  cluster_id: number;
  pattern_name: string;
  total_incidents: number;
  categories_represented: CategoryRepresentation[];
}

export interface CrossCrimePatternDetail extends CrossCrimePatternSummary {
  dominant_behavioral_characteristics: Record<string, string>;
  inter_category_similarities: Record<string, number>;
  exemplar_incidents: ExemplarIncident[];
  exemplar_pairwise_similarities: Record<string, number> | any[];
  cross_crime_evidence: Record<string, string>;
}

export interface SignificantShift {
  shift_id: string;
  domain?: string;
  title?: string;
  baseline_period?: string;
  peak_period?: string;
  delta_magnitude?: string;
  statistical_test?: string;
  test_statistic?: string;
  p_value?: number;
  statistical_significance: string;
  behavioral_explanation?: string;
}

export interface EvolutionTimeline {
  metadata: Record<string, any>;
  cluster_timeline: Record<string, any>;
  feature_timeline: Record<string, any>;
  significant_shifts: SignificantShift[];
}

export interface BehavioralOutlier {
  incident_id: string;
  novelty_score: number;
  novelty_tier: string;
  nearest_cluster: {
    cluster_id: number;
    name: string;
    distance: number;
  };
  second_nearest_cluster: {
    cluster_id: number;
    name: string;
    distance: number;
  };
  unusual_features: Array<{
    feature: string;
    incident_value: number;
    population_mean?: number;
    deviation_z_score?: number;
  }>;
  behavioral_summary: string;
}

export interface AnomalySummary {
  version: string;
  total_incidents: number;
  algorithm: string;
  hyperparameters: Record<string, any>;
  thresholds: Record<string, number>;
  tier_counts: Record<string, number>;
  tier_percentages: Record<string, number>;
  score_statistics: {
    mean: number;
    std: number;
    median: number;
    min: number;
    max: number;
  };
}

export interface GroupContribution {
  group_key: string;
  display_name: string;
  absolute_contribution: number;
  percentage_of_similarity: number;
}

export interface FeatureContribution {
  feature_name: string;
  contribution: number;
  incident_1_value: number;
  incident_2_value: number;
  description?: string;
}

export interface BehavioralGroupComparison {
  group_key: string;
  group_name: string;
  status: 'match' | 'divergence';
  indicator: string;
  label: string;
  raw_label?: string;
  match_tier: string;
  similarity_score: number;
  contribution_score: number;
  share_percentage: number;
  details?: string;
}

export interface SimilarityExplanation {
  incident_pair: [string, string];
  similarity_score_pct: number;
  cosine_similarity_raw: number;
  plain_english_explanation?: string;
  behavioral_group_comparisons?: BehavioralGroupComparison[];
  main_contributing_similarities: string[];
  differences: string[];
  group_contributions: GroupContribution[];
  top_contributing_features: FeatureContribution[];
  formatted_text_summary: string;
  disclaimer: string;
}

export interface IncidentInputPayload {
  scenario_title?: string;
  incident_date?: string;
  incident_time?: string;
  incident_hour?: number;
  incident_month?: number;
  incident_weekday?: number;
  is_weekend?: boolean;
  is_night?: boolean;
  crime_category: string;
  is_attempted?: boolean;
  offense_count?: number;
  offense_categories_count?: number;
  population_setting?: string;
  population?: number;
  location_count?: number;
  has_weapon?: boolean;
  weapon_count?: number;
  weapon_types_count?: number;
  has_criminal_activity?: boolean;
  criminal_activity_count?: number;
  has_relationship?: boolean;
  victim_count?: number;
  victim_avg_age?: number;
  victim_sexes_count?: number;
  victim_types_count?: number;
  offender_count?: number;
  offender_avg_age?: number;
  offender_sexes_count?: number;
  has_property?: boolean;
  property_record_count?: number;
  has_stolen_property?: boolean;
  stolen_count?: number;
  property_value?: number;
  is_cargo_theft?: boolean;
  has_injury?: boolean;
  injury_record_count?: number;
  has_drug?: boolean;
  suspected_drug_count?: number;
  estimated_drug_quantity?: number;
  has_bias_motivation?: boolean;
  has_arrest?: boolean;
  arrest_count?: number;
  user_id?: string;

  // India-ready Location & Regional fields (optional, backward-compatible)
  country?: string;
  state_ut?: string;
  district?: string;
  city_town?: string;
  locality?: string;
  pin_code?: string;
  currency?: 'INR' | 'USD';
  timezone?: string;
}

export interface ScenarioPreset {
  id: string;
  title: string;
  description: string;
  category: string;
  payload: IncidentInputPayload;
}

export interface HiddenBehavioralPattern {
  pattern_detected: boolean;
  pattern_identifier: string;
  pattern_name: string;
  archetype_name: string;
  behavioral_characteristics: string[];
  behavioral_formula: string;
  number_of_supporting_historical_incidents: number;
  number_of_crime_categories_represented: number;
  relevant_crime_categories: Array<{
    category_name: string;
    incident_count: number;
    percentage: number;
  }>;
  association_strength: {
    association_score: number;
    confidence_score_pct: number;
    confidence_tier: string;
    distance_to_centroid: number;
    metric: string;
  };
  is_cross_crime_pattern: boolean;
  cross_crime_summary: string;
  shared_profile_text: string;
  associated_patterns?: Array<{
    pattern_identifier: string;
    cluster_id: number;
    pattern_name: string;
    association_score: number;
    confidence_score_pct: number;
    confidence_tier: string;
    supporting_historical_incidents: number;
    categories_represented_count: number;
    is_primary: boolean;
  }>;
  inter_category_similarities?: Record<string, number>;
  cross_crime_evidence?: Record<string, any>;
  ethical_advisory: string;
  cluster_id: number;
  cluster_name: string;
  macro_category: string;
  distance_to_centroid: number;
  cluster_summary: string;
  archetype_details?: Record<string, any>;
}

export interface TimelineStage {
  stage_id: string;
  period_label: string;
  time_range: string;
  behavioral_formula: string;
  behavioral_characteristics: string[];
  summary: string;
  metrics: {
    nighttime_pct: number;
    weapon_presence_pct: number;
    physical_injury_pct: number;
    property_involvement_pct: number;
    incident_volume: number;
  };
}

export interface BehavioralEvolutionTimeline {
  timeline_title: string;
  pattern_identifier: string;
  pattern_name: string;
  dataset_time_span: string;
  evolution_interpretation: string;
  timeline_stages: TimelineStage[];
  aligned_statistical_shifts?: Array<{
    shift_id: string;
    domain?: string;
    title?: string;
    baseline_period?: string;
    peak_period?: string;
    delta_magnitude?: string;
    statistical_test?: string;
    statistical_significance?: string;
    behavioral_explanation?: string;
  }>;
  ethical_advisory: string;
  calendar_month?: number;
  hour_of_day?: number;
  baseline_alignment_note?: string;
  historical_longitudinal_context?: string;
}

export interface InputAnalysisResult {
  analysis_id: string;
  timestamp: string;
  scenario_title: string;
  data_coverage?: DataCoverage;
  hidden_behavioral_patterns?: HiddenBehavioralPattern;
  behavioral_evolution?: BehavioralEvolutionTimeline;
  behavioral_dna: {
    vector_dimension: number;
    subprofile_energies: Record<string, number>;
    top_active_traits: Array<{ feature: string; value: number }>;
    data_coverage?: DataCoverage;
    human_readable?: {
      title: string;
      summary_chips: string[];
      compact_traits?: CompactTrait[];
      traits: Array<{
        id: string;
        icon: string;
        label: string;
        category: string;
        description: string;
        is_elevated: boolean;
      }>;
      plain_text: string;
    };
    machine_readable?: {
      vector_dimension: number;
      l2_norm: number;
      feature_names: string[];
      raw_vector: number[];
      normalized_vector: number[];
      feature_vector_dict: Record<string, number>;
      subprofile_energies: Record<string, number>;
      top_active_traits: Array<{ feature: string; value: number; description?: string }>;
    };
  };
  human_readable_dna?: {
    title: string;
    summary_chips: string[];
    compact_traits?: CompactTrait[];
    traits: Array<{
      id: string;
      icon: string;
      label: string;
      category: string;
      description: string;
      is_elevated: boolean;
    }>;
    plain_text: string;
  };
  machine_readable_dna?: {
    vector_dimension: number;
    l2_norm: number;
    feature_names: string[];
    raw_vector: number[];
    normalized_vector: number[];
    feature_vector_dict: Record<string, number>;
    subprofile_energies: Record<string, number>;
    top_active_traits: Array<{ feature: string; value: number; description?: string }>;
  };
  cluster_assignment: {
    cluster_id: number;
    cluster_name: string;
    macro_category: string;
    distance_to_centroid: number;
    cluster_summary: string;
    pattern_identifier?: string;
    pattern_name?: string;
    behavioral_characteristics?: string[];
    behavioral_formula?: string;
    number_of_supporting_historical_incidents?: number;
    number_of_crime_categories_represented?: number;
    relevant_crime_categories?: Array<{
      category_name: string;
      incident_count: number;
      percentage: number;
    }>;
    association_strength?: {
      association_score: number;
      confidence_score_pct: number;
      confidence_tier: string;
      distance_to_centroid: number;
      metric: string;
    };
    cross_crime_summary?: string;
    shared_profile_text?: string;
  };
  cross_crime_mapping: {
    dominant_cross_crime_pattern: string;
    cross_crime_pattern_name: string;
    represented_categories: string[];
    behavioral_synergy: string;
  };
  novelty_assessment: {
    novelty_score: number;
    novelty_tier: string;
    neutral_label?: string;
    neutral_label_description?: string;
    method_used?: string;
    data_limitations?: string;
    observed_features_contributing?: string[];
    percentile_description: string;
    distance_to_nearest_cluster: number;
    nearest_cluster_name: string;
    behavioral_pattern_fit?: {
      fit_score: number;
      fit_percentage: number;
      fit_level: string;
      fit_summary: string;
      cosine_alignment_to_archetype_pct: number;
    };
    is_novel?: boolean;
    is_unusual?: boolean;
    banner_title?: string;
    banner_message?: string;
    unusual_behavioral_factors?: Array<{
      feature_name: string;
      factor_name: string;
      incident_value: number;
      cluster_baseline_value: number;
      deviation_delta: number;
      direction: string;
      explanation: string;
    }>;
    thresholds?: Record<string, number>;
    ethical_advisory?: string;
    unusual_features: Array<{
      feature_name: string;
      incident_value: number;
      cluster_centroid_value: number;
      deviation_delta: number;
      direction: string;
      explanation: string;
    }>;
  };
  similar_historical_incidents: SimilarMatch[];
  similar_behavioral_incidents?: {
    title: string;
    query_crime_category: string;
    cross_crime_indicator: string;
    has_cross_crime_matches: boolean;
    same_category_count: number;
    cross_category_count: number;
    matches: SimilarMatch[];
    grouped_by_category_relationship: {
      same_crime_category: SimilarMatch[];
      different_crime_categories: SimilarMatch[];
    };
    ethical_advisory: string;
  };
  why_similar_explanation: {
    target_incident_id: string;
    overall_similarity_pct: number;
    plain_english_explanation?: string;
    behavioral_group_comparisons?: BehavioralGroupComparison[];
    observed_feature_comparison?: ObservedFeatureComparison;
    cosine_metric_explanation?: string;
    non_offender_disclaimer?: string;
    group_attributions: Array<{
      group_key: string;
      display_name: string;
      raw_attribution: number;
      share_percentage: number;
    }>;
    top_matching_features: Array<{
      feature_name: string;
      contribution: number;
      input_value: number;
      match_value: number;
      description: string;
    }>;
    main_contributing_similarities: string[];
    semantic_differences: string[];
  };
  evolutionary_context: {
    incident_hour?: number;
    time_window?: string;
    active_era?: string;
    hourly_cluster_trend?: string;
    stability_classification?: string;
    timeline_title?: string;
    pattern_identifier?: string;
    pattern_name?: string;
    dataset_time_span?: string;
    evolution_interpretation?: string;
    timeline_stages?: TimelineStage[];
    aligned_statistical_shifts?: any[];
    ethical_advisory?: string;
    calendar_month?: number;
    hour_of_day?: number;
    baseline_alignment_note?: string;
    historical_longitudinal_context?: string;
  };
  dna_comparison: {
    input_subprofile_energies: Record<string, number>;
    top_match_incident_id: string;
    top_match_subprofile_energies: Record<string, number>;
  };
  analysis_record?: AnalysisRecord;
  ethical_advisory: string;
}

export interface AnalysisRecord {
  analysis_id: string;
  user_id: string;
  timestamp: string;
  input_summary: {
    scenario_title: string;
    crime_category: string;
    population_setting: string;
    temporal_profile: Record<string, any>;
    behavioral_flags: Record<string, boolean>;
    incident_counts: Record<string, number>;
  };
  behavioral_dna: {
    vector_dimension: number;
    subprofile_energies: Record<string, number>;
    top_active_traits: Array<{ feature: string; value: number }>;
    human_readable_fingerprint?: any;
  };
  similarity_summary: {
    top_matched_incident_id?: string;
    similarity_percentage: number;
    distance_metric: string;
    category_relationship: string;
    has_cross_crime_match: boolean;
    k_neighbors_searched: number;
  };
  pattern_summary: {
    pattern_id: string;
    cluster_id: number;
    pattern_name: string;
    behavioral_formula: string;
    supporting_incident_count: number;
    crime_categories_represented_count: number;
    association_strength_score: number;
    association_tier: string;
  };
  novelty_summary: {
    novelty_score: number;
    novelty_tier: string;
    is_novel: boolean;
    pattern_fit_score: number;
    fit_description: string;
    unusual_factors: string[];
  };
  ethical_advisory: string;
  full_result?: any;
}

export interface AnalysisRecordListResponse {
  total_count: number;
  user_id?: string;
  limit?: number;
  offset?: number;
  records: AnalysisRecord[];
}

export interface DnaComparisonTableRow {
  feature: string;
  incident_a: string;
  incident_b: string;
  result: string;
  match_status: string;
  details?: string;
}

export interface DnaComparisonSimilarity {
  similarity_score_pct: number;
  cosine_distance: number;
  match_tier: string;
  affinity_summary: string;
}

export interface WhatChangedDetail {
  headline: string;
  escalations: string[];
  transitions: string[];
  narrative: string;
  match_count: number;
  differ_count: number;
  unknown_count?: number;
  total_dimensions_compared: number;
  summary_match_line?: string;
  summary_differ_line?: string;
  summary_text?: string;
  match_items: string[];
  differ_items: string[];
  unknown_items?: string[];
  same_crime_category: boolean;
  crime_category_status: string;
  crime_category_detail: string;
  strongest_similarities: string[];
  most_meaningful_differences: string[];
}

export interface DnaComparisonResponse {
  comparison_title: string;
  incident_a: {
    label: string;
    incident_id?: string;
    source_type: string;
  };
  incident_b: {
    label: string;
    incident_id?: string;
    source_type: string;
  };
  dna_similarity: DnaComparisonSimilarity;
  dna_comparison_table: DnaComparisonTableRow[];
  matching_characteristics: string[];
  differing_characteristics: string[];
  unknown_characteristics?: string[];
  what_changed: WhatChangedDetail;
  subprofile_comparison: Array<{
    group_name: string;
    energy_a: number;
    energy_b: number;
    delta: number;
    alignment: string;
  }>;
  ethical_advisory: string;
  network_map_disclaimer?: string;
}

export interface ComparisonPreset {
  id: string;
  title: string;
  description: string;
  incident_a: {
    label: string;
    incident_id?: string;
    input_data?: any;
  };
  incident_b: {
    label: string;
    incident_id?: string;
    input_data?: any;
  };
}

export interface PatternCardSummary {
  pattern_id: string;
  cluster_id: number;
  pattern_code: string;
  pattern_name: string;
  behavioral_formula: string;
  key_characteristics: string[];
  supporting_incident_count: number;
  percentage_of_total: number;
  crime_categories_summary: string;
  top_crime_categories: string[];
  time_information: string;
  similarity_strength_score: number;
  similarity_strength_label: string;
  summary: string;
}

export interface PatternEvolutionStage {
  stage_id: string;
  period_label: string;
  time_range: string;
  behavioral_formula: string;
  summary: string;
  metrics: Record<string, any>;
}

export interface PatternDetailViewResponse {
  pattern_id: string;
  cluster_id: number;
  pattern_code: string;
  pattern_name: string;
  behavioral_formula: string;
  key_characteristics: string[];
  supporting_incident_count: number;
  percentage_of_total: number;
  crime_categories_summary: string;
  top_crime_categories: string[];
  time_information: string;
  similarity_strength_score: number;
  similarity_strength_label: string;
  summary: string;
  why_this_pattern_exists: string;
  crime_categories_involved: Array<{
    category_name: string;
    incident_count: number;
    percentage: number;
  }>;
  behavioral_characteristics: Record<string, any>;
  evolution_timeline: PatternEvolutionStage[];
  supporting_evidence: {
    total_incidents: number;
    categories_count: number;
    avg_inter_category_similarity_pct: number;
    shannon_entropy: number;
    simpson_diversity: number;
    cross_crime_incidents_count: number;
    exemplar_incidents?: Array<{
      incident_id: string;
      offense_category: string;
      similarity: number;
    }>;
  };
  analysis_details: {
    top_distinctive_features: Array<{
      feature: string;
      cluster_mean: number;
      global_mean: number;
      difference: number;
    }>;
    clustering_algorithm: string;
    vector_dimension: number;
    distance_metric: string;
    inter_category_similarities?: Record<string, number>;
  };
  ethical_advisory: string;
}

export interface ExplorePatternsResponse {
  total_patterns: number;
  corpus_incident_count: number;
  patterns: PatternCardSummary[];
}

export interface SharedBehavioralDna {
  time: string;
  location: string;
  property: string;
  weapon: string;
  context_harm: string;
  key_shared_traits: string[];
  why_connected: string;
  metrics?: Record<string, number>;
}

export interface GraphNode {
  id: string;
  label: string;
  title: string;
  type: 'crime_category' | 'behavioral_pattern';
  incident_count: number;
  percentage: number;
  color: string;
  details?: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  source_label: string;
  target_label: string;
  incident_count: number;
  percentage_of_pattern: number;
  percentage_of_category: number;
  similarity_score: number;
  strength_label: string;
  shared_behavioral_dna: SharedBehavioralDna;
}

export interface BehavioralConnectionMapResponse {
  title: string;
  corpus_incident_count: number;
  total_nodes: number;
  total_edges: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
  ethical_advisory: string;
}

export interface InvestigatorFeedbackPayload {
  is_useful: boolean;
  target_type?: string;
  target_id?: string;
  useful_aspects?: string[];
  notes?: string;
}

export interface InvestigatorFeedbackResponse {
  feedback_id: string;
  status: string;
  recorded_at: string;
  is_useful: boolean;
  useful_aspects: string[];
  disclaimer: string;
}

export interface FeedbackSummaryResponse {
  total_feedback_count: number;
  useful_count: number;
  not_useful_count: number;
  useful_percentage: number;
  aspects_breakdown: Record<string, number>;
  recent_feedback: Array<{
    feedback_id: string;
    created_at: string;
    is_useful: boolean;
    target_type?: string;
    target_id?: string;
    useful_aspects: string[];
  }>;
  disclaimer: string;
}

// ============================================================================
// User Dataset Upload & Analysis Types
// ============================================================================

export interface ColumnMappingDetail {
  standard_field: string;
  label: string;
  description: string;
  category: string;
  required: boolean;
  suggested_column?: string | null;
  confidence: string;
}

export interface ColumnSummary {
  name: string;
  inferred_type: string;
  non_null_count: number;
  null_count: number;
  sample_values: string[];
}

export interface DatasetValidationResult {
  file_token: string;
  filename: string;
  file_size_bytes: number;
  total_records: number;
  total_columns: number;
  columns: string[];
  column_summaries: ColumnSummary[];
  preview_rows: Record<string, any>[];
  suggested_mapping: Record<string, string>;
  mapping_details: ColumnMappingDetail[];
  unmapped_user_columns: string[];
  missing_cells: number;
  missing_percentage: number;
  duplicate_rows: number;
  available_locations: {
    countries: string[];
    states: string[];
    districts: string[];
    cities: string[];
    localities: string[];
  };
  date_range: {
    min_date: string | null;
    max_date: string | null;
  };
  warnings: string[];
  is_valid: boolean;
  validation_time_ms: number;
}

export interface DatasetPattern {
  pattern_id: string;
  title: string;
  description: string;
  incident_count: number;
  percentage_of_dataset: number;
  defining_traits: string[];
  represented_categories: string[];
  category_breakdown: Record<string, number>;
  sample_incident_ids: string[];
}

export interface DatasetSimilarIncident {
  source_id: string;
  target_id: string;
  similarity_score: number;
  source_category: string;
  target_category: string;
  source_cluster: string;
  target_cluster: string;
  matching_characteristics: string[];
  differing_characteristics: string[];
}

export interface CrossCrimePatternItem {
  category_a: string;
  category_b: string;
  behavioral_similarity: number;
  shared_observed_traits: string[];
  explanation: string;
  non_offender_disclaimer: string;
}

export interface LocationAreaSummary {
  area_name: string;
  incident_count: number;
  proportion_of_dataset: number;
  primary_observed_category: string;
  category_proportions: Record<string, number>;
  pattern_proportions: Record<string, number>;
}

export interface LocationInsights {
  is_available: boolean;
  granularity: string;
  areas: LocationAreaSummary[];
  disclaimer: string;
}

export interface TemporalPeriodSummary {
  period: string;
  incident_count: number;
  proportion: number;
}

export interface TemporalEvolution {
  is_available: boolean;
  period_breakdown: TemporalPeriodSummary[];
  hourly_distribution: Record<string, number>;
  disclaimer: string;
}

export interface UnusualCombinationItem {
  incident_id: string;
  novelty_score: number;
  novelty_label: string;
  assigned_pattern: string;
  crime_category: string;
  contributing_features: string[];
  explanation: string;
}

export interface DatasetSummary {
  dataset_name: string;
  total_records: number;
  initial_records_count: number;
  excluded_by_scope: number;
  number_of_categories: number;
  date_range: string;
  geographic_scope: string;
  fields_used: string[];
}

export interface DatasetAnalysisResult {
  analysis_id: string;
  user_id: string;
  created_at: string;
  filename: string;
  dataset_summary: DatasetSummary;
  behavioral_patterns: DatasetPattern[];
  similar_incidents: DatasetSimilarIncident[];
  cross_crime_patterns: CrossCrimePatternItem[];
  location_insights: LocationInsights;
  temporal_evolution: TemporalEvolution;
  unusual_combinations: UnusualCombinationItem[];
  reference_comparison?: {
    status: string;
    reference_dataset: string;
    alignments: Array<{
      dataset_pattern_id: string;
      dataset_pattern_title: string;
      closest_historical_pattern_id: string;
      cosine_alignment: number;
      interpretation: string;
    }>;
    disclaimer: string;
  } | null;
  why_these_results: {
    observed_facts: string[];
    algorithm_findings: string[];
    interpretations: string[];
    limitations: string[];
  };
  technical_details: {
    records_analyzed: number;
    records_excluded_by_scope: number;
    feature_space: string;
    clustering_algorithm: string;
    similarity_metric: string;
    novelty_algorithm: string;
    missing_data_handling: string;
    privacy_compliance: string;
    execution_time_ms: number;
  };
}





