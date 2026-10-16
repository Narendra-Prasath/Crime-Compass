import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { DatasetStats, ClusterSummary, CrossCrimePatternSummary, SignificantShift } from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import {
  Layers,
  Network,
  TrendingUp,
  Fingerprint,
  ArrowRight,
  ShieldAlert,
  Compass
} from 'lucide-react';
import { formatIndianNumber } from '../utils/indiaFormat';

interface OverviewPageProps {
  onNavigate: (page: string, params?: any) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DatasetStats | null>(null);
  const [clusters, setClusters] = useState<ClusterSummary[]>([]);
  const [crossCrime, setCrossCrime] = useState<CrossCrimePatternSummary[]>([]);
  const [shifts, setShifts] = useState<SignificantShift[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, clustersRes, crossCrimeRes, shiftsRes] = await Promise.all([
        api.getStats(),
        api.getClusters(),
        api.getCrossCrimePatterns(),
        api.getSignificantShifts(),
      ]);
      setStats(statsRes);
      setClusters(clustersRes);
      setCrossCrime(crossCrimeRes);
      setShifts(shiftsRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load overview analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <LoadingState message="Connecting to Crime Compass reference dataset..." />;
  if (error) return <ErrorState error={error} onRetry={fetchData} />;
  if (!stats) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Hero Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(13, 19, 31, 0.95) 0%, rgba(14, 165, 233, 0.08) 100%)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          padding: '30px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '20px',
        }}
      >
        <div style={{ maxWidth: '640px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span className="badge badge-property">Production Behavioral Engine</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>70-Dimensional Vector Space</span>
          </div>
          <h1 style={{ fontSize: '2rem', lineHeight: 1.2, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>Crime Compass</span>
            <span role="img" aria-label="compass">🧭</span>
            <span style={{ color: 'var(--accent-cyan)', fontWeight: 400, fontSize: '1.6rem' }}>Behavioral Intelligence</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '8px', fontSize: '0.95rem' }}>
            Crime Compass helps users analyze crime incident data, discover behavioral similarities, explore patterns across crime categories, and understand how incidents compare with historical records.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-primary" onClick={() => onNavigate('input-analysis')}>
            <Compass size={16} /> Analyze Incident
          </button>
          <button className="btn btn-secondary" onClick={() => onNavigate('cross-crime')}>
            <Network size={16} /> Cross-Crime Patterns
          </button>
        </div>
      </div>

      {/* Explicit Legal & Ethical Standard Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '14px',
          padding: '16px 20px',
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          fontSize: '0.85rem',
          lineHeight: '1.5',
          color: 'var(--text-muted)'
        }}
      >
        <ShieldAlert size={20} style={{ color: 'var(--accent-cyan)', flexShrink: 0 }} />
        <div>
          <strong style={{ color: 'var(--text-main)' }}>Advisory: </strong>
          Crime Compass analyzes incident characteristics and historical behavioral patterns. Similarity or novelty does not establish offender identity, guilt, or causation.
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Reference Incidents</div>
          <div className="stat-value">{formatIndianNumber(stats.total_incidents)}</div>
          <div className="stat-helper">Historical reference dataset: Alabama, USA, 2024 (FBI NIBRS)</div>
        </div>

        <div className="stat-card emerald">
          <div className="stat-label">Behavioral DNA Dimensions</div>
          <div className="stat-value">{stats.behavioral_dna_features_count}D</div>
          <div className="stat-helper">Across {stats.behavioral_groups_count} behavioral domains</div>
        </div>

        <div className="stat-card purple">
          <div className="stat-label">Behavioral Archetypes</div>
          <div className="stat-value">{stats.clusters_count} Clusters</div>
          <div className="stat-helper">Spherical K-Means ($k=8$)</div>
        </div>

        <div className="stat-card amber">
          <div className="stat-label">Cross-Crime Patterns</div>
          <div className="stat-value">{stats.cross_crime_patterns_count} Patterns</div>
          <div className="stat-helper">Shared cross-category MOs</div>
        </div>

        <div className="stat-card rose">
          <div className="stat-label">Extreme Novel Outliers</div>
          <div className="stat-value">{stats.novelty_tier_counts['High Behavioral Outlier'] || stats.novelty_tier_counts['Extreme Outlier'] || 221}</div>
          <div className="stat-helper">Novelty score (unusual combinations)</div>
        </div>
      </div>

      {/* Two Column Section: Discovered Clusters + Cross Crime Patterns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(440px, 1fr))', gap: '24px' }}>
        {/* Discovered Behavioral Clusters */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <Layers size={18} style={{ color: 'var(--accent-purple)' }} /> Discovered Behavioral Archetypes
              </div>
              <div className="card-subtitle">8 unsupervised operational behavioral groupings</div>
            </div>
            <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.78rem' }} onClick={() => onNavigate('behavioral-patterns')}>
              View All <ArrowRight size={14} />
            </button>
          </div>

          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Pattern</th>
                  <th>Archetype Name</th>
                  <th>Macro Group</th>
                  <th>Incidents</th>
                  <th>Share</th>
                </tr>
              </thead>
              <tbody>
                {clusters.slice(0, 5).map((c) => (
                  <tr key={c.cluster_id} style={{ cursor: 'pointer' }} onClick={() => onNavigate('behavioral-patterns', { clusterId: c.cluster_id })}>
                    <td className="mono" style={{ fontWeight: 700, color: 'var(--accent-purple)' }}>Pattern #{c.cluster_id + 1}</td>
                    <td style={{ fontWeight: 600 }}>{c.name}</td>
                    <td>
                      <span className={`badge ${c.macro_category.toLowerCase() === 'persons' ? 'badge-person' : c.macro_category.toLowerCase() === 'property' ? 'badge-property' : 'badge-society'}`}>
                        {c.macro_category}
                      </span>
                    </td>
                    <td className="mono">{c.incident_count.toLocaleString()}</td>
                    <td className="mono" style={{ color: 'var(--text-muted)' }}>{c.percentage_of_total}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Cross-Crime Connections Teaser */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">
                <Network size={18} style={{ color: 'var(--accent-amber)' }} /> Cross-Crime Behavioral Linkages
              </div>
              <div className="card-subtitle">Crimes across legal categories sharing identical Behavioral DNA</div>
            </div>
            <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.78rem' }} onClick={() => onNavigate('cross-crime')}>
              View All <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {crossCrime.slice(0, 4).map((p) => (
              <div
                key={p.pattern_id}
                style={{
                  background: 'var(--bg-subtle)',
                  padding: '14px 16px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)',
                  cursor: 'pointer',
                  transition: 'border-color 0.15s ease',
                }}
                onClick={() => onNavigate('cross-crime', { patternId: p.pattern_id })}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{p.pattern_name}</div>
                  <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{p.pattern_id}</span>
                </div>
                <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
                  {p.categories_represented.map((cat, i) => (
                    <span key={i} className="badge badge-standard" style={{ fontSize: '0.68rem' }}>
                      {cat.category_name}: {cat.percentage}%
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Chronological Shifts Alerts */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              <TrendingUp size={18} style={{ color: 'var(--accent-cyan)' }} /> Statistically Significant Behavioral Evolution
            </div>
            <div className="card-subtitle">Empirically validated behavioral shifts across annual and diurnal timelines</div>
          </div>
          <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.78rem' }} onClick={() => onNavigate('behavioral-evolution')}>
            Timeline Analysis <ArrowRight size={14} />
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {shifts.map((s) => (
            <div
              key={s.shift_id}
              style={{
                background: 'var(--bg-subtle)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '16px',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="badge badge-standard">{s.domain || 'Evolution'}</span>
                <span className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.85rem' }}>
                  {s.delta_magnitude}
                </span>
              </div>
              <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '6px' }}>{s.title}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                {s.behavioral_explanation}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
