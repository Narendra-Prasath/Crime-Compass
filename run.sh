#!/usr/bin/env bash
# ==============================================================================
# Crime Compass 🧭 — All-in-One Application Launcher
# Starts both FastAPI Backend (port 8000) and React Frontend (port 5173).
# Pressing Ctrl+C gracefully terminates both processes.
# ==============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 1. Resolve Python interpreter
if [ -d ".venv" ]; then
    PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
elif [ -d "../Zero_Spoil/.venv" ]; then
    PYTHON_CMD="$PROJECT_ROOT/../Zero_Spoil/.venv/bin/python"
else
    PYTHON_CMD="python3"
fi

echo "=========================================================="
echo "          🧭 STARTING CRIME COMPASS APPLICATION           "
echo "=========================================================="
echo " Python:   $PYTHON_CMD"
echo " Backend:  http://127.0.0.1:8000  (API & Swagger Docs)"
echo " Frontend: http://localhost:5173  (Web Dashboard)"
echo "=========================================================="

# Cleanup handler on exit or Ctrl+C
cleanup() {
    echo ""
    echo "=========================================================="
    echo " Shutting down Crime Compass 🧭 processes..."
    echo "=========================================================="
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    wait 2>/dev/null || true
    echo " All processes stopped cleanly."
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 2. Launch Backend in background
echo "[1/2] Launching Backend Engine..."
"$PYTHON_CMD" -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend models to initialize..."
BACKEND_HEALTHY=false
for i in {1..30}; do
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "❌ [ERROR] Backend process terminated unexpectedly during startup."
        exit 1
    fi
    if curl -s http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
        echo " Backend is ONLINE and healthy!"
        BACKEND_HEALTHY=true
        break
    fi
    sleep 0.5
done

if [ "$BACKEND_HEALTHY" != "true" ]; then
    echo "⚠️ Warning: Backend did not respond within 15 seconds. Proceeding..."
fi

# 3. Launch Frontend in foreground
echo "[2/2] Launching React Dashboard..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo "=========================================================="
echo " 🧭 Crime Compass is now LIVE:"
echo "    👉 Dashboard: http://localhost:5173"
echo "    👉 API Docs:  http://localhost:8000/docs"
echo "    (Press Ctrl+C to stop both)"
echo "=========================================================="

# Wait for background processes
wait "$BACKEND_PID" "$FRONTEND_PID"
