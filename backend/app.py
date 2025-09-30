from flask import Flask
from database import db
from routes import routes

app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init DB
db.init_app(app)

# Register routes
app.register_blueprint(routes)

@app.route("/")
def home():
    return "To-Do App backend is running 🚀"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)