import React, { useState, useEffect } from 'react';
import { api } from '../api';
import type { EvolutionTimeline, SignificantShift } from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import { TrendingUp, Activity } from 'lucide-react';

interface BehavioralEvolutionPageProps {
  onNavigate: (page: string, params?: any) => void;
}

const FEATURE_NAMES: Record<string, string> = {
  is_night: 'Nocturnal Crime Proportion (is_night)',
  has_weapon: 'Weapon Involvement Share (has_weapon)',
  has_injury: 'Injury / Victim Harm Share (has_injury)',
  has_arrest: 'On-Scene Arrest Rate (has_arrest)',
  has_drug: 'Drug Nexus Incident Share (has_drug)',
  crime_against_person: 'Crime Against Person Share (violent)',
};

export const BehavioralEvolutionPage: React.FC<BehavioralEvolutionPageProps> = () => {
  const [timeline, setTimeline] = useState<EvolutionTimeline | null>(null);
  const [shifts, setShifts] = useState<SignificantShift[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFeature, setActiveFeature] = useState<string>('is_night');

  const fetchEvolutionData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [tRes, sRes] = await Promise.all([
        api.getEvolutionTimeline(),
        api.getSignificantShifts(),
      ]);
      setTimeline(tRes);
      setShifts(sRes);
    } catch (err: any) {
      setError(err.message || 'Could not load behavioral evolution metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvolutionData();
  }, []);

  if (loading) return <LoadingState message="Aggregating chronological behavioral trajectories and ANOVA tests..." />;
  if (error) return <ErrorState error={error} onRetry={fetchEvolutionData} />;
  if (!timeline) return null;

  const months: string[] = timeline.feature_timeline?.months || [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];

  const seriesDict = timeline.feature_timeline?.series || {};
  const currentSeries = seriesDict[activeFeature] || { values: [] };
  const values: number[] = currentSeries.values || [];

  const minVal = values.length > 0 ? Math.min(...values) : 0;
  const maxVal = values.length > 0 ? Math.max(...values) : 100;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <TrendingUp size={22} style={{ color: 'var(--accent-cyan)' }} />
          <h1 style={{ fontSize: '1.75rem' }}>Behavioral Evolution Over Time</h1>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Chronological analysis of population-level behavioral pattern changes across seasonal and annual epochs.
        </p>
      </div>

      {/* Statistically Significant Shifts Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Statistically Significant Behavioral Shifts</div>
            <div className="card-subtitle">
              Empirically verified shifts using ANOVA F-tests, regression trends, and &chi;&sup2; test of independence
            </div>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Shift ID</th>
                <th>Behavioral Phenomenon</th>
                <th>Baseline</th>
                <th>Peak</th>
                <th>Delta</th>
                <th>Significance</th>
                <th>Empirical Mechanism</th>
              </tr>
            </thead>
            <tbody>
              {shifts.map((s) => (
                <tr key={s.shift_id}>
                  <td className="mono" style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>
                    {s.shift_id}
                  </td>
                  <td style={{ fontWeight: 600 }}>{s.title}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{s.baseline_period}</td>
                  <td style={{ color: 'var(--text-main)' }}>{s.peak_period}</td>
                  <td className="mono" style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>
                    {s.delta_magnitude}
                  </td>
                  <td>
                    <span className="badge badge-standard" style={{ fontSize: '0.7rem' }}>
                      {s.statistical_significance}
                    </span>
                  </td>
                  <td style={{ maxWidth: '340px', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                    {s.behavioral_explanation}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dynamic 12-Month Temporal Trajectory from Backend */}
      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div className="card-title">Chronological Feature Trajectory (12 Months)</div>
            <div className="card-subtitle">
              Monthly behavioral proportion across {timeline.metadata?.total_incidents?.toLocaleString() || '220,663'} crime incidents
            </div>
          </div>

          {/* Feature Selector Tabs */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {Object.keys(seriesDict).map((fKey) => (
              <button
                key={fKey}
                type="button"
                className={`btn ${activeFeature === fKey ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '4px 10px', fontSize: '0.72rem' }}
                onClick={() => setActiveFeature(fKey)}
              >
                {fKey.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>

        <div style={{ padding: '20px 0 10px' }}>
          <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '14px' }}>
            {FEATURE_NAMES[activeFeature] || activeFeature}
          </div>

          {/* SVG Bar Chart for 12 months with Real Empirical Backend Percentages */}
          <div style={{ display: 'flex', alignItems: 'flex-end', height: '180px', gap: '14px', paddingBottom: '30px', borderBottom: '1px solid var(--border-subtle)', position: 'relative' }}>
            {values.map((pct, idx) => {
              const heightPct = Math.max(12, Math.min(100, ((pct - (minVal * 0.85)) / (maxVal * 1.15 - (minVal * 0.85))) * 100));
              const isPeak = pct === maxVal;
              const isTrough = pct === minVal;

              return (
                <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                  <div
                    style={{
                      width: '100%',
                      height: `${heightPct}%`,
                      backgroundColor: isPeak ? 'var(--accent-cyan)' : isTrough ? 'var(--accent-amber)' : 'var(--bg-subtle)',
                      borderTop: `2px solid ${isPeak ? '#38bdf8' : isTrough ? '#fbbf24' : 'var(--border-subtle)'}`,
                      borderRadius: '4px 4px 0 0',
                      transition: 'all 0.2s ease',
                      position: 'relative',
                    }}
                    title={`${months[idx]}: ${pct.toFixed(2)}%`}
                  >
                    <span
                      className="mono"
                      style={{
                        position: 'absolute',
                        top: '-20px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        color: isPeak ? 'var(--accent-cyan)' : 'var(--text-muted)',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {pct.toFixed(1)}%
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '8px' }}>
                    {typeof months[idx] === 'string' ? months[idx].slice(0, 3) : `M${idx + 1}`}
                  </span>
                </div>
              );
            })}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            <div>
              Baseline Low: <strong style={{ color: 'var(--accent-amber)' }}>{minVal.toFixed(2)}%</strong>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Activity size={13} style={{ color: 'var(--accent-cyan)' }} />
              <span>Real empirical monthly trend extracted from Behavioral DNA features</span>
            </div>
            <div>
              Observed Peak: <strong style={{ color: 'var(--accent-cyan)' }}>{maxVal.toFixed(2)}%</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Cluster Evolution Overview */}
      {timeline.cluster_timeline?.series && Array.isArray(timeline.cluster_timeline.series) && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">Behavioral Pattern Stability Across 12 Months</div>
          </div>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Behavioral Pattern</th>
                  <th>Jan</th>
                  <th>Mar</th>
                  <th>Jun</th>
                  <th>Sep</th>
                  <th>Dec</th>
                  <th>Annual Avg</th>
                </tr>
              </thead>
              <tbody>
                {timeline.cluster_timeline.series.map((c: any) => {
                  const p = c.percentages || [];
                  const avg = p.length > 0 ? p.reduce((a: number, b: number) => a + b, 0) / p.length : 0;
                  return (
                    <tr key={c.cluster_id}>
                      <td style={{ fontWeight: 600 }}>
                        <span className="mono" style={{ color: 'var(--accent-cyan)', marginRight: '6px' }}>
                          Pattern #{c.cluster_id + 1}
                        </span>
                        {c.cluster_name}
                      </td>
                      <td className="mono">{p[0] !== undefined ? `${p[0]}%` : '-'}</td>
                      <td className="mono">{p[2] !== undefined ? `${p[2]}%` : '-'}</td>
                      <td className="mono">{p[5] !== undefined ? `${p[5]}%` : '-'}</td>
                      <td className="mono">{p[8] !== undefined ? `${p[8]}%` : '-'}</td>
                      <td className="mono">{p[11] !== undefined ? `${p[11]}%` : '-'}</td>
                      <td className="mono" style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>
                        {avg.toFixed(1)}%
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
  );
};
