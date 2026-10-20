# syntax=docker/dockerfile:1
# ----------------------------------------------------------------------------
# CRIME COMPASS 🧭 — Multi-stage Production Dockerfile
# Stage 1: Build React/Vite Frontend
# Stage 2: Fast, Slim Python 3.11 Backend Runner with Unified Static Serving
# ----------------------------------------------------------------------------

# --- Stage 1: Frontend Build ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Production Python Backend & Unified App ---
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    DEBUG=0

# Install minimal OS dependencies for health checks and fast I/O
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code and config
COPY src/ ./src/

# Copy pre-trained models, indices, and processed datasets
# Required for zero-retraining instant startup
COPY data/processed/ ./data/processed/

# Copy compiled frontend from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose default port (overridden dynamically by hosting platforms via $PORT)
EXPOSE 8000

# Healthcheck targeting lightweight endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/healthz || exit 1

# Start Uvicorn bound to dynamic $PORT
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --timeout-keep-alive 65"]
