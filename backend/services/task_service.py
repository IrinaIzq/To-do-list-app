from backend.database import db
from backend.models.task import Task
from backend.models.category import Category

class TaskValidationError(Exception):
    pass

class TaskNotFoundError(Exception):
    pass

class TaskService:

    def create_task(self, title, description, priority, hours, category_id):
        if not title or not description:
            raise TaskValidationError("Missing fields")

        if priority < 0 or hours < 0:
            raise TaskValidationError("Invalid values")

        if not Category.query.get(category_id):
            raise TaskValidationError("Category not found")

        task = Task(
            title=title,
            description=description,
            priority=priority,
            hours=hours,
            category_id=category_id
        )

        db.session.add(task)
        db.session.commit()
        return task

    def get_all_tasks(self):
        return Task.query.all()

    def get_task(self, id):
        task = Task.query.get(id)
        if not task:
            raise TaskNotFoundError("Task not found")
        return task

    def update_task(self, id, title, description, priority, hours, category_id):
        task = Task.query.get(id)
        if not task:
            raise TaskNotFoundError("Task not found")

        task.title = title
        task.description = description
        task.priority = priority
        task.hours = hours
        task.category_id = category_id
        db.session.commit()
        return task

    def delete_task(self, id):
        task = Task.query.get(id)
        if not task:
            raise TaskNotFoundError("Task not found")
        db.session.delete(task)
        db.session.commit()