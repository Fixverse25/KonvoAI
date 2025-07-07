#!/bin/bash

# =============================================================================
# EVA-Dev Backend Production Startup Script
# =============================================================================

set -e

echo "Starting EVA-Dev Backend..."

# Check if running in production
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in production mode"
    
    # Use Gunicorn for production
    exec gunicorn app.main:app \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 30 \
        --keep-alive 2 \
        --log-level info \
        --access-logfile - \
        --error-logfile -
else
    echo "Running in development mode"
    
    # Use Uvicorn for development
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level info
fi
