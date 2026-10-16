import React, { useEffect, useState } from 'react';
import {
  Compass,
  Layers,
  History,
  GitCompare,
  Network,
  ArrowRight,
  Fingerprint,
  Cpu,
  HelpCircle,
  TrendingUp,
  ShieldAlert,
  Database,
  CheckCircle2,
  Sparkles,
  Search,
  Globe2
} from 'lucide-react';
import { api } from '../api';
import type { DatasetStats } from '../types';
import { formatIndianNumber } from '../utils/indiaFormat';

interface HomePageProps {
  onNavigate: (page: string, params?: any) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DatasetStats | null>(null);

  useEffect(() => {
    let mounted = true;
    api.getStats()
      .then((data) => {
        if (mounted) setStats(data);
      })
      .catch(() => {});
    return () => { mounted = false; };
  }, []);

  return (
    <div className="page-container" style={{ maxWidth: '1240px', margin: '0 auto', paddingBottom: '60px' }}>
      {/* =========================================================================
          1. HERO HEADER SECTION
          ========================================================================= */}
      <section
        style={{
          background: 'linear-gradient(135deg, rgba(13, 19, 31, 0.95) 0%, rgba(14, 165, 233, 0.12) 100%)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-xl)',
          padding: '48px 36px',
          marginBottom: '32px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: 'var(--shadow-md)'
        }}
      >
        <div style={{ maxWidth: '780px', position: 'relative', zIndex: 2 }}>
          {/* Tag */}
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 12px',
                borderRadius: '999px',
                background: 'rgba(14, 165, 233, 0.15)',
                color: 'var(--accent-cyan)',
                border: '1px solid var(--accent-cyan-border)',
                fontSize: '0.78rem',
                fontWeight: 700,
                letterSpacing: '0.04em'
              }}
            >
              <Sparkles size={14} />
              BEHAVIORAL CRIME INTELLIGENCE
            </span>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                padding: '4px 10px',
                borderRadius: '999px',
                background: 'rgba(30, 41, 59, 0.7)',
                color: '#94a3b8',
                border: '1px solid var(--border-subtle)',
                fontSize: '0.74rem'
              }}
            >
              <Globe2 size={13} style={{ color: 'var(--accent-cyan)' }} />
              Historical Reference: Alabama, USA, 2024 (FBI NIBRS)
            </span>
          </div>

          {/* Main Title */}
          <h1
            style={{
              fontSize: '3rem',
              fontWeight: 900,
              letterSpacing: '-0.03em',
              lineHeight: 1.1,
              color: 'var(--text-main)',
              margin: '0 0 12px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              flexWrap: 'wrap'
            }}
          >
            <span>Crime Compass</span>
            <span role="img" aria-label="compass">🧭</span>
          </h1>

          {/* Tagline */}
          <h2
            style={{
              fontSize: '1.4rem',
              fontWeight: 700,
              color: '#38bdf8',
              margin: '0 0 16px',
              letterSpacing: '-0.01em'
            }}
          >
            Different Incidents. Shared Behavioral Patterns.
          </h2>

          {/* Simple Explanation */}
          <p
            style={{
              fontSize: '1.05rem',
              lineHeight: 1.6,
              color: 'var(--text-muted)',
              margin: '0 0 28px',
              maxWidth: '700px'
            }}
          >
            Crime Compass helps users analyze crime incident data, discover behavioral similarities, explore patterns across crime categories, and understand how incidents compare with historical records.
          </p>

          {/* Primary Call to Action Button */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => onNavigate('input-analysis')}
              style={{
                padding: '14px 28px',
                fontSize: '1.05rem',
                fontWeight: 700,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '10px',
                borderRadius: 'var(--radius-md)',
                boxShadow: '0 4px 20px rgba(14, 165, 233, 0.35)',
                background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)'
              }}
            >
              <Compass size={20} />
              <span>ANALYZE INCIDENT</span>
              <ArrowRight size={18} />
            </button>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => onNavigate('behavioral-patterns')}
              style={{
                padding: '14px 22px',
                fontSize: '0.95rem',
                fontWeight: 600,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <Layers size={18} />
              <span>Explore Patterns</span>
            </button>
          </div>
        </div>

        {/* Decorative background watermark */}
        <div
          style={{
            position: 'absolute',
            right: '-20px',
            bottom: '-20px',
            opacity: 0.04,
            pointerEvents: 'none',
            color: 'var(--accent-cyan)'
          }}
        >
          <Fingerprint size={380} />
        </div>
      </section>

      {/* =========================================================================
          2. CORE ARCHITECTURAL PIPELINE FLOW
          INPUT ↓ BEHAVIORAL FINGERPRINT ↓ ML ANALYSIS ↓ PATTERNS ↓ EXPLANATION
          ========================================================================= */}
      <section style={{ marginBottom: '36px' }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 6px' }}>
            How Crime Compass Works
          </h3>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: 0 }}>
            From incident characteristics to explainable behavioral intelligence in 5 transparent stages.
          </p>
        </div>

        {/* 5-Stage Pipeline Flow */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
            position: 'relative'
          }}
        >
          {/* Stage 1: INPUT */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '20px 18px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '10px',
                background: 'rgba(56, 189, 248, 0.12)',
                color: '#38bdf8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '12px'
              }}
            >
              <Compass size={22} />
            </div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8', letterSpacing: '0.05em' }}>
              STAGE 1
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, margin: '4px 0 6px', color: 'var(--text-main)' }}>
              INPUT
            </h4>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.45 }}>
              Enter clean incident attributes: location setting (India or Global), weapons, property, victims, and timing.
            </p>
          </div>

          {/* Stage 2: BEHAVIORAL FINGERPRINT */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '20px 18px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '10px',
                background: 'rgba(168, 85, 247, 0.12)',
                color: 'var(--accent-purple)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '12px'
              }}
            >
              <Fingerprint size={22} />
            </div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-purple)', letterSpacing: '0.05em' }}>
              STAGE 2
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, margin: '4px 0 6px', color: 'var(--text-main)' }}>
              BEHAVIORAL FINGERPRINT
            </h4>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.45 }}>
              Encodes modus operandi into a normalized 70-dimensional behavioral fingerprint across 7 behavioral domains.
            </p>
          </div>

          {/* Stage 3: ML ANALYSIS */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '20px 18px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '10px',
                background: 'rgba(16, 185, 129, 0.12)',
                color: 'var(--accent-emerald)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '12px'
              }}
            >
              <Cpu size={22} />
            </div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-emerald)', letterSpacing: '0.05em' }}>
              STAGE 3
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, margin: '4px 0 6px', color: 'var(--text-main)' }}>
              SIMILARITY MATCHING
            </h4>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.45 }}>
              Executes behavioral similarity ranking against {stats ? formatIndianNumber(stats.total_incidents) : '2,20,663'} historical reference incidents.
            </p>
          </div>

          {/* Stage 4: PATTERNS */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '20px 18px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '10px',
                background: 'rgba(245, 158, 11, 0.12)',
                color: 'var(--accent-amber)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '12px'
              }}
            >
              <Layers size={22} />
            </div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-amber)', letterSpacing: '0.05em' }}>
              STAGE 4
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, margin: '4px 0 6px', color: 'var(--text-main)' }}>
              GROUPS & NOVELTY
            </h4>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.45 }}>
              Discovers groups of similar patterns, cross-category behavioral links, and unusual behavioral combinations.
            </p>
          </div>

          {/* Stage 5: EXPLANATION */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '20px 18px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '10px',
                background: 'rgba(14, 165, 233, 0.12)',
                color: 'var(--accent-cyan)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '12px'
              }}
            >
              <HelpCircle size={22} />
            </div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-cyan)', letterSpacing: '0.05em' }}>
              STAGE 5
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, margin: '4px 0 6px', color: 'var(--text-main)' }}>
              WHY INCIDENTS MATCH
            </h4>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.45 }}>
              Provides clear explanations showing which specific behavioral details matched and what sets them apart.
            </p>
          </div>
        </div>
      </section>

      {/* =========================================================================
          3. FOUR MAJOR PRODUCT PILLARS
          ========================================================================= */}
      <section style={{ marginBottom: '32px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(270px, 1fr))', gap: '16px' }}>
          {/* Section 1: ANALYZE INCIDENT */}
          <div
            onClick={() => onNavigate('input-analysis')}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
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
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                <div
                  style={{
                    padding: '10px',
                    borderRadius: '8px',
                    background: 'rgba(14, 165, 233, 0.15)',
                    color: 'var(--accent-cyan)'
                  }}
                >
                  <Compass size={22} />
                </div>
                <span className="badge badge-property" style={{ fontSize: '0.7rem' }}>PRIMARY PRODUCT</span>
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 6px' }}>
                Analyze Incident
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                Enter or evaluate an incident with Indian or international location details. Generate a behavioral fingerprint, similarity matches, and cross-category insights.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)', fontSize: '0.85rem', fontWeight: 600, marginTop: '20px' }}>
              <span>Launch Analyzer</span>
              <ArrowRight size={14} />
            </div>
          </div>

          {/* Section 2: EXPLORE PATTERNS */}
          <div
            onClick={() => onNavigate('behavioral-patterns')}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-purple)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)';
              e.currentTarget.style.transform = 'none';
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                <div
                  style={{
                    padding: '10px',
                    borderRadius: '8px',
                    background: 'rgba(168, 85, 247, 0.15)',
                    color: 'var(--accent-purple)'
                  }}
                >
                  <Layers size={22} />
                </div>
                <span className="badge" style={{ fontSize: '0.7rem', background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>
                  8 ARCHETYPES
                </span>
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 6px' }}>
                Groups of Similar Patterns
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                Browse the 8 overarching behavioral archetypes uncovered across {stats ? formatIndianNumber(stats.total_incidents) : '2,20,663'} historical reference incidents.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-purple)', fontSize: '0.85rem', fontWeight: 600, marginTop: '20px' }}>
              <span>View 8 Patterns</span>
              <ArrowRight size={14} />
            </div>
          </div>

          {/* Section 3: INCIDENT HISTORY */}
          <div
            onClick={() => onNavigate('incident-history')}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-emerald)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)';
              e.currentTarget.style.transform = 'none';
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                <div
                  style={{
                    padding: '10px',
                    borderRadius: '8px',
                    background: 'rgba(16, 185, 129, 0.15)',
                    color: 'var(--accent-emerald)'
                  }}
                >
                  <History size={22} />
                </div>
                <span className="badge" style={{ fontSize: '0.7rem', background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
                  AUDIT LOG
                </span>
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 6px' }}>
                Incident History
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                Review past analytical submissions with pagination, search, zero PII preservation, and one-click result inspection.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-emerald)', fontSize: '0.85rem', fontWeight: 600, marginTop: '20px' }}>
              <span>Audit History</span>
              <ArrowRight size={14} />
            </div>
          </div>

          {/* Section 4: BEHAVIORAL COMPARISON */}
          <div
            onClick={() => onNavigate('dna-comparison')}
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent-amber)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)';
              e.currentTarget.style.transform = 'none';
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                <div
                  style={{
                    padding: '10px',
                    borderRadius: '8px',
                    background: 'rgba(245, 158, 11, 0.15)',
                    color: 'var(--accent-amber)'
                  }}
                >
                  <GitCompare size={22} />
                </div>
                <span className="badge" style={{ fontSize: '0.7rem', background: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' }}>
                  PAIRWISE
                </span>
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 6px' }}>
                Behavioral Comparison
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                Perform direct, head-to-head pairwise behavioral comparison between two incidents with dimension-by-dimension alignment.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-amber)', fontSize: '0.85rem', fontWeight: 600, marginTop: '20px' }}>
              <span>Compare Incidents</span>
              <ArrowRight size={14} />
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          4. BENCHMARK TELEMETRY STRIP
          ========================================================================= */}
      <section
        style={{
          background: 'var(--bg-subtle)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 24px',
          display: 'flex',
          justifyContent: 'space-around',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '20px'
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>
            {stats ? formatIndianNumber(stats.total_incidents) : '2,20,663'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Historical Reference Incidents
          </div>
        </div>

        <div style={{ width: '1px', height: '32px', background: 'var(--border-subtle)' }} />

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-main)' }}>
            70D
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Behavioral Fingerprint Dimensions
          </div>
        </div>

        <div style={{ width: '1px', height: '32px', background: 'var(--border-subtle)' }} />

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-purple)' }}>
            8
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Archetype Clusters
          </div>
        </div>

        <div style={{ width: '1px', height: '32px', background: 'var(--border-subtle)' }} />

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>
            &lt; 15ms
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Retrieval Latency
          </div>
        </div>
      </section>

      {/* =========================================================================
          MANDATORY ADVISORY
          ========================================================================= */}
      <div
        style={{
          marginTop: '24px',
          padding: '14px 20px',
          background: 'rgba(59, 130, 246, 0.05)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}
      >
        <ShieldAlert size={18} style={{ color: '#60a5fa', flexShrink: 0 }} />
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
          <strong style={{ color: '#93c5fd' }}>Advisory: </strong>
          Crime Compass analyzes incident characteristics and historical behavioral patterns. Similarity or novelty does not establish offender identity, guilt, or causation.
        </div>
      </div>
    </div>
  );
};
