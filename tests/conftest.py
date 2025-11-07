"""
Pytest configuration and shared fixtures for testing.
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db, User, Category, Task
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
    
    return {
        'id': user.id,
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
def test_category(app, category_service):
    """Create a test category."""
    with app.app_context():
        category = category_service.create_category({
            'name': 'Test Category',
            'description': 'Test description'
        })
        db.session.commit()
        return category


@pytest.fixture(scope='function')
def test_task(app, task_service, category_service, test_category):
    """Create a test task."""
    with app.app_context():
        task = task_service.create_task({
            'title': 'Test Task',
            'description': 'Test description',
            'category_id': test_category.id,
            'priority': 'High',
            'estimated_hours': 5.0
        }, category_service)
        db.session.commit()
        return task


@pytest.fixture(scope='function')
def multiple_tasks(app, task_service, category_service, test_category):
    """Create multiple test tasks with different priorities."""
    tasks = []
    with app.app_context():
        # High priority task
        tasks.append(task_service.create_task({
            'title': 'High Priority Task',
            'category_id': test_category.id,
            'priority': 'High',
            'due_date': '2025-12-01',
            'estimated_hours': 10.0
        }, category_service))
        
        # Medium priority task
        tasks.append(task_service.create_task({
            'title': 'Medium Priority Task',
            'category_id': test_category.id,
            'priority': 'Medium',
            'due_date': '2025-12-01',
            'estimated_hours': 5.0
        }, category_service))
        
        # Low priority task
        tasks.append(task_service.create_task({
            'title': 'Low Priority Task',
            'category_id': test_category.id,
            'priority': 'Low',
            'due_date': '2025-12-15',
            'estimated_hours': 2.0
        }, category_service))
        
        db.session.commit()
        return tasks