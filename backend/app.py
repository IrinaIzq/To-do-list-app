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
    config_name = config_name or os.getenv("FLASK_ENV", "production")
    config_class = get_config(config_name)

    app = Flask(__name__, static_folder="../frontend")
    app.config.from_object(config_class)

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

    app.register_blueprint(create_routes(auth_service, task_service, category_service))

    @app.get("/")
    def index():
        return send_from_directory("../frontend", "index.html")

    @app.get("/health")
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


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)