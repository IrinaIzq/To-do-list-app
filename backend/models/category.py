from backend.database import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, nullable=False, default=1)

    tasks = db.relationship("Task", backref="category", lazy=True)