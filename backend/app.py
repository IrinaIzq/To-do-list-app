import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from backend.database import db, init_models
from backend.config import get_config
from backend.routes import create_routes
from backend.services.auth_service import AuthService
from backend.services.task_service import TaskService
from backend.services.category_service import CategoryService
from sqlalchemy import text


def create_app(config_name=None):
    config_name = config_name or os.getenv("FLASK_ENV", "production")
    config_class = get_config(config_name)

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure static folder
    # In Docker, frontend is at /app/frontend
    # In local dev, frontend is at ../frontend
    if os.path.exists("/app/frontend"):
        app.static_folder = "/app/frontend"
    else:
        app.static_folder = os.path.join(os.path.dirname(__file__), "../frontend")

    db.init_app(app)
    CORS(app, origins="*")
    init_models()

    auth_service = AuthService(
        secret_key=app.config["SECRET_KEY"],
        algorithm=app.config["JWT_ALGORITHM"],
        expiration_hours=app.config["JWT_EXPIRATION_HOURS"],
    )
    task_service = TaskService()
    category_service = CategoryService()

    # Register API routes
    app.register_blueprint(create_routes(auth_service, task_service, category_service))

    @app.route("/")
    def index():
        """Serve the main index.html"""
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:filename>")
    def serve_static_files(filename):
        """Serve static files (CSS, JS, etc.)"""
        # Only serve actual files, not API endpoints
        if filename.startswith(("api/", "register", "login", "tasks", "categories", "health")):
            return jsonify({"error": "Not found"}), 404
        
        try:
            return send_from_directory(app.static_folder, filename)
        except:
            # If file not found, return index.html for SPA routing
            return send_from_directory(app.static_folder, "index.html")

    @app.route("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception as e:
            db_status = str(e)
        return {
            "status": "ok",
            "database": db_status,
            "version": app.config["APP_VERSION"]
        }

    return app


# Only create app instance when running directly, not during imports
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)