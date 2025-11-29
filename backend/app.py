import os
from flask import Flask
from backend.database import db, init_models
from backend.routes import create_routes
from backend.services.auth_service import AuthService
from backend.services.category_service import CategoryService
from backend.services.task_service import TaskService

def create_app(config_name="default"):
    app = Flask(__name__)

    # The tests expect the DB to be in-memory ALWAYS
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SECRET_KEY"] = "secret"
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["JWT_EXPIRATION_HOURS"] = 24

    db.init_app(app)
    init_models()

    with app.app_context():
        db.create_all()

    auth = AuthService(
        secret_key=app.config["SECRET_KEY"],
        algorithm=app.config["JWT_ALGORITHM"],
        expiration_hours=app.config["JWT_EXPIRATION_HOURS"]
    )

    category_service = CategoryService()
    task_service = TaskService()

    app.register_blueprint(
        create_routes(auth, category_service, task_service)
    )

    # Add health check route (the tests need it)
    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run()