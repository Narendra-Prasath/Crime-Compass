import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { IncidentProfile, BehavioralDNA, SimilarIncidentsResponse } from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import { DNARadarChart } from '../components/DNARadarChart';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { Search, Fingerprint, Shield, Globe2, AlertCircle, ArrowRight } from 'lucide-react';
import { formatCurrency } from '../utils/indiaFormat';

interface IncidentAnalyzerPageProps {
  initialIncidentId?: string;
  onNavigate: (page: string, params?: any) => void;
}

const PRESET_INCIDENTS = ['INC_136975', 'INC_145291', 'INC_171133', 'INC_082341', 'INC_135749'];

const getDimensionFriendlyLabel = (feature: string, label?: string): string => {
  if (label && label !== feature) return label;
  const friendlyMap: Record<string, string> = {
    time_hour_sin: 'Diurnal Rhythm (Sine)',
    time_hour_cos: 'Diurnal Rhythm (Cos)',
    time_month_sin: 'Seasonal Timing (Sine)',
    time_month_cos: 'Seasonal Timing (Cos)',
    time_weekday_sin: 'Weekly Rhythm (Sine)',
    time_weekday_cos: 'Weekly Rhythm (Cos)',
    time_is_weekend: 'Weekend Occurrence',
    time_is_night: 'Nocturnal Execution (Night)',
    crime_against_person: 'Crimes Against Person',
    crime_against_property: 'Property Offense',
    crime_against_society: 'Societal Regulation Offense',
    crime_against_person_property: 'Dual Person & Property Offense',
    crime_against_person_society: 'Person & Society Crime',
    crime_against_property_society: 'Property & Society Crime',
    crime_against_person_property_society: 'Multi-Category Crime',
    offense_count_scaled: 'Offense Count Volume',
    offense_categories_count_scaled: 'Category Diversity',
    is_attempted: 'Attempted Offense',
    location_count_scaled: 'Multi-Location Scene',
    population_log_scaled: 'Urban Population Density',
    'population_group_desc_cities_from_10,000_thru_24,999': 'Small City (10k-25k pop.)',
    'population_group_desc_cities_from_100,000_thru_249,999': 'Metropolitan Core (100k-250k)',
    'population_group_desc_cities_from_2,500_thru_9,999': 'Town Setting (2.5k-10k pop.)',
    'population_group_desc_cities_from_25,000_thru_49,999': 'Mid-Sized City (25k-50k pop.)',
    'population_group_desc_cities_from_50,000_thru_99,999': 'Medium-Large City (50k-100k)',
    'population_group_desc_cities_under_2,500': 'Rural Municipality (<2.5k pop.)',
    'population_group_desc_msa_counties_100,000_or_over': 'Major Metro County (>100k)',
    'population_group_desc_msa_counties_from_10,000_thru_24,999': 'Small Metro County (10k-25k)',
    'population_group_desc_msa_counties_from_25,000_thru_99,999': 'Mid-Metro County (25k-100k)',
    'population_group_desc_msa_counties_under_10,000': 'Rural Metro County (<10k)',
    'population_group_desc_non_msa_state_police': 'State Police Corridor',
    'population_group_desc_non_msa_counties_from_10,000_thru_24,999': 'Rural County (10k-25k pop.)',
    'population_group_desc_non_msa_counties_from_25,000_thru_99,999': 'Mid-Rural County (25k-100k)',
    'population_group_desc_non_msa_counties_under_10,000': 'Remote Rural County (<10k)',
    agency_is_state_police: 'State Police Jurisdiction',
    has_weapon: 'Weapon Deployed',
    weapon_count_scaled: 'Weapon Volume',
    weapon_types_count_scaled: 'Weapon Diversity',
    is_multi_weapon: 'Multi-Weapon Arsenal',
    has_criminal_activity: 'Secondary Criminal Activity',
    criminal_activity_count_scaled: 'Enterprise Activity Volume',
    has_relationship: 'Prior Victim-Offender Relationship',
    relationship_count_scaled: 'Interpersonal Ties Complexity',
    victim_count_scaled: 'Victim Headcount',
    is_multi_victim: 'Multiple Victims Targeted',
    victim_age_known: 'Documented Victim Demographics',
    victim_avg_age_scaled: 'Victim Age Index',
    victim_age_spread_scaled: 'Cross-Generational Victim Spread',
    victim_sexes_count_scaled: 'Mixed-Gender Victim Group',
    victim_types_count_scaled: 'Diverse Victim Types',
    offender_count_scaled: 'Offender Group Size',
    is_co_offender: 'Co-Offenders Present',
    offender_age_known: 'Documented Offender Profile',
    offender_avg_age_scaled: 'Offender Age Index',
    offender_age_spread_scaled: 'Perpetrator Age Dispersion',
    offender_sexes_count_scaled: 'Mixed-Gender Co-Offenders',
    has_property: 'Property Loss / Targeted',
    property_record_count_scaled: 'Property Records Volume',
    has_stolen_property: 'Stolen Property Involved',
    stolen_count_scaled: 'Stolen Item Volume',
    property_value_log_scaled: 'Financial Valuation Index',
    is_cargo_theft: 'Commercial Cargo Theft',
    has_injury: 'Bodily Harm / Injury Inflicted',
    injury_record_count_scaled: 'Injury Severity Volume',
    has_drug: 'Narcotics Involvement',
    suspected_drug_count_scaled: 'Suspected Drug Varieties',
    estimated_drug_quantity_log_scaled: 'Contraband Quantity Volume',
    has_bias_motivation: 'Hate / Bias Motivation',
    has_arrest_on_scene: 'Immediate Scene Arrest',
    arrest_count_scaled: 'On-Scene Arrest Volume',
  };
  return friendlyMap[feature] || feature.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
};

