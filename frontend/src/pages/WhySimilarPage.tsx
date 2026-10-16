import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { SimilarityExplanation } from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import { ExplanationCard } from '../components/ExplanationCard';
import { FeedbackWidget } from '../components/FeedbackWidget';
import { Sparkles, ArrowLeftRight, HelpCircle } from 'lucide-react';

interface WhySimilarPageProps {
  initialInc1?: string;
  initialInc2?: string;
  onNavigate: (page: string, params?: any) => void;
}

const SAMPLE_PAIRS = [
  { inc1: 'INC_136975', inc2: 'INC_145291', label: 'Cross-Crime: Assault vs Robbery' },
  { inc1: 'INC_136975', inc2: 'INC_135749', label: 'High Alignment: Domestic Assault Pair' },
  { inc1: 'INC_171133', inc2: 'INC_042891', label: 'Cross-Crime: Theft vs Drug Offense' },
];

export const WhySimilarPage: React.FC<WhySimilarPageProps> = ({
  initialInc1 = 'INC_136975',
  initialInc2 = 'INC_145291',
  onNavigate,
}) => {
  const [inc1, setInc1] = useState(initialInc1);
  const [inc2, setInc2] = useState(initialInc2);
  const [explanation, setExplanation] = useState<SimilarityExplanation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchExplanation = async (id1: string, id2: string) => {
    if (!id1.trim() || !id2.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.getExplanation(id1.trim(), id2.trim());
      setExplanation(res);
      setInc1(id1);
      setInc2(id2);
    } catch (err: any) {
      setError(err.message || `Could not compute explanation for ${id1} and ${id2}`);
      setExplanation(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExplanation(initialInc1, initialInc2);
  }, [initialInc1, initialInc2]);

  const handleRun = (e: React.FormEvent) => {
    e.preventDefault();
    fetchExplanation(inc1, inc2);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <Sparkles size={20} style={{ color: 'var(--accent-cyan)' }} />
          <h1 style={{ fontSize: '1.75rem' }}>Explainable Behavioral Similarity ("Why Similar?")</h1>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Breakdown of behavioral similarity across 7 Behavioral DNA domains and contrastive feature differences.
        </p>
      </div>

      {/* Query Bar */}
      <div className="card" style={{ padding: '16px 20px' }}>
        <form onSubmit={handleRun} style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Incident 1:</span>
            <input
              type="text"
              value={inc1}
              onChange={(e) => setInc1(e.target.value)}
              className="search-input"
              style={{
                width: '160px',
                padding: '8px 12px',
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
                padding: '8px 12px',
                background: 'var(--bg-subtle)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
              }}
            />
          </div>

          <button type="submit" className="btn btn-primary">
            Explain Similarity
          </button>
        </form>

        {/* Sample Pairs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Precomputed Sample Pairs:</span>
          {SAMPLE_PAIRS.map((pair, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-chip"
              onClick={() => {
                setInc1(pair.inc1);
                setInc2(pair.inc2);
                fetchExplanation(pair.inc1, pair.inc2);
              }}
            >
              {pair.label}
            </button>
          ))}
        </div>
      </div>

      {loading && <LoadingState message="Analyzing behavioral similarity drivers across behavioral domains..." />}
      {error && <ErrorState error={error} onRetry={() => fetchExplanation(inc1, inc2)} />}

      {!loading && !error && explanation && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <ExplanationCard explanation={explanation} />
          <FeedbackWidget
            targetType="similarity_explanation"
            targetId={`${explanation.incident_pair[0]}_${explanation.incident_pair[1]}`}
          />
        </div>
      )}
    </div>
  );
};
