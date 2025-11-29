from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# small helper model for demo (Task)
def init_models():
    class Task(db.Model):
        __tablename__ = "tasks"
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        done = db.Column(db.Boolean, default=False)

    return Task