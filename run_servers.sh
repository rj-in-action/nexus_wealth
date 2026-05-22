#!/usr/bin/env bash
# Nexus Wealth — startup script for macOS / Linux
set -e

BACKEND_PORT=8000
FRONTEND_PORT=3000
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Checking for existing servers on ports $BACKEND_PORT and $FRONTEND_PORT..."
for port in $BACKEND_PORT $FRONTEND_PORT; do
    pid=$(lsof -ti tcp:$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo "   Stopping process $pid on port $port"
        kill -9 $pid 2>/dev/null || true
    fi
done

# ─── Backend ───────────────────────────────────────────────────────────────
echo "🚀 Starting backend on port $BACKEND_PORT..."
cd "$SCRIPT_DIR/backend"

if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv and install deps if needed
source .venv/bin/activate
pip install -q -r requirements.txt

uvicorn main:app --reload --port $BACKEND_PORT &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# ─── Frontend ──────────────────────────────────────────────────────────────
echo "🌐 Starting frontend on port $FRONTEND_PORT..."
cd "$SCRIPT_DIR/frontend"
python3 -m http.server $FRONTEND_PORT &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# ─── Open browser ─────────────────────────────────────────────────────────
sleep 1
URL="http://127.0.0.1:$FRONTEND_PORT/index.html"
echo "🖥  Opening $URL"
if command -v open &>/dev/null; then
    open "$URL"           # macOS
elif command -v xdg-open &>/dev/null; then
    xdg-open "$URL"       # Linux
fi

echo ""
echo "✅ Servers running. Press Ctrl+C to stop."
wait
