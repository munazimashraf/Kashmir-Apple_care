#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "================================================================="
echo "   KASHMIR APPLE CARE — AI Leaf Disease & SKUAST-K Advisory"
echo "================================================================="
echo ""

# Make sure scripts are executable
chmod +x "$DIR/start_backend.sh" "$DIR/start_frontend.sh" 2>/dev/null || true

# Start backend in background
echo "-> Starting Backend API server on http://127.0.0.1:8000..."
"$DIR/start_backend.sh" &
BACKEND_PID=$!

# Trap Ctrl+C to cleanly kill both services
cleanup() {
    echo ""
    echo "Shutting down Kashmir Apple Care services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Wait 2 seconds for backend to initialize
sleep 2

# Start frontend in background
echo "-> Starting Frontend UI server on http://127.0.0.1:5173..."
"$DIR/start_frontend.sh" &
FRONTEND_PID=$!

sleep 2

# Open browser on macOS
if command -v open &>/dev/null; then
    open "http://127.0.0.1:5173"
fi

echo ""
echo "================================================================="
echo "  AppleCare is RUNNING!"
echo "  • Web Application : http://127.0.0.1:5173"
echo "  • Backend API Docs: http://127.0.0.1:8000/docs"
echo "  Press CTRL+C anytime to stop both services."
echo "================================================================="
echo ""

# Keep running
wait
