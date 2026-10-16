import React, { useState, useEffect } from 'react';
import { api } from '../api';
import type { IncidentProfile, BehavioralDNA, SimilarIncidentsResponse, SimilarityExplanation } from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import { DNARadarChart } from '../components/DNARadarChart';
import { SubprofileBars } from '../components/SubprofileBars';
import { ArrowLeftRight, Sparkles, Shield } from 'lucide-react';

interface SimilarityViewPageProps {
  initialInc1?: string;
  initialInc2?: string;
  onNavigate: (page: string, params?: any) => void;
}

export const SimilarityViewPage: React.FC<SimilarityViewPageProps> = ({
  initialInc1 = 'INC_136975',
  initialInc2 = 'INC_145291',
  onNavigate,
}) => {
  const [inc1, setInc1] = useState(initialInc1);
  const [inc2, setInc2] = useState(initialInc2);

  const [profile1, setProfile1] = useState<IncidentProfile | null>(null);
  const [profile2, setProfile2] = useState<IncidentProfile | null>(null);
  const [dna1, setDna1] = useState<BehavioralDNA | null>(null);
  const [dna2, setDna2] = useState<BehavioralDNA | null>(null);
  const [similarData, setSimilarData] = useState<SimilarIncidentsResponse | null>(null);
  const [explanation, setExplanation] = useState<SimilarityExplanation | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPairData = async (id1: string, id2: string) => {
    if (!id1.trim() || !id2.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const [p1, p2, d1, d2, sim, exp] = await Promise.all([
        api.getIncident(id1.trim()),
        api.getIncident(id2.trim()),
        api.getIncidentDNA(id1.trim()),
        api.getIncidentDNA(id2.trim()),
        api.getSimilarIncidents(id1.trim(), 20),
        api.getExplanation(id1.trim(), id2.trim()).catch(() => null),
      ]);
      setProfile1(p1);
      setProfile2(p2);
      setDna1(d1);
      setDna2(d2);
      setSimilarData(sim);
      setExplanation(exp);
    } catch (err: any) {
      setError(err.message || 'Could not load comparative incident profiles.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPairData(initialInc1, initialInc2);
  }, [initialInc1, initialInc2]);

  // Compute exact similarity score from backend calculation (no fake fallbacks)
  const matchRecord = similarData?.matches.find((m) => m.incident_id === inc2.trim());
  const overallSim = explanation?.similarity_score_pct ?? matchRecord?.similarity_score_pct ?? null;

  // Build subprofile similarity breakdown from real backend mathematical attribution
  const subprofileBreakdown: Record<string, number> = {};
  if (matchRecord?.subprofile_similarity_pct) {
    Object.assign(subprofileBreakdown, matchRecord.subprofile_similarity_pct);
  } else if (explanation?.group_contributions) {
    for (const g of explanation.group_contributions) {
      subprofileBreakdown[g.group_key] = g.percentage_of_similarity;
    }
  }

  const handleCompare = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPairData(inc1, inc2);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem' }}>Comparative Behavioral Similarity View</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Side-by-side behavioral alignment analysis across two independent crime incidents.
          </p>
        </div>

        <button
          className="btn btn-primary"
          onClick={() => onNavigate('why-similar', { inc1, inc2 })}
        >
          <Sparkles size={16} /> Explain Mathematical Attribution (Why Similar?)
        </button>
      </div>

      {/* Selector Inputs */}
      <div className="card" style={{ padding: '16px 20px' }}>
        <form onSubmit={handleCompare} style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Incident 1:</span>
            <input
              type="text"
              value={inc1}
              onChange={(e) => setInc1(e.target.value)}
              className="search-input"
              style={{
                width: '160px',
                padding: '6px 12px',
                background: 'var(--bg-subtle)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
              }}
            />
          </div>

          <ArrowLeftRight size={18} style={{ color: 'var(--accent-cyan)' }} />

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Incident 2:</span>
            <input
              type="text"
              value={inc2}
              onChange={(e) => setInc2(e.target.value)}
              className="search-input"
              style={{
                width: '160px',
                padding: '6px 12px',
                background: 'var(--bg-subtle)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
              }}
            />
          </div>

          <button type="submit" className="btn btn-secondary">
            Compare Pair
          </button>
        </form>
      </div>

      {loading && <LoadingState message={`Computing Behavioral DNA alignment between ${inc1} and ${inc2}...`} />}
      {error && <ErrorState error={error} onRetry={() => fetchPairData(inc1, inc2)} />}

      {!loading && !error && profile1 && profile2 && dna1 && dna2 && (
        <>
          {/* Similarity Headline Card */}
          <div
            className="card"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '20px',
              background: 'linear-gradient(135deg, var(--bg-card) 0%, rgba(14, 165, 233, 0.05) 100%)',
            }}
          >
            <div>
              <span className="stat-label">Calculated Behavioral Similarity</span>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginTop: '4px' }}>
                <span className="mono" style={{ fontSize: '2.5rem', fontWeight: 900, color: 'var(--accent-cyan)' }}>
                  {overallSim !== null ? `${overallSim.toFixed(1)}%` : 'N/A'}
                </span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  Cosine vector similarity over 70 behavioral dimensions
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                className="btn btn-secondary"
                onClick={() => onNavigate('why-similar', { inc1, inc2 })}
              >
                View Detailed Attribution Breakdown
              </button>
            </div>
          </div>

          {/* Dual Profile Summary */}
          <div className="grid-2">
            {/* Incident 1 Card */}
            <div className="card" style={{ borderLeft: '4px solid var(--accent-cyan)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span className="mono" style={{ fontWeight: 800, fontSize: '1.2rem', color: 'var(--accent-cyan)' }}>
                  {profile1.incident_id}
                </span>
                <span className="badge badge-cyan">Primary Target</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
                <div><strong>Category:</strong> {profile1.context.primary_crime_category}</div>
                <div><strong>Timing:</strong> {profile1.context.incident_hour}:00 ({profile1.context.is_night ? 'Night' : 'Day'})</div>
                <div><strong>Jurisdiction Size:</strong> {profile1.context.population.toLocaleString()} pop</div>
                <div><strong>Force / Weapon:</strong> {profile1.context.has_weapon ? 'Weapon Present' : 'Unarmed'}</div>
                <div><strong>Harm / Injury:</strong> {profile1.context.has_injury ? 'Injury Sustained' : 'No Injury'}</div>
                <div><strong>Property Valuation:</strong> {profile1.context.property_value > 0 ? `$${profile1.context.property_value.toLocaleString()}` : 'None'}</div>
                <div><strong>Enforcement:</strong> {profile1.context.has_arrest ? 'Arrest Made' : 'No Arrest'}</div>
              </div>
            </div>

            {/* Incident 2 Card */}
            <div className="card" style={{ borderLeft: '4px solid var(--accent-amber)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span className="mono" style={{ fontWeight: 800, fontSize: '1.2rem', color: 'var(--accent-amber)' }}>
                  {profile2.incident_id}
                </span>
                <span className="badge badge-amber">Comparison Target</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
                <div><strong>Category:</strong> {profile2.context.primary_crime_category}</div>
                <div><strong>Timing:</strong> {profile2.context.incident_hour}:00 ({profile2.context.is_night ? 'Night' : 'Day'})</div>
                <div><strong>Jurisdiction Size:</strong> {profile2.context.population.toLocaleString()} pop</div>
                <div><strong>Force / Weapon:</strong> {profile2.context.has_weapon ? 'Weapon Present' : 'Unarmed'}</div>
                <div><strong>Harm / Injury:</strong> {profile2.context.has_injury ? 'Injury Sustained' : 'No Injury'}</div>
                <div><strong>Property Valuation:</strong> {profile2.context.property_value > 0 ? `$${profile2.context.property_value.toLocaleString()}` : 'None'}</div>
                <div><strong>Enforcement:</strong> {profile2.context.has_arrest ? 'Arrest Made' : 'No Arrest'}</div>
              </div>
            </div>
          </div>

          {/* Visual Behavioral Overlay */}
          <div className="grid-2">
            <div className="card">
              <div className="card-header">
                <span className="card-title">Behavioral DNA Comparative Overlay</span>
              </div>
              <DNARadarChart
                data={dna1.group_energies}
                compareData={dna2.group_energies}
                size={340}
              />
              <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '14px', fontSize: '0.78rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: 12, height: 12, borderRadius: 2, background: 'var(--accent-cyan)' }} />
                  <span>{profile1.incident_id}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: 12, height: 12, borderRadius: 2, background: 'var(--accent-amber)' }} />
                  <span>{profile2.incident_id}</span>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <span className="card-title">Domain Similarity Attribution</span>
              </div>
              {Object.keys(subprofileBreakdown).length > 0 ? (
                <SubprofileBars
                  breakdown={subprofileBreakdown}
                  title="Percentage Similarity Across 7 Behavioral Dimensions"
                />
              ) : (
                <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem', padding: '20px 0' }}>
                  Subprofile breakdown calculated on demand via the Why Similar? engine.
                </div>
              )}
            </div>
          </div>
        </>
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
