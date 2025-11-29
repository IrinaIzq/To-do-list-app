from backend.database import db
from backend.models.task import Task


class TaskValidationError(Exception):
    """Raised when task validation fails."""
    pass


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""
    pass


class TaskService:

    def get_all_tasks(self):
        """Return all tasks."""
        return Task.query.all()

    def get_task(self, task_id):
        """Get a task or raise error if not found."""
        task = Task.query.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    def create_task(self, title, category_id=None, user_id=None):
        """Create a task with validation."""

        if not title or title.strip() == "":
            raise TaskValidationError("Title is required")

        task = Task(
            title=title,
            category_id=category_id,
            user_id=user_id,
            completed=False
        )
        db.session.add(task)
        db.session.commit()
        return task

    def delete_task(self, task_id):
        """Delete a task or raise error if not found."""
        task = Task.query.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")

        db.session.delete(task)
        db.session.commit()
        return True

    def update_task(self, task_id, **kwargs):
        """Update a task by ID."""

        task = Task.query.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")

        # Allowed fields
        allowed_fields = {"title", "completed", "category_id"}

        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(task, field, value)

        db.session.commit()
        return task