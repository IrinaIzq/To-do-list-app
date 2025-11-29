from datetime import datetime
from backend.database import db


class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # priority expected to be integer 1..3 in tests
    priority = db.Column(db.Integer, nullable=False, default=3)

    # tests use "hours" field
    hours = db.Column(db.Integer, nullable=False, default=0)

    # optional due date
    due_date = db.Column(db.DateTime, nullable=True)

    # status column used in some tests
    status = db.Column(db.String(32), nullable=True, default="Pending")

    # user_id NOT NULL in DB; tests sometimes create categories/tasks without explicit user
    user_id = db.Column(db.Integer, nullable=False, default=1)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id"),
        nullable=True
    )

    def __repr__(self):
        return f"<Task {self.id} {self.title}>"