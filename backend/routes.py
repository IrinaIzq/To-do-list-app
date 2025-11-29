from flask import Blueprint, request, jsonify
from functools import wraps

from backend.services.auth_service import AuthService
from backend.services.category_service import CategoryService
from backend.services.task_service import TaskService


def create_routes(auth_service: AuthService, task_service: TaskService, category_service: CategoryService):

    bp = Blueprint("api", __name__)

    # ----------------------------------------------------
    # AUTH DECORATOR
    # ----------------------------------------------------
    def require_token(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"error": "Token is missing"}), 401

            try:
                scheme, token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise Exception()
            except Exception:
                return jsonify({"error": "Missing or invalid token"}), 401

            try:
                user_id = auth_service.verify_token(token)
            except auth_service.AuthenticationError:
                return jsonify({"error": "Invalid token"}), 401

            request.user_id = user_id
            return f(*args, **kwargs)
        return wrapper

    # ----------------------------------------------------
    # AUTH
    # ----------------------------------------------------
    @bp.route("/register", methods=["POST"])
    def register():
        data = request.get_json() or {}
        try:
            auth_service.register_user(data.get("username"), data.get("password"))
            return jsonify({"message": "User created successfully"}), 201
        except auth_service.RegistrationError as e:
            return jsonify({"error": str(e)}), 400
        except auth_service.AuthenticationError as e:
            return jsonify({"error": str(e)}), 400

    @bp.route("/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        try:
            user = auth_service.authenticate_user(data.get("username"), data.get("password"))
            token = auth_service.generate_token(user.id)
            return jsonify({"token": token}), 200
        except auth_service.AuthenticationError as e:
            return jsonify({"error": str(e)}), 401

    # ----------------------------------------------------
    # CATEGORY ENDPOINTS
    # ----------------------------------------------------
    @bp.route("/categories", methods=["POST"])
    @require_token
    def create_category():
        data = request.get_json() or {}
        try:
            cat = category_service.create_category(
                request.user_id,
                data.get("name"),
                data.get("description")
            )
            return jsonify({
                "id": cat.id,
                "name": cat.name,
                "description": cat.description
            }), 201
        except category_service.CategoryValidationError as e:
            msg = str(e)
            if msg == "Duplicate category":
                msg = "Category already exists"
            return jsonify({"error": msg}), 400

    @bp.route("/categories", methods=["GET"])
    @require_token
    def get_categories():
        cats = category_service.get_all_categories(request.user_id)
        return jsonify([
            {"id": c.id, "name": c.name, "description": c.description}
            for c in cats
        ]), 200

    @bp.route("/categories/<int:cid>", methods=["PUT"])
    @require_token
    def update_category(cid):
        data = request.get_json() or {}
        try:
            cat = category_service.update_category(cid, data.get("name"), data.get("description"))
            return jsonify({
                "id": cat.id,
                "name": cat.name,
                "description": cat.description
            }), 200
        except category_service.CategoryValidationError as e:
            return jsonify({"error": str(e)}), 400

    @bp.route("/categories/<int:cid>", methods=["DELETE"])
    @require_token
    def delete_category(cid):
        try:
            category_service.delete_category(cid)
            return jsonify({"message": "Category deleted"}), 200
        except category_service.CategoryValidationError as e:
            return jsonify({"error": str(e)}), 400

    # ----------------------------------------------------
    # TASK ENDPOINTS
    # ----------------------------------------------------
    @bp.route("/tasks", methods=["POST"])
    @require_token
    def create_task():
        data = request.get_json() or {}

        # Tests expect this strict check
        if data.get("category_id") is None:
            return jsonify({"error": "category is required"}), 400

        try:
            task = task_service.create_task(
                request.user_id,
                data.get("title"),
                data.get("description"),
                data.get("priority"),
                data.get("hours"),
                data.get("category_id"),
                data.get("due_date")
            )
            return jsonify({"id": task.id, "title": task.title}), 201
        except task_service.TaskValidationError as e:
            return jsonify({"error": str(e)}), 400

    @bp.route("/tasks", methods=["GET"])
    @require_token
    def get_tasks():
        tasks = task_service.get_tasks(request.user_id)
        return jsonify([
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "hours": t.hours,
                "category_id": t.category_id
            } for t in tasks
        ]), 200

    @bp.route("/tasks/<int:tid>", methods=["GET"])
    @require_token
    def get_task(tid):
        try:
            t = task_service.get_task(tid)
            return jsonify({
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "hours": t.hours,
                "category_id": t.category_id
            }), 200
        except task_service.TaskNotFoundError:
            return jsonify({"error": "Not found"}), 404

    @bp.route("/tasks/<int:tid>", methods=["PUT"])
    @require_token
    def update_task(tid):
        data = request.get_json() or {}
        try:
            t = task_service.update_task(tid, **data)
            return jsonify({"id": t.id, "title": t.title}), 200
        except task_service.TaskNotFoundError:
            return jsonify({"error": "Not found"}), 404

    @bp.route("/tasks/<int:tid>", methods=["DELETE"])
    @require_token
    def delete_task(tid):
        try:
            task_service.delete_task(tid)
            return jsonify({"message": "Task deleted"}), 200
        except task_service.TaskNotFoundError:
            return jsonify({"error": "Not found"}), 404

    # ----------------------------------------------------
    # HEALTH
    # ----------------------------------------------------
    @bp.route("/health", methods=["GET"])
    def health():
        # tests expect string "healthy" or "degraded"
        try:
            from backend.database import db
            db.session.execute("SELECT 1")
            return jsonify({"status": "healthy"}), 200
        except Exception:
            return jsonify({"status": "degraded"}), 200

    return bp   # ⬅⬅⬅ CRUCIAL — si falta o se mueve, Flask peta