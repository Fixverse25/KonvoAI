# =============================================================================
# EVA-Dev Backend Dockerfile
# Multi-stage build for development and production
# =============================================================================

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# =============================================================================
# Development Stage
# =============================================================================
FROM base as development

# Install development dependencies
RUN pip install watchdog

# Copy application code
COPY . .

# Create non-root user for development
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# Production Stage
# =============================================================================
FROM base as production

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app && \
    chown -R app:app /app && \
    chmod +x /app/scripts/start.sh

USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["./scripts/start.sh"]
