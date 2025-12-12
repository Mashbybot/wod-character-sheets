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
echo "🎭 Installing system dependencies for Chromium..."
apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2t64 \
    libatspi2.0-0 \
    libxshmfence1 \
    --no-install-recommends

echo ""
echo "🎭 Installing Playwright Chromium browser..."
python3 -m playwright install chromium

echo ""
echo "🗄️  Running database migrations..."
python3 migrate.py

echo ""
echo "🚀 Starting web server..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
