from flask import Flask, jsonify, request
from models import db, Task, Category

app = Flask(__name__)

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return "To-Do App backend is running 🚀"

# Task routes
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    result = []
    for t in tasks:
        result.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "estimated_hours": t.estimated_hours,
            "due_date": t.due_date,
            "priority": t.priority,
            "status": t.status,
            "category_id": t.category_id
        })
    return jsonify(result)

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    new_task = Task(
        title=data.get("title"),
        description=data.get("description"),
        estimated_hours=data.get("estimated_hours"),
        due_date=data.get("due_date"),
        priority=data.get("priority"),
        status=data.get("status", "pending"),
        category_id=data.get("category_id")
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created", "id": new_task.id}), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.estimated_hours = data.get("estimated_hours", task.estimated_hours)
    task.due_date = data.get("due_date", task.due_date)
    task.priority = data.get("priority", task.priority)
    task.status = data.get("status", task.status)
    task.category_id = data.get("category_id", task.category_id)
    db.session.commit()
    return jsonify({"message": "Task updated"})

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})

# Category routes
@app.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        result.append({
            "id": c.id,
            "name": c.name,
            "description": c.description
        })
    return jsonify(result)

@app.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    new_category = Category(
        name=data.get("name"),
        description=data.get("description")
    )
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Category created", "id": new_category.id}), 201

@app.route("/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    category.name = data.get("name", category.name)
    category.description = data.get("description", category.description)
    db.session.commit()
    return jsonify({"message": "Category updated"})

@app.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"})

# Main
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)