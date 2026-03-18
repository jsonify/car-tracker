#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cleanup() {
  echo ""
  echo "Shutting down..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting Car Tracker Dashboard..."

# Backend: FastAPI via uvicorn
cd "$ROOT_DIR"
uv run uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
echo "  Backend PID $BACKEND_PID → http://127.0.0.1:8000"

# Frontend: Vite dev server
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "  Frontend PID $FRONTEND_PID → http://localhost:5173"

echo ""
echo "Press Ctrl+C to stop both servers."
wait
