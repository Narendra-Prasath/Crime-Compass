import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { PatternCardSummary, PatternDetailViewResponse } from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import {
  Layers,
  ChevronRight,
  ArrowLeft,
  Clock,
  Shield,
  ShieldAlert,
  Sparkles,
  Calendar,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Activity,
  Compass,
  TrendingUp,
  FileText,
  Search,
  Hash
} from 'lucide-react';

interface BehavioralPatternsPageProps {
  initialClusterId?: number;
  onNavigate?: (page: string, params?: any) => void;
}

export const BehavioralPatternsPage: React.FC<BehavioralPatternsPageProps> = ({
  initialClusterId = 0,
  onNavigate,
}) => {
  const [patterns, setPatterns] = useState<PatternCardSummary[]>([]);
  const [corpusTotal, setCorpusTotal] = useState<number>(220663);
  const [selectedPatternId, setSelectedPatternId] = useState<string | null>(null);
  const [detailData, setDetailData] = useState<PatternDetailViewResponse | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAnalysisDetails, setShowAnalysisDetails] = useState(false);

  // Fetch list of clean pattern cards
  const fetchPatterns = async () => {
    setLoadingList(true);
    setError(null);
    try {
      const res = await api.getExplorePatterns();
      setPatterns(res.patterns);
      setCorpusTotal(res.corpus_incident_count);
      
      // If initialClusterId was provided, auto-load its detail if valid
      if (initialClusterId !== undefined && initialClusterId >= 0 && initialClusterId < res.patterns.length) {
        const target = res.patterns[initialClusterId];
        if (target) {
          // Open detail directly if requested
          loadDetail(target.pattern_id);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Could not load behavioral patterns');
    } finally {
      setLoadingList(false);
    }
  };

  // Fetch detailed profile for selected pattern
  const loadDetail = async (patId: string) => {
    setSelectedPatternId(patId);
    setLoadingDetail(true);
    setShowAnalysisDetails(false);
    try {
      const detail = await api.getPatternDetail(patId);
      setDetailData(detail);
    } catch (err: any) {
      console.error('Failed to load pattern detail:', err);
    } finally {
      setLoadingDetail(false);
    }
  };

  useEffect(() => {
    fetchPatterns();
  }, []);

  const handleCloseDetail = () => {
    setSelectedPatternId(null);
    setDetailData(null);
  };

  // Filter cards by search query (formula, name, categories)
  const filteredPatterns = patterns.filter((p) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      p.pattern_id.toLowerCase().includes(q) ||
      p.pattern_name.toLowerCase().includes(q) ||
      p.behavioral_formula.toLowerCase().includes(q) ||
      p.crime_categories_summary.toLowerCase().includes(q) ||
      p.key_characteristics.some((k) => k.toLowerCase().includes(q))
    );
  });

  if (loadingList) {
    return <LoadingState message="Discovering empirical behavioral patterns from 220,663 historical incidents..." />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchPatterns} />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '1280px', margin: '0 auto' }}>
      {/* Detail View Overlay / Modal */}
      {selectedPatternId && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--accent-purple-border)',
            borderRadius: 'var(--radius-lg)',
            padding: '28px',
            boxShadow: 'var(--shadow-lg)',
            animation: 'fadeIn 0.2s ease',
          }}
        >
          {loadingDetail || !detailData ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <LoadingState message={`Retrieving empirical profile for ${selectedPatternId}...`} />
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* Detail Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
                <div>
                  <button
                    onClick={handleCloseDetail}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      background: 'none',
                      border: 'none',
                      color: 'var(--accent-purple)',
                      fontSize: '0.88rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      padding: 0,
                      marginBottom: '10px',
                    }}
                  >
                    <ArrowLeft size={16} /> Back to All Patterns
                  </button>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                    <span
                      style={{
                        background: 'var(--accent-purple-bg)',
                        color: 'var(--accent-purple)',
                        border: '1px solid var(--accent-purple-border)',
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-sm)',
                        fontWeight: 800,
                        fontSize: '0.85rem',
                        letterSpacing: '0.05em',
                      }}
                      className="mono"
                    >
                      {detailData.pattern_id}
                    </span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }} className="mono">
                      CODE: {detailData.pattern_code}
                    </span>
                  </div>
                  <h1 style={{ fontSize: '1.75rem', marginTop: '6px', color: 'var(--text-main)' }}>
                    {detailData.pattern_name}
                  </h1>
                  {/* Clean Formula */}
                  <div
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                      marginTop: '8px',
                      padding: '6px 14px',
                      background: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid var(--border-bright)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '1rem',
                      fontWeight: 700,
                      color: 'var(--text-main)',
                    }}
                  >
                    <Sparkles size={16} style={{ color: 'var(--accent-cyan)' }} />
                    {detailData.behavioral_formula}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <button
                    onClick={handleCloseDetail}
                    className="btn btn-secondary"
                    style={{ padding: '8px 16px', fontSize: '0.85rem' }}
                  >
                    Close Detail View
                  </button>
                </div>
              </div>

              {/* Key Quantitative Metrics Cards */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '14px',
                }}
              >
                <div
                  style={{
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '16px',
                  }}
                >
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Supporting Incidents
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-purple)', marginTop: '4px' }}>
                    {detailData.supporting_incident_count.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {detailData.percentage_of_total.toFixed(1)}% of historical dataset
                  </div>
                </div>

                <div
                  style={{
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '16px',
                  }}
                >
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Crime Categories
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '4px' }}>
                    {detailData.crime_categories_involved.length} Categories
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Cross-category behavioral convergence
                  </div>
                </div>

                <div
                  style={{
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '16px',
                  }}
                >
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Timing Profile
                  </div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--accent-amber)', marginTop: '8px' }}>
                    {detailData.time_information}
                  </div>
                </div>

                <div
                  style={{
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '16px',
                  }}
                >
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Pattern Cohesion
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-emerald)', marginTop: '4px' }}>
                    {detailData.similarity_strength_score.toFixed(1)}%
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {detailData.similarity_strength_label}
                  </div>
                </div>
              </div>

              {/* 1. Why This Pattern Exists */}
              <div
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '20px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Compass size={18} style={{ color: 'var(--accent-cyan)' }} />
                  <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Why This Pattern Exists</h3>
                </div>
                <p style={{ color: 'var(--text-main)', fontSize: '0.92rem', lineHeight: '1.6' }}>
                  {detailData.why_this_pattern_exists}
                </p>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '8px', fontStyle: 'italic' }}>
                  {detailData.summary}
                </p>
              </div>

              {/* 2. Crime Categories Involved */}
              <div
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '20px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                  <Layers size={18} style={{ color: 'var(--accent-purple)' }} />
                  <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Crime Categories Involved</h3>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
                  {detailData.crime_categories_involved.map((cat, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '12px 16px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.9rem' }}>
                          {cat.category_name}
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                          {cat.incident_count.toLocaleString()} historical incidents
                        </div>
                      </div>
                      <span
                        style={{
                          background: 'var(--accent-cyan-bg)',
                          color: 'var(--accent-cyan)',
                          border: '1px solid var(--accent-cyan-border)',
                          padding: '3px 8px',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.8rem',
                          fontWeight: 700,
                        }}
                        className="mono"
                      >
                        {cat.percentage.toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* 3. Behavioral Characteristics */}
              <div
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '20px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                  <Activity size={18} style={{ color: 'var(--accent-emerald)' }} />
                  <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Behavioral Characteristics</h3>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
                  {Object.entries(detailData.behavioral_characteristics).map(([groupKey, groupVals]: [string, any], idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '14px',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.78rem',
                          fontWeight: 700,
                          color: 'var(--accent-emerald)',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                          marginBottom: '8px',
                        }}
                      >
                        {groupKey.replace(/_/g, ' ')}
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {typeof groupVals === 'object' && groupVals !== null ? (
                          Object.entries(groupVals).map(([propKey, propVal]: [string, any], pIdx) => (
                            <div
                              key={pIdx}
                              style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                fontSize: '0.82rem',
                                color: 'var(--text-muted)',
                              }}
                            >
                              <span>{propKey.replace(/_/g, ' ')}:</span>
                              <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>
                                {typeof propVal === 'number' ? (propVal > 1 ? propVal.toFixed(1) : `${(propVal * 100).toFixed(1)}%`) : String(propVal)}
                              </span>
                            </div>
                          ))
                        ) : (
                          <span style={{ fontSize: '0.82rem', color: 'var(--text-main)' }}>{String(groupVals)}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 4. Behavioral Evolution Timeline (3 Stages) */}
              <div
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '20px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <TrendingUp size={18} style={{ color: 'var(--accent-amber)' }} />
                  <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Behavioral Evolution Over Time</h3>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
                  Behavioral characteristics changed over the observed historical dataset period.
                </p>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '16px',
                    position: 'relative',
                  }}
                >
                  {detailData.evolution_timeline.map((stage, idx) => (
                    <div
                      key={stage.stage_id}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-bright)',
                        borderRadius: 'var(--radius-md)',
                        padding: '16px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span
                          style={{
                            fontSize: '0.75rem',
                            fontWeight: 800,
                            letterSpacing: '0.08em',
                            textTransform: 'uppercase',
                            color: idx === 0 ? 'var(--accent-cyan)' : idx === 1 ? 'var(--accent-amber)' : 'var(--accent-purple)',
                          }}
                        >
                          {stage.period_label}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }} className="mono">
                          {stage.time_range}
                        </span>
                      </div>

                      <div
                        style={{
                          fontWeight: 700,
                          fontSize: '0.95rem',
                          color: 'var(--text-main)',
                          padding: '6px 10px',
                          background: 'rgba(255, 255, 255, 0.03)',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--border-subtle)',
                        }}
                      >
                        {stage.behavioral_formula}
                      </div>

                      <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                        {stage.summary}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 5. Supporting Evidence */}
              <div
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '20px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                  <FileText size={18} style={{ color: 'var(--accent-cyan)' }} />
                  <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Supporting Empirical Evidence</h3>
                </div>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '12px',
                    marginBottom: '16px',
                  }}
                >
                  <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Inter-Category Similarity</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
                      {detailData.supporting_evidence.avg_inter_category_similarity_pct.toFixed(1)}%
                    </div>
                  </div>
                  <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Shannon Entropy</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }} className="mono">
                      {detailData.supporting_evidence.shannon_entropy.toFixed(3)}
                    </div>
                  </div>
                  <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Simpson Diversity</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }} className="mono">
                      {detailData.supporting_evidence.simpson_diversity.toFixed(3)}
                    </div>
                  </div>
                </div>

                {detailData.supporting_evidence.exemplar_incidents && detailData.supporting_evidence.exemplar_incidents.length > 0 && (
                  <div>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '8px' }}>
                      Exemplar Incidents Matching Centroid:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {detailData.supporting_evidence.exemplar_incidents.map((ex, exIdx) => (
                        <div
                          key={exIdx}
                          style={{
                            padding: '6px 12px',
                            background: 'var(--bg-card)',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.8rem',
                            display: 'flex',
                            gap: '8px',
                            alignItems: 'center',
                          }}
                        >
                          <span className="mono" style={{ color: 'var(--accent-purple)', fontWeight: 700 }}>
                            {ex.incident_id}
                          </span>
                          <span style={{ color: 'var(--text-muted)' }}>{ex.offense_category}</span>
                          <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>
                            {(ex.similarity * 100).toFixed(1)}% match
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 6. Technical "View Analysis Details" Collapsible Toggle */}
              <div
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-bright)',
                  borderRadius: 'var(--radius-md)',
                  overflow: 'hidden',
                }}
              >
                <button
                  type="button"
                  onClick={() => setShowAnalysisDetails(!showAnalysisDetails)}
                  style={{
                    width: '100%',
                    padding: '16px 20px',
                    background: 'none',
                    border: 'none',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    color: 'var(--text-main)',
                    fontSize: '0.92rem',
                    fontWeight: 600,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Hash size={16} style={{ color: 'var(--text-dim)' }} />
                    <span>View Analysis Details (Technical Model Weights & Features)</span>
                  </div>
                  {showAnalysisDetails ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </button>

                {showAnalysisDetails && (
                  <div style={{ padding: '0 20px 20px 20px', borderTop: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '14px 0' }}>
                      Clustering Algorithm: <strong>{detailData.analysis_details.clustering_algorithm}</strong> &bull; Distance Metric: <strong>{detailData.analysis_details.distance_metric}</strong> &bull; DNA Dimensions: <strong>{detailData.analysis_details.vector_dimension}D</strong>
                    </div>

                    <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '8px' }}>
                      Top Distinctive Cluster Feature Divergences:
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {detailData.analysis_details.top_distinctive_features.map((feat, fIdx) => (
                        <div
                          key={fIdx}
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: '6px 10px',
                            background: 'var(--bg-subtle)',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.8rem',
                            fontFamily: 'var(--font-mono)',
                          }}
                        >
                          <span style={{ color: 'var(--text-main)' }}>{feat.feature}</span>
                          <span style={{ color: feat.difference >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                            Δ {feat.difference >= 0 ? '+' : ''}{feat.difference.toFixed(3)} (Cluster: {feat.cluster_mean.toFixed(3)} vs Global: {feat.global_mean.toFixed(3)})
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Ethical & Non-Offender Advisory */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px',
                  padding: '14px 18px',
                  background: 'rgba(244, 63, 94, 0.08)',
                  border: '1px solid var(--accent-rose-border)',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <ShieldAlert size={18} style={{ color: 'var(--accent-rose)', flexShrink: 0, marginTop: '2px' }} />
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                  <strong style={{ color: 'var(--text-main)' }}>Scientific Advisory: </strong>
                  {detailData.ethical_advisory}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Main Page Content (Header + Cards Grid) */}
      {!selectedPatternId && (
        <>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <span
                  style={{
                    background: 'var(--accent-purple-bg)',
                    color: 'var(--accent-purple)',
                    border: '1px solid var(--accent-purple-border)',
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                  }}
                  className="mono"
                >
                  HISTORICAL DATASET PATTERNS
                </span>
                <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>
                  {corpusTotal.toLocaleString()} Incidents Indexed
                </span>
              </div>
              <h1 style={{ fontSize: '2rem', letterSpacing: '-0.02em', color: 'var(--text-main)' }}>
                Explore Behavioral Patterns
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '6px', maxWidth: '780px' }}>
                Modus operandi patterns discovered from the 220,663 incident historical dataset. Each pattern represents an unsupervised behavioral archetype spanning multiple crime categories.
              </p>
            </div>

            {/* Quick Search Input */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '8px 14px',
                  minWidth: '240px',
                }}
              >
                <Search size={16} style={{ color: 'var(--text-dim)' }} />
                <input
                  type="text"
                  placeholder="Filter by formula or trait..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    background: 'none',
                    border: 'none',
                    outline: 'none',
                    color: 'var(--text-main)',
                    fontSize: '0.88rem',
                    width: '100%',
                  }}
                />
              </div>
            </div>
          </div>

          {/* Clean Pattern Cards Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
              gap: '20px',
            }}
          >
            {filteredPatterns.map((pat) => (
              <div
                key={pat.pattern_id}
                onClick={() => loadDetail(pat.pattern_id)}
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '22px',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '14px',
                  transition: 'all 0.18s cubic-bezier(0.16, 1, 0.3, 1)',
                  boxShadow: 'var(--shadow-sm)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--accent-purple)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                }}
              >
                {/* Card Header: Pattern ID & Incident Count */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span
                      style={{
                        background: 'var(--accent-purple-bg)',
                        color: 'var(--accent-purple)',
                        border: '1px solid var(--accent-purple-border)',
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-sm)',
                        fontWeight: 800,
                        fontSize: '0.8rem',
                      }}
                      className="mono"
                    >
                      {pat.pattern_id}
                    </span>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }} className="mono">
                      {pat.pattern_code}
                    </span>
                  </div>

                  <span
                    style={{
                      fontSize: '0.8rem',
                      color: 'var(--text-dim)',
                      fontWeight: 600,
                    }}
                  >
                    {pat.supporting_incident_count.toLocaleString()} incidents
                  </span>
                </div>

                {/* Pattern Title */}
                <div>
                  <h2 style={{ fontSize: '1.15rem', color: 'var(--text-main)', lineHeight: '1.3' }}>
                    {pat.pattern_name}
                  </h2>
                </div>

                {/* Behavioral Formula Block */}
                <div
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-bright)',
                    borderRadius: 'var(--radius-md)',
                    padding: '10px 14px',
                    fontSize: '0.92rem',
                    fontWeight: 700,
                    color: 'var(--text-main)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <Sparkles size={15} style={{ color: 'var(--accent-cyan)', flexShrink: 0 }} />
                  <span>{pat.behavioral_formula}</span>
                </div>

                {/* Crime Categories Summary */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Layers size={14} style={{ color: 'var(--accent-purple)' }} />
                  <span style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    {pat.crime_categories_summary}
                  </span>
                </div>

                {/* Key Characteristics Pills */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {pat.key_characteristics.map((char, cIdx) => (
                    <span
                      key={cIdx}
                      style={{
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-sm)',
                        background: 'var(--bg-subtle)',
                        border: '1px solid var(--border-subtle)',
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                      }}
                    >
                      {char}
                    </span>
                  ))}
                </div>

                {/* Card Footer: Timing & Strength & Click Hint */}
                <div
                  style={{
                    marginTop: 'auto',
                    paddingTop: '12px',
                    borderTop: '1px solid var(--border-subtle)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '0.78rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--text-dim)' }}>
                    <Clock size={13} />
                    <span>{pat.time_information.split('(')[0].trim()}</span>
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      color: 'var(--accent-purple)',
                      fontWeight: 600,
                    }}
                  >
                    <span>View Detail</span>
                    <ChevronRight size={14} />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredPatterns.length === 0 && (
            <div
              style={{
                textAlign: 'center',
                padding: '48px',
                background: 'var(--bg-card)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
                No behavioral patterns matched your search term "{searchQuery}".
              </p>
              <button
                onClick={() => setSearchQuery('')}
                className="btn btn-secondary"
                style={{ marginTop: '12px' }}
              >
                Clear Filter
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
