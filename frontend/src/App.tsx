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
import { NotFoundPage } from './pages/NotFoundPage';
import { ErrorBoundary } from './components/ErrorBoundary';
import { api } from './api';
import { formatIndianNumber } from './utils/indiaFormat';

type PageId =
  | 'home'
  | 'overview'
  | 'input-analysis'
  | 'incident-analyzer'
  | 'incident-history'
  | 'dna-comparison'
  | 'similarity-view'
  | 'why-similar'
  | 'behavioral-patterns'
  | 'connection-map'
  | 'cross-crime'
  | 'behavioral-evolution'
  | 'novel'
  | 'not-found';

// Normalize page aliases so both shorthand, hyphenated routes, and direct URLs work
function normalizePageId(page: string): PageId {
  const clean = (page || '').toLowerCase().trim().replace(/^\/+|\/+$/g, '');
  switch (clean) {
    case '':
    case 'home':
    case 'index.html':
      return 'home';
    case 'analyze':
    case 'input':
    case 'simulator':
    case 'input-analysis':
    case 'analyze-incident':
      return 'input-analysis';
    case 'analyzer':
    case 'incident-analyzer':
    case 'fingerprint':
    case 'lookup':
    case 'fingerprint-analyzer':
      return 'incident-analyzer';
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
    case 'behavioral-comparison':
      return 'dna-comparison';
    case 'map':
    case 'connection-map':
    case 'behavioral-connection-map':
      return 'connection-map';
    case 'similarity':
    case 'similarity-view':
      return 'similarity-view';
    case 'why-similar':
      return 'why-similar';
    case 'cross-crime':
      return 'cross-crime';
    case 'evolution':
    case 'behavioral-evolution':
      return 'behavioral-evolution';
    case 'novel':
    case 'novel-behavior':
      return 'novel';
    case 'overview':
      return 'overview';
    default:
      return 'not-found';
  }
}

function getInitialRoute(): { page: PageId; params: Record<string, any> } {
  try {
    const path = window.location.pathname.replace(/^\/+|\/+$/g, '');
    const hash = window.location.hash.replace(/^#\/?/, '');
    const target = hash || path;
    const searchParams = new URLSearchParams(window.location.search);
    const params: Record<string, any> = {};
    searchParams.forEach((val, key) => {
      params[key] = val;
    });

    if (!target) {
      return { page: 'home', params };
    }

    const normalized = normalizePageId(target);
    return { page: normalized, params };
  } catch {
    return { page: 'home', params: {} };
  }
}

interface NavItem {
  id: PageId;
  label: string;
  icon: React.ComponentType<{ className?: string; size?: number }>;
  badge?: string;
}

// 5 MAIN PRODUCT SECTIONS — Fully Restored Navigation
const MAIN_NAV_ITEMS: NavItem[] = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'input-analysis', label: 'Analyze Incident', icon: Compass, badge: 'Main' },
  { id: 'incident-analyzer', label: 'Incident Fingerprint Analyzer', icon: Fingerprint, badge: 'Lookup' },
  { id: 'behavioral-patterns', label: 'Explore Patterns', icon: Layers, badge: '8 Patterns' },
  { id: 'incident-history', label: 'Incident History', icon: History, badge: 'Audit' },
];

// OPTIONAL INVESTIGATION TOOLS
const OPTIONAL_NAV_ITEMS: NavItem[] = [
  { id: 'dna-comparison', label: 'Behavioral Comparison', icon: GitCompare, badge: 'A vs B' },
  { id: 'connection-map', label: 'Connection Map', icon: Network, badge: 'Graph' },
];

export function App() {
  const initial = getInitialRoute();
  const [activePage, setActivePage] = useState<PageId>(initial.page);
  const [pageParams, setPageParams] = useState<Record<string, any>>(initial.params);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);
  const [apiLatency, setApiLatency] = useState<number | null>(null);
  const [totalIncidents, setTotalIncidents] = useState<number | null>(null);

  // Sync browser Back/Forward navigation (popstate)
  useEffect(() => {
    const handlePopState = () => {
      const current = getInitialRoute();
      setActivePage(current.page);
      setPageParams(current.params);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Update browser tab title
  useEffect(() => {
    document.title = 'Crime Compass 🧭 — Different Incidents. Shared Behavioral Patterns.';
  }, []);

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
    } else {
      setPageParams({});
    }
    setMobileMenuOpen(false);

    // Sync browser URL bar without page refresh
    const targetUrl = normalized === 'home' ? '/' : `/${normalized}`;
    if (window.location.pathname !== targetUrl) {
      try {
        window.history.pushState({}, '', targetUrl);
      } catch {
        // Fallback if pushState fails
      }
    }

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
          {/* Main 5 Sections */}
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
            Investigation Tools
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
        {/* Topbar with Mandatory Scientific Advisory */}
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

            {/* MANDATORY LEGAL & SCIENTIFIC ADVISORY */}
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

        {/* View Container wrapped in global ErrorBoundary */}
        <main className="content-viewport">
          <ErrorBoundary
            fallbackTitle="Crime Compass View Recovery"
            onNavigateHome={() => handleNavigate('home')}
          >
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

            {activePage === 'incident-analyzer' && (
              <IncidentAnalyzerPage
                initialIncidentId={pageParams.incidentId || 'INC_136975'}
                onNavigate={handleNavigate}
              />
            )}

            {activePage === 'incident-history' && (
              <IncidentHistoryPage onNavigate={handleNavigate} />
            )}

            {activePage === 'dna-comparison' && (
              <DnaComparisonPage onNavigate={handleNavigate} />
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

            {activePage === 'not-found' && (
              <NotFoundPage
                attemptedPath={window.location.pathname}
                onNavigate={handleNavigate}
              />
            )}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}

export default App;
