# Multi-stage Dockerfile for production deployment

# Stage 1: Base Python image
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 — Final application image
FROM base AS final

WORKDIR /app

# Copy backend and frontend
COPY backend ./backend
COPY frontend ./frontend

# Ensure backend is treated as a Python module
RUN touch backend/__init__.py

# Expose port 80 for Azure
EXPOSE 80

# Start the app using Gunicorn (must match backend.wsgi:app)
CMD ["gunicorn", "-b", "0.0.0.0:80", "backend.wsgi:app"]