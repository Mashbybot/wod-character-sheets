#!/bin/bash
# Startup script for Railway - runs migrations then starts the app

set -e  # Exit on error

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
