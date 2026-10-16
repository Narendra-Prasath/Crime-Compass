/**
 * Crime Compass 🧭 — Clean API Client Layer
 * Connects the web frontend to the FastAPI backend with environment-based configuration,
 * timeout management, structured error classification, and zero mock fallbacks.
 */

import type {
  HealthResponse,
  DatasetStats,
  IncidentProfile,
  BehavioralDNA,
  SimilarIncidentsResponse,
  ClusterSummary,
  ClusterDetail,
  CrossCrimePatternSummary,
  CrossCrimePatternDetail,
  EvolutionTimeline,
  SignificantShift,
  AnomalySummary,
  BehavioralOutlier,
  SimilarityExplanation,
  IncidentInputPayload,
  ScenarioPreset,
  InputAnalysisResult,
  DnaComparisonResponse,
  ComparisonPreset,
  ExplorePatternsResponse,
  PatternDetailViewResponse,
  BehavioralConnectionMapResponse,
  InvestigatorFeedbackPayload,
  InvestigatorFeedbackResponse,
  FeedbackSummaryResponse,
  AnalysisRecord,
  AnalysisRecordListResponse,
  DatasetValidationResult,
  DatasetAnalysisResult
} from './types';

// Read API base URL from Vite environment variables (fallback to /api for Vite proxy)
const ENV_API_BASE = import.meta.env.VITE_API_BASE_URL;
export const API_BASE = (typeof ENV_API_BASE === 'string' && ENV_API_BASE.trim().length > 0)
  ? ENV_API_BASE.trim().replace(/\/+$/, '')
  : '/api';

const DEFAULT_TIMEOUT_MS = 15000;

export class ApiError extends Error {
  statusCode: number;
  errorName?: string;
  detail?: string;

