import React from 'react';
import { Compass, Home, Layers, History, GitCompare, Network, ArrowRight, Fingerprint } from 'lucide-react';

interface NotFoundPageProps {
  attemptedPath?: string;
  onNavigate: (page: string) => void;
}

export const NotFoundPage: React.FC<NotFoundPageProps> = ({ attemptedPath, onNavigate }) => {
  return (
    <div className="page-container" style={{ maxWidth: '860px', margin: '40px auto', textAlign: 'center' }}>
      <div
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-xl)',
          padding: '48px 32px',
          boxShadow: 'var(--shadow-md)'
        }}
      >
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'rgba(14, 165, 233, 0.15)',
            color: 'var(--accent-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px'
          }}
        >
          <Compass size={32} />
        </div>

        <span
          style={{
            fontSize: '0.8rem',
            fontWeight: 800,
            letterSpacing: '0.08em',
            color: 'var(--accent-cyan)',
            textTransform: 'uppercase',
            background: 'rgba(14, 165, 233, 0.1)',
            padding: '4px 12px',
            borderRadius: '999px',
            border: '1px solid var(--accent-cyan-border)'
          }}
        >
          404 — Route Not Found
        </span>

        <h1 style={{ fontSize: '2.2rem', fontWeight: 900, color: 'var(--text-main)', margin: '16px 0 8px' }}>
          Destination Off the Map
        </h1>

        <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', maxWidth: '540px', margin: '0 auto 24px', lineHeight: 1.6 }}>
          {attemptedPath ? (
            <>The requested route <code className="mono" style={{ color: 'var(--accent-cyan)' }}>{attemptedPath}</code> does not match any Crime Compass section.</>
          ) : (
            <>The page you are looking for does not exist or has been relocated.</>
          )}
        </p>

        <button
          type="button"
          className="btn btn-primary"
          onClick={() => onNavigate('home')}
          style={{
            padding: '12px 28px',
            fontSize: '0.95rem',
            fontWeight: 700,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '36px'
          }}
        >
          <Home size={18} />
          <span>Return to Crime Compass 🧭 Home</span>
        </button>

        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '28px', textAlign: 'left' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '14px', textAlign: 'center' }}>
            Available Crime Compass Navigation Pages
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
            {[
              { id: 'input-analysis', label: 'Analyze Incident', icon: Compass, desc: 'Generate 70D fingerprint from input' },
              { id: 'incident-analyzer', label: 'Incident Fingerprint Analyzer', icon: Fingerprint, desc: 'Historical ID lookup & radar' },
              { id: 'behavioral-patterns', label: 'Explore Patterns', icon: Layers, desc: '8 empirical behavioral archetypes' },
              { id: 'incident-history', label: 'Incident History', icon: History, desc: 'Audit log of prior analyses' },
              { id: 'dna-comparison', label: 'Behavioral Comparison', icon: GitCompare, desc: 'Side-by-side incident comparison' },
              { id: 'connection-map', label: 'Connection Map', icon: Network, desc: 'Interactive behavioral graph' },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  style={{
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '12px 14px',
                    cursor: 'pointer',
                    transition: 'all 0.18s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'var(--accent-cyan)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--border-subtle)';
                    e.currentTarget.style.transform = 'none';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '0.88rem', color: 'var(--text-main)', marginBottom: '3px' }}>
                    <Icon size={16} style={{ color: 'var(--accent-cyan)' }} />
                    <span>{item.label}</span>
                  </div>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                    {item.desc}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
