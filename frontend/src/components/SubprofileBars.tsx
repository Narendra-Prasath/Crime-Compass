import React from 'react';

interface SubprofileBarsProps {
  breakdown: Record<string, number>;
  title?: string;
}

const LABELS: Record<string, { label: string; color: string }> = {
  temporal_dynamics: { label: 'Temporal Dynamics (Time, Day/Night)', color: '#0ea5e9' },
  crime_characteristics: { label: 'Crime Characteristics (Category)', color: '#f43f5e' },
  location_and_environment: { label: 'Location & Environment (Jurisdiction)', color: '#10b981' },
  method_and_activity: { label: 'Method & Weapon (Force Context)', color: '#f59e0b' },
  people_and_demographics: { label: 'People & Relational Demographics', color: '#a855f7' },
  property_and_economics: { label: 'Property & Economics (Loss/Stolen)', color: '#06b6d4' },
  context_and_harm: { label: 'Harm & Enforcement (Injury/Arrest)', color: '#ec4899' },
};

export const SubprofileBars: React.FC<SubprofileBarsProps> = ({ breakdown, title }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {title && <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>{title}</div>}
      {Object.entries(breakdown).map(([key, val]) => {
        const meta = LABELS[key] || { label: key.replace(/_/g, ' '), color: 'var(--accent-cyan)' };
        const score = typeof val === 'number' ? Math.round(val * 10) / 10 : 0;
        return (
          <div key={key}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>{meta.label}</span>
              <span className="mono" style={{ color: meta.color, fontWeight: 700 }}>
                {score}%
              </span>
            </div>
            <div className="progress-bar-container">
              <div
                className="progress-bar-fill"
                style={{
                  width: `${Math.min(100, Math.max(0, score))}%`,
                  backgroundColor: meta.color,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};
