#!/bin/bash
# Railway startup script
# This runs before the web server starts

set -e  # Exit on error

echo "🎭 Installing Playwright Chromium browser..."
playwright install chromium

echo "🗄️  Running database migrations..."
alembic upgrade head

echo "🚀 Starting web server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
