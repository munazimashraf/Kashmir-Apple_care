#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "==================================================="
echo "  Starting Kashmir Apple Care Vite Frontend UI"
echo "==================================================="
echo "Frontend URL: http://127.0.0.1:5173"
echo ""

exec npm run dev -- --host 127.0.0.1 --port 5173
