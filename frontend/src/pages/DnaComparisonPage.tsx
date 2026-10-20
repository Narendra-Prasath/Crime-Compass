import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import {
  DnaComparisonResponse,
  ComparisonPreset
} from '../types';
import { LoadingState, ErrorState } from '../components/StateViews';
import {
  ArrowLeftRight,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  TrendingUp,
  Info,
  ChevronDown,
  ChevronUp,
  Code2,
  Compass
} from 'lucide-react';

interface DnaComparisonPageProps {
  onNavigate?: (page: string, params?: Record<string, any>) => void;
}

export function DnaComparisonPage({ onNavigate: _onNavigate }: DnaComparisonPageProps = {}) {
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

  // Expandable sections
  const [showHowCalculated, setShowHowCalculated] = useState<boolean>(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);

  const applyPreset = useCallback((preset: ComparisonPreset) => {
    setSelectedPresetId(preset.id);
    if (preset.incident_a.incident_id) {
      setModeA('historical');
      setHistIdA(preset.incident_a.incident_id);
    } else {
      setModeA('custom');
      setPayloadA(preset.incident_a.input_data || {});
    }

    if (preset.incident_b.incident_id) {
      setModeB('historical');
      setHistIdB(preset.incident_b.incident_id);
    } else {
      setModeB('custom');
      setPayloadB(preset.incident_b.input_data || {});
    }
  }, []);

  const handleCompare = useCallback(async () => {
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
  }, [modeA, modeB, histIdA, histIdB, payloadA, payloadB]);

  // Load presets on mount
  useEffect(() => {
    let active = true;
    api.getComparisonPresets()
      .then((data) => {
        if (!active) return;
        if (data.presets && data.presets.length > 0) {
          setPresets(data.presets);
          applyPreset(data.presets[0]);
        }
      })
      .catch((err) => {
        console.warn('Failed to load comparison presets', err);
      });
    return () => {
      active = false;
    };
  }, [applyPreset]);

  // Run initial comparison on mount
  useEffect(() => {
    let active = true;
    const fetchInitial = async () => {
      setLoading(true);
      setError(null);
      const specA = modeA === 'historical'
        ? { incident_id: histIdA.trim() }
        : { input_data: payloadA, label: payloadA.scenario_title || 'Incident A' };
      const specB = modeB === 'historical'
        ? { incident_id: histIdB.trim() }
        : { input_data: payloadB, label: payloadB.scenario_title || 'Incident B' };

      try {
        const res = await api.compareIncidents({ incident_a: specA, incident_b: specB });
        if (active) setComparisonResult(res);
      } catch (err: any) {
        if (active) setError(err?.detail || err?.message || 'Comparison failed. Please verify input values.');
      } finally {
        if (active) setLoading(false);
      }
    };

    fetchInitial();
    return () => {
      active = false;
    };
  }, [selectedPresetId, modeA, modeB, histIdA, histIdB, payloadA, payloadB]);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '28px 18px', color: 'var(--text-main)' }}>
      {/* =========================================================================
          TOP: BEHAVIORAL COMPARISON HEADER & SELECTORS
          ========================================================================= */}
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <div
            style={{
              padding: '10px',
              borderRadius: '10px',
              background: 'rgba(56, 189, 248, 0.15)',
              color: '#38bdf8'
            }}
          >
            <Compass size={24} />
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-bright)', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>BEHAVIORAL COMPARISON</span>
              <span role="img" aria-label="compass">🧭</span>
            </h1>
            <p style={{ margin: '4px 0 0', fontSize: '0.92rem', color: 'var(--text-muted)' }}>
              Compare two incidents to understand what they have in common, what differs, and which information is unavailable.
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
            padding: '14px 18px',
            marginBottom: '22px'
          }}
        >
          <div style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
            Quick Comparison Presets
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {presets.map((p) => {
              const isActive = selectedPresetId === p.id;
              return (
                <button
                  key={p.id}
                  onClick={() => applyPreset(p)}
                  style={{
                    padding: '7px 14px',
                    borderRadius: '8px',
                    border: isActive ? '1px solid #38bdf8' : '1px solid var(--border-subtle)',
                    background: isActive ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-dark)',
                    color: isActive ? '#38bdf8' : 'var(--text-bright)',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {p.title}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Comparison Setup Grid: Incident A & Incident B */}
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
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.1rem' }}>🅰️</span>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                Incident A: {payloadA.scenario_title || histIdA}
              </h3>
            </div>
            {/* Mode Toggle */}
            <div style={{ display: 'flex', background: 'var(--bg-dark)', padding: '2px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              <button
                type="button"
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
                type="button"
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
                    Weapon Context
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

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Property Involved
                  </label>
                  <select
                    value={payloadA.has_property ? 'yes' : 'no'}
                    onChange={(e) => setPayloadA({ ...payloadA, has_property: e.target.value === 'yes' })}
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
                    <option value="yes">Yes (Property Target)</option>
                    <option value="no">No Property</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Physical Injury
                  </label>
                  <select
                    value={payloadA.has_injury ? 'yes' : 'no'}
                    onChange={(e) => setPayloadA({ ...payloadA, has_injury: e.target.value === 'yes' })}
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
                    <option value="no">No Injury Reported</option>
                    <option value="yes">Physical Harm Reported</option>
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
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.1rem' }}>🅱️</span>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                Incident B: {payloadB.scenario_title || histIdB}
              </h3>
            </div>
            {/* Mode Toggle */}
            <div style={{ display: 'flex', background: 'var(--bg-dark)', padding: '2px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              <button
                type="button"
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
                type="button"
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
                    Weapon Context
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

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Property Involved
                  </label>
                  <select
                    value={payloadB.has_property ? 'yes' : 'no'}
                    onChange={(e) => setPayloadB({ ...payloadB, has_property: e.target.value === 'yes' })}
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
                    <option value="yes">Yes (Property Target)</option>
                    <option value="no">No Property</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Physical Injury
                  </label>
                  <select
                    value={payloadB.has_injury ? 'yes' : 'no'}
                    onChange={(e) => setPayloadB({ ...payloadB, has_injury: e.target.value === 'yes' })}
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
                    <option value="no">No Injury Reported</option>
                    <option value="yes">Physical Harm Reported</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* [Compare Incidents] Action Button */}
      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '32px' }}>
        <button
          type="button"
          onClick={handleCompare}
          disabled={loading}
          style={{
            padding: '12px 36px',
            borderRadius: '10px',
            border: 'none',
            background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
            color: '#fff',
            fontSize: '1rem',
            fontWeight: 700,
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            boxShadow: '0 4px 16px rgba(2, 132, 199, 0.35)',
            transition: 'transform 0.15s ease'
          }}
        >
          <ArrowLeftRight size={18} />
          {loading ? 'Comparing Incidents...' : 'Compare Incidents'}
        </button>
      </div>

      {error && (
        <div style={{ marginBottom: '24px' }}>
          <ErrorState error={error} onRetry={handleCompare} />
        </div>
      )}

      {loading && !comparisonResult && (
        <div style={{ padding: '40px 0' }}>
          <LoadingState message="Computing Behavioral DNA hypersphere projection and pairwise alignment..." />
        </div>
      )}

      {/* =========================================================================
          AFTER ANALYSIS: SECTIONS 1 TO 8 IN EXACT SPECIFIED ORDER
          ========================================================================= */}
      {comparisonResult && !loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>

          {/* =====================================================================
              SECTION 1: SIMPLE SUMMARY
              ===================================================================== */}
          <section
            id="section-simple-summary"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '14px',
              padding: '24px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)'
            }}
          >
            <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '8px' }}>
              SECTION 1: SIMPLE SUMMARY
            </div>

            {/* Plain-Language Lead-in Headline */}
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-bright)', marginBottom: '16px', lineHeight: 1.4 }}>
              {comparisonResult.what_changed.match_count === 7
                ? 'These incidents exhibit identical recorded characteristics across compared dimensions.'
                : 'These incidents share some characteristics, but they are not identical.'}
            </div>

            {/* Score & Counters Grid */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '16px',
                marginBottom: '18px'
              }}
            >
              {/* Behavioral Similarity Metric */}
              <div
                style={{
                  background: 'var(--bg-dark)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center'
                }}
              >
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Behavioral Similarity
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '6px' }}>
                  <span style={{ fontSize: '2.4rem', fontWeight: 900, color: '#38bdf8', lineHeight: 1 }}>
                    {comparisonResult.dna_similarity.similarity_score_pct.toFixed(1)}%
                  </span>
                </div>
                <div style={{ marginTop: '8px' }}>
                  <span
                    style={{
                      display: 'inline-block',
                      padding: '3px 8px',
                      borderRadius: '12px',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      background: 'rgba(56, 189, 248, 0.15)',
                      color: '#38bdf8',
                      border: '1px solid rgba(56, 189, 248, 0.3)'
                    }}
                  >
                    {comparisonResult.dna_similarity.match_tier}
                  </span>
                </div>
              </div>

              {/* Matched Counter */}
              <div
                style={{
                  background: 'var(--bg-dark)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '10px',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center'
                }}
              >
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Matched Characteristics
                </div>
                <div style={{ fontSize: '2.4rem', fontWeight: 900, color: '#10b981', marginTop: '6px', lineHeight: 1 }}>
                  {comparisonResult.what_changed.match_count}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                  Shared recorded features
                </div>
              </div>

              {/* Differing Counter */}
              <div
                style={{
                  background: 'var(--bg-dark)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: '10px',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center'
                }}
              >
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Differing Characteristics
                </div>
                <div style={{ fontSize: '2.4rem', fontWeight: 900, color: '#f59e0b', marginTop: '6px', lineHeight: 1 }}>
                  {comparisonResult.what_changed.differ_count}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                  Distinct operational features
                </div>
              </div>

              {/* Unknown / Unavailable Counter */}
              <div
                style={{
                  background: 'var(--bg-dark)',
                  border: '1px solid rgba(148, 163, 184, 0.25)',
                  borderRadius: '10px',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center'
                }}
              >
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Unknown / Unavailable
                </div>
                <div style={{ fontSize: '2.4rem', fontWeight: 900, color: '#94a3b8', marginTop: '6px', lineHeight: 1 }}>
                  {comparisonResult.what_changed.unknown_count ?? 0}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                  Excluded from matching
                </div>
              </div>
            </div>

            {/* Threshold & Non-Proof Disclaimer Callout */}
            <div
              style={{
                background: 'rgba(56, 189, 248, 0.05)',
                border: '1px solid rgba(56, 189, 248, 0.2)',
                borderRadius: '8px',
                padding: '12px 16px',
                fontSize: '0.82rem',
                color: 'var(--text-muted)',
                lineHeight: 1.5
              }}
            >
              <div style={{ fontWeight: 700, color: '#38bdf8', marginBottom: '4px' }}>
                Interpretation Basis & Product-Defined Thresholds:
              </div>
              <p style={{ margin: '0 0 6px 0' }}>
                Similarity is a measure of feature alignment, not proof that the same person committed both incidents.
                Labels are product-defined interpretations: <strong>High Affinity</strong> (≥90.0%), <strong>Moderate Affinity</strong> (75.0%–89.9%), <strong>Partial Overlap</strong> (50.0%–74.9%), and <strong>Divergent</strong> (&lt;50.0%).
              </p>
              <div style={{ fontSize: '0.76rem', color: 'var(--text-dim)' }}>
                {comparisonResult.what_changed.narrative}
              </div>
            </div>
          </section>

          {/* =====================================================================
              SECTION 2: WHAT MATCHES?
              ===================================================================== */}
          <section
            id="section-what-matches"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '14px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <CheckCircle2 size={20} style={{ color: '#10b981' }} />
              <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#10b981' }}>
                SECTION 2: WHAT MATCHES?
              </h2>
            </div>
            <p style={{ margin: '0 0 16px 0', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
              A simple list of shared characteristics verified directly from underlying records.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(comparisonResult.what_changed.matched_statements && comparisonResult.what_changed.matched_statements.length > 0)
                ? comparisonResult.what_changed.matched_statements.map((stmt, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '12px 16px',
                        borderRadius: '8px',
                        background: 'var(--bg-dark)',
                        border: '1px solid rgba(16, 185, 129, 0.25)',
                        fontSize: '0.88rem',
                        color: 'var(--text-bright)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px'
                      }}
                    >
                      <span style={{ color: '#10b981', fontWeight: 800, fontSize: '1.1rem' }}>✓</span>
                      <span>{stmt}</span>
                    </div>
                  ))
                : (comparisonResult.what_changed.match_items && comparisonResult.what_changed.match_items.length > 0)
                ? comparisonResult.what_changed.match_items.map((item, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '12px 16px',
                        borderRadius: '8px',
                        background: 'var(--bg-dark)',
                        border: '1px solid rgba(16, 185, 129, 0.25)',
                        fontSize: '0.88rem',
                        color: 'var(--text-bright)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px'
                      }}
                    >
                      <span style={{ color: '#10b981', fontWeight: 800, fontSize: '1.1rem' }}>✓</span>
                      <span>{item}</span>
                    </div>
                  ))
                : (
                    <div style={{ padding: '14px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      No identical behavioral characteristics identified across compared fields.
                    </div>
                  )}
            </div>
          </section>

          {/* =====================================================================
              SECTION 3: WHAT IS DIFFERENT?
              ===================================================================== */}
          <section
            id="section-what-is-different"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '14px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <AlertTriangle size={20} style={{ color: '#f59e0b' }} />
              <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#f59e0b' }}>
                SECTION 3: WHAT IS DIFFERENT?
              </h2>
            </div>
            <p style={{ margin: '0 0 16px 0', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
              A neutral, factual explanation of differences observed between Incident A and Incident B.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(comparisonResult.what_changed.differing_statements && comparisonResult.what_changed.differing_statements.length > 0)
                ? comparisonResult.what_changed.differing_statements.map((stmt, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '12px 16px',
                        borderRadius: '8px',
                        background: 'var(--bg-dark)',
                        border: '1px solid rgba(245, 158, 11, 0.25)',
                        fontSize: '0.88rem',
                        color: 'var(--text-bright)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px'
                      }}
                    >
                      <span style={{ color: '#f59e0b', fontWeight: 800, fontSize: '1rem' }}>△</span>
                      <span>{stmt}</span>
                    </div>
                  ))
                : (comparisonResult.what_changed.differ_items && comparisonResult.what_changed.differ_items.length > 0)
                ? comparisonResult.what_changed.differ_items.map((item, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '12px 16px',
                        borderRadius: '8px',
                        background: 'var(--bg-dark)',
                        border: '1px solid rgba(245, 158, 11, 0.25)',
                        fontSize: '0.88rem',
                        color: 'var(--text-bright)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px'
                      }}
                    >
                      <span style={{ color: '#f59e0b', fontWeight: 800, fontSize: '1rem' }}>△</span>
                      <span>{item}</span>
                    </div>
                  ))
                : (
                    <div style={{ padding: '14px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      Zero behavioral divergences detected across compared dimensions.
                    </div>
                  )}
            </div>
          </section>

          {/* =====================================================================
              SECTION 4: WHAT IS UNKNOWN?
              ===================================================================== */}
          <section
            id="section-what-is-unknown"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '14px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <HelpCircle size={20} style={{ color: '#94a3b8' }} />
              <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#94a3b8' }}>
                SECTION 4: WHAT IS UNKNOWN?
              </h2>
            </div>
            <p style={{ margin: '0 0 16px 0', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
              Fields that cannot be compared because the information is missing, unobserved, or not applicable.
            </p>

            {/* Explicit Distinction Guide */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                gap: '10px',
                marginBottom: '16px'
              }}
            >
              <div style={{ background: 'var(--bg-dark)', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>Missing or Unknown</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Field unrecorded in primary report. Never counts as a match.
                </div>
              </div>
              <div style={{ background: 'var(--bg-dark)', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#c084fc', textTransform: 'uppercase' }}>Not Applicable</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Sub-field does not apply (e.g. weapon details for unarmed incident).
                </div>
              </div>
              <div style={{ background: 'var(--bg-dark)', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#10b981', textTransform: 'uppercase' }}>Recorded & Equal</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Explicitly verified match across both records (✓).
                </div>
              </div>
              <div style={{ background: 'var(--bg-dark)', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase' }}>Recorded & Different</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Explicitly verified divergence across both records (△).
                </div>
              </div>
            </div>

            {/* List of Unknown Statements */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(comparisonResult.what_changed.unknown_statements && comparisonResult.what_changed.unknown_statements.length > 0)
                ? comparisonResult.what_changed.unknown_statements.map((stmt, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '12px 16px',
                        borderRadius: '8px',
                        background: 'var(--bg-dark)',
                        border: '1px solid rgba(148, 163, 184, 0.25)',
                        fontSize: '0.88rem',
                        color: 'var(--text-muted)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px'
                      }}
                    >
                      <span style={{ color: '#94a3b8', fontWeight: 800, fontSize: '1.1rem' }}>?</span>
                      <span>{stmt}</span>
                    </div>
                  ))
                : (
                    <div style={{ padding: '14px', borderRadius: '8px', background: 'var(--bg-dark)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      All compared behavioral dimensions were recorded in both incidents. No unknown fields.
                    </div>
                  )}
            </div>

            <div style={{ marginTop: '12px', fontSize: '0.78rem', color: '#f59e0b', fontStyle: 'italic' }}>
              Rule: Unknown values must never automatically count as matches. Missing or unavailable fields are excluded from behavioral alignment.
            </div>
          </section>

          {/* =====================================================================
              SECTION 5: WHY ARE THEY SIMILAR?
              ===================================================================== */}
          <section
            id="section-why-are-they-similar"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '14px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <Sparkles size={20} style={{ color: '#10b981' }} />
              <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-bright)' }}>
                SECTION 5: WHY ARE THEY SIMILAR?
              </h2>
            </div>
            <p style={{ margin: '0 0 16px 0', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
              Most influential shared feature groups based on actual comparison logic and coordinate dot-product attribution.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
              {comparisonResult.what_changed.strongest_similarities?.map((sim, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '12px 16px',
                    borderRadius: '8px',
                    background: 'var(--bg-dark)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '0.86rem',
                    color: 'var(--text-bright)',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px'
                  }}
                >
                  <span style={{ color: '#10b981', fontWeight: 800 }}>•</span>
                  <span>{sim}</span>
                </div>
              ))}
            </div>

            {/* Top Contributing Domains (from audited dot product decomposition) */}
            {comparisonResult.subprofile_comparison && (
              <div style={{ background: 'var(--bg-dark)', borderRadius: '10px', padding: '16px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>
                  Demonstrated Mathematical Contribution to Similarity Score
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px' }}>
                  {comparisonResult.subprofile_comparison
                    .filter((sp) => (sp.domain_contribution_pct ?? 0) > 0)
                    .sort((a, b) => (b.domain_contribution_pct ?? 0) - (a.domain_contribution_pct ?? 0))
                    .slice(0, 4)
                    .map((sp, idx) => (
                      <div key={idx} style={{ padding: '8px 12px', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-bright)' }}>{sp.group_name}</span>
                          <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#10b981' }}>
                            +{sp.domain_contribution_pct}% share
                          </span>
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                          {sp.alignment} (A: {(sp.score_a_pct ?? (sp.energy_a * 100)).toFixed(1)}%, B: {(sp.score_b_pct ?? (sp.energy_b * 100)).toFixed(1)}%)
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </section>

          {/* =====================================================================
              SECTION 6: WHY ARE THEY DIFFERENT?
              ===================================================================== */}
          <section
            id="section-why-are-they-different"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '14px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <TrendingUp size={20} style={{ color: '#f59e0b' }} />
              <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-bright)' }}>
                SECTION 6: WHY ARE THEY DIFFERENT?
              </h2>
            </div>
            <p style={{ margin: '0 0 16px 0', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
              Most meaningful observed differences and their relationship to behavioral modus operandi.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '14px' }}>
              {comparisonResult.what_changed.most_meaningful_differences?.map((diff, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '12px 16px',
                    borderRadius: '8px',
                    background: 'var(--bg-dark)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '0.86rem',
                    color: 'var(--text-bright)',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px'
                  }}
                >
                  <span style={{ color: '#f59e0b', fontWeight: 800 }}>•</span>
                  <span>{diff}</span>
                </div>
              ))}
            </div>

            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
              Note: The comparison engine describes observed empirical differences in incident characteristics (such as timing, weapon context, or valuation) rather than claiming unverified causal or psychological progression.
            </div>
          </section>

          {/* =====================================================================
              SECTION 7: BEHAVIORAL DOMAIN ENERGIES
              ===================================================================== */}
          <section
            id="section-behavioral-domain-energies"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '14px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', flexWrap: 'wrap', gap: '10px' }}>
              <div>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>
                  SECTION 7: BEHAVIORAL DOMAIN ENERGIES
                </div>
                <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-bright)' }}>
                  Seven-Domain Behavioral Overlay & Activation Audit
                </h2>
              </div>

              {/* Tooltip Badge */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: 'rgba(56, 189, 248, 0.1)',
                  border: '1px solid rgba(56, 189, 248, 0.25)',
                  padding: '6px 12px',
                  borderRadius: '20px',
                  fontSize: '0.74rem',
                  color: '#38bdf8'
                }}
                title="Domain scores summarize selected features within a domain. They are not crime severity scores, offender identity scores, or probabilities of guilt."
              >
                <Info size={14} />
                <span>Feature activation metrics, not offender guilt or severity</span>
              </div>
            </div>

            <p style={{ margin: '0 0 16px 0', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
              Summary of all seven behavioral domains. Sign convention: <strong>Δ = Incident B minus Incident A</strong>. A positive delta means higher activation in B; a zero delta means equal scores.
            </p>

            {/* Compact Comparison Table */}
            <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.84rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px 14px', fontWeight: 700 }}>Domain</th>
                    <th style={{ padding: '12px 14px', fontWeight: 700, width: '110px' }}>Incident A</th>
                    <th style={{ padding: '12px 14px', fontWeight: 700, width: '110px' }}>Incident B</th>
                    <th style={{ padding: '12px 14px', fontWeight: 700, width: '170px' }}>Difference (Δ = B - A)</th>
                    <th style={{ padding: '12px 14px', fontWeight: 700, width: '130px' }}>Data Coverage</th>
                    <th style={{ padding: '12px 14px', fontWeight: 700 }}>Plain-English Interpretation</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonResult.subprofile_comparison.map((sp, idx) => {
                    const scoreA = sp.score_a_pct ?? (sp.energy_a * 100);
                    const scoreB = sp.score_b_pct ?? (sp.energy_b * 100);
                    const isZeroBoth = sp.energy_a === 0 && sp.energy_b === 0;

                    return (
                      <tr
                        key={idx}
                        style={{
                          borderBottom: '1px solid var(--border-subtle)',
                          background: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.01)'
                        }}
                      >
                        {/* Domain Column with Visual Bar */}
                        <td style={{ padding: '12px 14px' }}>
                          <div style={{ fontWeight: 700, color: 'var(--text-bright)' }}>{sp.group_name}</div>
                          {sp.description && (
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                              {sp.description}
                            </div>
                          )}
                          {/* Paired Mini Activation Bars */}
                          <div style={{ marginTop: '6px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                              <span style={{ width: '12px' }}>A:</span>
                              <div style={{ flex: 1, height: '4px', background: 'var(--bg-dark)', borderRadius: '2px', overflow: 'hidden' }}>
                                <div style={{ width: `${Math.min(100, Math.max(0, scoreA))}%`, height: '100%', background: '#38bdf8' }} />
                              </div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                              <span style={{ width: '12px' }}>B:</span>
                              <div style={{ flex: 1, height: '4px', background: 'var(--bg-dark)', borderRadius: '2px', overflow: 'hidden' }}>
                                <div style={{ width: `${Math.min(100, Math.max(0, scoreB))}%`, height: '100%', background: '#c084fc' }} />
                              </div>
                            </div>
                          </div>
                        </td>

                        {/* Incident A Score */}
                        <td style={{ padding: '12px 14px', fontFamily: 'monospace', fontWeight: 600, color: '#38bdf8' }}>
                          {isZeroBoth ? (
                            <span style={{ color: 'var(--text-dim)' }}>0.0% (0.000)</span>
                          ) : (
                            `${scoreA.toFixed(1)}% (${sp.energy_a.toFixed(3)})`
                          )}
                        </td>

                        {/* Incident B Score */}
                        <td style={{ padding: '12px 14px', fontFamily: 'monospace', fontWeight: 600, color: '#c084fc' }}>
                          {isZeroBoth ? (
                            <span style={{ color: 'var(--text-dim)' }}>0.0% (0.000)</span>
                          ) : (
                            `${scoreB.toFixed(1)}% (${sp.energy_b.toFixed(3)})`
                          )}
                        </td>

                        {/* Difference Column */}
                        <td style={{ padding: '12px 14px', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                          {sp.delta > 0.001 ? (
                            <span style={{ color: '#10b981', fontWeight: 700 }}>
                              {sp.delta_display || `+${(sp.delta * 100).toFixed(1)} pp (+${sp.delta.toFixed(3)})`}
                            </span>
                          ) : sp.delta < -0.001 ? (
                            <span style={{ color: '#f59e0b', fontWeight: 700 }}>
                              {sp.delta_display || `${(sp.delta * 100).toFixed(1)} pp (${sp.delta.toFixed(3)})`}
                            </span>
                          ) : (
                            <span style={{ color: 'var(--text-muted)' }}>
                              0.0 pp (0.000)
                            </span>
                          )}
                        </td>

                        {/* Data Coverage Column */}
                        <td style={{ padding: '12px 14px' }}>
                          <span
                            style={{
                              display: 'inline-block',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              fontSize: '0.72rem',
                              fontWeight: 700,
                              background: sp.data_coverage_status === 'Sufficient data'
                                ? 'rgba(16, 185, 129, 0.12)'
                                : sp.data_coverage_status === 'Insufficient data'
                                ? 'rgba(239, 68, 68, 0.12)'
                                : 'rgba(245, 158, 11, 0.12)',
                              color: sp.data_coverage_status === 'Sufficient data'
                                ? '#10b981'
                                : sp.data_coverage_status === 'Insufficient data'
                                ? '#ef4444'
                                : '#f59e0b',
                              border: '1px solid currentColor'
                            }}
                          >
                            {sp.data_coverage_status || 'Sufficient data'}
                          </span>
                          {(sp.data_coverage_a || sp.data_coverage_b) && (
                            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                              A: {sp.data_coverage_a} &bull; B: {sp.data_coverage_b}
                            </div>
                          )}
                        </td>

                        {/* Plain-English Interpretation */}
                        <td style={{ padding: '12px 14px', color: 'var(--text-bright)', fontSize: '0.82rem', lineHeight: 1.4 }}>
                          {sp.interpretation || (
                            sp.delta > 0
                              ? `Incident B exhibits higher ${sp.group_name.toLowerCase()} score.`
                              : sp.delta < 0
                              ? `Incident A exhibits higher ${sp.group_name.toLowerCase()} score.`
                              : `Both incidents exhibit equal ${sp.group_name.toLowerCase()} score.`
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Expandable "How is this calculated?" Section */}
            <div
              style={{
                background: 'var(--bg-dark)',
                borderRadius: '10px',
                border: '1px solid var(--border-subtle)',
                overflow: 'hidden'
              }}
            >
              <button
                type="button"
                onClick={() => setShowHowCalculated(!showHowCalculated)}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-bright)',
                  fontWeight: 700,
                  fontSize: '0.84rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <HelpCircle size={16} style={{ color: '#38bdf8' }} />
                  <span>How is Behavioral Domain Energy calculated? (Mathematical Audit & Rules)</span>
                </div>
                {showHowCalculated ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>

              {showHowCalculated && (
                <div style={{ padding: '0 16px 16px', fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.6, borderTop: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginTop: '12px' }}>
                    <div>
                      <strong style={{ color: 'var(--text-bright)' }}>1. Domain Energy Formula:</strong>
                      <p style={{ margin: '4px 0 8px 0', fontFamily: 'monospace', fontSize: '0.8rem', color: '#38bdf8' }}>
                        E_g = ||v_g||₂ = √(∑(i ∈ g) v_i²) over unit hypersphere S⁶⁹
                      </p>
                      <p style={{ margin: 0 }}>
                        The 70-dimensional feature vector is normalized to unit length (||v||₂ = 1.000). The domain energy is the Euclidean coordinate magnitude of the subvector corresponding to that domain. The sum of squared domain energies across all 7 domains equals exactly 1.000.
                      </p>
                    </div>

                    <div>
                      <strong style={{ color: 'var(--text-bright)' }}>2. Sign Convention & Meaning of Delta:</strong>
                      <p style={{ margin: '4px 0 8px 0', fontFamily: 'monospace', fontSize: '0.8rem', color: '#10b981' }}>
                        Delta = Score_B - Score_A
                      </p>
                      <p style={{ margin: 0 }}>
                        A positive delta indicates that Incident B has a higher coordinate activation in that domain. A negative delta indicates Incident A is higher. A zero delta indicates equal activation; it does not automatically mean all underlying fields are identical.
                      </p>
                    </div>

                    <div>
                      <strong style={{ color: 'var(--text-bright)' }}>3. Energy vs. Coverage vs. Similarity:</strong>
                      <ul style={{ margin: '4px 0 0', paddingLeft: '18px' }}>
                        <li><strong>Energy:</strong> Normalized feature activation coordinate magnitude [0.0, 1.0].</li>
                        <li><strong>Coverage:</strong> How many expected fields are filled in the police record (e.g. 4 of 4 fields).</li>
                        <li><strong>Similarity:</strong> Angular cosine alignment between subvectors u_g and v_g.</li>
                      </ul>
                    </div>

                    <div>
                      <strong style={{ color: 'var(--text-bright)' }}>4. Meaning of Zero (0.000):</strong>
                      <p style={{ margin: '4px 0 0 0' }}>
                        A score of 0.000 indicates an absence of recorded signal in that domain (for example, zero weapon involvement or no victim injury reported), not a system error or missing calculation.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* =====================================================================
              PRESERVED: 7-DIMENSION DNA COMPARISON TABLE (FEATURE BY FEATURE)
              ===================================================================== */}
          <section
            id="section-feature-comparison-table"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '14px',
              padding: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1.2rem' }}>🧬</span>
                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-bright)' }}>
                  DNA COMPARISON: OBSERVABLE FEATURE TABLE
                </h3>
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Comparing {comparisonResult.incident_a.label} vs {comparisonResult.incident_b.label}
              </span>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px 14px', fontWeight: 600 }}>Feature</th>
                    <th style={{ padding: '12px 14px', fontWeight: 600 }}>Incident A ({comparisonResult.incident_a.label})</th>
                    <th style={{ padding: '12px 14px', fontWeight: 600 }}>Incident B ({comparisonResult.incident_b.label})</th>
                    <th style={{ padding: '12px 14px', fontWeight: 600, textAlign: 'center' }}>Result</th>
                    <th style={{ padding: '12px 14px', fontWeight: 600 }}>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonResult.dna_comparison_table.map((row, idx) => {
                    const isMatch = row.result === '✓';
                    const isUnknown = row.result === '?';

                    return (
                      <tr
                        key={idx}
                        style={{
                          borderBottom: '1px solid var(--border-subtle)',
                          background: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.01)'
                        }}
                      >
                        <td style={{ padding: '12px 14px', fontWeight: 700, color: 'var(--text-bright)' }}>
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
                              background: isMatch
                                ? 'rgba(16, 185, 129, 0.15)'
                                : isUnknown
                                ? 'rgba(148, 163, 184, 0.15)'
                                : 'rgba(245, 158, 11, 0.15)',
                              color: isMatch ? '#10b981' : isUnknown ? '#94a3b8' : '#f59e0b',
                              border: isMatch
                                ? '1px solid rgba(16, 185, 129, 0.3)'
                                : isUnknown
                                ? '1px solid rgba(148, 163, 184, 0.3)'
                                : '1px solid rgba(245, 158, 11, 0.3)'
                            }}
                          >
                            {row.result}
                          </span>
                        </td>
                        <td style={{ padding: '12px 14px', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                          {row.details || row.match_status}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          {/* =====================================================================
              SECTION 8: TECHNICAL DETAILS (EXPANDABLE)
              ===================================================================== */}
          <section
            id="section-technical-details"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '14px',
              overflow: 'hidden'
            }}
          >
            <button
              type="button"
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              style={{
                width: '100%',
                padding: '18px 24px',
                background: 'transparent',
                border: 'none',
                color: 'var(--text-bright)',
                fontWeight: 800,
                fontSize: '1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Code2 size={20} style={{ color: '#38bdf8' }} />
                <span>SECTION 8: VIEW TECHNICAL DETAILS (Advanced Model Metrics & Vector Specs)</span>
              </div>
              {showTechnicalDetails ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>

            {showTechnicalDetails && (
              <div style={{ padding: '0 24px 24px', borderTop: '1px solid var(--border-subtle)' }}>
                <p style={{ margin: '14px 0 16px 0', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                  Underlying high-dimensional feature embeddings, distance metrics, and vector geometry for Incident A and Incident B.
                </p>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                    gap: '16px',
                    marginBottom: '20px'
                  }}
                >
                  <div style={{ background: 'var(--bg-dark)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                      Feature Embedding Space
                    </div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#38bdf8', marginTop: '4px' }}>
                      70-Dimensional Unit Hypersphere (S⁶⁹)
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                      Normalized using Euclidean L2 norm (||v||₂ = 1.0000). Eliminates count/frequency scale distortions.
                    </div>
                  </div>

                  <div style={{ background: 'var(--bg-dark)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                      Cosine Distance
                    </div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#f59e0b', marginTop: '4px' }}>
                      {comparisonResult.dna_similarity.cosine_distance.toFixed(4)}
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                      d(u, v) = 1.0 - cos(θ). Angular divergence on hypersphere surface.
                    </div>
                  </div>

                  <div style={{ background: 'var(--bg-dark)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                      Similarity Conversion Formula
                    </div>
                    <div style={{ fontSize: '1rem', fontWeight: 800, color: '#10b981', marginTop: '4px', fontFamily: 'monospace' }}>
                      Sim% = max(0, min(100, cos(θ) × 100))
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                      Linear projection of hypersphere dot product into [0.0%, 100.0%].
                    </div>
                  </div>
                </div>

                {/* Domain Attributions Table */}
                {comparisonResult.technical_details?.domain_attributions && (
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-bright)', marginBottom: '8px' }}>
                      Additive Dot Product Decomposition (u · v = ∑ u_g · v_g)
                    </div>
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
                        <thead>
                          <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                            <th style={{ padding: '8px', textAlign: 'left' }}>Domain</th>
                            <th style={{ padding: '8px', textAlign: 'right' }}>Dot Product (u_g · v_g)</th>
                            <th style={{ padding: '8px', textAlign: 'right' }}>Contribution to Similarity</th>
                          </tr>
                        </thead>
                        <tbody>
                          {comparisonResult.technical_details.domain_attributions.map((da, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                              <td style={{ padding: '8px', color: 'var(--text-bright)' }}>{da.domain}</td>
                              <td style={{ padding: '8px', textAlign: 'right', fontFamily: 'monospace' }}>{da.dot_product.toFixed(4)}</td>
                              <td style={{ padding: '8px', textAlign: 'right', fontFamily: 'monospace', color: '#10b981' }}>{da.contribution_pct.toFixed(1)}%</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>

          {/* =====================================================================
              ETHICAL ATTRIBUTION NOTICE
              ===================================================================== */}
          <div
            style={{
              padding: '16px 20px',
              borderRadius: '12px',
              background: 'rgba(245, 158, 11, 0.08)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '14px'
            }}
          >
            <ShieldCheck size={22} style={{ color: '#f59e0b', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.9rem', color: '#f59e0b', marginBottom: '4px' }}>
                ETHICAL ATTRIBUTION & SYSTEM BOUNDARIES
              </div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.55 }}>
                {comparisonResult.ethical_advisory ||
                  'Crime Compass analyzes recorded incident characteristics and historical behavioral patterns. Similarity and novelty scores describe patterns in the available data. They do not establish offender identity, guilt, causation, or investigative linkage. Connection maps represent incident categories, behavioral clusters, or environmental patterns, not identified persons.'}
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
