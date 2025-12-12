#!/bin/bash
# Railway startup script
# This runs before the web server starts

set -e  # Exit on error

echo "========================================="
echo "🎭 Railway Startup Script"
echo "========================================="

# Debug: Show Python location
echo "Python location: $(which python3)"
python3 --version

echo ""
echo "🎭 Installing Playwright Chromium browser..."
python3 -m playwright install chromium

echo ""
echo "🗄️  Running database migrations..."
python3 -m alembic upgrade head

echo ""
echo "🚀 Starting web server..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
