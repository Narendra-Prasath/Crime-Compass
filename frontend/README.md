# Crime Compass 🧭 Frontend Analytics Dashboard

> **"Different Incidents. Shared Behavioral Patterns."**

A modern, high-performance investigative analytics dashboard built with **React**, **TypeScript**, and **Vite**.

---

### Mandatory Legal & Scientific Advisory
> **CRITICAL NOTICE:** Crime Compass analyzes incident characteristics and historical behavioral patterns. Similarity or novelty does not establish offender identity, guilt, or causation.
>
> **Based on patterns learned from historical incidents.**
>
> All analytics, similarities, and patterns displayed are computed strictly by the backend machine learning pipeline on empirical historical incident records without identifying persons, predicting future crimes, evaluating criminality scores, or establishing guilt.

---

## Architecture Overview

```
frontend/
├── index.html                  # HTML entry with tactical Google Fonts (Inter, JetBrains Mono, Outfit)
├── vite.config.ts              # Vite config with /api reverse proxy to http://127.0.0.1:8000
├── tsconfig.json               # Root TS config
├── tsconfig.app.json           # Application TS compiler rules
└── src/
    ├── main.tsx                # React DOM root entry
    ├── App.tsx                 # Core router, responsive sidebar, topbar, and live health monitor
    ├── index.css               # Tactical dark analytics design system (pure CSS tokens, cards, badges)
    ├── types.ts                # TypeScript interfaces matching backend FastAPI Pydantic schemas
    ├── api.ts                  # REST API client wrapping fetch with timeout and error handling
    ├── utils/
    │   └── indiaFormat.ts      # Indian currency (₹), number grouping, date/time, and regional lists
    ├── components/
    │   ├── StateViews.tsx      # Reusable LoadingState, ErrorState, and EmptyState views
    │   ├── DNARadarChart.tsx   # Pure SVG 7-axis radar chart (supports single and dual comparative overlay)
    │   ├── SubprofileBars.tsx  # 7-domain behavioral intensity progress bars
    │   ├── ExplanationCard.tsx # Detailed "Why Similar?" breakdown cards with difference list
    │   └── CrimeDnaResultExperience.tsx # Complete 12-stage interactive behavioral analysis result view
    └── pages/
        ├── HomePage.tsx               # Hero landing with quick navigation and India-ready metrics
        ├── InputAnalysisPage.tsx      # Incident analyzer with India and international location selectors
        ├── OverviewPage.tsx           # Global statistics, archetypes, cross-crime teasers, shifts
        ├── IncidentAnalyzerPage.tsx   # Search/select incident, 70D Behavioral Fingerprint radar, and matches
        ├── SimilarityViewPage.tsx     # Side-by-side incident comparison, dual overlaid radar
        ├── WhySimilarPage.tsx         # Mathematical feature-group similarity & difference breakdown
        ├── BehavioralPatternsPage.tsx # 8 discovered cluster archetypes with behavioral profiles
        ├── CrossCrimePage.tsx         # 8 cross-crime behavioral patterns and category distributions
        ├── BehavioralEvolutionPage.tsx# 12-month diurnal cycle evolution and ANOVA shift tests
        ├── NovelBehaviorPage.tsx      # Top 50 unusual behavioral combinations with anomaly score explanations
        ├── DnaComparisonPage.tsx      # Dedicated pairwise Behavioral Comparison
        ├── BehavioralConnectionMapPage.tsx # Interactive high-dimensional topology map
        └── IncidentHistoryPage.tsx    # Local audit history of analyzed incidents
```

---

## Key Features

1. **Crime Compass 🧭 Incident Analyzer**
   - Country & Region Selector: India (default) and International mode.
   - Comprehensive selection of 28 Indian States and 8 Union Territories.
   - Administrative district, city/town, locality, and optional 6-digit PIN code inputs.
   - Currency display in INR (₹) with Indian number formatting (`1,00,000`).
   - Standard Indian date (`DD/MM/YYYY`) and 12-hour AM/PM time with `Asia/Kolkata` (IST) default.
   - Complete 70-dimensional Behavioral Fingerprint generation in under 10 ms.

2. **Groups of Similar Patterns (Clustering)**
   - 8 distinct behavioral archetypes discovered via K-Means clustering.
   - Prominent modus operandi descriptions, time patterns, location contexts, and weapon types.

3. **Behavioral Similarity & Cross-Crime Connections**
   - High-dimensional cosine similarity indexing across 2,20,663 historical reference cases.
   - Cross-crime pattern discovery linking distinct offenses (e.g., Robbery matching Burglary).

4. **Why These Incidents Are Similar (Explainability)**
   - Normalized feature attribution decomposing similarity into exact additive percentage shares summing to 100%.
   - "Which Details Match" breakdown paired with key operational differences.

5. **Unusual Behavioral Combinations (Novelty Detection)**
   - Dual-paradigm novelty assessment combining cluster centroid distance and Isolation Forest path lengths.

6. **Behavioral Evolution**
   - 12-month temporal timeline and diurnal rhythm analysis.

7. **Incident Analysis History**
   - Local SQLite audit trail of all analyzed incidents with Indian date/time formatting.

---

## Getting Started

### Prerequisites
- Node.js >= 18
- Python virtual environment with FastAPI backend dependencies installed

### 1. Start the Backend API
From the project root directory:
```bash
./start_backend.sh
```
API docs available at: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend Dev Server
From the `frontend/` directory:
```bash
npm run dev
```
Open your browser at `http://localhost:5173/`.

### 3. Production Build
```bash
npm run build
```
Generates a static production bundle in `frontend/dist/`.
