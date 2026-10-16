import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  History,
  Search,
  Filter,
  RefreshCw,
  ExternalLink,
  Trash2,
  Copy,
  Check,
  ChevronLeft,
  ChevronRight,
  Database,
  UserCheck,
  ShieldAlert,
  AlertTriangle,
  Fingerprint,
  Layers,
  ArrowRight,
  X,
  LayoutList,
  LayoutGrid,
  Info,
  Calendar,
  Sparkles,
  Compass,
  Tag
} from 'lucide-react';
import { api } from '../api';
import type { AnalysisRecord } from '../types';

interface IncidentHistoryPageProps {
  onNavigate: (page: string, params?: Record<string, any>) => void;
}

export const IncidentHistoryPage: React.FC<IncidentHistoryPageProps> = ({ onNavigate }) => {
  // Data states
  const [records, setRecords] = useState<AnalysisRecord[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter & Pagination states
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');

  // Selected Record Modal
  const [selectedRecord, setSelectedRecord] = useState<AnalysisRecord | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [deletePendingId, setDeletePendingId] = useState<string | null>(null);
  const [deleteActionLoading, setDeleteActionLoading] = useState<boolean>(false);

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setPage(1); // Reset to first page on search
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Load records
  const fetchRecords = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const offset = (page - 1) * pageSize;
      const res = await api.getAnalysisRecords({
        search: debouncedSearch.trim() || undefined,
        category: selectedCategory !== 'all' ? selectedCategory : undefined,
        limit: pageSize,
        offset: offset,
      });
      setRecords(res.records || []);
      setTotalCount(res.total_count ?? 0);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve analysis history.');
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, selectedCategory, page, pageSize]);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  // Copy Analysis ID
  const handleCopyId = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Delete Record
  const handleDeleteRecord = async (analysisId: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (!window.confirm(`Are you sure you want to permanently delete analysis record ${analysisId} from your local history?`)) {
      return;
    }

    setDeleteActionLoading(true);
    try {
      await api.deleteAnalysisRecord(analysisId);
      if (selectedRecord?.analysis_id === analysisId) {
        setSelectedRecord(null);
      }
      fetchRecords();
    } catch (err: any) {
      alert(`Could not delete record: ${err.message || 'Unknown error'}`);
    } finally {
      setDeleteActionLoading(false);
      setDeletePendingId(null);
    }
  };

  // Format timestamp (Indian Format: DD/MM/YYYY, 12h AM/PM, Asia/Kolkata)
  const formatDateTime = (isoString?: string) => {
    if (!isoString) return 'Unknown Date';
    try {
      const date = new Date(isoString);
      if (isNaN(date.getTime())) return isoString;
      return new Intl.DateTimeFormat('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
        timeZone: 'Asia/Kolkata'
      }).format(date);
    } catch {
      return isoString;
    }
  };

  // Relative time helper
  const getRelativeTime = (isoString?: string) => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 30) return `${diffDays}d ago`;
      return '';
    } catch {
      return '';
    }
  };

  // Category badge colors
  const getCategoryBadgeStyle = (category?: string) => {
    const cat = (category || '').toLowerCase();
    if (cat.includes('violent property')) {
      return { bg: 'rgba(245, 158, 11, 0.15)', text: '#f59e0b', border: 'rgba(245, 158, 11, 0.3)' };
    }
    if (cat.includes('person') || cat.includes('violent')) {
      return { bg: 'rgba(244, 63, 94, 0.15)', text: '#f43f5e', border: 'rgba(244, 63, 94, 0.3)' };
    }
    if (cat.includes('property')) {
      return { bg: 'rgba(14, 165, 233, 0.15)', text: '#0ea5e9', border: 'rgba(14, 165, 233, 0.3)' };
    }
    if (cat.includes('society')) {
      return { bg: 'rgba(168, 85, 247, 0.15)', text: '#c084fc', border: 'rgba(168, 85, 247, 0.3)' };
    }
    return { bg: 'rgba(148, 163, 184, 0.15)', text: '#94a3b8', border: 'rgba(148, 163, 184, 0.3)' };
  };

  // Novelty badge styling
  const getNoveltyBadgeStyle = (tier?: string, isNovel?: boolean) => {
    if (isNovel || (tier && (tier.includes('Outlier') || tier.includes('Novel')))) {
      return { bg: 'rgba(244, 63, 94, 0.15)', text: '#f43f5e', border: 'rgba(244, 63, 94, 0.3)', label: tier || 'Novel Outlier' };
    }
    if (tier && tier.includes('Moderate')) {
      return { bg: 'rgba(245, 158, 11, 0.15)', text: '#f59e0b', border: 'rgba(245, 158, 11, 0.3)', label: tier };
    }
    return { bg: 'rgba(16, 185, 129, 0.15)', text: '#10b981', border: 'rgba(16, 185, 129, 0.3)', label: tier || 'Standard Pattern' };
  };

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  return (
    <div className="page-container" style={{ maxWidth: '1360px', margin: '0 auto', paddingBottom: '80px' }}>
      {/* Page Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                padding: '10px',
                borderRadius: '10px',
                background: 'rgba(14, 165, 233, 0.15)',
                color: 'var(--accent-cyan)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <History size={24} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
                Incident Analysis History
              </h1>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                Audit, compare, and inspect previously analyzed behavioral evaluations.
              </p>
            </div>
          </div>

          {/* Quick Action Button */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => onNavigate('input-analysis')}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', fontSize: '0.85rem' }}
            >
              <Compass size={16} />
              <span>Analyze New Incident 🧭</span>
            </button>
          </div>
        </div>
      </div>

      {/* ARCHITECTURAL DISTINCTION BANNER: Historical Reference Dataset vs User Analysis History */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(18, 25, 39, 0.85) 0%, rgba(13, 19, 31, 0.95) 100%)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          padding: '16px 20px',
          marginBottom: '24px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '16px',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Left Column: Historical Reference Dataset */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
          <div
            style={{
              padding: '8px',
              borderRadius: '8px',
              background: 'rgba(14, 165, 233, 0.12)',
              color: 'var(--accent-cyan)',
              flexShrink: 0
            }}
          >
            <Database size={18} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--accent-cyan)' }}>
                Historical Reference Dataset
              </span>
              <span className="badge" style={{ fontSize: '0.65rem', background: 'rgba(14, 165, 233, 0.2)', color: 'var(--accent-cyan)' }}>
                2,20,663 Incidents (Alabama, USA, 2024)
              </span>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
              The immutable FBI NIBRS benchmark reference corpus powering all 70D behavioral fingerprint representations, cluster centroids, and nearest-neighbor indexes. Completely read-only and preserved for scientific validation.
            </p>
          </div>
        </div>

        {/* Right Column: User Analysis History */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
          <div
            style={{
              padding: '8px',
              borderRadius: '8px',
              background: 'rgba(16, 185, 129, 0.12)',
              color: 'var(--accent-emerald)',
              flexShrink: 0
            }}
          >
            <UserCheck size={18} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--accent-emerald)' }}>
                User Analysis History
              </span>
              <span className="badge" style={{ fontSize: '0.65rem', background: 'rgba(16, 185, 129, 0.2)', color: 'var(--accent-emerald)' }}>
                Isolated Local Audit Log
              </span>
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
              Stores evaluated incident outputs (<code style={{ color: 'var(--accent-emerald)', fontSize: '0.78rem' }}>ANA_...</code>) for investigator auditing. Contains strictly zero personal data (Zero PII) and is <strong>never</strong> injected into the historical reference corpus.
            </p>
          </div>
        </div>
      </div>

      {/* FILTER & CONTROLS TOOLBAR */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '16px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '12px 16px'
        }}
      >
        {/* Search Input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: '240px' }}>
          <div style={{ position: 'relative', width: '100%', maxWidth: '360px' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
            <input
              type="text"
              className="input-field"
              placeholder="Search by ID, title, or pattern..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                paddingLeft: '36px',
                paddingRight: searchTerm ? '32px' : '12px',
                paddingTop: '7px',
                paddingBottom: '7px',
                fontSize: '0.85rem',
                background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)'
              }}
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => setSearchTerm('')}
                style={{
                  position: 'absolute',
                  right: '8px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-dim)',
                  cursor: 'pointer',
                  padding: '2px'
                }}
              >
                <X size={14} />
              </button>
            )}
          </div>

          {/* Category Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Filter size={15} style={{ color: 'var(--text-dim)' }} />
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setPage(1);
              }}
              style={{
                background: 'var(--bg-subtle)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '7px 10px',
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              <option value="all">All Categories</option>
              <option value="property">Property Offenses</option>
              <option value="person">Person / Violent</option>
              <option value="society">Society / Morals</option>
              <option value="person_property">Violent Property (Robbery)</option>
            </select>
          </div>
        </div>

        {/* View Mode & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {/* Total Count Pill */}
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
            {totalCount} {totalCount === 1 ? 'analysis' : 'analyses'}
          </span>

          {/* Table / Card View Toggle */}
          <div style={{ display: 'flex', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)', padding: '2px', border: '1px solid var(--border-subtle)' }}>
            <button
              type="button"
              onClick={() => setViewMode('table')}
              title="Table View"
              style={{
                background: viewMode === 'table' ? 'var(--bg-card)' : 'transparent',
                color: viewMode === 'table' ? 'var(--accent-cyan)' : 'var(--text-dim)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '5px 8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              <LayoutList size={16} />
            </button>
            <button
              type="button"
              onClick={() => setViewMode('cards')}
              title="Card View"
              style={{
                background: viewMode === 'cards' ? 'var(--bg-card)' : 'transparent',
                color: viewMode === 'cards' ? 'var(--accent-cyan)' : 'var(--text-dim)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '5px 8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              <LayoutGrid size={16} />
            </button>
          </div>

          {/* Refresh Button */}
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => fetchRecords()}
            title="Refresh History"
            style={{ padding: '6px 10px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem' }}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* CONTENT AREA: Loading, Error, Empty, or Data Display */}
      {loading ? (
        /* LOADING STATE */
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '40px 20px', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', padding: '14px', borderRadius: '50%', background: 'rgba(14, 165, 233, 0.1)', color: 'var(--accent-cyan)', marginBottom: '14px' }}>
            <RefreshCw size={26} className="spin" />
          </div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '6px' }}>
            Retrieving Incident Analysis History...
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
            Querying local privacy-preserving analytical records repository.
          </p>
        </div>
      ) : error ? (
        /* ERROR STATE */
        <div
          style={{
            background: 'rgba(244, 63, 94, 0.08)',
            border: '1px solid var(--accent-rose-border)',
            borderRadius: 'var(--radius-md)',
            padding: '24px',
            textAlign: 'center'
          }}
        >
          <div style={{ color: 'var(--accent-rose)', display: 'inline-flex', marginBottom: '10px' }}>
            <AlertTriangle size={32} />
          </div>
          <h3 style={{ color: 'var(--accent-rose)', fontSize: '1.1rem', fontWeight: 600, marginBottom: '8px' }}>
            Failed to Load Analysis History
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '480px', margin: '0 auto 16px' }}>
            {error}
          </p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => fetchRecords()}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}
          >
            <RefreshCw size={14} />
            <span>Try Again</span>
          </button>
        </div>
      ) : records.length === 0 ? (
        /* EMPTY STATE */
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px dashed var(--border-bright)',
            borderRadius: 'var(--radius-lg)',
            padding: '48px 24px',
            textAlign: 'center'
          }}
        >
          <div
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'rgba(14, 165, 233, 0.08)',
              color: 'var(--accent-cyan)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '16px'
            }}
          >
            <History size={32} />
          </div>

          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
            {searchTerm || selectedCategory !== 'all' ? 'No Matching Analyses Found' : 'No Previous Analyses Yet'}
          </h3>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', maxWidth: '520px', margin: '0 auto 20px', lineHeight: 1.5 }}>
            {searchTerm || selectedCategory !== 'all'
              ? 'No analysis records matched your active filter or search keywords. Try clearing the search query or selecting all categories.'
              : 'When you record and analyze incident scenarios in Crime Compass, your privacy-preserving analysis audit records will appear here.'}
          </p>

          {searchTerm || selectedCategory !== 'all' ? (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
              }}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            >
              <X size={15} />
              <span>Clear Search & Filters</span>
            </button>
          ) : (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => onNavigate('input-analysis')}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <Compass size={16} />
              <span>Analyze Incident 🧭</span>
            </button>
          )}
        </div>
      ) : viewMode === 'table' ? (
        /* CLEAN TABLE VIEW */
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            overflow: 'hidden',
            boxShadow: 'var(--shadow-sm)'
          }}
        >
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr
                  style={{
                    background: 'var(--bg-subtle)',
                    borderBottom: '1px solid var(--border-subtle)',
                    color: 'var(--text-muted)',
                    fontSize: '0.75rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    fontWeight: 600
                  }}
                >
                  <th style={{ padding: '12px 16px' }}>Analysis ID</th>
                  <th style={{ padding: '12px 16px' }}>Date / Time</th>
                  <th style={{ padding: '12px 16px' }}>Crime Category</th>
                  <th style={{ padding: '12px 16px' }}>Behavioral Pattern</th>
                  <th style={{ padding: '12px 16px' }}>Similarity Summary</th>
                  <th style={{ padding: '12px 16px' }}>Novelty Summary</th>
                  <th style={{ padding: '12px 16px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map((rec) => {
                  const catStyle = getCategoryBadgeStyle(rec.input_summary?.crime_category);
                  const novStyle = getNoveltyBadgeStyle(rec.novelty_summary?.novelty_tier, rec.novelty_summary?.is_novel);
                  const isTopMatched = rec.similarity_summary?.top_matched_incident_id;

                  return (
                    <tr
                      key={rec.analysis_id}
                      onClick={() => setSelectedRecord(rec)}
                      style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        cursor: 'pointer',
                        transition: 'background-color 0.15s ease'
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      {/* Analysis ID */}
                      <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span
                            className="mono"
                            style={{
                              fontWeight: 600,
                              color: 'var(--accent-cyan)',
                              fontSize: '0.8rem',
                              background: 'var(--accent-cyan-bg)',
                              padding: '2px 6px',
                              borderRadius: '4px',
                              border: '1px solid var(--accent-cyan-border)'
                            }}
                          >
                            {rec.analysis_id}
                          </span>
                          <button
                            type="button"
                            onClick={(e) => handleCopyId(rec.analysis_id, e)}
                            title="Copy Analysis ID"
                            style={{
                              background: 'transparent',
                              border: 'none',
                              color: copiedId === rec.analysis_id ? 'var(--accent-emerald)' : 'var(--text-dim)',
                              cursor: 'pointer',
                              padding: '2px'
                            }}
                          >
                            {copiedId === rec.analysis_id ? <Check size={13} /> : <Copy size={13} />}
                          </button>
                        </div>
                        {rec.input_summary?.scenario_title && (
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '4px', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {rec.input_summary.scenario_title}
                          </div>
                        )}
                      </td>

                      {/* Date / Time */}
                      <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                        <div style={{ color: 'var(--text-main)', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Calendar size={13} style={{ color: 'var(--text-dim)' }} />
                          <span>{formatDateTime(rec.timestamp)}</span>
                        </div>
                        {getRelativeTime(rec.timestamp) && (
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                            {getRelativeTime(rec.timestamp)}
                          </div>
                        )}
                      </td>

                      {/* Crime Category */}
                      <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            padding: '3px 8px',
                            borderRadius: '999px',
                            fontSize: '0.74rem',
                            fontWeight: 600,
                            background: catStyle.bg,
                            color: catStyle.text,
                            border: `1px solid ${catStyle.border}`
                          }}
                        >
                          <Tag size={11} />
                          <span>{(rec.input_summary?.crime_category || 'Unspecified').replace('_', ' ').toUpperCase()}</span>
                        </span>
                      </td>

                      {/* Behavioral Pattern */}
                      <td style={{ padding: '14px 16px', minWidth: '180px', maxWidth: '240px' }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.82rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {rec.pattern_summary?.pattern_name || `Behavioral Pattern #${(rec.pattern_summary?.cluster_id ?? 0) + 1}`}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '3px' }}>
                          <span className="badge" style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.06)' }}>
                            {rec.pattern_summary?.pattern_id || `CL_${rec.pattern_summary?.cluster_id}`}
                          </span>
                          {rec.pattern_summary?.association_tier && (
                            <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>
                              &bull; {rec.pattern_summary.association_tier}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Similarity Summary */}
                      <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                        {isTopMatched ? (
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span style={{ fontWeight: 700, color: 'var(--accent-emerald)', fontSize: '0.85rem' }}>
                                {(rec.similarity_summary?.similarity_percentage ?? 0).toFixed(1)}% Match
                              </span>
                              <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                                vs {rec.similarity_summary.top_matched_incident_id}
                              </span>
                            </div>
                            {rec.similarity_summary?.has_cross_crime_match && (
                              <div style={{ marginTop: '3px' }}>
                                <span className="badge" style={{ fontSize: '0.65rem', background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>
                                  Cross-Crime Link
                                </span>
                              </div>
                            )}
                          </div>
                        ) : (
                          <span style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>No match recorded</span>
                        )}
                      </td>

                      {/* Novelty Summary */}
                      <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span
                            style={{
                              padding: '2px 7px',
                              borderRadius: '999px',
                              fontSize: '0.72rem',
                              fontWeight: 600,
                              background: novStyle.bg,
                              color: novStyle.text,
                              border: `1px solid ${novStyle.border}`
                            }}
                          >
                            {novStyle.label}
                          </span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                            Score: {(rec.novelty_summary?.novelty_score ?? 0).toFixed(3)}
                          </span>
                        </div>
                        {rec.novelty_summary?.pattern_fit_score !== undefined && (
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                            Fit: {rec.novelty_summary.pattern_fit_score.toFixed(1)}%
                          </div>
                        )}
                      </td>

                      {/* Actions */}
                      <td style={{ padding: '14px 16px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                          <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedRecord(rec);
                            }}
                            title="Open Stored Analysis Result"
                            style={{ padding: '4px 8px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                          >
                            <span>Open</span>
                            <ArrowRight size={12} />
                          </button>
                          <button
                            type="button"
                            onClick={(e) => handleDeleteRecord(rec.analysis_id, e)}
                            title="Delete Record"
                            style={{
                              background: 'transparent',
                              border: 'none',
                              color: 'var(--text-dim)',
                              cursor: 'pointer',
                              padding: '5px',
                              borderRadius: '4px',
                              display: 'flex',
                              alignItems: 'center'
                            }}
                            onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--accent-rose)')}
                            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-dim)')}
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* CARD VIEW LAYOUT */
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '16px' }}>
          {records.map((rec) => {
            const catStyle = getCategoryBadgeStyle(rec.input_summary?.crime_category);
            const novStyle = getNoveltyBadgeStyle(rec.novelty_summary?.novelty_tier, rec.novelty_summary?.is_novel);
            const isTopMatched = rec.similarity_summary?.top_matched_incident_id;

            return (
              <div
                key={rec.analysis_id}
                onClick={() => setSelectedRecord(rec)}
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '18px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: 'var(--shadow-sm)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-bright)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  e.currentTarget.style.transform = 'none';
                  e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                }}
              >
                <div>
                  {/* Card Top Row: ID & Category Badge */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span
                        className="mono"
                        style={{
                          fontWeight: 700,
                          color: 'var(--accent-cyan)',
                          fontSize: '0.8rem',
                          background: 'var(--accent-cyan-bg)',
                          padding: '3px 7px',
                          borderRadius: '4px',
                          border: '1px solid var(--accent-cyan-border)'
                        }}
                      >
                        {rec.analysis_id}
                      </span>
                      <button
                        type="button"
                        onClick={(e) => handleCopyId(rec.analysis_id, e)}
                        title="Copy ID"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: copiedId === rec.analysis_id ? 'var(--accent-emerald)' : 'var(--text-dim)',
                          cursor: 'pointer',
                          padding: '2px'
                        }}
                      >
                        {copiedId === rec.analysis_id ? <Check size={13} /> : <Copy size={13} />}
                      </button>
                    </div>

                    <span
                      style={{
                        padding: '3px 8px',
                        borderRadius: '999px',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        background: catStyle.bg,
                        color: catStyle.text,
                        border: `1px solid ${catStyle.border}`
                      }}
                    >
                      {(rec.input_summary?.crime_category || 'Offense').replace('_', ' ').toUpperCase()}
                    </span>
                  </div>

                  {/* Title & Date */}
                  <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 6px' }}>
                    {rec.input_summary?.scenario_title || 'Simulated Crime Incident'}
                  </h4>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '14px' }}>
                    <Calendar size={13} />
                    <span>{formatDateTime(rec.timestamp)}</span>
                    {getRelativeTime(rec.timestamp) && <span>&bull; {getRelativeTime(rec.timestamp)}</span>}
                  </div>

                  {/* Highlights Grid */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr',
                      gap: '8px',
                      background: 'var(--bg-subtle)',
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-md)',
                      marginBottom: '14px',
                      border: '1px solid var(--border-subtle)'
                    }}
                  >
                    {/* Pattern */}
                    <div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Behavioral Pattern
                      </div>
                      <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {rec.pattern_summary?.pattern_name || `Behavioral Pattern #${(rec.pattern_summary?.cluster_id ?? 0) + 1}`}
                      </div>
                    </div>

                    {/* Similarity */}
                    <div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Historical Match
                      </div>
                      <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-emerald)', marginTop: '2px' }}>
                        {isTopMatched ? `${(rec.similarity_summary?.similarity_percentage ?? 0).toFixed(1)}%` : 'None'}
                        {isTopMatched && (
                          <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginLeft: '4px' }}>
                            ({rec.similarity_summary?.top_matched_incident_id})
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card Footer: Novelty Pill & View Button */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '10px', marginTop: '6px' }}>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: '999px',
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      background: novStyle.bg,
                      color: novStyle.text,
                      border: `1px solid ${novStyle.border}`
                    }}
                  >
                    {novStyle.label}
                  </span>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <button
                      type="button"
                      onClick={(e) => handleDeleteRecord(rec.analysis_id, e)}
                      title="Delete Record"
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-dim)',
                        cursor: 'pointer',
                        padding: '4px'
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--accent-rose)')}
                      onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-dim)')}
                    >
                      <Trash2 size={14} />
                    </button>

                    <span style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '3px', fontWeight: 600 }}>
                      <span>View</span>
                      <ArrowRight size={13} />
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* PAGINATION BAR */}
      {totalCount > 0 && !loading && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
            marginTop: '20px',
            padding: '12px 16px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)'
          }}
        >
          {/* Range indicator */}
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Showing {Math.min(totalCount, (page - 1) * pageSize + 1)}–{Math.min(totalCount, page * pageSize)} of {totalCount} analyses
          </div>

          {/* Page controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {/* Page Size Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginRight: '12px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Per page:</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
                style={{
                  background: 'var(--bg-subtle)',
                  color: 'var(--text-main)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '3px 8px',
                  fontSize: '0.78rem',
                  cursor: 'pointer'
                }}
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>

            {/* Prev Page Button */}
            <button
              type="button"
              className="btn btn-secondary"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              style={{
                padding: '5px 10px',
                fontSize: '0.8rem',
                opacity: page <= 1 ? 0.5 : 1,
                cursor: page <= 1 ? 'not-allowed' : 'pointer'
              }}
            >
              <ChevronLeft size={14} />
              <span>Prev</span>
            </button>

            {/* Page info */}
            <span style={{ fontSize: '0.8rem', color: 'var(--text-main)', padding: '0 4px', fontWeight: 600 }}>
              Page {page} of {totalPages}
            </span>

            {/* Next Page Button */}
            <button
              type="button"
              className="btn btn-secondary"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              style={{
                padding: '5px 10px',
                fontSize: '0.8rem',
                opacity: page >= totalPages ? 0.5 : 1,
                cursor: page >= totalPages ? 'not-allowed' : 'pointer'
              }}
            >
              <span>Next</span>
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          STORED ANALYSIS RESULT MODAL / INSPECTOR
          Opens when user clicks an analysis in the table or cards.
          ========================================================================= */}
      {selectedRecord && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(5px)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px'
          }}
          onClick={() => setSelectedRecord(null)}
        >
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-bright)',
              borderRadius: 'var(--radius-xl)',
              maxWidth: '860px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              boxShadow: 'var(--shadow-lg)',
              display: 'flex',
              flexDirection: 'column'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div
              style={{
                padding: '20px 24px',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                gap: '16px',
                position: 'sticky',
                top: 0,
                background: 'var(--bg-card)',
                zIndex: 10
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <span
                    className="mono"
                    style={{
                      fontSize: '0.85rem',
                      fontWeight: 700,
                      color: 'var(--accent-cyan)',
                      background: 'var(--accent-cyan-bg)',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      border: '1px solid var(--accent-cyan-border)'
                    }}
                  >
                    {selectedRecord.analysis_id}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleCopyId(selectedRecord.analysis_id)}
                    title="Copy Analysis ID"
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: copiedId === selectedRecord.analysis_id ? 'var(--accent-emerald)' : 'var(--text-dim)',
                      cursor: 'pointer',
                      padding: '2px'
                    }}
                  >
                    {copiedId === selectedRecord.analysis_id ? <Check size={14} /> : <Copy size={14} />}
                  </button>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                    &bull; Analyzed {formatDateTime(selectedRecord.timestamp)}
                  </span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0, color: 'var(--text-bright)' }}>
                  {selectedRecord.input_summary?.scenario_title || 'Stored Incident Analysis Result'}
                </h3>
              </div>

              <button
                type="button"
                className="btn-icon"
                onClick={() => setSelectedRecord(null)}
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '50%',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  color: 'var(--text-muted)'
                }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Informational Callout */}
              <div
                style={{
                  background: 'rgba(14, 165, 233, 0.08)',
                  border: '1px solid var(--accent-cyan-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: '12px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}
              >
                <Info size={18} style={{ color: 'var(--accent-cyan)', flexShrink: 0 }} />
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  This analytical audit record is securely preserved in your isolated user history. Based on patterns learned from historical incidents, reference scores and similarity metrics were evaluated against the historical incident dataset without altering model weights.
                </div>
              </div>

              {/* Quick Metrics Bar */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
                  gap: '12px'
                }}
              >
                {/* Metric: Historical Match */}
                <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '12px 14px' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Top Historical Match
                  </div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-emerald)', marginTop: '4px' }}>
                    {(selectedRecord.similarity_summary?.similarity_percentage ?? 0).toFixed(1)}%
                  </div>
                  <div className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    vs {selectedRecord.similarity_summary?.top_matched_incident_id || 'None'}
                  </div>
                </div>

                {/* Metric: Behavioral Pattern */}
                <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '12px 14px' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Behavioral Pattern
                  </div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {selectedRecord.pattern_summary?.pattern_name || `Behavioral Pattern #${(selectedRecord.pattern_summary?.cluster_id ?? 0) + 1}`}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {selectedRecord.pattern_summary?.association_tier || 'Standard Confidence'}
                  </div>
                </div>

                {/* Metric: Novelty Assessment */}
                <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '12px 14px' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Novelty Assessment
                  </div>
                  <div
                    style={{
                      fontSize: '1.05rem',
                      fontWeight: 700,
                      color: selectedRecord.novelty_summary?.is_novel ? 'var(--accent-rose)' : 'var(--accent-emerald)',
                      marginTop: '4px'
                    }}
                  >
                    {selectedRecord.novelty_summary?.novelty_tier || 'Standard'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Fit: {(selectedRecord.novelty_summary?.pattern_fit_score ?? 100).toFixed(1)}%
                  </div>
                </div>

                {/* Metric: Vector Dimensions */}
                <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '12px 14px' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    Behavioral DNA
                  </div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '4px' }}>
                    {selectedRecord.behavioral_dna?.vector_dimension || 70}D
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Unit L2 Hyper-Sphere
                  </div>
                </div>
              </div>

              {/* BEHAVIORAL PATTERN & FORMULA */}
              {selectedRecord.pattern_summary && (
                <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <Layers size={16} style={{ color: 'var(--accent-cyan)' }} />
                    <h4 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      Behavioral Pattern Formula & Clustering
                    </h4>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '10px' }}>
                    Assigned to archetype <strong>{selectedRecord.pattern_summary.pattern_name}</strong> (<code style={{ color: 'var(--accent-cyan)' }}>{selectedRecord.pattern_summary.pattern_id}</code>).
                  </div>
                  {selectedRecord.pattern_summary.behavioral_formula && (
                    <div
                      className="mono"
                      style={{
                        background: 'rgba(0, 0, 0, 0.35)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '10px 14px',
                        fontSize: '0.78rem',
                        color: 'var(--accent-cyan)',
                        wordBreak: 'break-word',
                        lineHeight: 1.5
                      }}
                    >
                      {selectedRecord.pattern_summary.behavioral_formula}
                    </div>
                  )}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginTop: '10px', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                    <span>Supporting Incidents: <strong>{selectedRecord.pattern_summary.supporting_incident_count.toLocaleString()}</strong></span>
                    <span>Confidence Score: <strong>{(selectedRecord.pattern_summary.association_strength_score).toFixed(1)}%</strong></span>
                  </div>
                </div>
              )}

              {/* BEHAVIORAL DNA SUB-PROFILE ENERGIES */}
              {selectedRecord.behavioral_dna?.subprofile_energies && (
                <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <Fingerprint size={16} style={{ color: 'var(--accent-cyan)' }} />
                    <h4 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      Behavioral DNA Sub-Profile Group Energies
                    </h4>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
                    {Object.entries(selectedRecord.behavioral_dna.subprofile_energies).map(([grp, score]) => {
                      const numVal = score as number;
                      const normVal = numVal > 1.0 ? numVal / 100.0 : numVal;
                      const pct = Math.min(100, Math.max(0, normVal * 100));
                      return (
                        <div key={grp} style={{ background: 'rgba(0,0,0,0.2)', padding: '8px 12px', borderRadius: 'var(--radius-sm)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
                            <span style={{ color: 'var(--text-muted)' }}>{grp.replace(/_/g, ' ').toUpperCase()}</span>
                            <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{normVal.toFixed(3)} ||v||₂</span>
                          </div>
                          <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.06)', borderRadius: '2px', overflow: 'hidden' }}>
                            <div style={{ width: `${pct}%`, height: '100%', background: 'var(--accent-cyan)' }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Top Active Traits Chips */}
                  {selectedRecord.behavioral_dna.top_active_traits && selectedRecord.behavioral_dna.top_active_traits.length > 0 && (
                    <div style={{ marginTop: '14px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '6px' }}>
                        Prominent Active Behavioral Traits:
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {selectedRecord.behavioral_dna.top_active_traits.slice(0, 6).map((trait: any, i: number) => (
                          <span
                            key={i}
                            className="badge"
                            style={{
                              fontSize: '0.72rem',
                              background: 'rgba(14, 165, 233, 0.1)',
                              color: 'var(--text-main)',
                              border: '1px solid var(--accent-cyan-border)'
                            }}
                          >
                            {trait.feature || trait.name || 'trait'}: {(trait.value ?? 0).toFixed(2)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* SIMULATED PARAMETERS SUMMARY (DATA MINIMIZATION / ZERO PII) */}
              {selectedRecord.input_summary && (
                <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <ShieldAlert size={16} style={{ color: 'var(--accent-emerald)' }} />
                    <h4 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      Simulated Incident Attributes (Zero PII Privacy Guard)
                    </h4>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px', fontSize: '0.8rem' }}>
                    <div>
                      <span style={{ color: 'var(--text-dim)' }}>Setting: </span>
                      <strong style={{ color: 'var(--text-main)' }}>{selectedRecord.input_summary.population_setting?.replace('_', ' ')}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-dim)' }}>Offenses: </span>
                      <strong style={{ color: 'var(--text-main)' }}>{selectedRecord.input_summary.incident_counts?.offense_count ?? 1}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-dim)' }}>Victims / Individuals Involved: </span>
                      <strong style={{ color: 'var(--text-main)' }}>
                        {selectedRecord.input_summary.incident_counts?.victim_count ?? 1} / {selectedRecord.input_summary.incident_counts?.offender_count ?? 1}
                      </strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-dim)' }}>Weapon Present: </span>
                      <strong style={{ color: selectedRecord.input_summary.behavioral_flags?.has_weapon ? 'var(--accent-amber)' : 'var(--text-muted)' }}>
                        {selectedRecord.input_summary.behavioral_flags?.has_weapon ? 'Yes' : 'No'}
                      </strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-dim)' }}>Injury Documented: </span>
                      <strong style={{ color: selectedRecord.input_summary.behavioral_flags?.has_injury ? 'var(--accent-rose)' : 'var(--text-muted)' }}>
                        {selectedRecord.input_summary.behavioral_flags?.has_injury ? 'Yes' : 'No'}
                      </strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-dim)' }}>Prior Relationship: </span>
                      <strong style={{ color: 'var(--text-main)' }}>
                        {selectedRecord.input_summary.behavioral_flags?.has_relationship ? 'Known' : 'Stranger / None'}
                      </strong>
                    </div>
                  </div>
                </div>
              )}

              {/* MANDATORY INVESTIGATIVE & ETHICAL ADVISORY */}
              <div
                style={{
                  background: 'rgba(244, 63, 94, 0.05)',
                  border: '1px solid rgba(244, 63, 94, 0.2)',
                  borderRadius: 'var(--radius-md)',
                  padding: '12px 16px',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px'
                }}
              >
                <ShieldAlert size={16} style={{ color: 'var(--accent-rose)', flexShrink: 0, marginTop: '2px' }} />
                <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
                  <strong style={{ color: 'var(--text-main)' }}>Advisory: </strong>
                  {selectedRecord.ethical_advisory || 'Crime Compass analyzes incident characteristics and historical behavioral patterns. Similarity or novelty does not establish offender identity, guilt, or causation.'}
                </div>
              </div>
            </div>

            {/* Modal Footer Actions */}
            <div
              style={{
                padding: '16px 24px',
                borderTop: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px',
                background: 'var(--bg-subtle)'
              }}
            >
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => handleDeleteRecord(selectedRecord.analysis_id)}
                disabled={deleteActionLoading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  color: 'var(--accent-rose)',
                  borderColor: 'rgba(244, 63, 94, 0.3)',
                  fontSize: '0.82rem'
                }}
              >
                <Trash2 size={14} />
                <span>Delete from History</span>
              </button>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {selectedRecord.similarity_summary?.top_matched_incident_id && (
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                      const matchedId = selectedRecord.similarity_summary.top_matched_incident_id;
                      setSelectedRecord(null);
                      onNavigate('incident-analyzer', { incidentId: matchedId });
                    }}
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem' }}
                  >
                    <ExternalLink size={14} />
                    <span>View Matched Incident ({selectedRecord.similarity_summary.top_matched_incident_id})</span>
                  </button>
                )}

                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => {
                    const fullRes = selectedRecord.full_result;
                    setSelectedRecord(null);
                    onNavigate('input-analysis', {
                      analysisId: selectedRecord.analysis_id,
                      analysisResult: fullRes,
                      initialPayload: selectedRecord.input_summary
                    });
                  }}
                  style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem' }}
                >
                  <Compass size={14} />
                  <span>Open Full Crime Compass Analysis 🧭</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
