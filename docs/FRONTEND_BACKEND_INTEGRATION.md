# CRIME DNA — Phase 13: Frontend-to-Backend Integration Report

> **"Different Crimes. Same Behavioral DNA."**

This document certifies the complete, end-to-end connection between the **React 19 / TypeScript** web frontend (`frontend/`) and the **FastAPI** machine learning backend (`src/api/`).

---

## 1. Executive Summary

Phase 13 establishes a verified, production-grade integration layer connecting the user interface directly to the underlying behavioral machine learning engines:
- **Zero Mock / Fabricated Data:** 100% of dashboard statistics, similarity matches, cluster profiles, cross-crime links, temporal trajectories, anomaly scores, and explainability attributions are dynamically computed by the backend models.
- **Environment-Driven API Client:** Configurable through `VITE_API_BASE_URL` with Vite reverse proxy support for local development and direct CORS connection support for distributed deployments.
- **Strict Error Handling:** Graceful handling of network timeouts, 404 (non-existent incidents), 400 (validation errors), 500 (internal exceptions), and empty result sets.
- **Verification:** 78 automated integration and component tests passing with sub-2ms endpoint response times across 220,663 real crime incidents.

---

## 2. API Client Architecture ([`frontend/src/api.ts`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/api.ts))

### 2.1 Configuration & Environment
The API client resolves its target backend via:
```ts
const ENV_API_BASE = import.meta.env.VITE_API_BASE_URL;
export const API_BASE = (typeof ENV_API_BASE === 'string' && ENV_API_BASE.trim().length > 0)
  ? ENV_API_BASE.trim().replace(/\/+$/, '')
  : '/api';
```
- **Local Dev (Vite Proxy):** `VITE_API_BASE_URL=/api` (proxied in `vite.config.ts` to `http://127.0.0.1:8000`).
- **Distributed / Docker / Cloud:** `VITE_API_BASE_URL=http://api.crimedna.internal/api`.

### 2.2 Timeout & Abort Handling
Every request uses `AbortController` bounded by a 15,000ms threshold:
```ts
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
```
If the backend drops or stalls, the frontend immediately surfaces a user-friendly error with retry action rather than hanging indefinitely.

### 2.3 Custom Error Classification (`ApiError`)
```ts
export class ApiError extends Error {
  statusCode: number;
  errorName?: string;
  detail?: string;
  ...
}
```
HTTP status codes and structured backend exception payloads (`detail` and `error` fields from `CrimeDNAException`) are parsed and rendered directly to the user.

---

## 3. End-to-End Endpoint Mapping

| Frontend View / Component | API Client Method | Backend FastAPI Endpoint | Model / Data Source Grounding |
| :--- | :--- | :--- | :--- |
| **Global Header / Sidebar** | `api.getHealth()` | `GET /api/health` | Active lifespan state probe; reports uptime, 220,663 indexed records, and 70D dimension. |
| **Overview Dashboard** | `api.getStats()` | `GET /api/stats` | Empirical dataset counts (220,663 incidents, 8 clusters, 8 cross-crime patterns, 2,207 high outliers). |
| **Overview Dashboard** | `api.getClusters()` | `GET /api/clusters` | 8 Spherical MiniBatchKMeans cluster archetypes and percentage distributions. |
| **Overview Dashboard** | `api.getCrossCrimePatterns()` | `GET /api/cross-crime` | 8 discovered cross-category operational patterns. |
| **Overview Dashboard** | `api.getSignificantShifts()` | `GET /api/evolution/shifts` | Statistically verified ANOVA shifts ($F$-test, $p < 0.001$). |
| **Incident Analyzer** | `api.getIncident(id)` | `GET /api/incidents/{id}` | In-memory incident registry lookup (sub-millisecond context retrieval). |
| **Incident Analyzer** | `api.getIncidentDNA(id)` | `GET /api/incidents/{id}/dna` | 70-dimensional $L_2$-normalized vector, 7 domain energies, top active traits. |
| **Incident Analyzer** | `api.getSimilarIncidents(id, k)` | `GET /api/similarity/similar/{id}?top_k={k}` | Cosine nearest-neighbor retrieval index excluding self-match. |
| **Similarity View** | `api.getExplanation(id1, id2)` | `GET /api/explain/{id1}/{id2}` | Exact cosine similarity score and 7-domain percentage decomposition. |
| **"Why Similar?"** | `api.getExplanation(id1, id2)` | `GET /api/explain/{id1}/{id2}` | Additive inner-product attribution, feature-level differences, and plain-English summary. |
| **Behavioral Patterns** | `api.getClusterDetail(id)` | `GET /api/clusters/{id}` | Dominant crime types, diurnal cycles, locations, weapons, and distinctive z-scores. |
| **Cross-Crime Links** | `api.getCrossCrimeDetail(id)` | `GET /api/cross-crime/{id}` | Inter-category proportions, shared behavioral drivers, and real exemplar incidents. |
| **Behavioral Evolution** | `api.getEvolutionTimeline()` | `GET /api/evolution/timeline` | 12-month empirical trajectories for `is_night`, `has_weapon`, `has_injury`, `has_arrest`, etc. |
| **Novel Behavior** | `api.getAnomalySummary()` | `GET /api/anomaly/summary` | Isolation Forest contamination threshold ($1.0\%$) and score distribution metrics. |
| **Novel Behavior** | `api.getTopOutliers(limit, offset)`| `GET /api/anomaly/outliers?limit={l}` | Top 50 ranked behavioral outliers with nearest cluster distances and unusual feature breakdown. |

---

## 4. Verification & Testing

### 4.1 Automated Test Execution
An automated test suite was constructed in [`tests/api/test_frontend_integration.py`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/tests/api/test_frontend_integration.py) covering the exact request flows of all 8 frontend pages:
```bash
/Users/nare/5th\ SEM/Zero_Spoil/.venv/bin/pytest tests/api/test_frontend_integration.py
```
**Result:** 9 passed in 1.40s.

Across the entire test suite:
```bash
/Users/nare/5th\ SEM/Zero_Spoil/.venv/bin/pytest tests/
```
**Result:** 78 passed in 5.09s (zero failures).

### 4.2 Frontend Production Build
```bash
cd frontend && npm run build
```
- TypeScript compilation: 0 errors
- Vite client bundle: `304.61 kB` (`86.79 kB` gzip)
- Build time: 162ms

---

## 5. Instructions for Running the Complete Connected System

### Step 1: Start Backend API
```bash
/Users/nare/5th\ SEM/Zero_Spoil/.venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
Swagger UI / OpenAPI docs: `http://127.0.0.1:8000/docs`

### Step 2: Start Frontend Application
```bash
cd frontend
npm run dev
```
Open your browser at `http://localhost:5173/`.
The sidebar footer will immediately show:
`Live Engine (2ms) • 220,663 Incidents • 70D DNA`
