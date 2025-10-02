from database import db

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f"<Category {self.name}>"

class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    estimated_hours = db.Column(db.Float)
    due_date = db.Column(db.String(20))  # YYYY-MM-DD simple
    priority = db.Column(db.Integer)
    status = db.Column(db.String(20), default="pending")
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    def __repr__(self):
        return f"<Task {self.title}>"