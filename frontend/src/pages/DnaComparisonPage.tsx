import React, { useState, useEffect } from 'react';
import { api } from '../api';
import {
  DnaComparisonResponse,
  ComparisonPreset
} from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import {
  ArrowLeftRight,
  Sparkles,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Zap,
  TrendingUp,
  Sliders,
  History,
  FileEdit,
  ChevronRight
} from 'lucide-react';

interface DnaComparisonPageProps {
  onNavigate?: (page: string, params?: Record<string, any>) => void;
}

export function DnaComparisonPage({ onNavigate }: DnaComparisonPageProps = {}) {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [presets, setPresets] = useState<ComparisonPreset[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>('preset_theft_vs_burglary');

  // Input modes for Incident A and B: 'custom' | 'historical'
  const [modeA, setModeA] = useState<'custom' | 'historical'>('custom');
  const [modeB, setModeB] = useState<'custom' | 'historical'>('custom');

  // Incident A state
  const [histIdA, setHistIdA] = useState<string>('INC_000001');
  const [payloadA, setPayloadA] = useState<any>({
    scenario_title: 'Daytime Residential Theft',
    incident_date: '2024-04-12',
    incident_time: '14:30',
    crime_category: 'theft',
    location_type: 'residential',
    is_weekend: false,
    has_property: true,
    property_value: 1200.0,
    has_weapon: false,
    has_injury: false,
    victim_count: 1
  });

  // Incident B state
  const [histIdB, setHistIdB] = useState<string>('INC_000002');
  const [payloadB, setPayloadB] = useState<any>({
    scenario_title: 'Nocturnal Residential Burglary',
    incident_date: '2024-04-18',
    incident_time: '02:15',
    crime_category: 'burglary',
    location_type: 'residential',
    is_weekend: true,
    has_property: true,
    property_value: 3500.0,
    has_weapon: true,
    weapon_count: 1,
    has_injury: false,
    victim_count: 1
  });

  const [comparisonResult, setComparisonResult] = useState<DnaComparisonResponse | null>(null);

  // Load presets on mount
  useEffect(() => {
    api.getComparisonPresets()
      .then((data) => {
        if (data.presets && data.presets.length > 0) {
          setPresets(data.presets);
          loadPreset(data.presets[0]);
        }
      })
      .catch((err) => {
        loggerError('Failed to load comparison presets', err);
      });
  }, []);

  const loggerError = (msg: string, err: any) => {
    console.warn(msg, err);
  };

  const loadPreset = (preset: ComparisonPreset) => {
    setSelectedPresetId(preset.id);
    // Configure Incident A
    if (preset.incident_a.incident_id) {
      setModeA('historical');
      setHistIdA(preset.incident_a.incident_id);
    } else {
      setModeA('custom');
      setPayloadA(preset.incident_a.input_data || {});
    }

    // Configure Incident B
    if (preset.incident_b.incident_id) {
      setModeB('historical');
      setHistIdB(preset.incident_b.incident_id);
    } else {
      setModeB('custom');
      setPayloadB(preset.incident_b.input_data || {});
    }
  };

  const handleCompare = async () => {
    setLoading(true);
    setError(null);

    const specA = modeA === 'historical'
      ? { incident_id: histIdA.trim() }
      : { input_data: payloadA, label: payloadA.scenario_title || 'Incident A' };

    const specB = modeB === 'historical'
      ? { incident_id: histIdB.trim() }
      : { input_data: payloadB, label: payloadB.scenario_title || 'Incident B' };

    try {
      const res = await api.compareIncidents({
        incident_a: specA,
        incident_b: specB
      });
      setComparisonResult(res);
    } catch (err: any) {
      setError(err?.detail || err?.message || 'Comparison failed. Please verify input values.');
    } finally {
      setLoading(false);
    }
  };

  // Run initial comparison when first loaded
  useEffect(() => {
    handleCompare();
  }, [selectedPresetId]);

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '24px 16px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
          <div
            style={{
              padding: '8px',
              borderRadius: '8px',
              background: 'rgba(56, 189, 248, 0.15)',
              color: '#38bdf8'
            }}
          >
            <ArrowLeftRight size={22} />
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-bright)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>⚖️ Behavioral Comparison</span>
              <span role="img" aria-label="compass">🧭</span>
            </h1>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Side-by-side comparative behavioral fingerprint analysis: Incident A vs Incident B
            </p>
          </div>
        </div>
      </div>

      {/* Preset Selector */}
      {presets.length > 0 && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '12px',
            padding: '16px 20px',
            marginBottom: '24px'
          }}
        >
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '10px' }}>
            Quick Comparison Presets
          </div>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {presets.map((p) => {
              const isActive = selectedPresetId === p.id;
              return (
                <button
                  key={p.id}
                  onClick={() => loadPreset(p)}
                  style={{
                    padding: '8px 14px',
                    borderRadius: '8px',
                    border: isActive ? '1px solid #38bdf8' : '1px solid var(--border-subtle)',
                    background: isActive ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-dark)',
                    color: isActive ? '#38bdf8' : 'var(--text-bright)',
                    fontSize: '0.82rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {p.title}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Comparison Setup Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '20px',
          marginBottom: '24px'
        }}
      >
        {/* Incident A Configuration Card */}
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '12px',
            padding: '20px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.1rem' }}>🅰️</span>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                Incident A
              </h3>
            </div>
            {/* Mode Toggle */}
            <div style={{ display: 'flex', background: 'var(--bg-dark)', padding: '2px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              <button
                onClick={() => setModeA('custom')}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  border: 'none',
                  background: modeA === 'custom' ? '#38bdf8' : 'transparent',
                  color: modeA === 'custom' ? '#000' : 'var(--text-muted)',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                Custom Input
              </button>
              <button
                onClick={() => setModeA('historical')}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  border: 'none',
                  background: modeA === 'historical' ? '#38bdf8' : 'transparent',
                  color: modeA === 'historical' ? '#000' : 'var(--text-muted)',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                Historical ID
              </button>
            </div>
          </div>

          {modeA === 'historical' ? (
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                Historical Incident ID
              </label>
              <input
                type="text"
                value={histIdA}
                onChange={(e) => setHistIdA(e.target.value)}
                placeholder="e.g. INC_000001"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  background: 'var(--bg-dark)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-bright)',
                  fontSize: '0.85rem'
                }}
              />
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginTop: '4px' }}>
                Loads existing 70D Behavioral DNA vector and ground truth metadata.
              </span>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Title / Scenario
                </label>
                <input
                  type="text"
                  value={payloadA.scenario_title || ''}
                  onChange={(e) => setPayloadA({ ...payloadA, scenario_title: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '6px 10px',
                    borderRadius: '6px',
                    background: 'var(--bg-dark)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-bright)',
                    fontSize: '0.8rem'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Crime Category
                  </label>
                  <select
                    value={payloadA.crime_category || 'theft'}
                    onChange={(e) => setPayloadA({ ...payloadA, crime_category: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '6px',
                      background: 'var(--bg-dark)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-bright)',
                      fontSize: '0.8rem'
                    }}
                  >
                    <option value="theft">Theft</option>
                    <option value="burglary">Burglary</option>
                    <option value="robbery">Robbery</option>
                    <option value="assault">Assault</option>
                    <option value="motor_vehicle_theft">Motor Vehicle Theft</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Location Type
                  </label>
                  <select
                    value={payloadA.location_type || 'residential'}
                    onChange={(e) => setPayloadA({ ...payloadA, location_type: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '6px',
                      background: 'var(--bg-dark)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-bright)',
                      fontSize: '0.8rem'
                    }}
                  >
                    <option value="residential">Residential</option>
                    <option value="commercial">Commercial</option>
                    <option value="street_outdoor">Street / Outdoor</option>
                    <option value="vehicle">Vehicle</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Incident Time
                  </label>
                  <input
                    type="time"
                    value={payloadA.incident_time || '14:30'}
                    onChange={(e) => setPayloadA({ ...payloadA, incident_time: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '6px',
                      background: 'var(--bg-dark)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-bright)',
                      fontSize: '0.8rem'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Weapon
                  </label>
                  <select
                    value={payloadA.has_weapon ? 'yes' : 'no'}
                    onChange={(e) => setPayloadA({ ...payloadA, has_weapon: e.target.value === 'yes', weapon_count: e.target.value === 'yes' ? 1 : 0 })}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '6px',
                      background: 'var(--bg-dark)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-bright)',
                      fontSize: '0.8rem'
                    }}
                  >
                    <option value="no">None (Unarmed)</option>
                    <option value="yes">Weapon Present</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Incident B Configuration Card */}
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '12px',
            padding: '20px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.1rem' }}>🅱️</span>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                Incident B
              </h3>
            </div>
            {/* Mode Toggle */}
            <div style={{ display: 'flex', background: 'var(--bg-dark)', padding: '2px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              <button
                onClick={() => setModeB('custom')}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  border: 'none',
                  background: modeB === 'custom' ? '#38bdf8' : 'transparent',
                  color: modeB === 'custom' ? '#000' : 'var(--text-muted)',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                Custom Input
              </button>
              <button
                onClick={() => setModeB('historical')}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  border: 'none',
                  background: modeB === 'historical' ? '#38bdf8' : 'transparent',
                  color: modeB === 'historical' ? '#000' : 'var(--text-muted)',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                Historical ID
              </button>
            </div>
          </div>

          {modeB === 'historical' ? (
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                Historical Incident ID
              </label>
              <input
                type="text"
                value={histIdB}
                onChange={(e) => setHistIdB(e.target.value)}
                placeholder="e.g. INC_000002"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  background: 'var(--bg-dark)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-bright)',
                  fontSize: '0.85rem'
                }}
              />
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginTop: '4px' }}>
                Loads existing 70D Behavioral DNA vector and ground truth metadata.
              </span>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Title / Scenario
                </label>
                <input
                  type="text"
                  value={payloadB.scenario_title || ''}
                  onChange={(e) => setPayloadB({ ...payloadB, scenario_title: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '6px 10px',
                    borderRadius: '6px',
                    background: 'var(--bg-dark)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-bright)',
                    fontSize: '0.8rem'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Crime Category
                  </label>
                  <select
                    value={payloadB.crime_category || 'burglary'}
                    onChange={(e) => setPayloadB({ ...payloadB, crime_category: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '6px',
                      background: 'var(--bg-dark)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-bright)',
                      fontSize: '0.8rem'
                    }}
                  >
                    <option value="theft">Theft</option>
                    <option value="burglary">Burglary</option>
                    <option value="robbery">Robbery</option>
                    <option value="assault">Assault</option>
                    <option value="motor_vehicle_theft">Motor Vehicle Theft</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Location Type
                  </label>
                  <select
                    value={payloadB.location_type || 'residential'}
                    onChange={(e) => setPayloadB({ ...payloadB, location_type: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '6px',
                      background: 'var(--bg-dark)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-bright)',
                      fontSize: '0.8rem'
                    }}
                  >
                    <option value="residential">Residential</option>
                    <option value="commercial">Commercial</option>
                    <option value="street_outdoor">Street / Outdoor</option>
                    <option value="vehicle">Vehicle</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Incident Time
                  </label>
                  <input
                    type="time"
                    value={payloadB.incident_time || '02:15'}
                    onChange={(e) => setPayloadB({ ...payloadB, incident_time: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '6px',
                      background: 'var(--bg-dark)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-bright)',
                      fontSize: '0.8rem'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Weapon
                  </label>
                  <select
                    value={payloadB.has_weapon ? 'yes' : 'no'}
                    onChange={(e) => setPayloadB({ ...payloadB, has_weapon: e.target.value === 'yes', weapon_count: e.target.value === 'yes' ? 1 : 0 })}
                    style={{
                      width: '100%',
                      padding: '6px 8px',
                      borderRadius: '6px',
                      background: 'var(--bg-dark)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-bright)',
                      fontSize: '0.8rem'
                    }}
                  >
                    <option value="no">None (Unarmed)</option>
                    <option value="yes">Weapon Present</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Button */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '28px' }}>
        <button
          onClick={handleCompare}
          disabled={loading}
          style={{
            padding: '12px 28px',
            borderRadius: '10px',
            border: 'none',
            background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
            color: '#fff',
            fontSize: '0.95rem',
            fontWeight: 700,
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            boxShadow: '0 4px 14px rgba(2, 132, 199, 0.35)',
            transition: 'transform 0.15s ease'
          }}
        >
          <ArrowLeftRight size={18} />
          {loading ? 'Comparing Behavioral DNA...' : 'Execute DNA Comparison'}
        </button>
      </div>

      {error && (
        <div style={{ marginBottom: '24px' }}>
          <ErrorState error={error} onRetry={handleCompare} />
        </div>
      )}

      {/* Comparison Results Presentation */}
      {comparisonResult && !loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Similarity Score Card */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '12px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Behavioral DNA Similarity
                </span>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginTop: '4px' }}>
                  <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#38bdf8' }}>
                    {comparisonResult.dna_similarity.similarity_score_pct.toFixed(1)}%
                  </div>
                  <div
                    style={{
                      padding: '4px 12px',
                      borderRadius: '16px',
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      background: 'rgba(56, 189, 248, 0.15)',
                      color: '#38bdf8',
                      border: '1px solid rgba(56, 189, 248, 0.3)'
                    }}
                  >
                    {comparisonResult.dna_similarity.match_tier}
                  </div>
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {comparisonResult.dna_similarity.affinity_summary} • Behavioral similarity distance: {comparisonResult.dna_similarity.cosine_distance.toFixed(4)}
                </div>
              </div>

              <div
                style={{
                  display: 'flex',
                  gap: '12px',
                  alignItems: 'center',
                  background: 'var(--bg-dark)',
                  padding: '12px 18px',
                  borderRadius: '10px',
                  border: '1px solid var(--border-subtle)'
                }}
              >
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#10b981' }}>
                    {comparisonResult.what_changed.match_count}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>MATCHED</div>
                </div>
                <div style={{ width: '1px', height: '24px', background: 'var(--border-subtle)' }} />
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f59e0b' }}>
                    {comparisonResult.what_changed.differ_count}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>DIVERGED</div>
                </div>
              </div>
            </div>
          </div>

          {/* 🧬 DNA COMPARISON Table */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '12px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <span style={{ fontSize: '1.2rem' }}>🧬</span>
              <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                DNA COMPARISON
              </h3>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px 14px', fontWeight: 600 }}>Feature</th>
                    <th style={{ padding: '12px 14px', fontWeight: 600 }}>{comparisonResult.incident_a.label}</th>
                    <th style={{ padding: '12px 14px', fontWeight: 600 }}>{comparisonResult.incident_b.label}</th>
                    <th style={{ padding: '12px 14px', fontWeight: 600, textAlign: 'center' }}>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonResult.dna_comparison_table.map((row, idx) => {
                    const isMatch = row.result === '✓';
                    return (
                      <tr
                        key={idx}
                        style={{
                          borderBottom: '1px solid var(--border-subtle)',
                          background: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.01)'
                        }}
                      >
                        <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--text-bright)' }}>
                          {row.feature}
                        </td>
                        <td style={{ padding: '12px 14px', color: 'var(--text-muted)' }}>
                          {row.incident_a}
                        </td>
                        <td style={{ padding: '12px 14px', color: 'var(--text-muted)' }}>
                          {row.incident_b}
                        </td>
                        <td style={{ padding: '12px 14px', textAlign: 'center' }}>
                          <span
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              width: '26px',
                              height: '26px',
                              borderRadius: '50%',
                              fontWeight: 800,
                              fontSize: '0.9rem',
                              background: isMatch ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                              color: isMatch ? '#10b981' : '#f59e0b',
                              border: isMatch ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(245, 158, 11, 0.3)'
                            }}
                          >
                            {row.result}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Prominent "What Changed?" Section */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(2, 132, 199, 0.08) 0%, rgba(15, 23, 42, 0.3) 100%)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              borderRadius: '12px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <TrendingUp size={22} style={{ color: '#38bdf8' }} />
              <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#38bdf8' }}>
                WHAT CHANGED?
              </h3>
            </div>

            {/* Non-Technical Summary Counters */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center', marginBottom: '18px' }}>
              <div
                style={{
                  padding: '8px 14px',
                  borderRadius: '8px',
                  background: 'rgba(16, 185, 129, 0.12)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  color: '#10b981',
                  fontWeight: 700,
                  fontSize: '0.9rem'
                }}
              >
                {comparisonResult.what_changed.summary_match_line || `${comparisonResult.what_changed.match_count} behavioral characteristics match.`}
              </div>
              <div
                style={{
                  padding: '8px 14px',
                  borderRadius: '8px',
                  background: 'rgba(245, 158, 11, 0.12)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  color: '#f59e0b',
                  fontWeight: 700,
                  fontSize: '0.9rem'
                }}
              >
                {comparisonResult.what_changed.summary_differ_line || `${comparisonResult.what_changed.differ_count} behavioral characteristics differ.`}
              </div>
              <div
                style={{
                  padding: '8px 14px',
                  borderRadius: '8px',
                  background: comparisonResult.what_changed.same_crime_category ? 'rgba(56, 189, 248, 0.12)' : 'rgba(168, 85, 247, 0.12)',
                  border: comparisonResult.what_changed.same_crime_category ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid rgba(168, 85, 247, 0.3)',
                  color: comparisonResult.what_changed.same_crime_category ? '#38bdf8' : '#c084fc',
                  fontWeight: 600,
                  fontSize: '0.85rem'
                }}
              >
                {comparisonResult.what_changed.crime_category_status}
              </div>
            </div>

            {/* Non-Technical MATCH vs DIFFER Comparison Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '20px' }}>
              {/* MATCH Column */}
              <div style={{ background: 'var(--bg-dark)', borderRadius: '10px', padding: '16px', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#10b981', letterSpacing: '0.5px', marginBottom: '10px' }}>
                  MATCH:
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {comparisonResult.what_changed.match_items && comparisonResult.what_changed.match_items.length > 0 ? (
                    comparisonResult.what_changed.match_items.map((item, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.88rem', color: 'var(--text-bright)' }}>
                        <span style={{ color: '#10b981', fontWeight: 800, fontSize: '1rem' }}>✓</span>
                        <span>{item}</span>
                      </div>
                    ))
                  ) : (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>None</div>
                  )}
                </div>
              </div>

              {/* DIFFER Column */}
              <div style={{ background: 'var(--bg-dark)', borderRadius: '10px', padding: '16px', border: '1px solid rgba(245, 158, 11, 0.25)' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#f59e0b', letterSpacing: '0.5px', marginBottom: '10px' }}>
                  DIFFER:
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {comparisonResult.what_changed.differ_items && comparisonResult.what_changed.differ_items.length > 0 ? (
                    comparisonResult.what_changed.differ_items.map((item, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.88rem', color: 'var(--text-bright)' }}>
                        <span style={{ color: '#f59e0b', fontWeight: 800, fontSize: '1rem' }}>△</span>
                        <span>{item}</span>
                      </div>
                    ))
                  ) : (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>None (identical behavioral execution)</div>
                  )}
                </div>
              </div>

              {/* UNKNOWN Column (Part I) */}
              <div style={{ background: 'var(--bg-dark)', borderRadius: '10px', padding: '16px', border: '1px solid rgba(148, 163, 184, 0.25)' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#94a3b8', letterSpacing: '0.5px', marginBottom: '10px' }}>
                  UNKNOWN / UNSPECIFIED:
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {comparisonResult.what_changed.unknown_items && comparisonResult.what_changed.unknown_items.length > 0 ? (
                    comparisonResult.what_changed.unknown_items.map((item, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                        <span style={{ color: '#94a3b8', fontWeight: 800, fontSize: '1rem' }}>?</span>
                        <span>{item}</span>
                      </div>
                    ))
                  ) : (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>None (all compared dimensions recorded)</div>
                  )}
                </div>
                <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--accent-amber)', fontStyle: 'italic' }}>
                  Rule: Unknown fields are strictly excluded and never counted as matches.
                </div>
              </div>
            </div>

            {/* Crime Category Relationship Context */}
            {comparisonResult.what_changed.crime_category_detail && (
              <div
                style={{
                  padding: '12px 16px',
                  borderRadius: '8px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  marginBottom: '18px',
                  fontSize: '0.85rem'
                }}
              >
                <strong style={{ color: 'var(--text-bright)', marginRight: '6px' }}>Crime Category Context:</strong>
                <span style={{ color: 'var(--text-muted)' }}>{comparisonResult.what_changed.crime_category_detail}</span>
              </div>
            )}

            {/* Strongest Similarities & Most Meaningful Differences */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '18px' }}>
              <div style={{ background: 'var(--bg-dark)', borderRadius: '8px', padding: '14px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#10b981', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px' }}>
                  Strongest Similarities (Why DNA Matched)
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {comparisonResult.what_changed.strongest_similarities?.map((sim, i) => (
                    <div key={i} style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
                      <span style={{ color: '#10b981', marginTop: '1px' }}>&bull;</span>
                      <span>{sim}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ background: 'var(--bg-dark)', borderRadius: '8px', padding: '14px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.5px' }}>
                  Most Meaningful Differences (Why DNA Diverged)
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {comparisonResult.what_changed.most_meaningful_differences?.map((diff, i) => (
                    <div key={i} style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
                      <span style={{ color: '#f59e0b', marginTop: '1px' }}>&bull;</span>
                      <span>{diff}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-bright)', marginBottom: '8px' }}>
              {comparisonResult.what_changed.headline}
            </div>

            <p style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
              {comparisonResult.what_changed.narrative}
            </p>

            {comparisonResult.what_changed.escalations.length > 0 && (
              <div style={{ marginBottom: '14px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ef4444', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
                  Identified Tactical Escalations
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {comparisonResult.what_changed.escalations.map((esc, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '8px 12px',
                        borderRadius: '6px',
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.25)',
                        fontSize: '0.82rem',
                        color: 'var(--text-bright)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                    >
                      <AlertTriangle size={15} style={{ color: '#ef4444', flexShrink: 0 }} />
                      <span>{esc}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {comparisonResult.what_changed.transitions.length > 0 && (
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
                  Operational Behavioral Transitions
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {comparisonResult.what_changed.transitions.map((trans, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '8px 12px',
                        borderRadius: '6px',
                        background: 'var(--bg-dark)',
                        border: '1px solid var(--border-subtle)',
                        fontSize: '0.82rem',
                        color: 'var(--text-muted)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                    >
                      <ChevronRight size={14} style={{ color: '#38bdf8', flexShrink: 0 }} />
                      <span>{trans}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Matching vs Differing Characteristics Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              gap: '20px'
            }}
          >
            {/* MATCHING CHARACTERISTICS */}
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '20px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <CheckCircle2 size={18} style={{ color: '#10b981' }} />
                <h4 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 700, color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Matching Characteristics ({comparisonResult.matching_characteristics.length})
                </h4>
              </div>

              {comparisonResult.matching_characteristics.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {comparisonResult.matching_characteristics.map((m, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '10px 12px',
                        borderRadius: '6px',
                        background: 'var(--bg-dark)',
                        border: '1px solid var(--border-subtle)',
                        fontSize: '0.82rem',
                        color: 'var(--text-bright)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                    >
                      <span style={{ color: '#10b981', fontWeight: 700 }}>✓</span>
                      <span>{m}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  No exact behavioral matches identified.
                </div>
              )}
            </div>

            {/* DIFFERING CHARACTERISTICS */}
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '20px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <AlertTriangle size={18} style={{ color: '#f59e0b' }} />
                <h4 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Differing Characteristics ({comparisonResult.differing_characteristics.length})
                </h4>
              </div>

              {comparisonResult.differing_characteristics.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {comparisonResult.differing_characteristics.map((d, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '10px 12px',
                        borderRadius: '6px',
                        background: 'var(--bg-dark)',
                        border: '1px solid var(--border-subtle)',
                        fontSize: '0.82rem',
                        color: 'var(--text-bright)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                    >
                      <span style={{ color: '#f59e0b', fontWeight: 700 }}>△</span>
                      <span>{d}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  No significant behavioral divergences observed.
                </div>
              )}
            </div>
          </div>

          {/* Subprofile Energy Overlay Breakdown */}
          {comparisonResult.subprofile_comparison && comparisonResult.subprofile_comparison.length > 0 && (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '20px'
              }}
            >
              <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '14px' }}>
                Behavioral Domain Energy Overlay (7 Subprofiles)
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '10px' }}>
                {comparisonResult.subprofile_comparison.map((sp, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '10px 12px',
                      borderRadius: '8px',
                      background: 'var(--bg-dark)',
                      border: '1px solid var(--border-subtle)',
                      fontSize: '0.78rem'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 600, color: 'var(--text-bright)' }}>{sp.group_name}</span>
                      <span style={{ color: sp.alignment === 'Aligned' ? '#10b981' : '#38bdf8', fontWeight: 600 }}>{sp.alignment}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.72rem' }}>
                      <span>A: {sp.energy_a.toFixed(3)}</span>
                      <span>B: {sp.energy_b.toFixed(3)}</span>
                      <span>Δ: {sp.delta > 0 ? `+${sp.delta.toFixed(3)}` : sp.delta.toFixed(3)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Ethical Advisory Shield Banner */}
          <div
            style={{
              padding: '14px 18px',
              borderRadius: '10px',
              background: 'rgba(245, 158, 11, 0.08)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px'
            }}
          >
            <ShieldCheck size={20} style={{ color: '#f59e0b', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#f59e0b', marginBottom: '2px' }}>
                ETHICAL ATTRIBUTION BOUNDARY
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.45' }}>
                {comparisonResult.ethical_advisory}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
