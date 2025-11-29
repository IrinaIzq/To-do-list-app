from flask import Flask, jsonify
from flask_cors import CORS

from backend.database import db
from backend.config import get_config
from backend.services.auth_service import AuthService
from backend.services.task_service import TaskService
from backend.services.category_service import CategoryService
from backend.routes import create_routes


def create_app():
    app = Flask(__name__)

    # Load config
    config = get_config()
    app.config.from_object(config)

    # Database
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Enable CORS for frontend
    CORS(app)

    # Initialize services
    auth_service = AuthService(
        secret_key=app.config["SECRET_KEY"],
        algorithm="HS256",
        expiration_hours=24
    )
    task_service = TaskService()
    category_service = CategoryService()

    # Register API routes
    bp = create_routes(auth_service, task_service, category_service)
    app.register_blueprint(bp)

    # Root route → API status ONLY (NO HTML)
    @app.route("/")
    def index():
        return jsonify({
            "status": "API running",
            "message": "Backend up and healthy"
        }), 200

    return app


# Azure entrypoint
app = create_app()
