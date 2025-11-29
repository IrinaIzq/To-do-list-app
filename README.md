# To-Do List Manager

![CI/CD Pipeline](https://github.com/IrinaIzq/To-do-list-app/actions/workflows/ci-cd.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/badge/license-Educational-orange)

A simple task manager application that allows users to create, organize, and prioritize tasks.  
Each task includes a title, description, category, due date, estimated hours, and status.  
The app is built with **Python (Flask) for the backend**, **SQLite for persistent storage**, and **HTML/CSS/JavaScript for the frontend**.  

---

## Features
- Complete CRUD operations for tasks and categories
- JWT-based authentication
- Prometheus metrics and Grafana dashboards
- Fully containerized with Docker
- Automated CI/CD pipeline
- Comprehensive test coverage (>70%)
- Health check endpoints
- SOLID principles and clean architecture
- **Live Demo**: https://irina-todoapp-backend-eug6ghdxh2cra6du.westeurope-01.azurewebsites.net  ← AÑADIR ESTO

---

## Table of Contents

1. Quick Start
2. Development Setup
3. Testing
4. Docker Deployment
5. CI/CD Pipeline
6. Monitoring
7. API Documentation
8. Architecture

---

## 1. Prerequisites

Python 3.10+
Docker & Docker Compose (for containerized deployment)
Git

Running with Docker (Recommended)
````bash
# Clone the repository
https://github.com/IrinaIzq/To-do-list-app.git
cd todo-list-app

# Create environment file
cp .env.example .env

# Start all services (app + monitoring)
docker-compose up -d

# Access the services:
# - Application: http://localhost:5000
# - Frontend: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
````

## 2. Deployed Application

**Live URL**: https://irina-todoapp-backend-eug6ghdxh2cra6du.westeurope-01.azurewebsites.net

**Quick Test:**
1. Visit the live URL
2. Click "Register" to create an account
3. Login with your credentials
4. Create a category (e.g., "Work")
5. Create a task and test the status buttons (Start → Complete)

**Health Check**: https://irina-todoapp-backend-eug6ghdxh2cra6du.westeurope-01.azurewebsites.net/health

---

## 3. Development Setup
### a. Clone and Setup Virtual Environment
````bash
https://github.com/IrinaIzq/To-do-list-app.git
cd todo-list-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
````

### b. Configure Environment Variables
Create a .env file in the root directory:
````bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///tasks.db

# Note: For Azure deployment, use sqlite:///:memory: due to ephemeral storage

# JWT Configuration
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
````

### c. Initialize database
````bash
cd backend
python app.py
# Database will be created automatically on first run
````

### d.  Run the Application
Terminal 1 - Backend:
````bash
cd backend
python app.py
# Backend running on http://127.0.0.1:5000
````

Terminal 2 - Frontend:
````bash
cd frontend
python -m http.server 8000
# Frontend running on http://localhost:8000
````

---

## 4. Testing
### a. Run All Tests
````bash
# Run all tests with coverage
pytest tests/ --cov=backend --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
````

### b. Run Specific Test Categories
````bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Test a specific file
pytest tests/unit/test_auth_service.py -v

# Run tests with detailed output
pytest -vv --tb=short
````

### c. Code Quality Checks
````bash
# Format code with Black
black backend/ tests/

# Sort imports with isort
isort backend/ tests/

# Run linter
flake8 backend/ tests/ --max-line-length=100

# Run all quality checks
black --check backend/ tests/ && \
isort --check-only backend/ tests/ && \
flake8 backend/ tests/ --max-line-length=100
````

---

## 5. Docker Deployment
### a. Build and Run
````bash
# Build the image
docker build -t todo-app:latest .

# Run the container
docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e FLASK_ENV=production \
  --name todo-app \
  todo-app:latest

# View logs
docker logs -f todo-app

# Stop container
docker stop todo-app
````

### b. Using Docker Compose
````bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
````

### c. Multi-Stage Build Benefits
- Smaller final image size
- Separate build and runtime dependencies
- Better layer caching
- Non-root user for security

---

## 6. CI/CD Pipeline
The project uses GitHub Actions for automated CI/CD:
### a. Pipeline Stages
- Lint - Code quality checks (Black, isort, Flake8)
- Test - Run tests with >70% coverage requirement
- Build - Build and push Docker image
- Deploy - Automatic deployment to production (main branch only)

### b. Pipeline Triggers
- Push to main or develop branches
- Pull requests to main

### c. Viewing Pipeline Status
````bash
# View pipeline runs
https://github.com/IrinaIzq/To-do-list-app/actions

# Pipeline badge
![CI/CD Pipeline](https://github.com/IrinaIzq/To-do-list-app/actions/workflows/ci-cd.yml/badge.svg)
````

---

## 7. Monitoring
### a. Health Check Endpoint
````bash
curl http://localhost:5000/health

# Response:
{
  "status": "healthy",
  "timestamp": "2025-11-06T10:30:00",
  "version": "2.0.0",
  "database": "healthy",
  "environment": "production"
}
````

### b. Prometheus Metrics
**Note**: Prometheus metrics collection is currently configured but not active in the Azure deployment due to in-memory database limitations. The configuration is available in `monitoring/prometheus.yml` for local Docker Compose deployment.

**For Local Development with Docker Compose:**
Access metrics at: http://localhost:5000/metrics
Key Metrics Tracked:
- flask_http_request_total - Total HTTP requests by method, endpoint, status
- flask_http_request_duration_seconds - Request latency
- flask_http_request_exceptions_total - Exception count
- process_resident_memory_bytes - Memory usage
- process_cpu_seconds_total - CPU usage

Grafana Dashboards
- Access Grafana: http://localhost:3000
- Login: admin / admin (change on first login)
- Navigate to Dashboards → Browse
- Select "To-Do App Dashboard"

Dashboard Panels:
- Request rate by endpoint
- Error rate (4xx, 5xx)
- Response time percentiles (p50, p95, p99)
- Active connections
- Memory and CPU usage

---

## 8. API Documentation
### a. Authentication
Register User:
````bash
POST /register
Content-Type: application/json

{
  "username": "user123",
  "password": "secure_password"
}
````

Login
````bash
POST /login
Content-Type: application/json

{
  "username": "user123",
  "password": "secure_password"
}

Response: { "token": "eyJ0..." }
````

### b. Categories
All category endpoints require authentication header:
Authorization: Bearer <token>

Get all categories:
````http
GET /categories
````

Create category:
````http
POST /categories
Content-Type: application/json

{
  "name": "Work",
  "description": "Work-related tasks"
}
````

Update category:
````http
PUT /categories/{id}
Content-Type: application/json

{
  "name": "Personal",
  "description": "Personal tasks"
}
````

Delete category:
````http
DELETE /categories/{id}
````

### c. Tasks
Get all tasks:
````http
GET /tasks
````

Tasks are automatically sorted by:
- Due Date (earliest first)
- Priority (High → Medium → Low)
- Estimated Hours (highest first)

Create task:
````http
POST /tasks
Content-Type: application/json

{
  "title": "Complete report",
  "description": "Q4 financial report",
  "category_name": "Work",
  "due_date": "2025-12-31",
  "estimated_hours": 5.0,
  "priority": "High"
}
````

Update task:
````http
PUT /tasks/{id}
Content-Type: application/json

{
  "title": "Updated title",
  "status": "Completed"
}
````

Delete task:
````http
DELETE /tasks/{id}
````

---

## 9. Architecture
### a. Tech Stack
- **Backend:** Python (Flask), Flask-SQLAlchemy, Flask-CORS, PyJWT
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Version Control:** Git & GitHub

---

### b. Project Structure
todo-list-app/
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # CI/CD pipeline
├── backend/
│   ├── services/               # Business logic (SOLID)
│   │   ├── auth_service.py
│   │   ├── task_service.py
│   │   └── category_service.py
│   ├── app.py                  # Application factory
│   ├── config.py               # Configuration management
│   ├── database.py             # Database models
│   └── routes.py               # API routes
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── scripts.js
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # Pytest fixtures
├── monitoring/
│   ├── prometheus.yml          # Prometheus config
│   └── grafana-dashboard.json  # Grafana dashboard
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Complete stack
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── .env.example                # Environment template
├── REPORT.md                   # Assignment report
└── README.md                   # This file

### c. Design Principles
SOLID Principles:
- Single Responsibility: Each service handles one domain
- Open/Closed: Services are extensible without modification
- Liskov Substitution: Proper inheritance hierarchies
- Interface Segregation: Focused service interfaces
- Dependency Inversion: Dependency injection in routes

Clean Architecture:
- Separation of concerns (routes → services → models)
- Business logic in services, not routes
- Centralized error handling
- Configuration management

---

## License
This project is for educational purposes.
