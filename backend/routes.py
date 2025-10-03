from flask import Blueprint, request, jsonify
from database import db, Task, Category, User
from utils import generate_token, token_required

routes = Blueprint("routes", __name__)

# Authentication routes
@routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Missing username or password"}), 400
    
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(username=data["username"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username")).first()
    if user and user.check_password(data.get("password")):
        token = generate_token(user.id)
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401


# Category routes
@routes.route("/categories", methods=["GET"])
@token_required
def get_categories(current_user_id):
    categories = Category.query.all()
    return jsonify([{"id": c.id, "name": c.name, "description": c.description} for c in categories])

@routes.route("/categories", methods=["POST"])
@token_required
def create_category(current_user_id):
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Category name is required"}), 400

    if Category.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Category already exists"}), 400

    category = Category(name=data["name"], description=data.get("description"))
    db.session.add(category)
    db.session.commit()
    return jsonify({"id": category.id, "name": category.name, "description": category.description}), 201

@routes.route("/categories/<int:category_id>", methods=["PUT"])
@token_required
def update_category(current_user_id, category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    
    if data.get("name"):
        category.name = data["name"]
    if data.get("description"):
        category.description = data["description"]
    
    db.session.commit()
    return jsonify({"message": "Category updated", "id": category.id})

@routes.route("/categories/<int:category_id>", methods=["DELETE"])
@token_required
def delete_category(current_user_id, category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"})


# Task routes
@routes.route("/tasks", methods=["GET"])
@token_required
def get_tasks(current_user_id):
    tasks = Task.query.all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "estimated_hours": t.estimated_hours,
        "due_date": t.due_date,
        "priority": t.priority,
        "category_id": t.category_id,
        "category": t.category.name if t.category else None
    } for t in tasks])

@routes.route("/tasks/<int:task_id>", methods=["GET"])
@token_required
def get_task(current_user_id, task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "estimated_hours": task.estimated_hours,
        "due_date": task.due_date,
        "priority": task.priority,
        "category_id": task.category_id,
        "category": task.category.name if task.category else None
    })

@routes.route("/tasks", methods=["POST"])
@token_required
def create_task(current_user_id):
    data = request.get_json()
    if not data.get("title"):
        return jsonify({"error": "Task title is required"}), 400

    # Check if category exists by name or id
    category = None
    if data.get("category_name"):
        category = Category.query.filter_by(name=data["category_name"]).first()
        if not category:
            category = Category(name=data["category_name"], description="Auto-created")
            db.session.add(category)
            db.session.commit()
    elif data.get("category_id"):
        category = Category.query.get(data["category_id"])

    task = Task(
        title=data["title"],
        description=data.get("description"),
        estimated_hours=data.get("estimated_hours"),
        due_date=data.get("due_date"),
        priority=data.get("priority"),
        status=data.get("status", "Pending"),
        category_id=category.id if category else None
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created", "id": task.id}), 201

@routes.route("/tasks/<int:task_id>", methods=["PUT"])
@token_required
def update_task(current_user_id, task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if data.get("title"):
        task.title = data["title"]
    if data.get("description"):
        task.description = data["description"]
    if data.get("status"):
        task.status = data["status"]
    if data.get("estimated_hours"):
        task.estimated_hours = data["estimated_hours"]
    if data.get("due_date"):
        task.due_date = data["due_date"]
    if data.get("priority"):
        task.priority = data["priority"]
    if data.get("category_name"):
        category = Category.query.filter_by(name=data["category_name"]).first()
        if category:
            task.category_id = category.id
    elif data.get("category_id"):
        task.category_id = data["category_id"]
    
    db.session.commit()
    return jsonify({"message": "Task updated", "id": task.id})

@routes.route("/tasks/<int:task_id>", methods=["DELETE"])
@token_required
def delete_task(current_user_id, task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})