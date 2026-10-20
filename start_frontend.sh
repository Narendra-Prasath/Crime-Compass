#!/usr/bin/env bash
# Crime Compass 🧭 — Start Frontend Dashboard

set -e

cd "$(dirname "$0")/frontend"

echo "=================================================="
echo " Starting Crime Compass 🧭 React / Vite Frontend  "
echo " URL: http://localhost:5173                       "
echo "=================================================="

exec npm run dev
