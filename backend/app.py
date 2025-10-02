from flask import Flask
from database import db
from routes import routes

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(routes)

@app.route("/")
def home():
    return "Hello, To-Do App with Users and Categories"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
