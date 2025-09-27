from flask import Flask

# Create Flask application
app = Flask(__name__)

# Test route
@app.route("/")
def home():
    return "Hello, To-Do App! Your backend is running 🚀"

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
