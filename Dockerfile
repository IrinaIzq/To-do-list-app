# Multi-stage Dockerfile for production deployment

# Stage 1: Base image with Python
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies as application

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create data directory for SQLite
RUN mkdir -p /app/data

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port required by Azure App Service
EXPOSE 80

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Production server (Gunicorn)
CMD ["gunicorn", "-b", "0.0.0.0:8000", "backend.wsgi:app"]

