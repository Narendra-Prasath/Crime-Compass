import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { CrossCrimePatternSummary, CrossCrimePatternDetail } from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import { Network, ArrowRight, Info } from 'lucide-react';

interface CrossCrimePageProps {
  initialPatternId?: string;
  onNavigate: (page: string, params?: any) => void;
}

export const CrossCrimePage: React.FC<CrossCrimePageProps> = ({
  initialPatternId = 'CCP_00',
  onNavigate,
}) => {
  const [patterns, setPatterns] = useState<CrossCrimePatternSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string>(initialPatternId);
  const [detail, setDetail] = useState<CrossCrimePatternDetail | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPatterns = async () => {
    setLoadingList(true);
    setError(null);
    try {
      const list = await api.getCrossCrimePatterns();
      setPatterns(list);
      if (list.length > 0 && !selectedId) {
        setSelectedId(list[0].pattern_id);
      }
    } catch (err: any) {
      setError(err.message || 'Could not load cross-crime patterns');
    } finally {
      setLoadingList(false);
    }
  };

  const fetchDetail = async (pid: string) => {
    setLoadingDetail(true);
    try {
      const data = await api.getCrossCrimeDetail(pid);
      setDetail(data);
      setSelectedId(pid);
    } catch (err: any) {
      setError(err.message || `Could not load details for ${pid}`);
    } finally {
      setLoadingDetail(false);
    }
  };

  useEffect(() => {
    fetchPatterns();
  }, []);

  useEffect(() => {
    if (selectedId) {
      fetchDetail(selectedId);
    }
  }, [selectedId]);

  if (loadingList) return <LoadingState message="Mapping cross-crime behavioral connections..." />;
  if (error) return <ErrorState error={error} onRetry={fetchPatterns} />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Network size={22} style={{ color: 'var(--accent-amber)' }} />
            <h1 style={{ fontSize: '1.75rem' }}>Cross-Crime Behavioral Connections</h1>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Uncovering incidents classified under different legal categories that share similar operational Behavioral DNA.
          </p>
        </div>
        <div>
          <button
            onClick={() => onNavigate('connection-map', { patternId: selectedId })}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', padding: '8px 14px' }}
          >
            <Network size={15} style={{ color: 'var(--accent-amber)' }} />
            <span>Open Interactive Connection Map &rarr;</span>
          </button>
        </div>
      </div>

      {/* Grid: Patterns Navigation on Left, Pattern Details on Right */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 340px) 1fr', gap: '24px' }}>
        {/* Left Column: Pattern Selectors */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {patterns.map((p) => {
            const isSelected = p.pattern_id === selectedId;
            return (
              <div
                key={p.pattern_id}
                onClick={() => setSelectedId(p.pattern_id)}
                style={{
                  background: isSelected ? 'var(--accent-amber-bg)' : 'var(--bg-card)',
                  border: `1px solid ${isSelected ? 'var(--accent-amber-border)' : 'var(--border-subtle)'}`,
                  borderRadius: 'var(--radius-md)',
                  padding: '16px 18px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span className="mono" style={{ fontWeight: 800, color: 'var(--accent-amber)', fontSize: '0.82rem' }}>
                    {p.pattern_id}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    Behavioral Pattern #{p.cluster_id + 1}
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-main)' }}>
                  {p.pattern_name}
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '10px' }}>
                  {p.categories_represented.map((cat, i) => (
                    <span key={i} className="badge badge-standard" style={{ fontSize: '0.65rem' }}>
                      {cat.category_name}: {cat.percentage}%
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Detailed Cross-Crime Evidence */}
        <div>
          {loadingDetail && <LoadingState message="Loading cross-crime pattern evidence..." />}
          {!loadingDetail && detail && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Pattern Header Card */}
              <div
                className="card"
                style={{
                  background: 'linear-gradient(135deg, var(--bg-card) 0%, rgba(245, 158, 11, 0.06) 100%)',
                  borderTop: '4px solid var(--accent-amber)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                  <div>
                    <span className="mono" style={{ fontSize: '0.85rem', color: 'var(--accent-amber)', fontWeight: 800 }}>
                      {detail.pattern_id} • Behavioral Pattern #{detail.cluster_id + 1}
                    </span>
                    <h2 style={{ fontSize: '1.4rem', marginTop: '4px' }}>{detail.pattern_name}</h2>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Total Incidents</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-heading)' }}>
                      {detail.total_incidents.toLocaleString()}
                    </div>
                  </div>
                </div>

                {/* Categories Represented Distribution Bar */}
                <div style={{ marginTop: '20px' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px', fontWeight: 600 }}>
                    Legal Categories Sharing Identical Behavior
                  </div>
                  <div style={{ display: 'flex', height: '10px', borderRadius: '5px', overflow: 'hidden', gap: '2px', background: 'var(--bg-subtle)' }}>
                    {detail.categories_represented.map((cat, idx) => {
                      const colors = ['#0ea5e9', '#f59e0b', '#f43f5e', '#a855f7'];
                      return (
                        <div
                          key={idx}
                          title={`${cat.category_name}: ${cat.percentage}%`}
                          style={{
                            width: `${Math.max(1, cat.percentage)}%`,
                            backgroundColor: colors[idx % colors.length],
                          }}
                        />
                      );
                    })}
                  </div>

                  <div style={{ display: 'flex', gap: '16px', marginTop: '10px', flexWrap: 'wrap' }}>
                    {detail.categories_represented.map((cat, idx) => {
                      const colors = ['#0ea5e9', '#f59e0b', '#f43f5e', '#a855f7'];
                      return (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem' }}>
                          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: colors[idx % colors.length] }}></span>
                          <span style={{ fontWeight: 600 }}>{cat.category_name}:</span>
                          <span className="mono" style={{ color: 'var(--text-muted)' }}>
                            {cat.incident_count.toLocaleString()} ({cat.percentage}%)
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Dominant Shared Characteristics */}
              <div className="card">
                <div className="card-header">
                  <div className="card-title">Shared Operational Modus Operandi (MO)</div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
                  {Object.entries(detail.dominant_behavioral_characteristics).map(([key, val]) => (
                    <div
                      key={key}
                      style={{
                        background: 'var(--bg-subtle)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        padding: '12px 14px',
                      }}
                    >
                      <div style={{ fontSize: '0.72rem', color: 'var(--accent-amber)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '8px' }}>
                        {key.replace(/_/g, ' ')}
                      </div>
                      {typeof val === 'object' && val !== null ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                          {Object.entries(val).map(([subKey, subVal]) => (
                            <div key={subKey} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                              <span style={{ color: 'var(--text-muted)' }}>{subKey.replace(/_/g, ' ')}:</span>
                              <span className="mono" style={{ fontWeight: 600, color: 'var(--text-main)' }}>{String(subVal)}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ fontSize: '0.82rem', color: 'var(--text-main)', marginTop: '4px', lineHeight: 1.4 }}>
                          {String(val)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Exemplar Incidents */}
              <div className="card">
                <div className="card-header">
                  <div>
                    <div className="card-title">Cross-Category Exemplar Incidents</div>
                    <div className="card-subtitle">Real incidents showing identical behavior across statutory classifications</div>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
                  {detail.exemplar_incidents.map((ex) => (
                    <div
                      key={ex.incident_id}
                      style={{
                        background: 'var(--bg-subtle)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        padding: '14px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <span className="mono" style={{ fontWeight: 800, color: 'var(--accent-cyan)' }}>
                          {ex.incident_id}
                        </span>
                        <span className="badge badge-property">{ex.crime_category}</span>
                      </div>
                      <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '8px' }}>
                        {ex.category_description}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                        {Object.entries(ex.behavioral_highlights).map(([k, v]) => (
                          <div key={k}>
                            <strong style={{ color: 'var(--text-dim)' }}>{k.replace(/_/g, ' ')}:</strong> {String(v)}
                          </div>
                        ))}
                      </div>

                      <button
                        className="btn btn-secondary"
                        style={{ marginTop: '12px', width: '100%', fontSize: '0.75rem', justifyContent: 'center' }}
                        onClick={() => onNavigate('incident-analyzer', { incidentId: ex.incident_id })}
                      >
                        Inspect Behavioral Fingerprint <ArrowRight size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Cross-Crime Evidence & Finding */}
              {detail.cross_crime_evidence && (
                <div
                  style={{
                    background: 'rgba(14, 165, 233, 0.06)',
                    border: '1px solid var(--accent-cyan-border)',
                    borderRadius: 'var(--radius-md)',
                    padding: '16px 20px',
                    fontSize: '0.84rem',
                    lineHeight: 1.6,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-cyan)', fontWeight: 700, marginBottom: '6px' }}>
                    <Info size={16} /> Behavioral Pattern Finding
                  </div>
                  <div>{detail.cross_crime_evidence.finding || 'Shared operational indicators characterize these disparate historical incidents.'}</div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Mandatory Scientific Advisory */}
      <div
        style={{
          marginTop: '16px',
          padding: '12px 18px',
          background: 'rgba(59, 130, 246, 0.05)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}
      >
        <Info size={18} style={{ color: '#60a5fa', flexShrink: 0 }} />
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
          <strong style={{ color: '#93c5fd' }}>Advisory: </strong>
          Crime Compass analyzes incident characteristics and historical behavioral patterns. Similarity or novelty does not establish offender identity, guilt, or causation.
        </div>
      </div>
    </div>
  );
};
