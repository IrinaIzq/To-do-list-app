from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_models():
    # Import models so SQLAlchemy registers them
    from backend.models.user import User
    from backend.models.task import Task
    from backend.models.category import Category