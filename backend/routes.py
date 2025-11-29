from flask import Blueprint, request, jsonify
from backend.services.auth_service import AuthService, AuthenticationError
from backend.services.category_service import CategoryService, CategoryValidationError
from backend.services.task_service import TaskService, TaskValidationError, TaskNotFoundError

bp = Blueprint("api", __name__)

auth: AuthService = None
category_service: CategoryService = None
task_service: TaskService = None

def create_routes(auth_service, cat_service, t_service):
    global auth, category_service, task_service
    auth = auth_service
    category_service = cat_service
    task_service = t_service

    return bp

#  AUTH 

@bp.post("/auth/register")
def register():
    data = request.json
    try:
        user = auth.register_user(data.get("username"), data.get("password"))
        return jsonify({"id": user.id}), 201
    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 400

@bp.post("/auth/login")
def login():
    data = request.json
    try:
        user = auth.authenticate_user(data.get("username"), data.get("password"))
        token = auth.generate_token(user.id)
        return jsonify({"token": token}), 200
    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 401

#  PROTECTED ENDPOINT 

@bp.get("/protected")
def protected():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        auth.verify_token(token)
        return jsonify({"message": "ok"}), 200
    except AuthenticationError:
        return jsonify({"error": "Unauthorized"}), 401

#  CATEGORIES 

@bp.post("/categories")
def create_category():
    data = request.json
    try:
        c = category_service.create_category(data["name"], data["description"])
        return jsonify({"id": c.id}), 201
    except CategoryValidationError as e:
        return jsonify({"error": str(e)}), 400

@bp.get("/categories")
def list_categories():
    cats = category_service.get_all_categories()
    return jsonify([{"id": c.id, "name": c.name, "description": c.description} for c in cats])

@bp.put("/categories/<int:id>")
def update_category(id):
    data = request.json
    try:
        c = category_service.update_category(id, data["name"], data["description"])
        return jsonify({"id": c.id}), 200
    except CategoryValidationError as e:
        return jsonify({"error": str(e)}), 400

@bp.delete("/categories/<int:id>")
def delete_category(id):
    try:
        category_service.delete_category(id)
        return jsonify({"deleted": True}), 200
    except CategoryValidationError as e:
        return jsonify({"error": str(e)}), 400

# TASKS 

@bp.post("/tasks")
def create_task():
    data = request.json
    try:
        t = task_service.create_task(
            data["title"], data["description"], data["priority"],
            data["hours"], data["category_id"]
        )
        return jsonify({"id": t.id}), 201
    except TaskValidationError as e:
        return jsonify({"error": str(e)}), 400

@bp.get("/tasks")
def list_tasks():
    tasks = task_service.get_all_tasks()
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "hours": t.hours,
            "category_id": t.category_id
        }
        for t in tasks
    ])

@bp.get("/tasks/<int:id>")
def get_task(id):
    try:
        t = task_service.get_task(id)
        return jsonify({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "hours": t.hours,
            "category_id": t.category_id
        })
    except TaskNotFoundError:
        return jsonify({"error": "Not found"}), 404

@bp.put("/tasks/<int:id>")
def update_task(id):
    data = request.json
    try:
        t = task_service.update_task(
            id, data["title"], data["description"], data["priority"],
            data["hours"], data["category_id"]
        )
        return jsonify({"id": t.id}), 200
    except (TaskNotFoundError, TaskValidationError) as e:
        return jsonify({"error": str(e)}), 400

@bp.delete("/tasks/<int:id>")
def delete_task(id):
    try:
        task_service.delete_task(id)
        return jsonify({"deleted": True}), 200
    except TaskNotFoundError:
        return jsonify({"error": "Not found"}), 404