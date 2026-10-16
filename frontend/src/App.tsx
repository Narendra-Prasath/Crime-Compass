import React, { useState, useEffect } from 'react';
import {
  Home,
  LayoutDashboard,
  Fingerprint,
  ArrowLeftRight,
  GitCompare,
  HelpCircle,
  Layers,
  Network,
  TrendingUp,
  AlertTriangle,
  ShieldAlert,
  Activity,
  Menu,
  X,
  Database,
  Compass,
  History
} from 'lucide-react';

import { HomePage } from './pages/HomePage';
import { OverviewPage } from './pages/OverviewPage';
import { IncidentAnalyzerPage } from './pages/IncidentAnalyzerPage';
import { SimilarityViewPage } from './pages/SimilarityViewPage';
import { WhySimilarPage } from './pages/WhySimilarPage';
import { BehavioralPatternsPage } from './pages/BehavioralPatternsPage';
import { CrossCrimePage } from './pages/CrossCrimePage';
import { BehavioralEvolutionPage } from './pages/BehavioralEvolutionPage';
import { NovelBehaviorPage } from './pages/NovelBehaviorPage';
import { InputAnalysisPage } from './pages/InputAnalysisPage';
import { DnaComparisonPage } from './pages/DnaComparisonPage';
import { BehavioralConnectionMapPage } from './pages/BehavioralConnectionMapPage';
import { IncidentHistoryPage } from './pages/IncidentHistoryPage';
import { api } from './api';
import { formatIndianNumber } from './utils/indiaFormat';

type PageId =
  | 'home'
  | 'overview'
  | 'input-analysis'
  | 'incident-history'
  | 'dna-comparison'
  | 'incident-analyzer'
  | 'similarity-view'
  | 'why-similar'
  | 'behavioral-patterns'
  | 'connection-map'
  | 'cross-crime'
  | 'behavioral-evolution'
  | 'novel';

// Normalize page aliases so both shorthand and hyphenated routes work
function normalizePageId(page: string): PageId {
  switch (page) {
    case 'home':
      return 'home';
    case 'analyze':
    case 'input':
    case 'simulator':
    case 'input-analysis':
      return 'input-analysis';
    case 'patterns':
    case 'explore-patterns':
    case 'behavioral-patterns':
      return 'behavioral-patterns';
    case 'history':
    case 'incident-history':
      return 'incident-history';
    case 'compare':
    case 'comparison':
    case 'dna-compare':
    case 'dna-comparison':
      return 'dna-comparison';
    case 'map':
    case 'connection-map':
    case 'behavioral-connection-map':
      return 'connection-map';
    case 'analyzer':
    case 'incident-analyzer':
      return 'incident-analyzer';
    case 'similarity':
    case 'similarity-view':
      return 'similarity-view';
    case 'evolution':
    case 'behavioral-evolution':
      return 'behavioral-evolution';
    case 'novel':
    case 'novel-behavior':
      return 'novel';
    case 'cross-crime':
      return 'cross-crime';
    case 'why-similar':
      return 'why-similar';
    case 'overview':
      return 'overview';
    default:
      return 'home';
  }
}

interface NavItem {
  id: PageId;
  label: string;
  icon: React.ComponentType<{ className?: string; size?: number }>;
  badge?: string;
}

// 4 MAIN PRODUCT SECTIONS
const MAIN_NAV_ITEMS: NavItem[] = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'input-analysis', label: 'Analyze Incident', icon: Compass, badge: 'Main' },
  { id: 'behavioral-patterns', label: 'Explore Patterns', icon: Layers, badge: '8 Patterns' },
  { id: 'incident-history', label: 'Incident History', icon: History, badge: 'Audit' },
];

// OPTIONAL INVESTIGATION TOOLS
const OPTIONAL_NAV_ITEMS: NavItem[] = [
  { id: 'dna-comparison', label: 'Behavioral Comparison', icon: GitCompare, badge: 'A vs B' },
  { id: 'connection-map', label: 'Connection Map', icon: Network, badge: 'Graph' },
];

