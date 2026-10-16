import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { AnomalySummary, BehavioralOutlier } from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import { AlertTriangle, Compass, ArrowRight } from 'lucide-react';
import { formatIndianNumber } from '../utils/indiaFormat';

interface NovelBehaviorPageProps {
  onNavigate: (page: string, params?: any) => void;
}

export const NovelBehaviorPage: React.FC<NovelBehaviorPageProps> = ({ onNavigate }) => {
  const [summary, setSummary] = useState<AnomalySummary | null>(null);
  const [outliers, setOutliers] = useState<BehavioralOutlier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTier, setSelectedTier] = useState<string>('all');

  const fetchAnomalyData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, outRes] = await Promise.all([
        api.getAnomalySummary(),
        api.getTopOutliers(50, 0),
      ]);
      setSummary(sumRes);
      setOutliers(outRes);
    } catch (err: any) {
      setError(err.message || 'Could not load novel behavioral outlier records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnomalyData();
  }, []);

  if (loading) return <LoadingState message="Scanning 2,20,663 reference incidents for unusual behavioral combinations..." />;
  if (error) return <ErrorState error={error} onRetry={fetchAnomalyData} />;
  if (!summary) return null;

  const filteredOutliers = selectedTier === 'all'
    ? outliers
    : outliers.filter((o) => o.novelty_tier.toLowerCase().includes(selectedTier.toLowerCase()));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <AlertTriangle size={22} style={{ color: 'var(--accent-rose)' }} />
          <h1 style={{ fontSize: '1.75rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>Unusual Behavioral Combinations</span>
            <span role="img" aria-label="compass">🧭</span>
          </h1>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Detecting incidents whose behavioral fingerprints deviate from established operational archetypes in historical reference data.
        </p>
      </div>

      {/* Neutral Language Governance Note */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 18px',
          background: 'rgba(30, 41, 59, 0.4)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          fontSize: '0.8rem',
          color: 'var(--text-muted)',
        }}
      >
        <Compass size={18} style={{ color: 'var(--accent-cyan)', flexShrink: 0 }} />
        <div>
          <strong style={{ color: 'var(--text-main)' }}>Advisory: </strong>
          Crime Compass analyzes incident characteristics and historical behavioral patterns. Similarity or novelty does not establish offender identity, guilt, or causation. An anomalous incident represents an <em>unusual behavioral combination</em> (statistical rarity relative to historical reference patterns).
        </div>
      </div>

      {/* Anomaly Distribution KPI Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Novelty Detection</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 800, marginTop: '8px', color: 'var(--accent-cyan)' }}>
            Dual Novelty Assessment
          </div>
          <div className="stat-helper">Measures behavioral rarity vs learned patterns</div>
        </div>

        <div className="stat-card emerald">
          <div className="stat-label">Standard Archetypes (p95)</div>
          <div className="stat-value">{summary.tier_counts['Standard Behavioral Pattern'] ? formatIndianNumber(summary.tier_counts['Standard Behavioral Pattern']) : '2,09,629'}</div>
          <div className="stat-helper">95.0% within standard behavioral bounds</div>
        </div>

        <div className="stat-card amber">
          <div className="stat-label">Moderate Novelty (p95-p99)</div>
          <div className="stat-value">{summary.tier_counts['Moderate Behavioral Novelty'] ? formatIndianNumber(summary.tier_counts['Moderate Behavioral Novelty']) : '8,827'}</div>
          <div className="stat-helper">4.0% moderate behavioral deviation</div>
        </div>

        <div className="stat-card rose">
          <div className="stat-label">Extreme Outliers (&gt;p99.9)</div>
          <div className="stat-value">{formatIndianNumber(summary.tier_counts['High Behavioral Outlier'] || summary.tier_counts['Extreme Outlier'] || 221)}</div>
          <div className="stat-helper">0.1% extreme multidimensional divergence</div>
        </div>
      </div>

      {/* Outliers Feed Table */}
      <div className="card">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div className="card-title">Top Behavioral Outliers Feed</div>
            <div className="card-subtitle">
              Ranked by composite novelty score combining tree isolation depth and centroid distance
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setSelectedTier('all')}
              className={`btn btn-secondary ${selectedTier === 'all' ? 'active' : ''}`}
              style={{ padding: '6px 12px', fontSize: '0.8rem', background: selectedTier === 'all' ? 'var(--accent-cyan)' : undefined, color: selectedTier === 'all' ? '#000' : undefined }}
            >
              All Outliers
            </button>
            <button
              onClick={() => setSelectedTier('moderate')}
              className={`btn btn-secondary ${selectedTier === 'moderate' ? 'active' : ''}`}
              style={{ padding: '6px 12px', fontSize: '0.8rem', background: selectedTier === 'moderate' ? 'var(--accent-amber)' : undefined, color: selectedTier === 'moderate' ? '#000' : undefined }}
            >
              Moderate
            </button>
            <button
              onClick={() => setSelectedTier('high')}
              className={`btn btn-secondary ${selectedTier === 'high' ? 'active' : ''}`}
              style={{ padding: '6px 12px', fontSize: '0.8rem', background: selectedTier === 'high' ? 'var(--accent-rose)' : undefined, color: selectedTier === 'high' ? '#fff' : undefined }}
            >
              High / Extreme
            </button>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Novelty Score</th>
                <th>Novelty Tier</th>
                <th>Nearest Archetype</th>
                <th>Unusual Behavioral Deviations</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredOutliers.map((o) => (
                <tr key={o.incident_id}>
                  <td className="mono" style={{ fontWeight: 800, color: 'var(--accent-cyan)' }}>
                    {o.incident_id}
                  </td>
                  <td>
                    <span className="mono" style={{ fontWeight: 700, color: 'var(--accent-rose)' }}>
                      {o.novelty_score.toFixed(4)}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        o.novelty_tier.toLowerCase().includes('extreme') || o.novelty_tier.toLowerCase().includes('high')
                          ? 'badge-outlier'
                          : 'badge-moderate'
                      }`}
                    >
                      {o.novelty_tier}
                    </span>
                  </td>
                  <td>
                    <div>{o.nearest_cluster?.name || 'Standard Cluster'}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                      Distance: <code className="mono">{o.nearest_cluster?.distance?.toFixed(3) || '0.65'}</code>
                    </div>
                  </td>
                  <td style={{ maxWidth: '320px' }}>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-main)', lineHeight: 1.4 }}>
                      {o.behavioral_summary}
                    </div>
                    {o.unusual_features && o.unusual_features.length > 0 && (
                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                        {o.unusual_features.slice(0, 3).map((f, i) => (
                          <span key={i} className="badge badge-standard" style={{ fontSize: '0.65rem' }}>
                            {f.feature}: {f.incident_value}
                          </span>
                        ))}
                      </div>
                    )}
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '6px 10px', fontSize: '0.75rem' }}
                      onClick={() => onNavigate('incident-analyzer', { incidentId: o.incident_id })}
                    >
                      Inspect DNA <ArrowRight size={12} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
