"""
Main Flask application
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import logging
from datetime import datetime
from sqlalchemy import text

from backend.database import db, init_models
from backend.config import get_config
from backend.routes import create_routes
from backend.services.auth_service import AuthService
from backend.services.task_service import TaskService
from backend.services.category_service import CategoryService
from backend.models.user import User
from backend.models.task import Task
from backend.models.category import Category


def create_app(config_name=None):
    # Detect environment (Azure uses production)
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "production")

    # The static folder is disabled; we serve frontend manually
    app = Flask(__name__, static_folder=None)

    # Load config
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)

    # Enable CORS for frontend consumption
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Prometheus metrics (optional)
    if not app.config.get("TESTING", False):
        try:
            metrics = PrometheusMetrics(app)
            metrics.info("app_info", "Application info", version=app.config["APP_VERSION"])
        except Exception as e:
            app.logger.warning(f"Prometheus init failed: {e}")

    # Services initialization
    auth_service = AuthService(
        secret_key=app.config["SECRET_KEY"],
        algorithm=app.config["JWT_ALGORITHM"],
        expiration_hours=app.config["JWT_EXPIRATION_HOURS"]
    )
    task_service = TaskService()
    category_service = CategoryService()

    # API routes (prefix: /api/*)
    app.register_blueprint(create_routes(auth_service, task_service, category_service))

    # Health check route
    @app.route("/health")
    def health_check():
        try:
            db.session.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        return jsonify({
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": app.config["APP_VERSION"],
            "database": db_status,
            "environment": config_name
        })

    # Serve frontend index.html
    @app.route("/", methods=["GET"])
    def serve_frontend():
        frontend_path = os.path.join(app.root_path, "..", "frontend")
        return send_from_directory(frontend_path, "index.html")

    # Serve frontend static files (CSS, JS)
    @app.route("/static/<path:filename>")
    def frontend_static(filename):
        frontend_path = os.path.join(app.root_path, "..", "frontend")
        return send_from_directory(frontend_path, filename)

    # Logging
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    return app


# Global app instance for Gunicorn
app = create_app(os.environ.get("FLASK_ENV", "production"))


def init_database(app_instance):
    with app_instance.app_context():
        db.create_all()


if __name__ == "__main__":
    init_database(app)
    app.run(host="0.0.0.0", port=80)
