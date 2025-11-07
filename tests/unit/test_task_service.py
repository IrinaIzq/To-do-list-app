"""Unit tests for TaskService."""
import pytest
from backend.services.task_service import TaskService, TaskValidationError, TaskNotFoundError

class TestTaskService:
    def test_create_task_success(self, app, task_service, category_service, test_category):
        """Test successful task creation."""
        with app.app_context():
            task = task_service.create_task({
                'title': 'Test Task',
                'category_id': test_category.id,
                'priority': 'High'
            }, category_service)
            
            assert task.title == 'Test Task'
            assert task.priority == 'High'
    
    def test_create_task_without_title(self, app, task_service, category_service):
        """Test task creation without title."""
        with app.app_context():
            with pytest.raises(TaskValidationError):
                task_service.create_task({}, category_service)