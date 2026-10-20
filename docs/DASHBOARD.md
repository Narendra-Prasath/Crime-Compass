# CRIME DNA — Dashboard Architecture & Specification

## 1. Executive Summary

Phase 12 delivers a professional, desktop-first, modern investigative analytics dashboard for **CRIME DNA** located in the `frontend/` directory.

- **Application Title:** CRIME DNA
- **Tagline:** *"Different Crimes. Same Behavioral DNA."*
- **Technology Stack:** React 19, TypeScript, Vite 8, Lucide React, Pure SVG Visualizations, Native CSS Design System.
- **Backend Integration:** Connects seamlessly to the FastAPI production API developed in Phase 11.
- **Mandatory Ethical Standard:** *The application analyzes behavioral similarity between incidents. It does NOT identify offenders or determine guilt.* This banner is permanently anchored across all application views.

---

## 2. Design System & User Interface Principles

### 2.1 Aesthetic & Visual Identity
The dashboard adopts a modern, tactical dark theme engineered for investigative clarity:
- **Palette Tokens:**
  - Background Canvas: `hsl(222, 47%, 7%)` (#090d16)
  - Sidebar Surface: `hsl(222, 47%, 9%)` (#0d131f)
  - Card & Container Surface: `hsl(217, 33%, 12%)` (#141c2b)
  - Primary Accent (Cyan): `hsl(199, 89%, 48%)` (#0ea5e9)
  - Secondary Accent (Teal / Emerald): `hsl(160, 84%, 39%)` (#10b981)
  - Warning Accent (Amber): `hsl(38, 92%, 50%)` (#f59e0b)
  - Highlight Accent (Purple): `hsl(258, 90%, 66%)` (#8b5cf6)
- **Typography:**
  - Headings: *Outfit* (Modern geometric sans-serif)
  - Data / Body: *Inter* (High-legibility interface font)
  - Identifiers / Metrics: *JetBrains Mono* (Clean tabular monospace)
- **No Sensational Imagery:** No gratuitous crime-scene photographs, red emergency flashers, or sensational badges. All iconography uses crisp, neutral stroke icons from `lucide-react`.
- **Zero Fake Statistics:** Every single metric, count, percentage, and coordinate rendered on the screen is parsed directly from the live FastAPI backend.

---

## 3. Implemented Views & Feature Breakdown

| View | Component File | Key Capabilities |
| :--- | :--- | :--- |
| **1. Overview Dashboard** | [`OverviewPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/OverviewPage.tsx) | Live KPI stat cards (186,881 records, 70D vector space, 8 clusters, 8 cross-crime patterns, 1,869 outliers); cluster distribution preview; high-confidence cross-crime teaser; temporal shift alerts. |
| **2. Incident Analyzer** | [`IncidentAnalyzerPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/IncidentAnalyzerPage.tsx) | Instant lookup by incident ID or preset chip; administrative metadata; pure SVG 7-axis Behavioral DNA radar chart; top active trait badges; similar incident retrieval with direct jump to Comparison. |
| **3. Similarity View** | [`SimilarityViewPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/SimilarityViewPage.tsx) | Side-by-side incident comparison; dual overlaid radar charts showing behavioral alignment and variance; subprofile domain similarity bars; one-click transition to mathematical explanation. |
| **4. "Why Similar?"** | [`WhySimilarPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/WhySimilarPage.tsx) | Mathematical feature-group attribution; group contribution percentage breakdown; ranking of similarity drivers; behavioral divergence callout; plain-English summary generator. |
| **5. Behavioral Patterns** | [`BehavioralPatternsPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/BehavioralPatternsPage.tsx) | Archetype selector across all 8 clusters; incident count and population shares; dominant crime types, diurnal cycles, locations, weapons, and harm context; top distinctive feature z-score table. |
| **6. Cross-Crime Links** | [`CrossCrimePage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/CrossCrimePage.tsx) | 8 cross-crime behavioral patterns; category composition progress bars; dominant shared traits; exemplar incidents with drill-down links. |
| **7. Behavioral Evolution** | [`BehavioralEvolutionPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/BehavioralEvolutionPage.tsx) | 12-month temporal timeline; stacked diurnal cycle bar chart (Night, Day, Weekend, Weekday); ANOVA $F$-statistic shifts ($p < 0.001$). |
| **8. Novel Behavior** | [`NovelBehaviorPage.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/pages/NovelBehaviorPage.tsx) | Strict neutral terminology banner; Isolation Forest anomaly score distribution; top 50 behavioral outliers with nearest cluster distances and unusual feature breakdown. |

---

## 4. Visual Components

### 4.1 Pure SVG 7-Axis DNA Radar Chart ([`DNARadarChart.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/components/DNARadarChart.tsx))
To eliminate heavy external charting dependencies and guarantee instantaneous 60fps rendering, the 7-axis Behavioral DNA radar chart was built directly in SVG:
- Computes polar-to-cartesian projection $(r \cos \theta, r \sin \theta)$ for:
  1. `time` (Temporal rhythm)
  2. `crime` (Statutory crime characteristics)
  3. `location` (Spatial & facility context)
  4. `method` (Operational method & weapon)
  5. `people` (Victim & offender demographics)
  6. `property` (Economic target & valuation)
  7. `context` (Harm, injury, drugs, and arrest)
- Supports single-incident mode and comparative dual-incident mode with contrasting cyan and amber polygons.

### 4.2 State Views ([`StateViews.tsx`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/components/StateViews.tsx))
All views feature:
- **`LoadingState`**: Smooth CSS spinner with descriptive investigative status text.
- **`ErrorState`**: Clear diagnostic error box with retry button and connection advice.
- **`EmptyState`**: Neutral prompt when no records or matches are found.

---

## 5. Reverse Proxy & API Client

In [`frontend/vite.config.ts`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/vite.config.ts), Vite's dev server proxies `/api` calls directly to FastAPI on `http://127.0.0.1:8000`:
```ts
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      secure: false,
    },
  },
}
```
In [`frontend/src/api.ts`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/frontend/src/api.ts), a centralized `ApiClient` handles requests with timeout bounds, network retry helpers, and strict schema deserialization into TypeScript types.

---

## 6. How to Run the Complete Stack

### Step 1: Start Backend API
```bash
/Users/nare/5th\ SEM/Zero_Spoil/.venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
Swagger UI will be live at: `http://127.0.0.1:8000/docs`

### Step 2: Start Frontend Web Dashboard
```bash
cd frontend
npm run dev
```
Open browser at `http://localhost:5173/`.
The live latency and connection status will immediately show in both the sidebar footer and topbar.

### Step 3: Production Build
```bash
cd frontend
npm run build
```
Creates an optimized static bundle in `frontend/dist/`.
