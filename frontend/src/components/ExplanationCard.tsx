import React from 'react';
import { SimilarityExplanation } from '../types';
import { CheckCircle2, XCircle, Info, ShieldAlert } from 'lucide-react';

interface ExplanationCardProps {
  explanation: SimilarityExplanation;
}

export const ExplanationCard: React.FC<ExplanationCardProps> = ({ explanation }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Banner: Score & Disclaimer */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(13, 19, 31, 0.9) 100%)',
          border: '1px solid var(--accent-cyan-border)',
          borderRadius: 'var(--radius-lg)',
          padding: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Mathematical Behavioral Alignment
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginTop: '4px' }}>
            <span style={{ fontSize: '2.5rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--accent-cyan)' }}>
              {Math.round(explanation.similarity_score_pct)}%
            </span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Cosine Inner Product: <code className="mono">{explanation.cosine_similarity_raw.toFixed(4)}</code>
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <div style={{ background: 'var(--bg-card)', padding: '8px 14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Incident A</div>
            <div className="mono" style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{explanation.incident_pair[0]}</div>
          </div>
          <div style={{ background: 'var(--bg-card)', padding: '8px 14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Incident B</div>
            <div className="mono" style={{ fontWeight: 700, color: 'var(--accent-rose)' }}>{explanation.incident_pair[1]}</div>
          </div>
        </div>
      </div>

      {/* WHY SIMILAR? Behavioral Alignment Card */}
      <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-bright)', letterSpacing: '0.02em' }}>
            WHY SIMILAR?
          </h3>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Behavioral Domain Alignment & Scientific Decomposition
          </span>
        </div>

        {/* Behavioral Group Checkmarks / Triangles */}
        {explanation.behavioral_group_comparisons && explanation.behavioral_group_comparisons.length > 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '10px' }}>
            {explanation.behavioral_group_comparisons.map((comp) => (
              <div
                key={comp.group_key}
                style={{
                  padding: '12px 14px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-subtle)',
                  border: comp.status === 'match' ? '1px solid rgba(16, 185, 129, 0.25)' : '1px solid rgba(245, 158, 11, 0.25)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '8px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    fontWeight: 800,
                    fontSize: '1rem',
                    color: comp.status === 'match' ? 'var(--accent-emerald)' : 'var(--accent-amber)'
                  }}>
                    {comp.indicator}
                  </span>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-bright)' }}>
                      {comp.raw_label || comp.label}
                    </div>
                    {comp.details && (
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                        {comp.details}
                      </div>
                    )}
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span
                    style={{
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: '4px',
                      background: comp.match_tier === 'Strong match'
                        ? 'rgba(16, 185, 129, 0.15)'
                        : (comp.match_tier === 'Moderate match' ? 'rgba(56, 189, 248, 0.15)' : 'rgba(245, 158, 11, 0.15)'),
                      color: comp.match_tier === 'Strong match'
                        ? 'var(--accent-emerald)'
                        : (comp.match_tier === 'Moderate match' ? 'var(--accent-cyan)' : 'var(--accent-amber)')
                    }}
                  >
                    {comp.match_tier}
                  </span>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                    {comp.share_percentage}% share
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Plain-English Explanation Banner */}
        {explanation.plain_english_explanation && (
          <div
            style={{
              padding: '16px 18px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(14, 165, 233, 0.08) 100%)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              fontSize: '0.88rem',
              color: '#e0e7ff',
              lineHeight: 1.6
            }}
          >
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--accent-indigo)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
              Investigative Behavioral Summary
            </div>
            "{explanation.plain_english_explanation}"
          </div>
        )}
      </div>

      {/* Main Contributing Similarities & Differences */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {/* Main Contributing Similarities */}
        <div className="card" style={{ borderLeft: '4px solid var(--accent-emerald)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <CheckCircle2 size={18} style={{ color: 'var(--accent-emerald)' }} />
            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Main Contributing Similarities</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {explanation.main_contributing_similarities.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.84rem' }}>
                <span style={{ color: 'var(--accent-emerald)', marginTop: '2px' }}>•</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Differences */}
        <div className="card" style={{ borderLeft: '4px solid var(--accent-amber)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <XCircle size={18} style={{ color: 'var(--accent-amber)' }} />
            <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Divergences & Contrasts</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {explanation.differences.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.84rem' }}>
                <span style={{ color: 'var(--accent-amber)', marginTop: '2px' }}>•</span>
                <span style={{ color: 'var(--text-muted)' }}>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Feature Group Attribution Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Behavioral Domain Contributions</div>
            <div className="card-subtitle">
              Exact additive decomposition: each group's inner-product contribution as a percentage of the total score.
            </div>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Behavioral Domain</th>
                <th>Inner Product</th>
                <th>Share of Similarity</th>
                <th>Contribution Bar</th>
              </tr>
            </thead>
            <tbody>
              {explanation.group_contributions.map((grp) => (
                <tr key={grp.group_key}>
                  <td style={{ fontWeight: 600 }}>{grp.display_name}</td>
                  <td className="mono">{grp.absolute_contribution.toFixed(4)}</td>
                  <td className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
                    {grp.percentage_of_similarity}%
                  </td>
                  <td style={{ width: '35%' }}>
                    <div className="progress-bar-container">
                      <div className="progress-bar-fill" style={{ width: `${Math.min(100, grp.percentage_of_similarity)}%` }} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Formatted Text Summary (matches user requested format) */}
      <div className="card" style={{ background: '#0b111e' }}>
        <div className="card-header">
          <div className="card-title" style={{ fontSize: '0.9rem' }}>
            <Info size={16} /> Standard Investigative Summary Text
          </div>
        </div>
        <pre
          className="mono"
          style={{
            fontSize: '0.82rem',
            color: 'var(--text-main)',
            whiteSpace: 'pre-wrap',
            lineHeight: 1.6,
            background: 'var(--bg-app)',
            padding: '16px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          {explanation.formatted_text_summary}
        </pre>
      </div>

      {/* Disclaimer */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '14px 18px',
          background: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: 'var(--radius-md)',
          fontSize: '0.8rem',
          color: '#fcd34d',
        }}
      >
        <ShieldAlert size={20} style={{ flexShrink: 0 }} />
        <div>{explanation.disclaimer}</div>
      </div>
    </div>
  );
};
