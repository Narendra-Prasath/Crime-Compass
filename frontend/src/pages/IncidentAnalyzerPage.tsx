import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { IncidentProfile, BehavioralDNA, SimilarIncidentsResponse } from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import { DNARadarChart } from '../components/DNARadarChart';
import { Search, Fingerprint, Shield } from 'lucide-react';

interface IncidentAnalyzerPageProps {
  initialIncidentId?: string;
  onNavigate: (page: string, params?: any) => void;
}

const PRESET_INCIDENTS = ['INC_136975', 'INC_145291', 'INC_171133', 'INC_082341', 'INC_135749'];

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
    if (!id.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const [profileRes, dnaRes, similarRes] = await Promise.all([
        api.getIncident(id),
        api.getIncidentDNA(id),
        api.getSimilarIncidents(id, 5),
      ]);
      setProfile(profileRes);
      setDna(dnaRes);
      setSimilar(similarRes);
      setActiveIncidentId(id);
    } catch (err: any) {
      setError(err.message || `Incident '${id}' could not be retrieved.`);
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
    fetchIncidentData(queryInput.trim());
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header & Search */}
      <div>
        <h1 style={{ fontSize: '1.75rem' }}>Incident Behavioral Fingerprint Analyzer</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
          Deconstructs any crime incident into its 70-dimensional Behavioral DNA representation and retrieves nearest behavioral matches.
        </p>
      </div>

      <div className="card" style={{ padding: '18px 22px' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} style={{ position: 'absolute', left: '14px', top: '13px', color: 'var(--text-dim)' }} />
            <input
              type="text"
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              placeholder="Enter Incident ID (e.g. INC_136975)..."
              className="search-input"
              style={{
                width: '100%',
                background: 'var(--bg-subtle)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '10px 14px 10px 42px',
              }}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Analyze DNA
          </button>
        </form>

        {/* Preset Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Sample Incidents:</span>
          {PRESET_INCIDENTS.map((id) => (
            <button
              key={id}
              type="button"
              className="preset-chip"
              onClick={() => {
                setQueryInput(id);
                fetchIncidentData(id);
              }}
            >
              {id}
            </button>
          ))}
        </div>
      </div>

      {loading && <LoadingState message={`Encoding Behavioral DNA for ${queryInput}...`} />}
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
                  Assigned Archetype: <strong style={{ color: 'var(--text-main)' }}>{profile.cluster.cluster_name}</strong>
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
                  {profile.context.incident_hour}:00 ({profile.context.is_night ? 'Night' : 'Day'})
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
                  {profile.context.property_value > 0 ? `$${profile.context.property_value.toLocaleString()}` : 'None'}
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

          {/* DNA Representation: Radar Chart & Top Active Traits */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
            <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div className="card-header" style={{ width: '100%' }}>
                <div>
                  <div className="card-title">
                    <Fingerprint size={18} style={{ color: 'var(--accent-cyan)' }} /> Behavioral DNA Radar
                  </div>
                  <div className="card-subtitle">Energy distribution across 7 behavioral dimensions</div>
                </div>
              </div>
              <DNARadarChart data={dna.group_energies} size={280} />
            </div>

            <div className="card">
              <div className="card-header">
                <div>
                  <div className="card-title">Top Active Behavioral Dimensions</div>
                  <div className="card-subtitle">Highest normalized components in this incident's fingerprint</div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {dna.top_active_traits.map((trait, idx) => (
                  <div key={idx}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '3px' }}>
                      <span className="mono" style={{ color: 'var(--text-main)' }}>{trait.feature}</span>
                      <span className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
                        {trait.value.toFixed(4)}
                      </span>
                    </div>
                    <div className="progress-bar-container">
                      <div className="progress-bar-fill" style={{ width: `${Math.min(100, trait.value * 250)}%` }} />
                    </div>
                  </div>
                ))}
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
                    Nearest neighbors in 70D Behavioral DNA space (self-match excluded)
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
                    {similar.matches.map((m) => (
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
                              {Math.round(m.similarity_score_pct)}%
                            </span>
                            <div className="progress-bar-container" style={{ width: '80px' }}>
                              <div
                                className="progress-bar-fill"
                                style={{ width: `${m.similarity_score_pct}%`, backgroundColor: 'var(--accent-emerald)' }}
                              />
                            </div>
                          </div>
                        </td>
                        <td>
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <button
                              className="btn btn-secondary"
                              style={{ padding: '4px 8px', fontSize: '0.72rem' }}
                              onClick={() => onNavigate('similarity-view', { inc1: activeIncidentId, inc2: m.incident_id })}
                            >
                              Compare
                            </button>
                            <button
                              className="btn btn-primary"
                              style={{ padding: '4px 8px', fontSize: '0.72rem' }}
                              onClick={() => onNavigate('why-similar', { inc1: activeIncidentId, inc2: m.incident_id })}
                            >
                              Why Similar?
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
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
  );
};
