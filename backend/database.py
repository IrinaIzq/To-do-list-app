from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# These imports will be resolved after models are defined
User = None
Category = None
Task = None

def init_models():
    global User, Category, Task
    from backend.models.user import User
    from backend.models.category import Category
    from backend.models.task import Task