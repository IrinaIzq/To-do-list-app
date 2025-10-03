from flask import Flask
from flask_cors import CORS
from database import db
from routes import routes

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Habilitar CORS para permitir peticiones desde el frontend
CORS(app)

db.init_app(app)
app.register_blueprint(routes)

@app.route("/")
def home():
    return "Hello, To-Do App with Users and Categories"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)