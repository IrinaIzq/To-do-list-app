from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so tests can import them from here
from backend.models.user import User
from backend.models.task import Task
from backend.models.category import Category

def init_models():
    pass

__all__ = ["db", "User", "Task", "Category", "init_models"]