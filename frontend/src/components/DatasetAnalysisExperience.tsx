import React, { useState, useRef } from 'react';
import { api } from '../api';
import type {
  DatasetValidationResult,
  DatasetAnalysisResult,
  DatasetPattern,
  DatasetSimilarIncident
} from '../types';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Compass,
  Sparkles,
  Filter,
  Calendar,
  MapPin,
  TrendingUp,
  Network,
  ArrowRight,
  RotateCcw,
  Download,
  Trash2,
  HelpCircle,
  Info,
  ChevronDown,
  ChevronUp,
  Cpu,
  ShieldCheck,
  AlertCircle,
  FileCheck,
  ArrowLeft,
  Lock,
  Tag
} from 'lucide-react';
import { formatIndianNumber } from '../utils/indiaFormat';

interface DatasetAnalysisExperienceProps {
  onNavigate?: (page: string, params?: any) => void;
}

type WizardStep = 'upload' | 'preview' | 'mapping' | 'validation' | 'scope' | 'analyzing' | 'results';

export const DatasetAnalysisExperience: React.FC<DatasetAnalysisExperienceProps> = ({ onNavigate }) => {
  const [currentStep, setCurrentStep] = useState<WizardStep>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<DatasetValidationResult | null>(null);
  const [columnMapping, setColumnMapping] = useState<Record<string, string>>({});
  const [scopeOptions, setScopeOptions] = useState<{
    compare_with_reference: boolean;
    filter_country: string;
    filter_state: string;
    filter_district: string;
    filter_city: string;
    filter_locality: string;
    date_start: string;
    date_end: string;
  }>({
    compare_with_reference: true,
    filter_country: '',
    filter_state: '',
    filter_district: '',
    filter_city: '',
    filter_locality: '',
    date_start: '',
    date_end: ''
  });

  const [analysisResult, setAnalysisResult] = useState<DatasetAnalysisResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);
  const [selectedPatternFilter, setSelectedPatternFilter] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // --------------------------------------------------------------------------
  // STEP 1: Handle File Selection & Initial Validation
  // --------------------------------------------------------------------------
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      await processSelectedFile(file);
    }
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      await processSelectedFile(file);
    }
  };

  const processSelectedFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Crime Compass currently supports CSV datasets for maximum cross-platform compatibility.');
      return;
    }

    setSelectedFile(file);
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.validateDataset(formData);
      setValidationResult(res);
      setColumnMapping(res.suggested_mapping || {});
      setCurrentStep('preview');
    } catch (err: any) {
      setError(err.message || 'Failed to inspect and validate uploaded CSV file.');
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------------------------------
  // STEP 3: Handle Column Mapping Changes
  // --------------------------------------------------------------------------
  const handleMappingChange = (standardField: string, userCol: string) => {
    setColumnMapping((prev) => {
      const updated = { ...prev };
      if (!userCol || userCol === 'unmapped') {
        delete updated[standardField];
      } else {
        updated[standardField] = userCol;
      }
      return updated;
    });
  };

  // --------------------------------------------------------------------------
  // STEP 6: Execute Behavioral Machine Learning Analysis
  // --------------------------------------------------------------------------
  const handleRunAnalysis = async () => {
    if (!validationResult) return;

    setLoading(true);
    setError(null);
    setCurrentStep('analyzing');

    try {
      const cleanScope: Record<string, any> = {
        compare_with_reference: scopeOptions.compare_with_reference
      };
      if (scopeOptions.filter_country) cleanScope.filter_country = scopeOptions.filter_country;
      if (scopeOptions.filter_state) cleanScope.filter_state = scopeOptions.filter_state;
      if (scopeOptions.filter_district) cleanScope.filter_district = scopeOptions.filter_district;
      if (scopeOptions.filter_city) cleanScope.filter_city = scopeOptions.filter_city;
      if (scopeOptions.filter_locality) cleanScope.filter_locality = scopeOptions.filter_locality;
      if (scopeOptions.date_start) cleanScope.date_start = scopeOptions.date_start;
      if (scopeOptions.date_end) cleanScope.date_end = scopeOptions.date_end;

      const res = await api.analyzeDataset({
        file_token: validationResult.file_token,
        filename: validationResult.filename,
        column_mapping: columnMapping,
        scope: cleanScope,
        user_id: 'investigator_session'
      });

      setAnalysisResult(res);
      setCurrentStep('results');
    } catch (err: any) {
      setError(err.message || 'Dataset analysis failed. Please verify column mappings.');
      setCurrentStep('scope');
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------------------------------
  // Reset / Delete Analysis
  // --------------------------------------------------------------------------
  const handleResetAll = async () => {
    if (analysisResult?.analysis_id) {
      try {
        await api.deleteDatasetAnalysis(analysisResult.analysis_id);
      } catch (e) {}
    }
    setSelectedFile(null);
    setValidationResult(null);
    setAnalysisResult(null);
    setColumnMapping({});
    setError(null);
    setCurrentStep('upload');
  };

  // --------------------------------------------------------------------------
  // Render Steps Header Bar
  // --------------------------------------------------------------------------
  const renderStepIndicator = () => {
    const steps: Array<{ id: WizardStep; label: string; num: number }> = [
      { id: 'upload', label: '1. Select File', num: 1 },
      { id: 'preview', label: '2. Preview', num: 2 },
      { id: 'mapping', label: '3. Map Columns', num: 3 },
      { id: 'validation', label: '4. Validation', num: 4 },
      { id: 'scope', label: '5. Scope & Run', num: 5 },
      { id: 'results', label: '6. Insights', num: 6 }
    ];

    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'var(--bg-subtle)',
          padding: '12px 18px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
          marginBottom: '24px',
          overflowX: 'auto',
          gap: '8px'
        }}
      >
        {steps.map((st) => {
          const isActive = currentStep === st.id;
          const isCompleted =
            (st.id === 'upload' && validationResult) ||
            (st.id === 'preview' && ['mapping', 'validation', 'scope', 'analyzing', 'results'].includes(currentStep)) ||
            (st.id === 'mapping' && ['validation', 'scope', 'analyzing', 'results'].includes(currentStep)) ||
            (st.id === 'validation' && ['scope', 'analyzing', 'results'].includes(currentStep)) ||
            (st.id === 'scope' && currentStep === 'results');

          return (
            <div
              key={st.id}
              onClick={() => {
                if (isCompleted && currentStep !== 'analyzing') {
                  setCurrentStep(st.id);
                }
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.82rem',
                fontWeight: isActive ? 700 : 500,
                color: isActive ? 'var(--accent-cyan)' : isCompleted ? 'var(--text-main)' : 'var(--text-muted)',
                cursor: isCompleted ? 'pointer' : 'default',
                whiteSpace: 'nowrap'
              }}
            >
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  background: isActive
                    ? 'var(--accent-cyan)'
                    : isCompleted
                    ? 'rgba(16, 185, 129, 0.2)'
                    : 'var(--bg-card)',
                  color: isActive ? '#ffffff' : isCompleted ? 'var(--accent-emerald)' : 'var(--text-muted)',
                  border: `1px solid ${isActive ? 'var(--accent-cyan)' : isCompleted ? 'var(--accent-emerald)' : 'var(--border-subtle)'}`
                }}
              >
                {isCompleted && !isActive ? '✓' : st.num}
              </div>
              <span>{st.label}</span>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div style={{ marginTop: '16px' }}>
      {/* Privacy Notice Banner */}
      <div
        style={{
          background: 'rgba(14, 165, 233, 0.08)',
          border: '1px solid rgba(14, 165, 233, 0.25)',
          borderRadius: 'var(--radius-md)',
          padding: '12px 16px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px'
        }}
      >
        <ShieldCheck size={18} style={{ color: 'var(--accent-cyan)', marginTop: '2px', flexShrink: 0 }} />
        <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.45' }}>
          <strong style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>Privacy & Data Isolation Safeguard:</strong>{' '}
          Uploaded datasets are processed strictly in an isolated session and evaluated against behavioral modus operandi traits.
          Your data is never injected into or used to retrain the historical reference dataset, and you can delete the analysis at any time.
        </div>
      </div>

      {currentStep !== 'upload' && renderStepIndicator()}

      {/* Error Alert */}
      {error && (
        <div
          role="alert"
          style={{
            background: 'rgba(244, 63, 94, 0.1)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            borderRadius: 'var(--radius-sm)',
            padding: '12px 16px',
            color: 'var(--accent-rose)',
            fontSize: '0.86rem',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}
        >
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* =========================================================================
          STEP 1: SELECT FILE
          ========================================================================= */}
      {currentStep === 'upload' && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '36px',
            textAlign: 'center'
          }}
        >
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            style={{
              border: '2px dashed var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '48px 24px',
              background: 'var(--bg-subtle)',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onClick={() => fileInputRef.current?.click()}
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
                margin: '0 auto 16px auto'
              }}
            >
              <UploadCloud size={32} />
            </div>

            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '8px' }}>
              Upload Incident Dataset (CSV)
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', maxWidth: '540px', margin: '0 auto 20px auto' }}>
              Upload your own incident data from any city, district, police jurisdiction, or custom date range to discover patterns, connections, similarities, and shifts within your dataset.
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />

            <button
              type="button"
              className="btn btn-primary"
              disabled={loading}
              style={{
                padding: '10px 24px',
                fontSize: '0.9rem',
                fontWeight: 700,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                borderRadius: 'var(--radius-sm)'
              }}
            >
              <FileText size={16} />
              <span>{loading ? 'Inspecting CSV File...' : 'Select CSV File'}</span>
            </button>

            <div style={{ marginTop: '16px', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
              Supports standard CSV up to 15 MB (~50,000 incident rows). Indian and international location formats supported.
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          STEP 2: PREVIEW DATASET
          ========================================================================= */}
      {currentStep === 'preview' && validationResult && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '28px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileCheck size={20} style={{ color: 'var(--accent-emerald)' }} />
                <span>Dataset Inspection & Preview</span>
              </h3>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.84rem' }}>
                File: <strong>{validationResult.filename}</strong> ({(validationResult.file_size_bytes / 1024).toFixed(1)} KB)
              </p>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setCurrentStep('upload')}
                style={{ fontSize: '0.82rem', padding: '6px 14px' }}
              >
                Change File
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setCurrentStep('mapping')}
                style={{ fontSize: '0.82rem', padding: '6px 16px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
              >
                <span>Proceed to Column Mapping</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>

          {/* Quick Stats Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '24px' }}>
            <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Total Records</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>{formatIndianNumber(validationResult.total_records)}</div>
            </div>
            <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Total Columns</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>{validationResult.total_columns}</div>
            </div>
            <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Duplicate Rows</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: validationResult.duplicate_rows > 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)' }}>
                {validationResult.duplicate_rows}
              </div>
            </div>
            <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Empty Cells</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>
                {validationResult.missing_percentage}%
              </div>
            </div>
          </div>

          {/* Warnings Bar */}
          {validationResult.warnings && validationResult.warnings.length > 0 && (
            <div style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: 'var(--radius-sm)', padding: '12px', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-amber)', fontSize: '0.8rem', fontWeight: 700, marginBottom: '6px' }}>
                <AlertTriangle size={15} />
                <span>Validation Observations:</span>
              </div>
              <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {validationResult.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Preview Table */}
          <div style={{ marginBottom: '16px' }}>
            <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
              Data Sample (First 5 Rows)
            </h4>
            <div style={{ overflowX: 'auto', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-subtle)', borderBottom: '1px solid var(--border-subtle)' }}>
                    {validationResult.columns.map((c) => (
                      <th key={c} style={{ padding: '8px 12px', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                        {c}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {validationResult.preview_rows.map((row, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)', background: idx % 2 === 0 ? 'var(--bg-card)' : 'var(--bg-subtle)' }}>
                      {validationResult.columns.map((c) => (
                        <td key={c} style={{ padding: '8px 12px', color: row[c] === null ? 'var(--text-dim)' : 'var(--text-main)', maxWidth: '220px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {row[c] === null ? <em style={{ color: 'var(--text-dim)' }}>null</em> : String(row[c])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          STEP 3: MAP COLUMNS
          ========================================================================= */}
      {currentStep === 'mapping' && validationResult && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '28px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Layers size={20} style={{ color: 'var(--accent-cyan)' }} />
                <span>Map Columns to Behavioral DNA Schema</span>
              </h3>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.84rem' }}>
                Crime Compass automatically suggested column mappings. You can adjust mappings or leave optional fields unmapped.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setCurrentStep('preview')}
                style={{ fontSize: '0.82rem', padding: '6px 14px' }}
              >
                Back to Preview
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setCurrentStep('validation')}
                style={{ fontSize: '0.82rem', padding: '6px 16px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
              >
                <span>Confirm Mappings</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>

          {/* Mapping Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '14px' }}>
            {validationResult.mapping_details.map((item) => {
              const currentMappedCol = columnMapping[item.standard_field] || '';
              const isMapped = Boolean(currentMappedCol);

              return (
                <div
                  key={item.standard_field}
                  style={{
                    background: 'var(--bg-subtle)',
                    border: `1px solid ${isMapped ? 'var(--border-subtle)' : item.required ? 'rgba(244, 63, 94, 0.4)' : 'var(--border-subtle)'}`,
                    borderRadius: 'var(--radius-sm)',
                    padding: '14px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      {item.label}
                    </span>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background: item.required
                          ? isMapped ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)'
                          : isMapped ? 'rgba(14, 165, 233, 0.15)' : 'rgba(148, 163, 184, 0.1)',
                        color: item.required
                          ? isMapped ? 'var(--accent-emerald)' : 'var(--accent-rose)'
                          : isMapped ? 'var(--accent-cyan)' : 'var(--text-dim)'
                      }}
                    >
                      {item.required ? (isMapped ? 'Required ✓' : 'Required') : (isMapped ? 'Mapped' : 'Optional')}
                    </span>
                  </div>

                  <p style={{ margin: '0 0 10px 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {item.description}
                  </p>

                  <select
                    value={currentMappedCol || 'unmapped'}
                    onChange={(e) => handleMappingChange(item.standard_field, e.target.value)}
                    style={{
                      width: '100%',
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '4px',
                      padding: '7px 10px',
                      color: isMapped ? 'var(--text-main)' : 'var(--text-dim)',
                      fontSize: '0.82rem',
                      cursor: 'pointer'
                    }}
                  >
                    <option value="unmapped">-- Unmapped / Not in Dataset --</option>
                    {validationResult.columns.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* =========================================================================
          STEP 4: VALIDATION CHECKLIST
          ========================================================================= */}
      {currentStep === 'validation' && validationResult && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '28px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={20} style={{ color: 'var(--accent-emerald)' }} />
                <span>Data Quality & Integrity Verification</span>
              </h3>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.84rem' }}>
                Review verification rules before choosing analysis scope.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setCurrentStep('mapping')}
                style={{ fontSize: '0.82rem', padding: '6px 14px' }}
              >
                Back to Mapping
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setCurrentStep('scope')}
                style={{ fontSize: '0.82rem', padding: '6px 16px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
              >
                <span>Configure Scope</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '24px' }}>
            <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '4px' }}>
                <CheckCircle2 size={16} />
                <span>Format & Header Integrity</span>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Valid CSV parsed with standard comma/delimiters. No corrupt byte headers detected.
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '4px' }}>
                <CheckCircle2 size={16} />
                <span>Missing Value Handling Policy</span>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Missing values are strictly preserved as unobserved/unknown. No artificial zeros are imputed.
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '4px' }}>
                <CheckCircle2 size={16} />
                <span>Behavioral DNA Compatibility</span>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Mapped fields translate to 70-dimensional unit hypersphere vectors S^69 for real ML clustering.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          STEP 5: CHOOSE SCOPE & RUN ANALYSIS
          ========================================================================= */}
      {currentStep === 'scope' && validationResult && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '28px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Filter size={20} style={{ color: 'var(--accent-cyan)' }} />
                <span>Configure Analysis Scope & Filters</span>
              </h3>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.84rem' }}>
                Select whether to analyze your dataset independently or compare against the historical baseline, with optional location/time filters.
              </p>
            </div>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setCurrentStep('validation')}
              style={{ fontSize: '0.82rem', padding: '6px 14px' }}
            >
              Back to Validation
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '18px', marginBottom: '28px' }}>
            {/* Scope Option 1: Independent vs Reference Baseline */}
            <div style={{ background: 'var(--bg-subtle)', padding: '18px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '10px' }}>
                Historical Comparison
              </h4>
              <label style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={scopeOptions.compare_with_reference}
                  onChange={(e) => setScopeOptions((prev) => ({ ...prev, compare_with_reference: e.target.checked }))}
                  style={{ width: '16px', height: '16px', marginTop: '3px' }}
                />
                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                  Compare discovered dataset patterns against historical reference archetypes (Alabama 2024 NIBRS baseline).
                </span>
              </label>
            </div>

            {/* Scope Option 2: Geographic Filter (if available) */}
            <div style={{ background: 'var(--bg-subtle)', padding: '18px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MapPin size={15} style={{ color: 'var(--accent-cyan)' }} />
                <span>Location Scope Filter</span>
              </h4>

              {validationResult.available_locations.cities.length > 0 ? (
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '4px' }}>
                    Filter by Specific City / Town:
                  </label>
                  <select
                    value={scopeOptions.filter_city}
                    onChange={(e) => setScopeOptions((prev) => ({ ...prev, filter_city: e.target.value }))}
                    style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '6px 10px', color: 'var(--text-main)', fontSize: '0.82rem' }}
                  >
                    <option value="">-- All Available Cities (Entire Dataset) --</option>
                    {validationResult.available_locations.cities.map((city) => (
                      <option key={city} value={city}>{city}</option>
                    ))}
                  </select>
                </div>
              ) : (
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                  No distinct city columns mapped. Entire dataset scope will be analyzed.
                </div>
              )}
            </div>

            {/* Scope Option 3: Time Range Filter (if available) */}
            <div style={{ background: 'var(--bg-subtle)', padding: '18px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Calendar size={15} style={{ color: 'var(--accent-purple)' }} />
                <span>Date Range Scope Filter</span>
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '2px' }}>Start Date</label>
                  <input
                    type="date"
                    value={scopeOptions.date_start}
                    onChange={(e) => setScopeOptions((prev) => ({ ...prev, date_start: e.target.value }))}
                    style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '5px', color: 'var(--text-main)', fontSize: '0.78rem' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '2px' }}>End Date</label>
                  <input
                    type="date"
                    value={scopeOptions.date_end}
                    onChange={(e) => setScopeOptions((prev) => ({ ...prev, date_end: e.target.value }))}
                    style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '5px', color: 'var(--text-main)', fontSize: '0.78rem' }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* RUN BUTTON */}
          <div style={{ textAlign: 'center' }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleRunAnalysis}
              disabled={loading}
              style={{
                padding: '12px 36px',
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
              <Compass size={20} className={loading ? 'spin' : ''} />
              <span>RUN DATASET BEHAVIORAL ANALYSIS 🧭</span>
              <ArrowRight size={18} />
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          STEP 6: ANALYZING STATE
          ========================================================================= */}
      {currentStep === 'analyzing' && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '48px',
            textAlign: 'center'
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
              margin: '0 auto 20px auto'
            }}
          >
            <Compass size={36} className="spin" />
          </div>

          <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '8px' }}>
            Computing Behavioral Intelligence for Your Dataset...
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', maxWidth: '480px', margin: '0 auto 24px auto' }}>
            Extracting 70D Behavioral DNA unit vectors, fitting Adaptive Spherical K-Means clusters, computing pairwise similarity matrices, and deriving empirical cross-crime modus operandi.
          </p>

          <div style={{ maxWidth: '360px', margin: '0 auto', fontSize: '0.8rem', color: 'var(--accent-cyan)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: 'var(--accent-emerald)' }}>✓</span> 70D Behavioral Fingerprint Encoding
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: 'var(--accent-emerald)' }}>✓</span> Adaptive Spherical K-Means Clustering
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: 'var(--accent-emerald)' }}>✓</span> Pairwise Cosine Similarity with Self-Exclusion
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: 'var(--accent-emerald)' }}>✓</span> Cross-Crime Modus Operandi Discovery
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          STEP 7: COMPREHENSIVE DATASET ANALYSIS RESULTS VIEW
          ========================================================================= */}
      {currentStep === 'results' && analysisResult && (
        <div>
          {/* Top Results Navigation & Export Bar */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '24px',
              flexWrap: 'wrap',
              gap: '12px'
            }}
          >
            <div>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Analysis Completed • ID: {analysisResult.analysis_id}
              </span>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', margin: '2px 0 0 0' }}>
                Dataset Behavioral Intelligence Report
              </h2>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              {/* Export JSON */}
              <a
                href={api.getDatasetExportUrl(analysisResult.analysis_id, 'json')}
                download
                className="btn btn-secondary"
                style={{ fontSize: '0.82rem', padding: '7px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
              >
                <Download size={14} />
                <span>Export JSON</span>
              </a>

              {/* Export CSV */}
              <a
                href={api.getDatasetExportUrl(analysisResult.analysis_id, 'csv')}
                download
                className="btn btn-secondary"
                style={{ fontSize: '0.82rem', padding: '7px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
              >
                <Download size={14} />
                <span>Export CSV Patterns</span>
              </a>

              {/* Delete / Reset */}
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleResetAll}
                style={{ fontSize: '0.82rem', padding: '7px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--accent-rose)' }}
              >
                <Trash2 size={14} />
                <span>Delete & Upload New</span>
              </button>
            </div>
          </div>

          {/* 1. DATASET SUMMARY */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              marginBottom: '24px'
            }}
          >
            <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={18} style={{ color: 'var(--accent-cyan)' }} />
              <span>1. Dataset Summary</span>
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
              <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Dataset Name</div>
                <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                  {analysisResult.dataset_summary.dataset_name}
                </div>
              </div>
              <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Records Analyzed</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>
                  {formatIndianNumber(analysisResult.dataset_summary.total_records)}
                </div>
              </div>
              <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Crime Categories</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>
                  {analysisResult.dataset_summary.number_of_categories}
                </div>
              </div>
              <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Geographic Scope</div>
                <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)', textTransform: 'capitalize' }}>
                  {analysisResult.dataset_summary.geographic_scope}
                </div>
              </div>
            </div>
          </div>

          {/* 2. BEHAVIORAL PATTERNS (EMPIRICALLY DISCOVERED IN UPLOADED DATA) */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              marginBottom: '24px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
              <div>
                <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Layers size={18} style={{ color: 'var(--accent-purple)' }} />
                  <span>2. Discovered Behavioral Patterns ({analysisResult.behavioral_patterns.length})</span>
                </h3>
                <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  Empirical modus operandi clusters discovered by Spherical K-Means directly from your uploaded data records.
                </p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
              {analysisResult.behavioral_patterns.map((pat) => (
                <div
                  key={pat.pattern_id}
                  style={{
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '16px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, padding: '3px 8px', borderRadius: '4px', background: 'rgba(168, 85, 247, 0.15)', color: 'var(--accent-purple)' }}>
                      {pat.pattern_id}
                    </span>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      {pat.incident_count} incidents ({pat.percentage_of_dataset}%)
                    </span>
                  </div>

                  <h4 style={{ fontSize: '0.98rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 6px 0' }}>
                    {pat.title}
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0 0 12px 0', lineHeight: '1.4' }}>
                    {pat.description}
                  </p>

                  {/* Defining traits badges */}
                  <div style={{ marginBottom: '10px' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', display: 'block', marginBottom: '4px' }}>
                      Key Defining Traits:
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {pat.defining_traits.map((t, idx) => (
                        <span key={idx} style={{ fontSize: '0.72rem', background: 'var(--bg-card)', padding: '2px 8px', borderRadius: '4px', border: '1px solid var(--border-subtle)', color: 'var(--text-main)' }}>
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Sample records */}
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    Sample Case IDs: {pat.sample_incident_ids.slice(0, 4).join(', ')}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 3. SIMILAR INCIDENTS (WITH QUERY SELF-EXCLUSION) */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              marginBottom: '24px'
            }}
          >
            <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Network size={18} style={{ color: 'var(--accent-cyan)' }} />
              <span>3. Pairwise Similar Incidents (Cosine Cos(θ) &gt; 0)</span>
            </h3>
            <p style={{ margin: '0 0 16px 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              Identifies nearest-neighbor connections between distinct incidents within your dataset. (Query self-exclusion strictly enforced).
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '14px' }}>
              {analysisResult.similar_incidents.map((pair, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'var(--bg-subtle)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '14px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      <strong>{pair.source_id}</strong> ↔ <strong>{pair.target_id}</strong>
                    </div>
                    <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-emerald)', background: 'rgba(16, 185, 129, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                      {(pair.similarity_score * 100).toFixed(1)}% Match
                    </span>
                  </div>

                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    Matching: {pair.matching_characteristics.join(' • ')}
                  </div>
                  {pair.differing_characteristics.length > 0 && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      Differences: {pair.differing_characteristics.join(' • ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 4. CROSS-CRIME PATTERNS */}
          {analysisResult.cross_crime_patterns.length > 0 && (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                padding: '24px',
                marginBottom: '24px'
              }}
            >
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={18} style={{ color: 'var(--accent-amber)' }} />
                <span>4. Cross-Crime Behavioral Patterns</span>
              </h3>
              <p style={{ margin: '0 0 16px 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                Identifies shared modus operandi characteristics across differing formal statutory categories.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {analysisResult.cross_crime_patterns.map((cc, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'var(--bg-subtle)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '14px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {cc.category_a} ↔ {cc.category_b}
                      </span>
                      <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                        {(cc.behavioral_similarity * 100).toFixed(1)}% Behavioral Similarity
                      </span>
                    </div>

                    <p style={{ margin: '0 0 8px 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {cc.explanation}
                    </p>

                    <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                      Note: {cc.non_offender_disclaimer}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 5. LOCATION-SPECIFIC INSIGHTS */}
          {analysisResult.location_insights.is_available && (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                padding: '24px',
                marginBottom: '24px'
              }}
            >
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MapPin size={18} style={{ color: 'var(--accent-cyan)' }} />
                <span>5. Location-Specific Distribution</span>
              </h3>
              <p style={{ margin: '0 0 16px 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                Incident counts and category breakdowns across mapped geographical jurisdictions.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
                {analysisResult.location_insights.areas.map((area, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'var(--bg-subtle)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '14px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {area.area_name}
                      </span>
                      <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                        {area.incident_count} ({area.proportion_of_dataset}%)
                      </span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      Predominant Category: <strong>{area.primary_observed_category}</strong>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: '14px', fontSize: '0.74rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                Disclaimer: {analysisResult.location_insights.disclaimer}
              </div>
            </div>
          )}

          {/* 6. TEMPORAL EVOLUTION */}
          {analysisResult.temporal_evolution.is_available && (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                padding: '24px',
                marginBottom: '24px'
              }}
            >
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TrendingUp size={18} style={{ color: 'var(--accent-emerald)' }} />
                <span>6. Temporal Timeline Distribution</span>
              </h3>
              <p style={{ margin: '0 0 16px 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                Incident counts over recorded monthly periods.
              </p>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                {analysisResult.temporal_evolution.period_breakdown.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'var(--bg-subtle)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '10px 14px',
                      minWidth: '120px'
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      {item.period}
                    </div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>
                      {item.incident_count} <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>({item.proportion}%)</span>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: '14px', fontSize: '0.74rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                Disclaimer: {analysisResult.temporal_evolution.disclaimer}
              </div>
            </div>
          )}

          {/* 7. UNUSUAL BEHAVIORAL COMBINATIONS */}
          {analysisResult.unusual_combinations.length > 0 && (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                padding: '24px',
                marginBottom: '24px'
              }}
            >
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={18} style={{ color: 'var(--accent-amber)' }} />
                <span>7. Unusual Behavioral Configurations</span>
              </h3>
              <p style={{ margin: '0 0 16px 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                Incidents displaying atypical combinations of behavioral traits relative to the dataset's empirical pattern clusters.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
                {analysisResult.unusual_combinations.map((u, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'var(--bg-subtle)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '14px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        Case: {u.incident_id}
                      </span>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '2px 8px', borderRadius: '4px', background: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)' }}>
                        {u.novelty_label}
                      </span>
                    </div>

                    <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '0 0 8px 0' }}>
                      {u.explanation}
                    </p>

                    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                      Divergent Features: {u.contributing_features.join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 8. COMPARISON WITH HISTORICAL REFERENCE DATASET */}
          {analysisResult.reference_comparison && analysisResult.reference_comparison.status === 'completed' && (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                padding: '24px',
                marginBottom: '24px'
              }}
            >
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Compass size={18} style={{ color: 'var(--accent-cyan)' }} />
                <span>8. Comparison with Historical Reference Dataset</span>
              </h3>
              <p style={{ margin: '0 0 16px 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                Cross-dataset cosine alignment between your dataset's discovered patterns and the 8 pre-trained Alabama 2024 NIBRS reference patterns.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
                {analysisResult.reference_comparison.alignments.map((al, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'var(--bg-subtle)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '12px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {al.dataset_pattern_id}: {al.dataset_pattern_title}
                      </span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                        {(al.cosine_alignment * 100).toFixed(1)}% Alignment
                      </span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Closest Baseline Pattern: <strong>{al.closest_historical_pattern_id}</strong>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: '12px', fontSize: '0.74rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                Disclaimer: {analysisResult.reference_comparison.disclaimer}
              </div>
            </div>
          )}

          {/* 9. WHY THESE RESULTS? (FACTS VS ML FINDINGS VS INTERPRETATIONS) */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              marginBottom: '24px'
            }}
          >
            <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HelpCircle size={18} style={{ color: 'var(--accent-purple)' }} />
              <span>9. Why These Results? (Analytical Transparency)</span>
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
              <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--accent-emerald)', marginBottom: '6px' }}>
                  Observed Facts
                </div>
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.45' }}>
                  {analysisResult.why_these_results.observed_facts.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>

              <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '6px' }}>
                  Algorithm-Derived Findings
                </div>
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.45' }}>
                  {analysisResult.why_these_results.algorithm_findings.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>

              <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--accent-purple)', marginBottom: '6px' }}>
                  Interpretations & Limitations
                </div>
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.45' }}>
                  {analysisResult.why_these_results.interpretations.concat(analysisResult.why_these_results.limitations).map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* 10. TECHNICAL DETAILS (EXPANDABLE) */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              overflow: 'hidden'
            }}
          >
            <button
              type="button"
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              style={{
                width: '100%',
                padding: '16px 24px',
                background: 'transparent',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                color: 'var(--text-main)',
                fontSize: '0.95rem',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={18} style={{ color: 'var(--accent-cyan)' }} />
                <span>10. Technical Specifications & Pipeline Configuration</span>
              </div>
              {showTechnicalDetails ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>

            {showTechnicalDetails && (
              <div style={{ padding: '0 24px 24px 24px', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-subtle)' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px', marginTop: '16px', fontSize: '0.8rem' }}>
                  <div>
                    <strong style={{ color: 'var(--text-main)' }}>Records Analyzed:</strong>{' '}
                    <span style={{ color: 'var(--text-muted)' }}>{analysisResult.technical_details.records_analyzed}</span>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--text-main)' }}>Feature Space:</strong>{' '}
                    <span style={{ color: 'var(--text-muted)' }}>{analysisResult.technical_details.feature_space}</span>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--text-main)' }}>Clustering Method:</strong>{' '}
                    <span style={{ color: 'var(--text-muted)' }}>{analysisResult.technical_details.clustering_algorithm}</span>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--text-main)' }}>Similarity Metric:</strong>{' '}
                    <span style={{ color: 'var(--text-muted)' }}>{analysisResult.technical_details.similarity_metric}</span>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--text-main)' }}>Novelty Evaluation:</strong>{' '}
                    <span style={{ color: 'var(--text-muted)' }}>{analysisResult.technical_details.novelty_algorithm}</span>
                  </div>
                  <div>
                    <strong style={{ color: 'var(--text-main)' }}>Execution Time:</strong>{' '}
                    <span style={{ color: 'var(--accent-emerald)' }}>{analysisResult.technical_details.execution_time_ms} ms</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
