import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.database import db, init_models
from backend.config import get_config
from backend.routes import create_routes
from backend.services.auth_service import AuthService
from backend.services.task_service import TaskService
from backend.services.category_service import CategoryService
from sqlalchemy import text


def create_app(config_name=None):
    """Application factory pattern - create and configure the Flask app"""
    config_name = config_name or os.getenv("FLASK_ENV", "production")
    config_class = get_config(config_name)

    app = Flask(__name__, static_folder="../frontend")
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, origins="*")
    init_models()

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✓ Database tables created successfully")
        except Exception as e:
            print(f"✗ Error creating database tables: {e}")

    # Create services
    auth_service = AuthService(
        secret_key=app.config["SECRET_KEY"],
        algorithm=app.config["JWT_ALGORITHM"],
        expiration_hours=app.config["JWT_EXPIRATION_HOURS"],
    )
    task_service = TaskService()
    category_service = CategoryService()

    # Register blueprints
    app.register_blueprint(create_routes(auth_service, task_service, category_service))

    # Static file route
    @app.route("/")
    def index():
        return send_from_directory("../frontend", "index.html")

    # Health check route
    @app.route("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            db_status = "healthy"
            status = "healthy"
        except Exception as e:
            db_status = f"degraded: {str(e)}"
            status = "degraded"
        return {
            "status": status,
            "database": db_status,
            "version": app.config["APP_VERSION"]
        }

    return app


# Only run when executing this file directly (not during imports/tests)
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)