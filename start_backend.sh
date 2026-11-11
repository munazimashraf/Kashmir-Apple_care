#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "==================================================="
echo "  Starting Kashmir Apple Care FastAPI Backend API"
echo "==================================================="

# Detect python executable
if [ -x "/usr/local/bin/python3.11" ]; then
    PYTHON_EXE="/usr/local/bin/python3.11"
elif [ -x "$DIR/.venv/bin/python" ]; then
    PYTHON_EXE="$DIR/.venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON_EXE="python3"
else
    PYTHON_EXE="python"
fi

export PYTHONPATH="$DIR/backend"
echo "Using Python: $PYTHON_EXE"
echo "Server URL:   http://127.0.0.1:8000"
echo "Docs URL:     http://127.0.0.1:8000/docs"
echo ""

exec "$PYTHON_EXE" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
