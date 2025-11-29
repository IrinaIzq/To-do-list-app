from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime, timezone
import traceback

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
        try:
            data = request.get_json() or {}
            
            # Validate input
            if not data.get("username") or not data.get("password"):
                return jsonify({"error": "Username and password are required"}), 400
            
            try:
                auth_service.register_user(data.get("username"), data.get("password"))
                return jsonify({"message": "User created successfully"}), 201
            except auth_service.RegistrationError as e:
                return jsonify({"error": str(e)}), 400
            except auth_service.AuthenticationError as e:
                return jsonify({"error": str(e)}), 400
        except Exception as e:
            # Log the full error for debugging
            print(f"ERROR in /register: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @bp.route("/login", methods=["POST"])
    def login():
        try:
            data = request.get_json() or {}
            
            # Validate input
            if not data.get("username") or not data.get("password"):
                return jsonify({"error": "Username and password are required"}), 400
            
            try:
                user = auth_service.authenticate_user(data.get("username"), data.get("password"))
                token = auth_service.generate_token(user.id)
                return jsonify({"token": token}), 200
            except auth_service.AuthenticationError as e:
                return jsonify({"error": str(e)}), 401
        except Exception as e:
            print(f"ERROR in /login: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    # ----------------------------------------------------
    # CATEGORY ENDPOINTS
    # ----------------------------------------------------
    @bp.route("/categories", methods=["POST"])
    @require_token
    def create_category():
        try:
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
        except Exception as e:
            print(f"ERROR in /categories POST: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @bp.route("/categories", methods=["GET"])
    @require_token
    def get_categories():
        try:
            cats = category_service.get_all_categories(request.user_id)
            return jsonify([
                {"id": c.id, "name": c.name, "description": c.description}
                for c in cats
            ]), 200
        except Exception as e:
            print(f"ERROR in /categories GET: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @bp.route("/categories/<int:cid>", methods=["PUT"])
    @require_token
    def update_category(cid):
        try:
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
        except Exception as e:
            print(f"ERROR in /categories PUT: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @bp.route("/categories/<int:cid>", methods=["DELETE"])
    @require_token
    def delete_category(cid):
        try:
            try:
                category_service.delete_category(cid)
                return jsonify({"message": "Category deleted"}), 200
            except category_service.CategoryValidationError as e:
                return jsonify({"error": str(e)}), 400
        except Exception as e:
            print(f"ERROR in /categories DELETE: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    # ----------------------------------------------------
    # TASK ENDPOINTS
    # ----------------------------------------------------
    @bp.route("/tasks", methods=["POST"])
    @require_token
    def create_task():
        try:
            data = request.get_json() or {}

            # Check if category_id is missing or None
            if data.get("category_id") is None:
                return jsonify({"error": "category is required"}), 400

            # Convert priority from string to integer if needed
            priority = data.get("priority")
            if isinstance(priority, str):
                priority_map = {"High": 1, "Medium": 2, "Low": 3}
                priority = priority_map.get(priority, 2)
            
            # Ensure hours is provided and valid
            hours = data.get("hours", data.get("estimated_hours", 0))
            if hours is None:
                hours = 0

            try:
                task = task_service.create_task(
                    request.user_id,
                    data.get("title"),
                    data.get("description"),
                    priority,
                    hours,
                    data.get("category_id"),
                    data.get("due_date")
                )
                return jsonify({"id": task.id, "message": "Task created"}), 201
            except task_service.TaskValidationError as e:
                return jsonify({"error": str(e)}), 400
        except Exception as e:
            print(f"ERROR in /tasks POST: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @bp.route("/tasks", methods=["GET"])
    @require_token
    def get_tasks():
        try:
            tasks = task_service.get_tasks(request.user_id)
            priority_map = {1: "High", 2: "Medium", 3: "Low"}
            return jsonify([
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": priority_map.get(t.priority, "Medium"),
                    "hours": t.hours,
                    "estimated_hours": t.hours,
                    "category_id": t.category_id,
                    "status": t.status,
                    "due_date": t.due_date.isoformat() if t.due_date else None
                } for t in tasks
            ]), 200
        except Exception as e:
            print(f"ERROR in /tasks GET: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @bp.route("/tasks/<int:tid>", methods=["GET"])
    @require_token
    def get_task(tid):
        try:
            try:
                t = task_service.get_task(tid)
                priority_map = {1: "High", 2: "Medium", 3: "Low"}
                return jsonify({
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": priority_map.get(t.priority, "Medium"),
                    "hours": t.hours,
                    "estimated_hours": t.hours,
                    "category_id": t.category_id,
                    "status": t.status,
                    "due_date": t.due_date.isoformat() if t.due_date else None
                }), 200
            except task_service.TaskNotFoundError:
                return jsonify({"error": "Not found"}), 404
        except Exception as e:
            print(f"ERROR in /tasks GET single: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @bp.route("/tasks/<int:tid>", methods=["PUT"])
    @require_token
    def update_task(tid):
        try:
            data = request.get_json() or {}
            
            # Convert priority from string to integer if provided
            if "priority" in data and isinstance(data["priority"], str):
                priority_map = {"High": 1, "Medium": 2, "Low": 3}
                data["priority"] = priority_map.get(data["priority"], 2)
            
            try:
                t = task_service.update_task(tid, **data)
                return jsonify({"id": t.id, "title": t.title}), 200
            except task_service.TaskNotFoundError:
                return jsonify({"error": "Not found"}), 404
        except Exception as e:
            print(f"ERROR in /tasks PUT: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    @bp.route("/tasks/<int:tid>", methods=["DELETE"])
    @require_token
    def delete_task(tid):
        try:
            try:
                task_service.delete_task(tid)
                return jsonify({"message": "Task deleted"}), 200
            except task_service.TaskNotFoundError:
                return jsonify({"error": "Not found"}), 404
        except Exception as e:
            print(f"ERROR in /tasks DELETE: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    # ----------------------------------------------------
    # HEALTH
    # ----------------------------------------------------
    @bp.route("/health", methods=["GET"])
    def health():
        try:
            from backend.database import db
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            db_status = "healthy"
            status = "healthy"
        except Exception as e:
            db_status = f"degraded: {str(e)}"
            status = "degraded"
        
        return jsonify({
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "database": db_status
        }), 200

    return bp