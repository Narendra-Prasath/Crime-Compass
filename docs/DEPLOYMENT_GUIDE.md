# Crime Compass 🧭 — Production Deployment & Operations Guide

**Document:** `docs/DEPLOYMENT_GUIDE.md`  
**System:** Crime Compass 🧭 (Machine Learning Behavioral Intelligence System)  
**Classification:** Production Operations Runbook  
**Last Updated:** October 2026  

---

## 1. Executive Summary & Architecture Selection

Crime Compass 🧭 consists of two layers:
1. **Python 3.11+ FastAPI Backend:** Preloads a 70D Behavioral DNA matrix, Cosine Nearest Neighbors index, 8 Spherical K-Means clusters, and Isolation Forest anomaly models across **2,20,663 historical incidents** (~600 MB resident memory footprint).
2. **React 19 + TypeScript + Vite Frontend:** Client-side SPA featuring Mode 1 Single Incident Analysis, Mode 2 Dataset Analysis, Behavioral Comparison, Connection Map, and India localization (₹ INR, IST).

### Recommended Hosting Arrangement

| Layer | Recommended Host | Runtime / Tier | Purpose |
|:---|:---|:---|:---|
| **Backend API** | **Render** (or **Railway**) | Python / Docker (1 GB RAM Starter) | Serves REST API and hosts pre-trained ML models in-memory with sub-10ms latency. |
| **Frontend** | **Vercel** | Node 20 / Vite Edge CDN | Delivers fast global SPA loading and handles client routing with zero server overhead. |

> [!IMPORTANT]
> **RAM Sizing Requirement:** The backend requires **at least 1 GB RAM** at startup to load the 2.2L incident similarity index (`knn_index.joblib`), vector matrix (`normalized_dna_matrix.npy`), and anomaly scores. Free hosting tiers restricted to 512 MB (such as Render Free) will experience Out-Of-Memory (OOM) crashes during startup. Select the **Starter (1 GB)** tier on Render or deploy on **Railway** / **Hugging Face Spaces**.

---

## 2. Step 1: Push Codebase to GitHub

Both Render and Vercel use Git-based continuous deployment.

1. **Initialize GitHub Remote:**
   Create a new private or public repository on GitHub (e.g. `crime-compass`).

2. **Commit and Push:**
   In your terminal inside `/Users/nare/5th SEM/Crime_DNA-ML/Crime-DNA`:
   ```bash
   git add .
   git commit -m "feat: prepare Crime Compass for production deployment"
   git branch -M main
   git remote add origin https://github.com/<your-username>/crime-compass.git
   git push -u origin main
   ```

   *(Note: Model files in `data/processed/` are under 100 MB each and will be pushed cleanly to GitHub. `crime_dna_ml.csv` is excluded via `.gitignore`.)*

---

## 3. Step 2: Deploy the Backend API First (Render)

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** $\to$ **Web Service**.
3. Select **Build and deploy from a Git repository** and connect your `crime-compass` repo.
4. Configure the service settings:
   - **Name:** `crime-compass-api`
   - **Region:** Any (e.g. `Oregon (US West)` or `Frankfurt (EU)`)
   - **Branch:** `main`
   - **Root Directory:** *(leave blank)*
   - **Runtime:** `Python 3` (or choose `Docker` to use the multi-stage `Dockerfile`)
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 1
     ```
   - **Instance Type:** **Starter ($7/mo - 1 GB RAM)** *(required for 2.2L records)*.

5. **Configure Backend Environment Variables:**
   Under **Environment Variables**, add:
   ```env
   PYTHON_VERSION = 3.11.8
   DEBUG = 0
   CORS_ORIGINS = *
   HOST = 0.0.0.0
   ```
   *(Note: We set `CORS_ORIGINS=*` temporarily until the frontend is deployed in Step 3).*

6. Click **Deploy Web Service**.
7. Monitor the build logs. You will see:
   ```log
   CRIME DNA Application State successfully initialized in 2.5s.
   All ML components successfully loaded.
   Uvicorn running on http://0.0.0.0:<PORT>
   ```
8. **Verify Backend Health:**
   Once deployment status is **Live**, copy your Render URL (e.g. `https://crime-compass-api.onrender.com`).
   Run in your terminal:
   ```bash
   curl -s https://crime-compass-api.onrender.com/healthz
   ```
   Expected response:
   ```json
   {"status":"ok","ready":true}
   ```
   And verify the API catalog:
   ```bash
   curl -s https://crime-compass-api.onrender.com/api
   ```

---

## 4. Step 3: Deploy the Frontend (Vercel)