export function App() {
  const [activePage, setActivePage] = useState<PageId>('home');
  const [pageParams, setPageParams] = useState<Record<string, any>>({});
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);
  const [apiLatency, setApiLatency] = useState<number | null>(null);

  const [totalIncidents, setTotalIncidents] = useState<number | null>(null);

  // Periodic health check
  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      const t0 = performance.now();
      try {
        const [health, stats] = await Promise.all([
          api.getHealth(),
          api.getStats().catch(() => null),
        ]);
        if (isMounted) {
          setApiLatency(Math.round(performance.now() - t0));
          setApiConnected(health.status === 'healthy');
          if (stats?.total_incidents) {
            setTotalIncidents(stats.total_incidents);
          }
        }
      } catch {
        if (isMounted) {
          setApiConnected(false);
          setApiLatency(null);
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleNavigate = (page: string, params?: Record<string, any>) => {
    const normalized = normalizePageId(page);
    setActivePage(normalized);
    if (params) {
      setPageParams(params);
    }
    setMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app-container">
      {/* Mobile Backdrop Overlay */}
      {mobileMenuOpen && (
        <div
          className="mobile-backdrop"
          onClick={() => setMobileMenuOpen(false)}
          aria-label="Close navigation overlay"
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-brand">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h1 className="brand-title" style={{ cursor: 'pointer' }} onClick={() => handleNavigate('home')}>
              <Compass size={22} style={{ color: 'var(--accent-cyan)' }} />
              <span>Crime Compass 🧭</span>
            </h1>
            {mobileMenuOpen && (
              <button
                type="button"
                className="btn-icon"
                onClick={() => setMobileMenuOpen(false)}
                aria-label="Close menu"
              >
                <X size={20} />
              </button>
            )}
          </div>
          <p className="brand-tagline">Different Incidents. Shared Behavioral Patterns.</p>
        </div>

        <nav className="nav-menu">
          {/* Main 4 Sections */}
          <div style={{ padding: '8px 16px 4px', fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Main Product
          </div>
          {MAIN_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                type="button"
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => handleNavigate(item.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
                  <Icon size={18} />
                  <span>{item.label}</span>
                </div>
                {item.badge && <span className="badge" style={{ fontSize: '0.65rem', padding: '2px 6px', background: isActive ? 'rgba(14, 165, 233, 0.2)' : 'rgba(255,255,255,0.06)' }}>{item.badge}</span>}
              </button>
            );
          })}

          {/* Optional Investigation Tools */}
          <div style={{ padding: '16px 16px 4px', fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Optional Tools
          </div>
          {OPTIONAL_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                type="button"
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => handleNavigate(item.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
                  <Icon size={18} />
                  <span>{item.label}</span>
                </div>
                {item.badge && <span className="badge" style={{ fontSize: '0.65rem', padding: '2px 6px', background: 'rgba(255,255,255,0.06)' }}>{item.badge}</span>}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer with Live Connection Status */}
        <div className="sidebar-footer">
          <div className="system-status">
            <span className={`status-dot ${apiConnected ? 'online' : 'offline'}`} />
            <span style={{ fontWeight: 600, color: apiConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
              {apiConnected === null ? 'Connecting...' : apiConnected ? `Live Engine (${apiLatency}ms)` : 'Backend Disconnected'}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
            <Database size={12} />
            <span>{totalIncidents ? `${formatIndianNumber(totalIncidents)} Historical Records` : '2,20,663 Historical Records'} &bull; 70D Fingerprint</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-wrapper">
        {/* Topbar with Mandatory Ethics & Neutrality Disclaimer */}
        <header className="topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%', justifyContent: 'space-between' }}>
            <button
              type="button"
              className="btn btn-secondary mobile-toggle"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open navigation menu"
            >
              <Menu size={18} />
            </button>

            {/* MANDATORY LEGAL & SCIENTIFIC DISCLAIMER */}
            <div className="topbar-disclaimer" style={{ flex: 1 }}>
              <ShieldAlert size={16} className="topbar-disclaimer-icon" />
              <div>
                <strong style={{ color: 'var(--text-main)', marginRight: '0.35rem' }}>Scientific Advisory:</strong>
                Crime Compass analyzes incident characteristics and historical behavioral patterns. Similarity or novelty does not establish offender identity, guilt, or causation.
              </div>
            </div>

            {/* Status indicator chip */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '5px 12px',
                borderRadius: '999px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                whiteSpace: 'nowrap',
              }}
            >
              <Activity size={13} style={{ color: apiConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)' }} />
              <span>{apiConnected ? 'Inference Engine Ready' : 'API Connecting...'}</span>
            </div>
          </div>
        </header>

        {/* View Container */}
        <main className="content-viewport">
          {activePage === 'home' && (
            <HomePage onNavigate={handleNavigate} />
          )}

          {activePage === 'overview' && (
            <OverviewPage onNavigate={handleNavigate} />
          )}

          {activePage === 'input-analysis' && (
            <InputAnalysisPage
              onNavigate={handleNavigate}
              initialAnalysisResult={pageParams.analysisResult}
              initialPayload={pageParams.initialPayload}
            />
          )}

          {activePage === 'incident-history' && (
            <IncidentHistoryPage onNavigate={handleNavigate} />
          )}

          {activePage === 'dna-comparison' && (
            <DnaComparisonPage onNavigate={handleNavigate} />
          )}

          {activePage === 'incident-analyzer' && (
            <IncidentAnalyzerPage
              initialIncidentId={pageParams.incidentId || 'INC_136975'}
              onNavigate={handleNavigate}
            />
          )}

          {activePage === 'similarity-view' && (
            <SimilarityViewPage
              initialInc1={pageParams.inc1 || 'INC_136975'}
              initialInc2={pageParams.inc2 || 'INC_145291'}
              onNavigate={handleNavigate}
            />
          )}

          {activePage === 'why-similar' && (
            <WhySimilarPage
              initialInc1={pageParams.inc1 || 'INC_136975'}
              initialInc2={pageParams.inc2 || 'INC_145291'}
              onNavigate={handleNavigate}
            />
          )}

          {activePage === 'behavioral-patterns' && (
            <BehavioralPatternsPage
              initialClusterId={pageParams.clusterId !== undefined ? pageParams.clusterId : 0}
              onNavigate={handleNavigate}
            />
          )}

          {activePage === 'connection-map' && (
            <BehavioralConnectionMapPage
              initialPatternId={pageParams.patternId}
              initialCategory={pageParams.category}
              onNavigate={handleNavigate}
            />
          )}

          {activePage === 'cross-crime' && (
            <CrossCrimePage
              initialPatternId={pageParams.patternId || 'CCP_00'}
              onNavigate={handleNavigate}
            />
          )}

          {activePage === 'behavioral-evolution' && (
            <BehavioralEvolutionPage onNavigate={handleNavigate} />
          )}

          {activePage === 'novel' && (
            <NovelBehaviorPage onNavigate={handleNavigate} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
