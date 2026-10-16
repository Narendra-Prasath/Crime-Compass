import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import type {
  IncidentInputPayload,
  ScenarioPreset,
  InputAnalysisResult
} from '../types';
import { FeedbackWidget } from '../components/FeedbackWidget';
import { CrimeDnaResultExperience } from '../components/CrimeDnaResultExperience';
import { DatasetAnalysisExperience } from '../components/DatasetAnalysisExperience';
import {
  Compass,
  Sparkles,
  ArrowRight,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Fingerprint,
  Layers,
  Network,
  HelpCircle,
  TrendingUp,
  Cpu,
  ChevronDown,
  ChevronUp,
  History,
  ShieldAlert,
  GitCompare,
  ExternalLink,
  Info,
  Clock,
  MapPin,
  Tag,
  DollarSign,
  AlertCircle,
  Globe2,
  UploadCloud,
  FileSpreadsheet
} from 'lucide-react';
import {
  INDIAN_STATES_AND_UTS,
  POPULAR_INDIAN_DISTRICTS,
  formatIndianNumber
} from '../utils/indiaFormat';

interface InputAnalysisPageProps {
  onNavigate: (page: string, params?: any) => void;
  initialAnalysisResult?: InputAnalysisResult | null;
  initialPayload?: any;
}

const DEFAULT_FORM_STATE: IncidentInputPayload = {
  scenario_title: 'Armed Commercial Robbery Case',
  incident_date: new Date().toISOString().split('T')[0],
  incident_time: '21:30',
  country: 'India',
  state_ut: 'Karnataka',
  district: 'Bengaluru Urban',
  city_town: 'Bengaluru',
  locality: 'Indiranagar',
  pin_code: '560038',
  currency: 'INR',
  timezone: 'Asia/Kolkata',
  crime_category: 'person_property',
  is_attempted: false,
  offense_count: 2,
  offense_categories_count: 2,
  population_setting: 'metropolitan_core',
  location_count: 1,
  has_weapon: true,
  weapon_count: 2,
  weapon_types_count: 1,
  has_criminal_activity: true,
  criminal_activity_count: 1,
  has_relationship: false,
  victim_count: 2,
  victim_avg_age: 34,
  victim_sexes_count: 2,
  victim_types_count: 1,
  offender_count: 2,
  offender_avg_age: 22,
  offender_sexes_count: 1,
  has_property: true,
  property_record_count: 1,
  has_stolen_property: true,
  stolen_count: 1,
  property_value: 350000,
  is_cargo_theft: false,
  has_injury: true,
  injury_record_count: 1,
  has_drug: false,
  suspected_drug_count: 0,
  estimated_drug_quantity: 0,
  has_bias_motivation: false,
  has_arrest: false,
  arrest_count: 0
};

