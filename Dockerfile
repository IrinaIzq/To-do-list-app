# Base image
FROM python:3.10-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code only
COPY backend/ ./backend/

# Expose the port Azure expects
EXPOSE 8000

# Use Gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:80", "wsgi:app"]

