#!/usr/bin/env bash
# ==============================================================================
# CRIME DNA — Universal Link Generator (Powered by Cloudflare)
# Exposes the frontend + backend securely over HTTPS to anyone worldwide.
# ==============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [ ! -f "$PROJECT_ROOT/bin/cloudflared" ]; then
    echo "❌ Cloudflare Tunnel binary not found. Please ensure bin/cloudflared exists."
    exit 1
fi

echo "=========================================================="
echo "       🧬 CRIME DNA — UNIVERSAL LINK GENERATOR            "
echo "=========================================================="
echo " • Make sure './run.sh' is active in another terminal."
echo " • Copy the 'https://...trycloudflare.com' link below."
echo " • Share it with your mentor & friends for full access!"
echo " • Press Ctrl+C anytime to stop sharing."
echo "=========================================================="
echo ""

exec "$PROJECT_ROOT/bin/cloudflared" tunnel --url http://localhost:5173
