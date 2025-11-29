"""Unit tests for TaskService."""
import pytest
from backend.services.task_service import TaskService, TaskValidationError, TaskNotFoundError

class TestTaskService:
    def test_create_task_success(self, app, task_service, category_service, test_category, test_user):
        """Test successful task creation."""
        with app.app_context():
            # FIX: Pass all required positional arguments
            task = task_service.create_task(
                test_user['id'],  # user_id
                'Test Task',  # title
                'Test description',  # description
                2,  # priority (as integer)
                5,  # hours
                test_category.id  # category_id
            )
            
            assert task.title == 'Test Task'
            assert task.priority == 2
    
    def test_create_task_without_title(self, app, task_service, category_service, test_category, test_user):
        """Test task creation without title."""
        with app.app_context():
            with pytest.raises(TaskValidationError):
                # FIX: Pass all required positional arguments with empty title
                task_service.create_task(
                    test_user['id'],
                    '',  # empty title
                    'Description',
                    2,
                    5,
                    test_category.id
                )