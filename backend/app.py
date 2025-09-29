from flask import Flask
from models import db

app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return "Hello, To-Do App! Database is ready"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # creates tables if not exist
    app.run(debug=True)
