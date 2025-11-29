from backend.database import db
from backend.models.task import Task


class TaskValidationError(Exception):
    """Raised when task validation fails."""
    pass


class TaskService:

    def get_all_tasks(self):
        return Task.query.all()

    def create_task(self, title, category_id=None, user_id=None):

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

    def get_task(self, task_id):
        return Task.query.get(task_id)

    def delete_task(self, task_id):
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return True
        return False

    def update_task(self, task_id, **kwargs):
        task = Task.query.get(task_id)
        if not task:
            return None

        for field, value in kwargs.items():
            if hasattr(task, field):
                setattr(task, field, value)

        db.session.commit()
        return task