const getDimensionDomain = (feature: string, domain?: string, domainLabel?: string): string => {
  if (domainLabel) return domainLabel;
  if (domain) return domain.replace(/_/g, ' ').toUpperCase();
  if (feature.startsWith('time_')) return 'Time Pattern';
  if (feature.startsWith('crime_') || feature.startsWith('offense_') || feature === 'is_attempted') return 'Crime Type';
  if (feature.startsWith('population_') || feature.startsWith('location_') || feature.includes('state_police')) return 'Location';
  if (feature.includes('weapon') || feature.includes('relationship') || feature.includes('criminal_activity')) return 'Method / MO';
  if (feature.includes('victim') || feature.includes('offender') || feature.includes('co_offender')) return 'People / Context';
  if (feature.includes('property') || feature.includes('stolen') || feature.includes('cargo')) return 'Property';
  if (feature.includes('injury') || feature.includes('drug') || feature.includes('bias') || feature.includes('arrest')) return 'Harm / Outcome';
  return 'Dimension';
};

export const IncidentAnalyzerPage: React.FC<IncidentAnalyzerPageProps> = ({
  initialIncidentId = 'INC_136975',
  onNavigate,
}) => {
  const [queryInput, setQueryInput] = useState(initialIncidentId);
  const [activeIncidentId, setActiveIncidentId] = useState(initialIncidentId);
  const [profile, setProfile] = useState<IncidentProfile | null>(null);
  const [dna, setDna] = useState<BehavioralDNA | null>(null);
  const [similar, setSimilar] = useState<SimilarIncidentsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchIncidentData = async (id: string) => {
    const trimmed = (id || '').trim();
    if (!trimmed) {
      setError('Please provide a valid Incident ID (e.g. INC_136975).');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const [profileRes, dnaRes, similarRes] = await Promise.all([
        api.getIncident(trimmed),
        api.getIncidentDNA(trimmed),
        api.getSimilarIncidents(trimmed, 5),
      ]);
      setProfile(profileRes);
      setDna(dnaRes);
      setSimilar(similarRes);
      setActiveIncidentId(trimmed);
    } catch (err: any) {
      setError(err.message || `Incident '${trimmed}' could not be retrieved from the reference database.`);
      setProfile(null);
      setDna(null);
      setSimilar(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidentData(initialIncidentId);
  }, [initialIncidentId]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryInput.trim()) {
      setError('Please enter a valid Incident ID (e.g. INC_136975).');
      return;
    }
    fetchIncidentData(queryInput.trim());
  };

  return (
    <ErrorBoundary fallbackTitle="Incident Analyzer View Recovery">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Header & Search */}
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.74rem', color: 'var(--accent-cyan)', background: 'rgba(14, 165, 233, 0.1)', padding: '3px 10px', borderRadius: '999px', marginBottom: '8px' }}>
            <Globe2 size={13} />
            <span>Historical Reference Dataset: Alabama, USA (2024 FBI NIBRS)</span>
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, margin: '0 0 6px' }}>
            Incident Behavioral Fingerprint Analyzer
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: 0, lineHeight: 1.5 }}>
            Deconstructs any historical incident into its 70-dimensional behavioral fingerprint representation and retrieves nearest behavioral matches across crime categories.
          </p>
        </div>

        <div className="card" style={{ padding: '18px 22px' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
              <Search size={18} style={{ position: 'absolute', left: '14px', top: '13px', color: 'var(--text-dim)' }} />
              <input
                type="text"
                value={queryInput}
                onChange={(e) => {
                  setQueryInput(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="Enter Incident ID (e.g. INC_136975)..."
                className="search-input"
                aria-label="Enter Incident ID"
                style={{
                  width: '100%',
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '10px 14px 10px 42px',
                  color: 'var(--text-main)',
                  fontSize: '0.9rem'
                }}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              <Fingerprint size={16} />
              <span>{loading ? 'Analyzing Fingerprint...' : 'Analyze Fingerprint'}</span>
            </button>
          </form>

          {/* Preset Chips */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '14px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>Sample Historical Incidents:</span>
            {PRESET_INCIDENTS.map((id) => (
              <button
                key={id}
                type="button"
                className="preset-chip"
                onClick={() => {
                  setQueryInput(id);
                  fetchIncidentData(id);
                }}
                disabled={loading}
                style={{
                  background: activeIncidentId === id ? 'var(--accent-cyan)' : 'var(--bg-subtle)',
                  color: activeIncidentId === id ? '#ffffff' : 'var(--text-main)',
                  border: `1px solid ${activeIncidentId === id ? 'var(--accent-cyan)' : 'var(--border-subtle)'}`,
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '0.78rem',
                  cursor: 'pointer'
                }}
              >
                {id}
              </button>
            ))}
          </div>
        </div>

        {loading && <LoadingState message={`Encoding Behavioral Fingerprint for ${queryInput}...`} />}
        {error && <ErrorState error={error} onRetry={() => fetchIncidentData(queryInput)} />}

        {!loading && !error && profile && dna && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Incident Overview Card */}
            <div
              className="card"
              style={{
                background: 'linear-gradient(135deg, var(--bg-card) 0%, rgba(14, 165, 233, 0.04) 100%)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span className="mono" style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>
                      {profile.incident_id}
                    </span>
                    <span
                      className={`badge ${
                        profile.context.primary_crime_category.includes('Person')
                          ? 'badge-person'
                          : profile.context.primary_crime_category.includes('Property')
                          ? 'badge-property'
                          : 'badge-society'
                      }`}
                    >
                      {profile.context.primary_crime_category}
                    </span>
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
                    Assigned Behavioral Archetype: <strong style={{ color: 'var(--text-main)' }}>{profile.cluster.cluster_name}</strong>
                  </div>
                </div>

                {/* Badges and Novelty */}
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <span
                    className={`badge ${
                      profile.novelty.novelty_tier.includes('Standard')
                        ? 'badge-standard'
                        : profile.novelty.novelty_tier.includes('Moderate')
                        ? 'badge-moderate'
                        : 'badge-outlier'
                    }`}
                    style={{ padding: '6px 12px' }}
                  >
                    {profile.novelty.novelty_tier} (Score: {profile.novelty.novelty_score.toFixed(3)})
                  </span>
                </div>
              </div>

              {/* Context Attributes Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                  gap: '12px',
                  marginTop: '20px',
                  paddingTop: '16px',
                  borderTop: '1px solid var(--border-subtle)',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Timing</div>
                  <div style={{ fontWeight: 600, fontSize: '0.86rem', marginTop: '2px' }}>
                    {profile.context.incident_hour}:00 ({profile.context.is_night ? 'Night' : 'Day'}) &bull; US Central (CDT)
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Day of Week</div>
                  <div style={{ fontWeight: 600, fontSize: '0.86rem', marginTop: '2px' }}>
                    Weekday {profile.context.incident_weekday} ({profile.context.is_weekend ? 'Weekend' : 'Weekday'})
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Force / Weapon</div>
                  <div style={{ fontWeight: 600, fontSize: '0.86rem', marginTop: '2px' }}>
                    {profile.context.has_weapon ? 'Weapon Present' : 'Unarmed'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Casualties / Harm</div>
                  <div style={{ fontWeight: 600, fontSize: '0.86rem', marginTop: '2px' }}>
                    {profile.context.has_injury ? 'Injury Sustained' : 'No Injuries'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Property Value</div>
                  <div style={{ fontWeight: 600, fontSize: '0.86rem', marginTop: '2px' }}>
                    {profile.context.property_value > 0 ? formatCurrency(profile.context.property_value, 'USD') : 'None'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Enforcement</div>
                  <div style={{ fontWeight: 600, fontSize: '0.86rem', marginTop: '2px' }}>
                    {profile.context.has_arrest ? 'Arrest At Scene' : 'No Arrest'}
                  </div>
                </div>
              </div>
            </div>

            {/* Fingerprint Representation: Radar Chart & Top Active Traits */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
              <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div className="card-header" style={{ width: '100%' }}>
                  <div>
                    <div className="card-title">
                      <Fingerprint size={18} style={{ color: 'var(--accent-cyan)' }} /> Behavioral Fingerprint Radar
                    </div>
                    <div className="card-subtitle">Energy distribution across 7 behavioral dimensions</div>
                  </div>
                </div>
                {dna.group_energies && Object.keys(dna.group_energies).length > 0 ? (
                  <DNARadarChart data={dna.group_energies} size={280} />
                ) : (
                  <div style={{ padding: '40px 0', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                    Radar profile data not available.
                  </div>
                )}
              </div>

              <div className="card">
                <div className="card-header">
                  <div>
                    <div className="card-title">Top Active Behavioral Dimensions</div>
                    <div className="card-subtitle">Highest normalized components in this incident's fingerprint</div>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {(dna.top_active_traits || []).map((trait, idx) => {
                    const friendlyName = getDimensionFriendlyLabel(trait.feature, trait.label);
                    const domainName = getDimensionDomain(trait.feature, trait.domain, trait.domain_label);
                    const energyPct = trait.energy_share_pct ?? Math.round(trait.value * trait.value * 1000) / 10;
                    return (
                      <div key={idx} style={{ padding: '2px 0' }}>
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            fontSize: '0.78rem',
                            marginBottom: '4px',
                            gap: '12px'
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', minWidth: 0, overflow: 'hidden' }}>
                            <span
                              style={{
                                color: 'var(--text-main)',
                                fontWeight: 600,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}
                              title={trait.description || `${friendlyName} (${trait.feature})`}
                            >
                              {friendlyName}
                            </span>
                            <span
                              style={{
                                fontSize: '0.64rem',
                                padding: '1px 5px',
                                borderRadius: '3px',
                                background: 'rgba(255,255,255,0.06)',
                                color: 'var(--text-dim)',
                                flexShrink: 0,
                                whiteSpace: 'nowrap'
                              }}
                            >
                              {domainName}
                            </span>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0, marginLeft: 'auto' }}>
                            <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }} title="Normalized component energy share (v²)">
                              {energyPct.toFixed(1)}% energy
                            </span>
                            <span className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
                              {trait.value.toFixed(4)}
                            </span>
                          </div>
                        </div>
                        <div className="progress-bar-container" style={{ height: '5px' }}>
                          <div
                            className="progress-bar-fill"
                            style={{
                              width: `${Math.min(100, Math.max(8, trait.value * 250))}%`,
                              backgroundColor: 'var(--accent-cyan)'
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Top Behaviorally Similar Incidents */}
            {similar && (
              <div className="card">
                <div className="card-header">
                  <div>
                    <div className="card-title">Top Behaviorally Similar Incidents</div>
                    <div className="card-subtitle">
                      Nearest neighbors in 70D behavioral space (self-match excluded)
                    </div>
                  </div>
                </div>

                {similar.has_cross_crime_matches && (
                  <div
                    style={{
                      margin: '0 20px 14px 20px',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      background: 'rgba(168, 85, 247, 0.12)',
                      border: '1px solid rgba(168, 85, 247, 0.35)',
                      fontSize: '0.8rem',
                      color: '#e9d5ff'
                    }}
                  >
                    <strong style={{ color: '#f3e8ff' }}>Cross-Crime Match: </strong>
                    Similar behavioral characteristics were found across different crime categories.
                  </div>
                )}

                <div className="table-wrapper">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Rank</th>
                        <th>Incident ID</th>
                        <th>Statutory Category</th>
                        <th>Assigned Archetype</th>
                        <th>Similarity Score</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(similar.matches || []).map((m) => {
                        const simPct = typeof m.similarity_score_pct === 'number' ? m.similarity_score_pct : 88;
                        return (
                          <tr key={m.incident_id}>
                            <td className="mono" style={{ fontWeight: 700 }}>#{m.rank}</td>
                            <td className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>
                              {m.incident_id}
                            </td>
                            <td>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <span
                                  className={`badge ${
                                    m.primary_crime_category?.includes('Person')
                                      ? 'badge-person'
                                      : m.primary_crime_category?.includes('Property')
                                      ? 'badge-property'
                                      : 'badge-society'
                                  }`}
                                >
                                  {m.primary_crime_category || 'Crime'}
                                </span>
                                {m.is_cross_crime_match && (
                                  <span
                                    style={{
                                      fontSize: '0.65rem',
                                      fontWeight: 700,
                                      padding: '2px 5px',
                                      borderRadius: '3px',
                                      background: 'rgba(236, 72, 153, 0.15)',
                                      color: '#f472b6',
                                      textTransform: 'uppercase'
                                    }}
                                  >
                                    Cross-Crime
                                  </span>
                                )}
                              </div>
                            </td>
                            <td>{m.cluster_name || 'Standard Cluster'}</td>
                            <td>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span className="mono" style={{ fontWeight: 700, color: 'var(--accent-emerald)' }}>
                                  {Math.round(simPct)}%
                                </span>
                                <div className="progress-bar-container" style={{ width: '80px' }}>
                                  <div
                                    className="progress-bar-fill"
                                    style={{ width: `${simPct}%`, backgroundColor: 'var(--accent-emerald)' }}
                                  />
                                </div>
                              </div>
                            </td>
                            <td>
                              <div style={{ display: 'flex', gap: '8px' }}>
                                <button
                                  type="button"
                                  className="btn btn-secondary"
                                  style={{ padding: '4px 8px', fontSize: '0.72rem' }}
                                  onClick={() => onNavigate('similarity-view', { inc1: activeIncidentId, inc2: m.incident_id })}
                                >
                                  Compare
                                </button>
                                <button
                                  type="button"
                                  className="btn btn-primary"
                                  style={{ padding: '4px 8px', fontSize: '0.72rem' }}
                                  onClick={() => onNavigate('why-similar', { inc1: activeIncidentId, inc2: m.incident_id })}
                                >
                                  Why Similar?
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Mandatory Scientific Advisory */}
        <div
          style={{
            marginTop: '20px',
            padding: '12px 18px',
            background: 'rgba(59, 130, 246, 0.05)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}
        >
          <Shield size={18} style={{ color: '#60a5fa', flexShrink: 0 }} />
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            <strong style={{ color: '#93c5fd' }}>Advisory: </strong>
            Crime Compass analyzes incident characteristics and historical behavioral patterns. Similarity or novelty does not establish offender identity, guilt, or causation.
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};
export default IncidentAnalyzerPage;