export const InputAnalysisPage: React.FC<InputAnalysisPageProps> = ({
  onNavigate,
  initialAnalysisResult,
  initialPayload
}) => {
  // Analysis Mode Switcher: Mode 1 (Single Incident) vs Mode 2 (Analyze My Dataset)
  const [analysisMode, setAnalysisMode] = useState<'single' | 'dataset'>('single');

  const [formData, setFormData] = useState<IncidentInputPayload>(
    initialPayload ? { ...DEFAULT_FORM_STATE, ...initialPayload } : DEFAULT_FORM_STATE
  );
  const [presets, setPresets] = useState<ScenarioPreset[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>('armed_commercial_robbery');
  const [analysisResult, setAnalysisResult] = useState<InputAnalysisResult | null>(
    initialAnalysisResult || null
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [is24Hour, setIs24Hour] = useState<boolean>(false);

  // Progressive Disclosure: Collapsible sections
  const [showAdvancedDetails, setShowAdvancedDetails] = useState<boolean>(false);

  const resultsRef = useRef<HTMLDivElement>(null);

  // Load realistic demo presets
  useEffect(() => {
    let mounted = true;
    api.getAnalysisPresets()
      .then((data) => {
        if (mounted) setPresets(data);
      })
      .catch(() => {});
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    if (initialAnalysisResult) {
      setAnalysisResult(initialAnalysisResult);
    }
  }, [initialAnalysisResult]);

  // Handle Quick Demo Preset loading
  const handleSelectPreset = (preset: ScenarioPreset) => {
    setSelectedPresetId(preset.id);
    setFormData({
      ...DEFAULT_FORM_STATE,
      ...preset.payload,
      scenario_title: preset.title
    });
    setError(null);
  };

  const handleFieldChange = (field: keyof IncidentInputPayload, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value
    }));
  };

  // Submit Incident Analysis with friendly client validation
  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    // Friendly Input Validation
    if (!formData.scenario_title || !formData.scenario_title.trim()) {
      setError('Please provide an Incident Case Title or Scenario description.');
      return;
    }
    if ((formData.victim_count ?? 0) < 1) {
      setError('Victim count must be at least 1.');
      return;
    }
    if ((formData.offender_count ?? 0) < 1) {
      setError('Involved individuals count must be at least 1.');
      return;
    }
    if ((formData.property_value ?? 0) < 0) {
      setError('Estimated property loss value cannot be negative.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await api.analyzeIncidentInput(formData);
      setAnalysisResult(res);

      // Smooth scroll to results
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze behavioral input.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetForm = () => {
    setFormData(DEFAULT_FORM_STATE);
    setSelectedPresetId('');
    setError(null);
    setAnalysisResult(null);
  };

  return (
    <div className="page-container" style={{ maxWidth: '1240px', margin: '0 auto', paddingBottom: '80px' }}>
      {/* =========================================================================
          PAGE HEADER
          ========================================================================= */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                padding: '10px',
                borderRadius: '10px',
                background: 'rgba(14, 165, 233, 0.15)',
                color: 'var(--accent-cyan)'
              }}
            >
              <Compass size={26} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, color: 'var(--text-main)', letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>Analyze Incident</span>
                <span role="img" aria-label="compass">🧭</span>
              </h1>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                {analysisMode === 'single'
                  ? 'Enter incident characteristics to generate a 70D Behavioral Fingerprint and match historical reference patterns.'
                  : 'Upload your own incident data to discover patterns, connections, similarities, and changes within that dataset.'}
              </p>
            </div>
          </div>

          {/* Top Quick Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => onNavigate('incident-history')}
              style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', padding: '7px 12px' }}
            >
              <History size={15} />
              <span>Incident History</span>
            </button>
          </div>
        </div>

        {/* =========================================================================
            ANALYSIS MODE SWITCHER (PRIMARY CHOICE)
            ========================================================================= */}
        <div
          style={{
            display: 'flex',
            background: 'var(--bg-subtle)',
            padding: '4px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            maxWidth: '560px'
          }}
        >
          <button
            type="button"
            onClick={() => {
              setAnalysisMode('single');
              setError(null);
            }}
            style={{
              flex: 1,
              padding: '10px 16px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              fontSize: '0.88rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.18s ease',
              background: analysisMode === 'single' ? 'var(--bg-card)' : 'transparent',
              color: analysisMode === 'single' ? 'var(--accent-cyan)' : 'var(--text-muted)',
              boxShadow: analysisMode === 'single' ? 'var(--shadow-sm)' : 'none'
            }}
          >
            <Compass size={17} />
            <span>Mode 1: Analyze a Single Incident</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setAnalysisMode('dataset');
              setError(null);
            }}
            style={{
              flex: 1,
              padding: '10px 16px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              fontSize: '0.88rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.18s ease',
              background: analysisMode === 'dataset' ? 'var(--bg-card)' : 'transparent',
              color: analysisMode === 'dataset' ? 'var(--accent-cyan)' : 'var(--text-muted)',
              boxShadow: analysisMode === 'dataset' ? 'var(--shadow-sm)' : 'none'
            }}
          >
            <FileSpreadsheet size={17} />
            <span>Mode 2: Analyze My Dataset</span>
          </button>
        </div>
      </div>

      {/* =========================================================================
          MODE 2: ANALYZE MY DATASET EXPERIENCE
          ========================================================================= */}
      {analysisMode === 'dataset' && (
        <DatasetAnalysisExperience onNavigate={onNavigate} />
      )}

      {/* =========================================================================
          MODE 1: ANALYZE A SINGLE INCIDENT (PROGRESSIVE DISCLOSURE)
          ========================================================================= */}
      {analysisMode === 'single' && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '28px',
            marginBottom: '32px',
            boxShadow: 'var(--shadow-sm)'
          }}
        >
          {/* Quick Demo Scenarios Bar */}
          {presets.length > 0 && (
            <div
              style={{
                background: 'var(--bg-subtle)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '14px 18px',
                marginBottom: '24px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                <Sparkles size={14} />
                <span>1-Click Demo Scenarios (Pre-configured for Rapid Testing)</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {presets.map((preset) => (
                  <button
                    key={preset.id}
                    type="button"
                    onClick={() => handleSelectPreset(preset)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      background: selectedPresetId === preset.id ? 'var(--accent-cyan)' : 'var(--bg-card)',
                      color: selectedPresetId === preset.id ? '#ffffff' : 'var(--text-main)',
                      border: `1px solid ${selectedPresetId === preset.id ? 'var(--accent-cyan)' : 'var(--border-subtle)'}`
                    }}
                  >
                    {preset.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* User Entered Facts vs Model Findings Badge */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'rgba(16, 185, 129, 0.08)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              borderRadius: 'var(--radius-sm)',
              padding: '10px 14px',
              marginBottom: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--accent-emerald)', background: 'rgba(16, 185, 129, 0.2)', padding: '2px 8px', borderRadius: '4px' }}>
                USER-ENTERED CASE FACTS
              </span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Fields below represent observed, user-reported incident characteristics.
              </span>
            </div>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>
              Analytical patterns & similarity scores are AI-derived on submission
            </span>
          </div>

          <form onSubmit={handleSubmit}>
            {/* =========================================================================
                SECTION 1: BASIC INCIDENT DETAILS
                ========================================================================= */}
            <div style={{ marginBottom: '28px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Tag size={16} style={{ color: 'var(--accent-cyan)' }} />
                <span>1. Basic Incident Details</span>
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '18px' }}>
                {/* Scenario Title */}
                <div style={{ gridColumn: 'span 2' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Incident Case Title / Scenario
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    value={formData.scenario_title}
                    onChange={(e) => handleFieldChange('scenario_title', e.target.value)}
                    placeholder="e.g. Armed Commercial Robbery Case"
                    required
                    style={{ width: '100%', background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 12px', color: 'var(--text-main)', fontSize: '0.88rem' }}
                  />
                </div>

                {/* Crime Category */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Statutory Crime Category
                  </label>
                  <select
                    value={formData.crime_category}
                    onChange={(e) => handleFieldChange('crime_category', e.target.value)}
                    style={{ width: '100%', background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 12px', color: 'var(--text-main)', fontSize: '0.88rem', cursor: 'pointer' }}
                  >
                    <option value="person_property">Robbery / Violent Property</option>
                    <option value="property">Property Offenses (Burglary, Theft)</option>
                    <option value="person">Person / Violent Offenses (Assault)</option>
                    <option value="society">Society Offenses (Narcotics, Weapons)</option>
                  </select>
                </div>

                {/* Attempted Status */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Attempted vs Completed
                  </label>
                  <select
                    value={formData.is_attempted ? 'true' : 'false'}
                    onChange={(e) => handleFieldChange('is_attempted', e.target.value === 'true')}
                    style={{ width: '100%', background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 12px', color: 'var(--text-main)', fontSize: '0.88rem', cursor: 'pointer' }}
                  >
                    <option value="false">Completed Offense</option>
                    <option value="true">Attempted Only</option>
                  </select>
                </div>

                {/* Date */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Incident Date
                  </label>
                  <input
                    type="date"
                    value={formData.incident_date}
                    onChange={(e) => handleFieldChange('incident_date', e.target.value)}
                    style={{ width: '100%', background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 12px', color: 'var(--text-main)', fontSize: '0.88rem' }}
                  />
                </div>

                {/* Time */}
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                      Incident Time {is24Hour ? '(24h)' : '(12h AM/PM)'}
                    </label>
                    <button
                      type="button"
                      onClick={() => setIs24Hour(!is24Hour)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--accent-cyan)',
                        fontSize: '0.74rem',
                        cursor: 'pointer',
                        padding: 0,
                        textDecoration: 'underline'
                      }}
                    >
                      Switch to {is24Hour ? '12h' : '24h'}
                    </button>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="time"
                      value={formData.incident_time}
                      onChange={(e) => handleFieldChange('incident_time', e.target.value)}
                      style={{ flex: 1, background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 12px', color: 'var(--text-main)', fontSize: '0.88rem' }}
                    />
                    <span
                      style={{
                        fontSize: '0.72rem',
                        color: '#94a3b8',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        padding: '8px 10px',
                        borderRadius: 'var(--radius-sm)',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      IST
                    </span>
                  </div>
                </div>
              </div>

              {/* Location Grid */}
              <div style={{ background: 'var(--bg-subtle)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <MapPin size={15} style={{ color: 'var(--accent-emerald)' }} />
                  <span>Geographic Location Details (India-Ready)</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                  {/* Country */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '4px' }}>Country</label>
                    <select
                      value={formData.country || 'India'}
                      onChange={(e) => {
                        const country = e.target.value;
                        handleFieldChange('country', country);
                        if (country === 'India') {
                          handleFieldChange('currency', 'INR');
                          handleFieldChange('timezone', 'Asia/Kolkata');
                          handleFieldChange('state_ut', 'Karnataka');
                          handleFieldChange('district', 'Bengaluru Urban');
                        }
                      }}
                      style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '7px 10px', color: 'var(--text-main)', fontSize: '0.82rem' }}
                    >
                      <option value="India">India (IST / ₹ INR)</option>
                      <option value="United States">United States</option>
                      <option value="United Kingdom">United Kingdom</option>
                    </select>
                  </div>

                  {/* State / UT */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '4px' }}>State / UT</label>
                    <input
                      type="text"
                      list="indian-states"
                      value={formData.state_ut || ''}
                      onChange={(e) => handleFieldChange('state_ut', e.target.value)}
                      placeholder="e.g. Karnataka"
                      style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '7px 10px', color: 'var(--text-main)', fontSize: '0.82rem' }}
                    />
                    <datalist id="indian-states">
                      {INDIAN_STATES_AND_UTS.map((st) => (
                        <option key={st} value={st} />
                      ))}
                    </datalist>
                  </div>

                  {/* District */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '4px' }}>District</label>
                    <input
                      type="text"
                      list="indian-districts"
                      value={formData.district || ''}
                      onChange={(e) => handleFieldChange('district', e.target.value)}
                      placeholder="e.g. Bengaluru Urban"
                      style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '7px 10px', color: 'var(--text-main)', fontSize: '0.82rem' }}
                    />
                    <datalist id="indian-districts">
                      {(formData.state_ut && POPULAR_INDIAN_DISTRICTS[formData.state_ut]
                        ? POPULAR_INDIAN_DISTRICTS[formData.state_ut]
                        : Object.values(POPULAR_INDIAN_DISTRICTS).flat()
                      ).map((d) => (
                        <option key={d} value={d} />
                      ))}
                    </datalist>
                  </div>

                  {/* City */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '4px' }}>City / Town</label>
                    <input
                      type="text"
                      value={formData.city_town || ''}
                      onChange={(e) => handleFieldChange('city_town', e.target.value)}
                      placeholder="e.g. Bengaluru"
                      style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '7px 10px', color: 'var(--text-main)', fontSize: '0.82rem' }}
                    />
                  </div>

                  {/* Locality */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '4px' }}>Locality / Police Station</label>
                    <input
                      type="text"
                      value={formData.locality || ''}
                      onChange={(e) => handleFieldChange('locality', e.target.value)}
                      placeholder="e.g. Indiranagar"
                      style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '7px 10px', color: 'var(--text-main)', fontSize: '0.82rem' }}
                    />
                  </div>

                  {/* PIN */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '4px' }}>PIN / Postal Code</label>
                    <input
                      type="text"
                      maxLength={6}
                      value={formData.pin_code || ''}
                      onChange={(e) => handleFieldChange('pin_code', e.target.value)}
                      placeholder="e.g. 560038"
                      style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '7px 10px', color: 'var(--text-main)', fontSize: '0.82rem' }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* =========================================================================
                SECTION 2: ADDITIONAL BEHAVIORAL DETAILS
                ========================================================================= */}
            <div style={{ marginBottom: '28px', borderTop: '1px solid var(--border-subtle)', paddingTop: '20px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Fingerprint size={16} style={{ color: 'var(--accent-purple)' }} />
                <span>2. Additional Behavioral Details</span>
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
                {/* Population Setting */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Jurisdiction Setting
                  </label>
                  <select
                    value={formData.population_setting}
                    onChange={(e) => handleFieldChange('population_setting', e.target.value)}
                    style={{ width: '100%', background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 12px', color: 'var(--text-main)', fontSize: '0.88rem', cursor: 'pointer' }}
                  >
                    <option value="metropolitan_core">Metropolitan Core (&gt;250k)</option>
                    <option value="large_city">Large City (100k–250k)</option>
                    <option value="mid_sized_city">Mid-Sized City (50k–100k)</option>
                    <option value="small_city">Small City / Suburban (10k–50k)</option>
                    <option value="rural_community">Rural Community (&lt;10k)</option>
                  </select>
                </div>

                {/* Weapons Involved */}
                <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                  <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', marginBottom: formData.has_weapon ? '8px' : 0 }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Weapon Involved?</span>
                    <input
                      type="checkbox"
                      checked={formData.has_weapon}
                      onChange={(e) => {
                        handleFieldChange('has_weapon', e.target.checked);
                        if (!e.target.checked) handleFieldChange('weapon_count', 0);
                        else handleFieldChange('weapon_count', 1);
                      }}
                      style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                    />
                  </label>
                  {formData.has_weapon && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Count:</span>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        value={formData.weapon_count}
                        onChange={(e) => handleFieldChange('weapon_count', Number(e.target.value))}
                        style={{ width: '60px', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '3px 6px', color: 'var(--text-main)', fontSize: '0.8rem' }}
                      />
                    </div>
                  )}
                </div>

                {/* Criminal Activity / Gang */}
                <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                  <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Gang / Syndicate Activity?</span>
                    <input
                      type="checkbox"
                      checked={formData.has_criminal_activity}
                      onChange={(e) => handleFieldChange('has_criminal_activity', e.target.checked)}
                      style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                    />
                  </label>
                </div>

                {/* Known Relationship / Domestic */}
                <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                  <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Known Offender / Domestic?</span>
                    <input
                      type="checkbox"
                      checked={formData.has_relationship}
                      onChange={(e) => handleFieldChange('has_relationship', e.target.checked)}
                      style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                    />
                  </label>
                </div>

                {/* Victims Count & Age */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Victims Count & Avg Age
                  </label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={formData.victim_count}
                      onChange={(e) => handleFieldChange('victim_count', Number(e.target.value))}
                      placeholder="Count"
                      style={{ width: '48%', background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 10px', color: 'var(--text-main)', fontSize: '0.88rem' }}
                    />
                    <input
                      type="number"
                      min="0"
                      max="110"
                      value={formData.victim_avg_age || ''}
                      onChange={(e) => handleFieldChange('victim_avg_age', e.target.value ? Number(e.target.value) : undefined)}
                      placeholder="Age"
                      style={{ width: '48%', background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 10px', color: 'var(--text-main)', fontSize: '0.88rem' }}
                    />
                  </div>
                </div>

                {/* Offenders Count & Age */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Suspects / Accused Count & Age
                  </label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={formData.offender_count}
                      onChange={(e) => handleFieldChange('offender_count', Number(e.target.value))}
                      placeholder="Count"
                      style={{ width: '48%', background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 10px', color: 'var(--text-main)', fontSize: '0.88rem' }}
                    />
                    <input
                      type="number"
                      min="0"
                      max="110"
                      value={formData.offender_avg_age || ''}
                      onChange={(e) => handleFieldChange('offender_avg_age', e.target.value ? Number(e.target.value) : undefined)}
                      placeholder="Age"
                      style={{ width: '48%', background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '9px 10px', color: 'var(--text-main)', fontSize: '0.88rem' }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* =========================================================================
                SECTION 3: ADVANCED / OPTIONAL DETAILS (COLLAPSIBLE PROGRESSIVE DISCLOSURE)
                ========================================================================= */}
            <div style={{ marginBottom: '28px', borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
              <button
                type="button"
                onClick={() => setShowAdvancedDetails(!showAdvancedDetails)}
                style={{
                  width: '100%',
                  background: 'transparent',
                  border: 'none',
                  padding: '8px 0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  color: 'var(--text-main)',
                  fontSize: '0.92rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ChevronDown size={18} style={{ transform: showAdvancedDetails ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s ease', color: 'var(--accent-cyan)' }} />
                  <span>3. Advanced & Optional Details (Property Values, Injuries, Narcotics, Bias Motivation, Custody)</span>
                </div>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontWeight: 500 }}>
                  {showAdvancedDetails ? 'Hide' : 'Show Advanced Details'}
                </span>
              </button>

              {showAdvancedDetails && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginTop: '14px' }}>
                  {/* Property Targeted / Stolen */}
                  <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', marginBottom: formData.has_property ? '8px' : 0 }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Property Loss / Stolen?</span>
                      <input
                        type="checkbox"
                        checked={formData.has_property}
                        onChange={(e) => {
                          handleFieldChange('has_property', e.target.checked);
                          handleFieldChange('has_stolen_property', e.target.checked);
                        }}
                        style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                      />
                    </label>

                    {formData.has_property && (
                      <div style={{ marginTop: '8px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                            Estimated Loss Value ({formData.currency || 'INR'})
                          </span>
                          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>
                            ₹ {formatIndianNumber(formData.property_value || 0)}
                          </span>
                        </div>
                        <input
                          type="number"
                          min="0"
                          step="1000"
                          value={formData.property_value}
                          onChange={(e) => handleFieldChange('property_value', Number(e.target.value))}
                          placeholder="e.g. 350000"
                          style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '6px 8px', color: 'var(--text-main)', fontSize: '0.82rem' }}
                        />
                      </div>
                    )}
                  </div>

                  {/* Physical Injury */}
                  <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Physical Injury Reported?</span>
                      <input
                        type="checkbox"
                        checked={formData.has_injury}
                        onChange={(e) => handleFieldChange('has_injury', e.target.checked)}
                        style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                      />
                    </label>
                  </div>

                  {/* Narcotics Involvement */}
                  <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Drug / Substance Involved?</span>
                      <input
                        type="checkbox"
                        checked={formData.has_drug}
                        onChange={(e) => handleFieldChange('has_drug', e.target.checked)}
                        style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                      />
                    </label>
                  </div>

                  {/* Bias Motivation */}
                  <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Suspected Bias / Hate Crime?</span>
                      <input
                        type="checkbox"
                        checked={formData.has_bias_motivation}
                        onChange={(e) => handleFieldChange('has_bias_motivation', e.target.checked)}
                        style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                      />
                    </label>
                  </div>

                  {/* Arrest Status */}
                  <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>Suspect in Custody / Arrested?</span>
                      <input
                        type="checkbox"
                        checked={formData.has_arrest}
                        onChange={(e) => handleFieldChange('has_arrest', e.target.checked)}
                        style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                      />
                    </label>
                  </div>
                </div>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div
                role="alert"
                style={{
                  background: 'rgba(244, 63, 94, 0.1)',
                  border: '1px solid rgba(244, 63, 94, 0.3)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '12px',
                  color: 'var(--accent-rose)',
                  fontSize: '0.85rem',
                  marginBottom: '18px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            )}

            {/* Form Actions: Primary Button */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleResetForm}
                style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}
                aria-label="Reset all incident form fields"
              >
                <RotateCcw size={15} />
                <span>Reset Incident Form</span>
              </button>

              {/* PRIMARY REQUIRED BUTTON: ANALYZE WITH CRIME COMPASS 🧭 */}
              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary"
                style={{
                  padding: '12px 28px',
                  fontSize: '1rem',
                  fontWeight: 800,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '10px',
                  borderRadius: 'var(--radius-md)',
                  boxShadow: '0 4px 18px rgba(14, 165, 233, 0.35)',
                  background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                <Compass size={18} className={loading ? 'spin' : ''} />
                <span>{loading ? 'ANALYZING WITH CRIME COMPASS 🧭...' : 'ANALYZE WITH CRIME COMPASS 🧭'}</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </form>
        </div>
      )}

      {/* =========================================================================
          MODE 1 RESULTS: CRIME COMPASS ANALYSIS RESULT EXPERIENCE
          ========================================================================= */}
      {analysisMode === 'single' && analysisResult && (
        <div ref={resultsRef} style={{ marginTop: '36px' }}>
          <CrimeDnaResultExperience
            analysisResult={analysisResult}
            formData={formData}
            onNavigate={onNavigate}
            onReset={() => {
              setAnalysisResult(null);
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
          />
        </div>
      )}
    </div>
  );
};
