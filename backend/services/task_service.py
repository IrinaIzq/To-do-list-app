from backend.database import db, init_models

Task = None
def ensure_task_model():
    global Task
    if Task is None:
        Task = init_models()
    return Task

class TaskService:
    def __init__(self):
        ensure_task_model()

    def list_tasks(self):
        return Task.query.all()

    def add_task(self, title):
        t = Task(title=title)
        db.session.add(t)
        db.session.commit()
        return t