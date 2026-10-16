import React, { useState } from 'react';
import { api } from '../api';
import { ThumbsUp, ThumbsDown, CheckCircle2, Shield, Info, Send } from 'lucide-react';

interface FeedbackWidgetProps {
  targetType?: string;
  targetId?: string;
  onFeedbackSubmitted?: (feedbackId: string) => void;
  style?: React.CSSProperties;
}

const ASPECT_OPTIONS = [
  { id: 'similar_time', label: 'Similar time' },
  { id: 'similar_location', label: 'Similar location' },
  { id: 'similar_property', label: 'Similar property' },
  { id: 'similar_method', label: 'Similar method' },
  { id: 'other', label: 'Other' },
];

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({
  targetType = 'incident_analysis',
  targetId,
  onFeedbackSubmitted,
  style,
}) => {
  const [selectedUtility, setSelectedUtility] = useState<boolean | null>(null);
  const [selectedAspects, setSelectedAspects] = useState<string[]>([]);
  const [notes, setNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggleAspect = (aspectId: string) => {
    setSelectedAspects((prev) =>
      prev.includes(aspectId) ? prev.filter((a) => a !== aspectId) : [...prev, aspectId]
    );
  };

  const handleSubmit = async () => {
    if (selectedUtility === null) return;
    setSubmitting(true);
    setError(null);

    try {
      const res = await api.submitFeedback({
        is_useful: selectedUtility,
        target_type: targetType,
        target_id: targetId,
        useful_aspects: selectedAspects,
        notes: notes.trim() || undefined,
      });
      setSubmitted(true);
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted(res.feedback_id);
      }
    } catch (err: any) {
      setError(err.message || 'Could not save feedback');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div
        style={{
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid var(--accent-emerald-border)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          ...style,
        }}
      >
        <CheckCircle2 size={20} style={{ color: 'var(--accent-emerald)', flexShrink: 0 }} />
        <div>
          <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.88rem' }}>
            Thank you for your evaluation feedback.
          </div>
          <div style={{ fontSize: '0.76rem', color: 'var(--text-dim)', marginTop: '2px' }}>
            Your assessment has been recorded for human-in-the-loop validation and audit. (Model is not automatically retrained).
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '18px 22px',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
        transition: 'all 0.2s ease',
        ...style,
      }}
    >
      {/* Top Prompt Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Human-In-The-Loop Evaluation
          </div>
          <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.95rem', marginTop: '2px' }}>
            Was this behavioral match useful?
          </div>
        </div>

        {/* Thumbs Up / Down Buttons */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            onClick={() => setSelectedUtility(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: 'var(--radius-sm)',
              border: `1px solid ${selectedUtility === true ? 'var(--accent-emerald)' : 'var(--border-subtle)'}`,
              background: selectedUtility === true ? 'var(--accent-emerald-bg)' : 'var(--bg-subtle)',
              color: selectedUtility === true ? 'var(--accent-emerald)' : 'var(--text-main)',
              cursor: 'pointer',
              fontSize: '0.86rem',
              fontWeight: 600,
              transition: 'all 0.15s ease',
            }}
          >
            <ThumbsUp size={15} />
            <span>Yes</span>
          </button>

          <button
            type="button"
            onClick={() => setSelectedUtility(false)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: 'var(--radius-sm)',
              border: `1px solid ${selectedUtility === false ? 'var(--accent-rose)' : 'var(--border-subtle)'}`,
              background: selectedUtility === false ? 'var(--accent-rose-bg)' : 'var(--bg-subtle)',
              color: selectedUtility === false ? 'var(--accent-rose)' : 'var(--text-main)',
              cursor: 'pointer',
              fontSize: '0.86rem',
              fontWeight: 600,
              transition: 'all 0.15s ease',
            }}
          >
            <ThumbsDown size={15} />
            <span>No</span>
          </button>
        </div>
      </div>

      {/* Expanded Aspect Identification Section (Shown once utility is clicked) */}
      {selectedUtility !== null && (
        <div
          style={{
            paddingTop: '12px',
            borderTop: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
            animation: 'fadeIn 0.18s ease',
          }}
        >
          <div>
            <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
              Optionally identify which aspects were useful / relevant:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {ASPECT_OPTIONS.map((opt) => {
                const isChecked = selectedAspects.includes(opt.id);
                return (
                  <label
                    key={opt.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '7px',
                      background: isChecked ? 'rgba(255, 255, 255, 0.08)' : 'var(--bg-subtle)',
                      border: `1px solid ${isChecked ? 'var(--accent-cyan)' : 'var(--border-subtle)'}`,
                      padding: '5px 12px',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.82rem',
                      color: isChecked ? 'var(--text-main)' : 'var(--text-muted)',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.12s ease',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => handleToggleAspect(opt.id)}
                      style={{ cursor: 'pointer', accentColor: 'var(--accent-cyan)' }}
                    />
                    <span>{opt.label}</span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Optional Short Operational Notes */}
          <div>
            <input
              type="text"
              placeholder="Optional operational notes on why this match was or wasn't useful (no PII)..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              maxLength={500}
              style={{
                width: '100%',
                background: 'var(--bg-subtle)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '8px 12px',
                color: 'var(--text-main)',
                fontSize: '0.82rem',
                outline: 'none',
              }}
            />
          </div>

          {/* Submission and Transparency Notice */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.74rem', color: 'var(--text-dim)', maxWidth: '580px' }}>
              <Shield size={13} style={{ flexShrink: 0 }} />
              <span>
                Feedback is recorded strictly for human-in-the-loop evaluation and validation; the model is not automatically retrained.
              </span>
            </div>

            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="btn btn-primary"
              style={{ padding: '6px 16px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Send size={13} />
              <span>{submitting ? 'Saving...' : 'Submit Feedback'}</span>
            </button>
          </div>

          {error && (
            <div style={{ color: 'var(--accent-rose)', fontSize: '0.78rem' }}>
              {error}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
