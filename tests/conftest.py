"""
Pytest configuration and shared fixtures for testing.
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db
from backend.models.user import User
from backend.models.task import Task
from backend.models.category import Category
from backend.services.auth_service import AuthService
from backend.services.task_service import TaskService
from backend.services.category_service import CategoryService


@pytest.fixture(scope='function')
def app():
    """Create and configure a test application instance."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def auth_service(app):
    """Create an AuthService instance."""
    return AuthService(
        secret_key=app.config['SECRET_KEY'],
        algorithm=app.config['JWT_ALGORITHM'],
        expiration_hours=app.config['JWT_EXPIRATION_HOURS']
    )


@pytest.fixture(scope='function')
def task_service(app):
    """Create a TaskService instance."""
    return TaskService()


@pytest.fixture(scope='function')
def category_service(app):
    """Create a CategoryService instance."""
    return CategoryService()


@pytest.fixture(scope='function')
def test_user(app, auth_service):
    """Create a test user and return credentials."""
    username = 'testuser'
    password = 'testpass123'
    
    with app.app_context():
        user = auth_service.register_user(username, password)
        db.session.commit()
        user_id = user.id  # Store ID inside context
    
    return {
        'id': user_id,
        'username': username,
        'password': password
    }


@pytest.fixture(scope='function')
def auth_token(app, auth_service, test_user):
    """Create an authentication token for the test user."""
    with app.app_context():
        return auth_service.generate_token(test_user['id'])


@pytest.fixture(scope='function')
def auth_headers(auth_token):
    """Create authorization headers with token."""
    return {'Authorization': f'Bearer {auth_token}'}


@pytest.fixture(scope='function')
def test_category(app, category_service, test_user):
    """Create a test category."""
    with app.app_context():
        # FIX: Pass user_id, name, description in correct order
        category = category_service.create_category(
            test_user['id'],
            'Test Category',
            'Test description'
        )
        db.session.commit()
        category_id = category.id
        category_name = category.name
    
    # Return a simple object with the data
    class CategoryData:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    return CategoryData(category_id, category_name)


@pytest.fixture(scope='function')
def test_task(app, task_service, category_service, test_category, test_user):
    """Create a test task."""
    with app.app_context():
        # FIX: Call create_task with correct positional arguments
        task = task_service.create_task(
            test_user['id'],  # user_id
            'Test Task',  # title
            'Test description',  # description
            2,  # priority (use integer)
            5,  # hours
            test_category.id,  # category_id
            None  # due_date
        )
        db.session.commit()
        task_id = task.id
        task_title = task.title
    
    # Return a simple object
    class TaskData:
        def __init__(self, id, title):
            self.id = id
            self.title = title
    
    return TaskData(task_id, task_title)


@pytest.fixture(scope='function')
def multiple_tasks(app, task_service, category_service, test_category, test_user):
    """Create multiple test tasks with different priorities."""
    with app.app_context():
        from datetime import datetime
        
        # High priority task (priority = 1)
        task1 = task_service.create_task(
            test_user['id'],
            'High Priority Task',
            'High description',
            1,  # priority
            10,  # hours
            test_category.id,
            datetime(2025, 12, 1)  # due_date as datetime object
        )
        
        # Medium priority task (priority = 2)
        task2 = task_service.create_task(
            test_user['id'],
            'Medium Priority Task',
            'Medium description',
            2,  # priority
            5,  # hours
            test_category.id,
            datetime(2025, 12, 1)  # due_date as datetime object
        )
        
        # Low priority task (priority = 3)
        task3 = task_service.create_task(
            test_user['id'],
            'Low Priority Task',
            'Low description',
            3,  # priority
            2,  # hours
            test_category.id,
            datetime(2025, 12, 15)  # due_date as datetime object
        )
        
        db.session.commit()
        
        # Store IDs inside context
        task_ids = [task1.id, task2.id, task3.id]
    
    return task_ids