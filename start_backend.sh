#!/usr/bin/env bash
# Crime Compass 🧭 — Start Backend FastAPI Server

set -e

# Detect virtual environment
if [ -d ".venv" ]; then
    PYTHON_CMD=".venv/bin/python"
elif [ -d "../Zero_Spoil/.venv" ]; then
    PYTHON_CMD="../Zero_Spoil/.venv/bin/python"
else
    PYTHON_CMD="python3"
fi

echo "=================================================="
echo " Starting Crime Compass 🧭 FastAPI Backend Engine "
echo " Python Interpreter: $PYTHON_CMD                 "
echo "=================================================="

exec "$PYTHON_CMD" -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
