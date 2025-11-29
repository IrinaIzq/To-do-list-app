from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so tests can import them directly from backend.database
from backend.models.user import User
from backend.models.category import Category
from backend.models.task import Task


def init_models():
    """
    This function exists only so that tests can call init_models()
    before creating tables.
    """
    pass