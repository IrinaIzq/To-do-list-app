# Stage 1: base
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Stage final
FROM base AS final
WORKDIR /app

COPY backend ./backend
COPY frontend ./frontend
# ensure package
RUN touch backend/__init__.py

EXPOSE 80

# Use gunicorn to run the wsgi app
CMD ["gunicorn", "-b", "0.0.0.0:80", "backend.wsgi:app"]