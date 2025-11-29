from backend.database import db
from backend.models.task import Task


class TaskValidationError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class TaskService:

    TaskValidationError = TaskValidationError
    TaskNotFoundError = TaskNotFoundError

    def create_task(self, user_id, title, description, priority, hours, category_id, due_date=None):
        if not title or not title.strip():
            raise TaskValidationError("title required")

        if priority not in [1, 2, 3]:
            raise TaskValidationError("invalid priority")

        if hours is None or hours < 0:
            raise TaskValidationError("hours must be non-negative")

        task = Task(
            title=title.strip(),
            description=description.strip() if description else None,
            priority=priority,
            hours=hours,
            category_id=category_id,
            user_id=user_id,
        )

        db.session.add(task)
        db.session.commit()
        return task

    def get_tasks(self, user_id):
        return Task.query.filter_by(user_id=user_id).order_by(Task.priority).all()

    def get_task(self, task_id):
        t = Task.query.get(task_id)
        if not t:
            raise TaskNotFoundError()
        return t

    def update_task(self, task_id, **kwargs):
        t = Task.query.get(task_id)
        if not t:
            raise TaskNotFoundError()

        for k, v in kwargs.items():
            if hasattr(t, k) and v is not None:
                setattr(t, k, v)

        db.session.commit()
        return t

    def delete_task(self, task_id):
        t = Task.query.get(task_id)
        if not t:
            raise TaskNotFoundError()

        db.session.delete(t)
        db.session.commit()