  constructor(message: string, statusCode: number, errorName?: string, detail?: string) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.errorName = errorName;
    this.detail = detail;
  }
}

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, ...fetchOptions } = options;
  const url = `${API_BASE}${endpoint}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        ...(fetchOptions.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        'Accept': 'application/json',
        ...(fetchOptions.headers || {}),
      },
      ...fetchOptions,
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let errorName = 'HttpError';
      let errorDetail: string | undefined;

      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorMessage = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
          errorDetail = errorMessage;
        } else if (errorJson.message) {
          errorMessage = errorJson.message;
        }
        if (errorJson.error) {
          errorName = errorJson.error;
        }
      } catch {
        // Response was not JSON
      }

      throw new ApiError(errorMessage, response.status, errorName, errorDetail);
    }

    return await response.json();
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }

    if (err.name === 'AbortError') {
      throw new ApiError(
        `Request to ${endpoint} timed out after ${timeoutMs}ms. Backend server might be under heavy load or disconnected.`,
        408,
        'TimeoutError'
      );
    }

    // Network / Connection Error
    throw new ApiError(
      `Unable to connect to Crime Compass 🧭 backend API at '${url}'. Please verify that the FastAPI backend server is running (e.g. uvicorn src.api.main:app --port 8000).`,
      0,
      'NetworkError'
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export const api = {
  /**
   * 1. Health check & model state probe
   */
  getHealth: () => request<HealthResponse>('/health'),

  /**
   * 2. Comprehensive dataset statistics
   */
  getStats: () => request<DatasetStats>('/stats'),

  /**
   * 3. Incident profile lookup by ID
   */
  getIncident: (incidentId: string) =>
    request<IncidentProfile>(`/incidents/${encodeURIComponent(incidentId.trim())}`),

  /**
   * 4. 70-dimensional Behavioral DNA vector & subprofiles
   */
  getIncidentDNA: (incidentId: string) =>
    request<BehavioralDNA>(`/incidents/${encodeURIComponent(incidentId.trim())}/dna`),

  /**
   * 5. Nearest-neighbor behavioral similarity search
   */
  getSimilarIncidents: (incidentId: string, topK: number = 5) =>
    request<SimilarIncidentsResponse>(
      `/similarity/similar/${encodeURIComponent(incidentId.trim())}?top_k=${topK}`
    ),

  searchSimilar: (incidentId: string, topK: number = 5) =>
    request<SimilarIncidentsResponse>('/similarity/search', {
      method: 'POST',
      body: JSON.stringify({ incident_id: incidentId.trim(), top_k: topK, include_breakdown: true }),
    }),

  /**
   * 6. Unsupervised Behavioral Clusters & archetypes
   */
  getClusters: () =>
    request<{ total_clusters: number; clusters: ClusterSummary[] }>('/clusters').then((res) => res.clusters),

  getClusterDetail: (clusterId: number) =>
    request<ClusterDetail>(`/clusters/${clusterId}`),

  /**
   * 7. Cross-Crime Behavioral Patterns
   */
  getCrossCrimePatterns: () =>
    request<{ total_patterns: number; patterns: CrossCrimePatternSummary[]; summary_metrics?: any }>('/cross-crime').then(
      (res) => res.patterns
    ),

  getCrossCrimeDetail: (patternId: string) =>
    request<CrossCrimePatternDetail>(`/cross-crime/${encodeURIComponent(patternId.trim())}`),

  /**
   * 8. Chronological Behavioral Evolution & Trends
   */
  getEvolutionTimeline: () =>
    request<EvolutionTimeline>('/evolution/timeline'),

  getSignificantShifts: () =>
    request<{ total_shifts: number; shifts: SignificantShift[] }>('/evolution/shifts').then((res) => res.shifts),

  /**
   * 9. Novel Behavior & Anomaly Detection (Outliers)
   */
  getAnomalySummary: () =>
    request<AnomalySummary>('/anomaly/summary'),

  getTopOutliers: (limit: number = 50, offset: number = 0) =>
    request<{ total_outliers_returned: number; total_extreme_outliers: number; outliers: BehavioralOutlier[] }>(
      `/anomaly/outliers?limit=${limit}&offset=${offset}`
    ).then((res) => res.outliers),

  getIncidentAnomaly: (incidentId: string) =>
    request<any>(`/anomaly/${encodeURIComponent(incidentId.trim())}`),

  /**
   * 10. Mathematically Grounded Similarity Explanation (XAI)
   */
  getExplanation: (inc1: string, inc2: string) =>
    request<SimilarityExplanation>(`/explain/${encodeURIComponent(inc1.trim())}/${encodeURIComponent(inc2.trim())}`),

  /**
   * 11. Incident Input & Real-Time Behavioral Analysis
   */
  getAnalysisPresets: () =>
    request<ScenarioPreset[]>('/analyze/presets'),

  analyzeIncidentInput: (payload: IncidentInputPayload) =>
    request<InputAnalysisResult>('/analyze/input', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getAnalysisRecords: (
    optionsOrUserId?: string | { userId?: string; search?: string; category?: string; limit?: number; offset?: number },
    limit: number = 50,
    offset: number = 0
  ) => {
    const params = new URLSearchParams();
    if (typeof optionsOrUserId === 'string') {
      if (optionsOrUserId) params.append('user_id', optionsOrUserId);
      params.append('limit', String(limit));
      params.append('offset', String(offset));
    } else if (optionsOrUserId && typeof optionsOrUserId === 'object') {
      if (optionsOrUserId.userId) params.append('user_id', optionsOrUserId.userId);
      if (optionsOrUserId.search) params.append('search', optionsOrUserId.search);
      if (optionsOrUserId.category) params.append('category', optionsOrUserId.category);
      params.append('limit', String(optionsOrUserId.limit ?? limit));
      params.append('offset', String(optionsOrUserId.offset ?? offset));
    } else {
      params.append('limit', String(limit));
      params.append('offset', String(offset));
    }
    return request<AnalysisRecordListResponse>(`/analyze/records?${params.toString()}`);
  },

  getAnalysisRecord: (analysisId: string) =>
    request<AnalysisRecord>(`/analyze/records/${encodeURIComponent(analysisId.trim())}`),

  deleteAnalysisRecord: (analysisId: string, userId?: string) => {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return request<{ status: string; analysis_id: string; message: string }>(
      `/analyze/records/${encodeURIComponent(analysisId.trim())}${qs}`,
      { method: 'DELETE' }
    );
  },

  /**
   * 12. Crime Compass Behavioral Comparison Feature
   */
  getComparisonPresets: () =>
    request<{ presets: ComparisonPreset[] }>('/compare/presets'),

  compareIncidents: (payload: { incident_a: any; incident_b: any }) =>
    request<DnaComparisonResponse>('/compare', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  /**
   * 13. Explore Behavioral Patterns (Clean Cards & Detail Views)
   */
  getExplorePatterns: () =>
    request<ExplorePatternsResponse>('/patterns'),

  getPatternDetail: (patternId: string | number) =>
    request<PatternDetailViewResponse>(`/patterns/${encodeURIComponent(String(patternId).trim())}`),

  /**
   * 14. Behavioral Connection Map
   */
  getConnectionMap: (patternId?: string, category?: string) => {
    const params = new URLSearchParams();
    if (patternId) params.append('pattern_id', patternId);
    if (category) params.append('category', category);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return request<BehavioralConnectionMapResponse>(`/patterns/connection-map${qs}`);
  },

  /**
   * 15. Human-in-the-Loop Investigator Feedback
   */
  submitFeedback: (payload: InvestigatorFeedbackPayload) =>
    request<InvestigatorFeedbackResponse>('/feedback', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getFeedbackSummary: () =>
    request<FeedbackSummaryResponse>('/feedback/summary'),

  /**
   * 16. User Dataset Upload & Behavioral Analysis
   */
  validateDataset: (formData: FormData) =>
    request<DatasetValidationResult>('/datasets/validate', {
      method: 'POST',
      body: formData,
      timeoutMs: 30000,
    }),

  analyzeDataset: (payload: {
    file_token?: string;
    csv_text?: string;
    filename: string;
    column_mapping: Record<string, string>;
    scope: Record<string, any>;
    user_id?: string;
  }) =>
    request<DatasetAnalysisResult>('/datasets/analyze', {
      method: 'POST',
      body: JSON.stringify(payload),
      timeoutMs: 60000,
    }),

  getDatasetAnalysis: (analysisId: string) =>
    request<DatasetAnalysisResult>(`/datasets/analyses/${encodeURIComponent(analysisId)}`),

  deleteDatasetAnalysis: (analysisId: string) =>
    request<{ status: string; analysis_id: string; deleted: boolean; message: string }>(
      `/datasets/analyses/${encodeURIComponent(analysisId)}`,
      { method: 'DELETE' }
    ),

  getDatasetExportUrl: (analysisId: string, format: 'json' | 'csv' = 'json') =>
    `${API_BASE}/datasets/analyses/${encodeURIComponent(analysisId)}/export?format=${format}`,
};




