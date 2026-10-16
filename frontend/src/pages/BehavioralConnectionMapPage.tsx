import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../api';
import {
  BehavioralConnectionMapResponse,
  GraphNode,
  GraphEdge
} from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import {
  Network,
  Clock,
  MapPin,
  Package,
  Shield,
  ShieldAlert,
  Sparkles,
  Layers,
  ChevronRight,
  Info,
  CheckCircle2,
  X,
  Filter,
  ArrowRight,
  RotateCcw
} from 'lucide-react';

interface BehavioralConnectionMapPageProps {
  initialPatternId?: string;
  initialCategory?: string;
  onNavigate?: (page: string, params?: any) => void;
}

export const BehavioralConnectionMapPage: React.FC<BehavioralConnectionMapPageProps> = ({
  initialPatternId,
  initialCategory,
  onNavigate,
}) => {
  const [graphData, setGraphData] = useState<BehavioralConnectionMapResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Interaction State
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [hoveredEdgeId, setHoveredEdgeId] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState<string>(initialCategory || 'ALL');
  const [patternFilter, setPatternFilter] = useState<string>(initialPatternId || 'ALL');

  const fetchGraph = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getConnectionMap();
      setGraphData(res);

      // Auto-select initial edge if params provided
      if (initialPatternId || initialCategory) {
        const matchingEdge = res.edges.find((e) => {
          if (initialPatternId && e.target_label !== initialPatternId) return false;
          if (initialCategory && e.source_label !== initialCategory) return false;
          return true;
        });
        if (matchingEdge) {
          setSelectedEdgeId(matchingEdge.id);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Could not load behavioral connection map');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  // Separate nodes by type
  const { categoryNodes, patternNodes, filteredEdges } = useMemo(() => {
    if (!graphData) return { categoryNodes: [], patternNodes: [], filteredEdges: [] };

    const cats = graphData.nodes.filter((n) => n.type === 'crime_category');
    const pats = graphData.nodes.filter((n) => n.type === 'behavioral_pattern');

    const edges = graphData.edges.filter((e) => {
      if (categoryFilter !== 'ALL' && e.source_label !== categoryFilter) return false;
      if (patternFilter !== 'ALL' && e.target_label !== patternFilter) return false;
      return true;
    });

    return { categoryNodes: cats, patternNodes: pats, filteredEdges: edges };
  }, [graphData, categoryFilter, patternFilter]);

  // Compute node coordinates for bipartite SVG layout
  const { nodeCoordinates, svgHeight } = useMemo(() => {
    const coords: Record<string, { x: number; y: number }> = {};
    const leftX = 180;
    const rightX = 740;

    const catSpacing = 74;
    const patSpacing = 72;
    const startY = 60;

    const totalHeight = Math.max(
      categoryNodes.length * catSpacing,
      patternNodes.length * patSpacing
    ) + 120;

    categoryNodes.forEach((node, i) => {
      coords[node.id] = {
        x: leftX,
        y: startY + i * catSpacing,
      };
    });

    patternNodes.forEach((node, j) => {
      coords[node.id] = {
        x: rightX,
        y: startY + j * patSpacing,
      };
    });

    return { nodeCoordinates: coords, svgHeight: Math.max(620, totalHeight) };
  }, [categoryNodes, patternNodes]);

  // Active selected edge
  const activeEdge = useMemo(() => {
    if (!graphData || !selectedEdgeId) return null;
    return graphData.edges.find((e) => e.id === selectedEdgeId) || null;
  }, [graphData, selectedEdgeId]);

  // Active selected node
  const activeNode = useMemo(() => {
    if (!graphData || !selectedNodeId) return null;
    return graphData.nodes.find((n) => n.id === selectedNodeId) || null;
  }, [graphData, selectedNodeId]);

  // Connected edges for the active/hovered node
  const highlightedNodeIds = useMemo(() => {
    const nodeFocus = hoveredNodeId || selectedNodeId;
    if (!nodeFocus || !graphData) return null;

    const connected = new Set<string>();
    connected.add(nodeFocus);

    graphData.edges.forEach((e) => {
      if (e.source === nodeFocus) connected.add(e.target);
      if (e.target === nodeFocus) connected.add(e.source);
    });

    return connected;
  }, [hoveredNodeId, selectedNodeId, graphData]);

  if (loading) {
    return <LoadingState message="Computing behavioral relationships across 220,663 crime incidents..." />;
  }

  if (error || !graphData) {
    return <ErrorState error={error || 'Failed to load graph'} onRetry={fetchGraph} />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '1360px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span
              style={{
                background: 'var(--accent-amber-bg)',
                color: 'var(--accent-amber)',
                border: '1px solid var(--accent-amber-border)',
                padding: '3px 8px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.75rem',
                fontWeight: 700,
              }}
              className="mono"
            >
              BEHAVIORAL NETWORK TOPOLOGY
            </span>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>
              {graphData.total_nodes} Nodes &bull; {graphData.total_edges} Empirical Connections &bull; {graphData.corpus_incident_count.toLocaleString()} Incidents
            </span>
          </div>
          <h1 style={{ fontSize: '1.9rem', color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
            Behavioral Connection Map
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginTop: '4px', maxWidth: '820px' }}>
            Visualizes empirical relationships between <strong>Crime Categories</strong> and <strong>Behavioral Patterns</strong>. Connections represent shared modus operandi characteristics (Time, Location, Property, Weapons) discovered via unsupervised machine learning.
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={() => {
              setCategoryFilter('ALL');
              setPatternFilter('ALL');
              setSelectedEdgeId(null);
              setSelectedNodeId(null);
            }}
            className="btn btn-secondary"
            style={{ fontSize: '0.82rem', padding: '7px 12px', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RotateCcw size={14} /> Reset View
          </button>
          {onNavigate && (
            <button
              onClick={() => onNavigate('behavioral-patterns')}
              className="btn btn-secondary"
              style={{ fontSize: '0.82rem', padding: '7px 12px' }}
            >
              Explore Pattern Cards →
            </button>
          )}
        </div>
      </div>

      {/* Mandatory Non-Offender & Scientific Disclaimer */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 16px',
          background: 'rgba(244, 63, 94, 0.08)',
          border: '1px solid var(--accent-rose-border)',
          borderRadius: 'var(--radius-md)',
        }}
      >
        <ShieldAlert size={18} style={{ color: 'var(--accent-rose)', flexShrink: 0 }} />
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
          <strong style={{ color: 'var(--text-main)' }}>Scientific Advisory: </strong>
          {graphData.ethical_advisory}
        </div>
      </div>

      {/* Interactive Controls Bar: Filter by Category / Pattern */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '14px',
          alignItems: 'center',
          padding: '12px 18px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.84rem', color: 'var(--text-dim)' }}>
          <Filter size={15} />
          <span>Filter Relationships:</span>
        </div>

        {/* Crime Category Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Category:</span>
          <select
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value);
              setSelectedEdgeId(null);
            }}
            style={{
              background: 'var(--bg-subtle)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-bright)',
              borderRadius: 'var(--radius-sm)',
              padding: '5px 10px',
              fontSize: '0.82rem',
              cursor: 'pointer',
              outline: 'none',
            }}
          >
            <option value="ALL">All Categories ({categoryNodes.length})</option>
            {categoryNodes.map((c) => (
              <option key={c.id} value={c.label}>
                {c.label} ({c.incident_count.toLocaleString()})
              </option>
            ))}
          </select>
        </div>

        {/* Behavioral Pattern Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Pattern:</span>
          <select
            value={patternFilter}
            onChange={(e) => {
              setPatternFilter(e.target.value);
              setSelectedEdgeId(null);
            }}
            style={{
              background: 'var(--bg-subtle)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-bright)',
              borderRadius: 'var(--radius-sm)',
              padding: '5px 10px',
              fontSize: '0.82rem',
              cursor: 'pointer',
              outline: 'none',
            }}
          >
            <option value="ALL">All Patterns ({patternNodes.length})</option>
            {patternNodes.map((p) => (
              <option key={p.id} value={p.label}>
                {p.label}: {p.title}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginLeft: 'auto', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
          Showing <strong>{filteredEdges.length}</strong> active connections
        </div>
      </div>

      {/* Main Graph Grid: Left SVG Graph, Right Shared DNA Inspector */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: activeEdge || activeNode ? 'minmax(540px, 1fr) 380px' : '1fr',
          gap: '20px',
          alignItems: 'start',
        }}
      >
        {/* SVG Interactive Canvas */}
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '16px',
            position: 'relative',
            overflowX: 'auto',
          }}
        >
          {/* Legend */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '4px 12px 14px 12px',
              borderBottom: '1px solid var(--border-subtle)',
              fontSize: '0.75rem',
              color: 'var(--text-dim)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#0ea5e9', display: 'inline-block' }} />
              <span><strong>Crime Categories</strong> (Statutory Offense Types)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontStyle: 'italic' }}>Click any line to inspect Shared Behavioral DNA</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#a855f7', display: 'inline-block' }} />
              <span><strong>Behavioral Patterns</strong> (Learned MO Archetypes)</span>
            </div>
          </div>

          <svg
            viewBox={`0 0 960 ${svgHeight}`}
            style={{ width: '100%', height: 'auto', minHeight: '560px', display: 'block' }}
          >
            <defs>
              {/* Glow filter for hovered / active edges */}
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Render Edges */}
            <g className="edges-layer">
              {filteredEdges.map((edge) => {
                const src = nodeCoordinates[edge.source];
                const tgt = nodeCoordinates[edge.target];
                if (!src || !tgt) return null;

                const isSelected = selectedEdgeId === edge.id;
                const isHovered = hoveredEdgeId === edge.id;
                const isNodeHighlighted =
                  highlightedNodeIds && (highlightedNodeIds.has(edge.source) && highlightedNodeIds.has(edge.target));

                // Bezier curve control points
                const x1 = src.x + 85;
                const y1 = src.y;
                const x2 = tgt.x - 90;
                const y2 = tgt.y;
                const cx1 = x1 + (x2 - x1) * 0.45;
                const cx2 = x2 - (x2 - x1) * 0.45;

                const pathData = `M ${x1} ${y1} C ${cx1} ${y1}, ${cx2} ${y2}, ${x2} ${y2}`;

                // Calculate stroke width based on incident count
                const strokeWidth = isSelected
                  ? 4.5
                  : isHovered
                  ? 3.8
                  : Math.max(1.5, Math.min(5, Math.log10(edge.incident_count + 1) * 1.1));

                const strokeColor = isSelected
                  ? 'var(--accent-amber)'
                  : isHovered
                  ? 'var(--accent-cyan)'
                  : isNodeHighlighted
                  ? 'var(--accent-purple)'
                  : 'rgba(255, 255, 255, 0.16)';

                const opacity = isSelected || isHovered ? 1.0 : isNodeHighlighted ? 0.85 : 0.28;

                return (
                  <path
                    key={edge.id}
                    d={pathData}
                    fill="none"
                    stroke={strokeColor}
                    strokeWidth={strokeWidth}
                    strokeOpacity={opacity}
                    filter={isSelected || isHovered ? 'url(#glow)' : undefined}
                    style={{
                      cursor: 'pointer',
                      transition: 'stroke 0.15s ease, stroke-width 0.15s ease, stroke-opacity 0.15s ease',
                    }}
                    onMouseEnter={() => setHoveredEdgeId(edge.id)}
                    onMouseLeave={() => setHoveredEdgeId(null)}
                    onClick={() => {
                      setSelectedEdgeId(edge.id);
                      setSelectedNodeId(null);
                    }}
                  />
                );
              })}
            </g>

            {/* Render Category Nodes (Left Column) */}
            <g className="category-nodes-layer">
              {categoryNodes.map((cat) => {
                const pos = nodeCoordinates[cat.id];
                if (!pos) return null;

                const isHighlighted = highlightedNodeIds ? highlightedNodeIds.has(cat.id) : true;
                const isSelected = selectedNodeId === cat.id;

                return (
                  <g
                    key={cat.id}
                    transform={`translate(${pos.x}, ${pos.y})`}
                    style={{ cursor: 'pointer', opacity: isHighlighted ? 1.0 : 0.35, transition: 'opacity 0.2s ease' }}
                    onMouseEnter={() => setHoveredNodeId(cat.id)}
                    onMouseLeave={() => setHoveredNodeId(null)}
                    onClick={() => {
                      setSelectedNodeId(cat.id);
                      // Clear edge selection if clicking node
                      setSelectedEdgeId(null);
                    }}
                  >
                    {/* Node Background Pill */}
                    <rect
                      x="-85"
                      y="-22"
                      width="170"
                      height="44"
                      rx="8"
                      fill="var(--bg-subtle)"
                      stroke={isSelected ? 'var(--accent-cyan)' : cat.color}
                      strokeWidth={isSelected ? 2.5 : 1.2}
                      strokeOpacity={0.8}
                    />

                    {/* Left Color Accent Bar */}
                    <rect x="-85" y="-22" width="6" height="44" rx="3" fill={cat.color} />

                    {/* Category Label */}
                    <text
                      x="-70"
                      y="-4"
                      fill="var(--text-main)"
                      fontSize="11.5"
                      fontWeight="700"
                      fontFamily="var(--font-sans)"
                    >
                      {cat.label.length > 20 ? `${cat.label.slice(0, 19)}...` : cat.label}
                    </text>

                    {/* Incident Count Badge */}
                    <text
                      x="-70"
                      y="13"
                      fill="var(--text-dim)"
                      fontSize="9.5"
                      fontFamily="var(--font-mono)"
                    >
                      {cat.incident_count.toLocaleString()} cases ({cat.percentage}%)
                    </text>
                  </g>
                );
              })}
            </g>

            {/* Render Behavioral Pattern Nodes (Right Column) */}
            <g className="pattern-nodes-layer">
              {patternNodes.map((pat) => {
                const pos = nodeCoordinates[pat.id];
                if (!pos) return null;

                const isHighlighted = highlightedNodeIds ? highlightedNodeIds.has(pat.id) : true;
                const isSelected = selectedNodeId === pat.id;

                return (
                  <g
                    key={pat.id}
                    transform={`translate(${pos.x}, ${pos.y})`}
                    style={{ cursor: 'pointer', opacity: isHighlighted ? 1.0 : 0.35, transition: 'opacity 0.2s ease' }}
                    onMouseEnter={() => setHoveredNodeId(pat.id)}
                    onMouseLeave={() => setHoveredNodeId(null)}
                    onClick={() => {
                      setSelectedNodeId(pat.id);
                      setSelectedEdgeId(null);
                    }}
                  >
                    {/* Node Background Pill */}
                    <rect
                      x="-90"
                      y="-22"
                      width="180"
                      height="44"
                      rx="8"
                      fill="var(--bg-subtle)"
                      stroke={isSelected ? 'var(--accent-purple)' : 'var(--accent-purple-border)'}
                      strokeWidth={isSelected ? 2.5 : 1.2}
                    />

                    {/* Right Color Accent Bar */}
                    <rect x="84" y="-22" width="6" height="44" rx="3" fill="var(--accent-purple)" />

                    {/* Pattern ID Badge */}
                    <text
                      x="-80"
                      y="-4"
                      fill="var(--accent-purple)"
                      fontSize="10"
                      fontWeight="800"
                      fontFamily="var(--font-mono)"
                    >
                      {pat.label}
                    </text>

                    {/* Pattern Title Short */}
                    <text
                      x="-80"
                      y="13"
                      fill="var(--text-main)"
                      fontSize="10"
                      fontWeight="600"
                      fontFamily="var(--font-sans)"
                    >
                      {pat.title.length > 22 ? `${pat.title.slice(0, 21)}...` : pat.title}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        {/* Right Inspection Drawer: Shared Behavioral DNA */}
        {(activeEdge || activeNode) && (
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--accent-amber-border)',
              borderRadius: 'var(--radius-lg)',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '18px',
              animation: 'fadeIn 0.15s ease',
              boxShadow: 'var(--shadow-md)',
            }}
          >
            {/* If an Edge is selected: Display Shared Behavioral DNA */}
            {activeEdge && (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <span
                      style={{
                        background: 'var(--accent-amber-bg)',
                        color: 'var(--accent-amber)',
                        border: '1px solid var(--accent-amber-border)',
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.72rem',
                        fontWeight: 800,
                      }}
                      className="mono"
                    >
                      SHARED BEHAVIORAL DNA
                    </span>
                    <h3 style={{ fontSize: '1.15rem', color: 'var(--text-main)', marginTop: '6px' }}>
                      {activeEdge.source_label} <span style={{ color: 'var(--text-dim)' }}>&harr;</span> {activeEdge.target_label}
                    </h3>
                  </div>
                  <button
                    onClick={() => setSelectedEdgeId(null)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer', padding: 0 }}
                  >
                    <X size={18} />
                  </button>
                </div>

                {/* Quantitative Link Metrics */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '10px',
                    background: 'var(--bg-subtle)',
                    padding: '12px',
                    borderRadius: 'var(--radius-sm)',
                  }}
                >
                  <div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                      Incidents In Common
                    </div>
                    <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--accent-amber)', marginTop: '2px' }}>
                      {activeEdge.incident_count.toLocaleString()}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {activeEdge.percentage_of_pattern.toFixed(1)}% of pattern
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                      Cosine Convergence
                    </div>
                    <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--accent-emerald)', marginTop: '2px' }}>
                      {activeEdge.similarity_score.toFixed(1)}%
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {activeEdge.strength_label}
                    </div>
                  </div>
                </div>

                {/* Key Shared Modus Operandi Dimensions */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Shared Behavioral Dimensions:
                  </div>

                  {/* 1. Time */}
                  <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: 'var(--accent-amber)', fontWeight: 700 }}>
                      <Clock size={14} /> Time Pattern
                    </div>
                    <div style={{ fontSize: '0.83rem', color: 'var(--text-main)', marginTop: '3px' }}>
                      {activeEdge.shared_behavioral_dna.time}
                    </div>
                  </div>

                  {/* 2. Location */}
                  <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: 'var(--accent-cyan)', fontWeight: 700 }}>
                      <MapPin size={14} /> Location & Jurisdiction
                    </div>
                    <div style={{ fontSize: '0.83rem', color: 'var(--text-main)', marginTop: '3px' }}>
                      {activeEdge.shared_behavioral_dna.location}
                    </div>
                  </div>

                  {/* 3. Property */}
                  <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: 'var(--accent-emerald)', fontWeight: 700 }}>
                      <Package size={14} /> Property Dynamics
                    </div>
                    <div style={{ fontSize: '0.83rem', color: 'var(--text-main)', marginTop: '3px' }}>
                      {activeEdge.shared_behavioral_dna.property}
                    </div>
                  </div>

                  {/* 4. Weapons & Method */}
                  <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: 'var(--accent-rose)', fontWeight: 700 }}>
                      <Shield size={14} /> Weapon & Harm
                    </div>
                    <div style={{ fontSize: '0.83rem', color: 'var(--text-main)', marginTop: '3px' }}>
                      {activeEdge.shared_behavioral_dna.weapon} &bull; {activeEdge.shared_behavioral_dna.context_harm}
                    </div>
                  </div>
                </div>

                {/* Key Shared Traits Badges */}
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '6px' }}>
                    Matching Modus Operandi Traits:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {activeEdge.shared_behavioral_dna.key_shared_traits.map((t, idx) => (
                      <span
                        key={idx}
                        style={{
                          fontSize: '0.75rem',
                          padding: '3px 8px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--text-main)',
                        }}
                      >
                        &check; {t}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Why Connected Narrative */}
                <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '10px' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.45', margin: 0 }}>
                    {activeEdge.shared_behavioral_dna.why_connected}
                  </p>
                </div>
              </>
            )}

            {/* If a Node is selected without an edge */}
            {activeNode && !activeEdge && (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <span
                      style={{
                        background: activeNode.type === 'crime_category' ? 'var(--accent-cyan-bg)' : 'var(--accent-purple-bg)',
                        color: activeNode.type === 'crime_category' ? 'var(--accent-cyan)' : 'var(--accent-purple)',
                        border: `1px solid ${activeNode.type === 'crime_category' ? 'var(--accent-cyan-border)' : 'var(--accent-purple-border)'}`,
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.72rem',
                        fontWeight: 800,
                      }}
                      className="mono"
                    >
                      {activeNode.type === 'crime_category' ? 'CRIME CATEGORY' : 'BEHAVIORAL PATTERN'}
                    </span>
                    <h3 style={{ fontSize: '1.15rem', color: 'var(--text-main)', marginTop: '6px' }}>
                      {activeNode.title}
                    </h3>
                  </div>
                  <button
                    onClick={() => setSelectedNodeId(null)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer', padding: 0 }}
                  >
                    <X size={18} />
                  </button>
                </div>

                <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Historical Incident Representation</div>
                  <div style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '2px' }}>
                    {activeNode.incident_count.toLocaleString()} cases
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {activeNode.percentage}% of the historical dataset
                  </div>
                </div>

                {activeNode.details && activeNode.details.formula && (
                  <div
                    style={{
                      padding: '10px 12px',
                      background: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid var(--border-bright)',
                      borderRadius: 'var(--radius-sm)',
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 700 }}>
                      Empirical Behavioral Formula:
                    </div>
                    <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
                      {activeNode.details.formula}
                    </div>
                  </div>
                )}

                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                  {activeNode.details && activeNode.details.description ? activeNode.details.description : activeNode.details?.summary}
                </p>

                <div style={{ fontSize: '0.78rem', color: 'var(--accent-amber)', fontStyle: 'italic' }}>
                  Tip: Click any connection line touching this node to see the exact shared Behavioral DNA!
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