1. Log in to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** $\to$ **Project**.
3. Import your `crime-compass` repository.
4. Configure Project Settings:
   - **Project Name:** `crime-compass`
   - **Framework Preset:** `Vite` (automatically detected)
   - **Root Directory:** Click Edit and select `frontend`
   - **Build Command:** `npm run build` (or `tsc -b && vite build`)
   - **Output Directory:** `dist`
5. **Configure Frontend Environment Variables:**
   Under **Environment Variables**, add:
   ```env
   VITE_API_BASE_URL = https://crime-compass-api.onrender.com/api
   ```
   *(Replace with your actual Render backend URL obtained in Step 2, appending `/api`)*.
6. Click **Deploy**.
7. Vercel will build the frontend in ~20-30 seconds and provide a production URL:
   `https://crime-compass.vercel.app` (or similar).

---

## 5. Step 4: Lock Down CORS on the Backend

Now that your official frontend URL is established:

1. Return to [Render Dashboard](https://dashboard.render.com) $\to$ `crime-compass-api` $\to$ **Environment**.
2. Update the `CORS_ORIGINS` variable:
   ```env
   CORS_ORIGINS = https://crime-compass.vercel.app
   ```
   *(If you have a custom domain, include it separated by comma: `https://crime-compass.vercel.app,https://crimecompass.org`)*.
3. Render will automatically redeploy the service with restricted production CORS and credentials enabled.

---

## 6. Step 5: End-to-End System Verification Checklist

Open `https://crime-compass.vercel.app` in your browser and verify:

1. [ ] **Home Page & Stats:** Incident counter loads `2,20,663` incidents, 70 Behavioral DNA features, and 8 clusters.
2. [ ] **Direct URL Entry:** Refreshing or navigating directly to `/compare`, `/patterns`, `/connection-map`, `/history`, or `/incident-analyzer` loads the full React page without 404/405 errors.
3. [ ] **Mode 1 Single Incident Analysis:** Fill in a test incident on `/input-analysis` and verify the radar chart (7 Domain Energies), cluster assignment, and top matches render.
4. [ ] **Mode 2 Analyze My Dataset:** Upload a sample CSV (e.g. `data/dataset_analyses/sample.csv`) on `/input-analysis` and confirm column mapping, cluster distribution, and outlier detection work.
5. [ ] **Behavioral Comparison:** Test `/compare` with two preset incidents and verify side-by-side DNA alignment.
6. [ ] **Explainable AI (XAI):** Open an incident match and verify feature-level dot-product contributions ($\Delta$).

---

## 7. Alternative: 1-Click Unified Container on Railway

If you prefer deploying a **single unified service** (one domain hosting both frontend and backend):

1. Log in to [Railway](https://railway.app).
2. Click **New Project** $\to$ **Deploy from GitHub repo**.
3. Select `crime-compass`. Railway will automatically detect the production [`Dockerfile`](file:///Users/nare/5th%20SEM/Crime_DNA-ML/Crime-DNA/Dockerfile).
4. In Railway project settings:
   - **Resources:** Set memory limit to at least **1 GB** (or 2 GB).
   - **Networking:** Click **Generate Domain**.
5. Railway builds the React frontend in Stage 1, sets up FastAPI in Stage 2, and serves both from one URL:
   `https://crime-compass-production.up.railway.app`.
   - Web app: `https://crime-compass-production.up.railway.app/`
   - API Docs: `https://crime-compass-production.up.railway.app/docs`
   - Healthcheck: `https://crime-compass-production.up.railway.app/healthz`

---

## 8. Rollback & Troubleshooting Procedures

### 8.1 Rollback Instructions

- **Vercel Frontend Rollback:**
  1. Go to Vercel Dashboard $\to$ **Deployments**.
  2. Locate the previous working deployment.
  3. Click the three dots ($\dots$) $\to$ **Instant Rollback**.
- **Render Backend Rollback:**
  1. Go to Render Dashboard $\to$ `crime-compass-api` $\to$ **Events**.
  2. Click on the commit hash of the previous deployment $\to$ **Rollback to this version**.

### 8.2 Common Operational Issues & Fixes

| Symptom | Probable Cause | Exact Solution |
|:---|:---|:---|
| **Backend crash with exit code 137** | Out of Memory (OOM) | Instance has only 512 MB RAM. Upgrade Render service to **Starter (1 GB)** or Railway to **1 GB+**. |
| **CORS error in browser console** | Origin mismatch | Verify `CORS_ORIGINS` on Render matches the exact Vercel URL (including `https://` and without trailing slash). |
| **Frontend shows "Unable to connect to backend"** | Backend asleep or cold | Free tier web services sleep after 15 min of inactivity. Upgrade to Starter or allow 30s for spin-up. |
| **Dataset upload rejects file** | Unapproved extension or binary content | Ensure file ends with `.csv`, `.tsv`, `.txt`, or `.xlsx` and is under 15 MB. |
