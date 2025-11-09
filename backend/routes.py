"""
Refactored routes using dependency injection and proper error handling.
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Callable

from backend.services.auth_service import AuthService, AuthenticationError
from backend.services.task_service import (
    TaskService, TaskNotFoundError, TaskValidationError
)
from backend.services.category_service import (
    CategoryService, CategoryNotFoundError, CategoryValidationError
)


def create_routes(auth_service: AuthService, 
                 task_service: TaskService,
                 category_service: CategoryService) -> Blueprint:
    """
    Create routes blueprint with injected dependencies.
    
    Args:
        auth_service: Authentication service instance
        task_service: Task service instance
        category_service: Category service instance
        
    Returns:
        Configured Blueprint
    """
    routes = Blueprint("routes", __name__)
    
    def token_required(f: Callable) -> Callable:
        """Decorator to require valid JWT token."""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if "Authorization" in request.headers:
                auth_header = request.headers["Authorization"]
                try:
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return jsonify({"error": "Invalid token format"}), 401
            
            if not token:
                return jsonify({"error": "Token is missing"}), 401
            
            try:
                current_user_id = auth_service.verify_token(token)
                if not current_user_id:
                    return jsonify({"error": "Invalid token"}), 401
            except AuthenticationError as e:
                return jsonify({"error": str(e)}), 401
            
            return f(current_user_id, *args, **kwargs)
        return decorated
    
    # Authentication routes
    @routes.route("/register", methods=["POST"])
    def register():
        """Register a new user."""
        try:
            data = request.get_json()
            user = auth_service.register_user(
                data.get("username"),
                data.get("password")
            )
            return jsonify({"message": "User created successfully"}), 201
        except AuthenticationError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Registration failed"}), 500
    
    @routes.route("/login", methods=["POST"])
    def login():
        """Login user and return JWT token."""
        try:
            data = request.get_json()
            user = auth_service.authenticate_user(
                data.get("username"),
                data.get("password")
            )
            
            if not user:
                return jsonify({"error": "Invalid credentials"}), 401
            
            token = auth_service.generate_token(user.id)
            return jsonify({"token": token}), 200
        except Exception as e:
            return jsonify({"error": "Login failed"}), 500
    
    # Category routes
    @routes.route("/categories", methods=["GET"])
    @token_required
    def get_categories(current_user_id):
        """Get all categories."""
        try:
            categories = category_service.get_all_categories()
            return jsonify([
                category_service.to_dict(c) for c in categories
            ]), 200
        except Exception as e:
            return jsonify({"error": "Failed to fetch categories"}), 500
    
    @routes.route("/categories", methods=["POST"])
    @token_required
    def create_category(current_user_id):
        """Create a new category."""
        try:
            data = request.get_json()
            category = category_service.create_category(data)
            return jsonify(category_service.to_dict(category)), 201
        except CategoryValidationError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Failed to create category"}), 500
    
    @routes.route("/categories/<int:category_id>", methods=["PUT"])
    @token_required
    def update_category(current_user_id, category_id):
        """Update a category."""
        try:
            data = request.get_json()
            category = category_service.update_category(category_id, data)
            return jsonify({
                "message": "Category updated",
                "id": category.id
            }), 200
        except CategoryNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except CategoryValidationError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Failed to update category"}), 500
    
    @routes.route("/categories/<int:category_id>", methods=["DELETE"])
    @token_required
    def delete_category(current_user_id, category_id):
        """Delete a category."""
        try:
            category_service.delete_category(category_id)
            return jsonify({"message": "Category deleted"}), 200
        except CategoryNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": "Failed to delete category"}), 500
    
    # Task routes
    @routes.route("/tasks", methods=["GET"])
    @token_required
    def get_tasks(current_user_id):
        """Get all tasks sorted by priority criteria."""
        try:
            tasks = task_service.get_all_tasks()
            return jsonify([
                task_service.to_dict(t) for t in tasks
            ]), 200
        except Exception as e:
            return jsonify({"error": "Failed to fetch tasks"}), 500
    
    @routes.route("/tasks/<int:task_id>", methods=["GET"])
    @token_required
    def get_task(current_user_id, task_id):
        """Get a specific task."""
        try:
            task = task_service.get_task_by_id(task_id)
            return jsonify(task_service.to_dict(task)), 200
        except TaskNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": "Failed to fetch task"}), 500
    
    @routes.route("/tasks", methods=["POST"])
    @token_required
    def create_task(current_user_id):
        """Create a new task."""
        try:
            data = request.get_json()
            task = task_service.create_task(data, category_service)
            return jsonify({
                "message": "Task created",
                "id": task.id
            }), 201
        except TaskValidationError as e:
            return jsonify({"error": str(e)}), 400
        except CategoryNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": "Failed to create task"}), 500
    
    @routes.route("/tasks/<int:task_id>", methods=["PUT"])
    @token_required
    def update_task(current_user_id, task_id):
        """Update a task."""
        try:
            data = request.get_json()
            task = task_service.update_task(task_id, data, category_service)
            return jsonify({
                "message": "Task updated",
                "id": task.id
            }), 200
        except TaskNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except TaskValidationError as e:
            return jsonify({"error": str(e)}), 400
        except CategoryNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": "Failed to update task"}), 500
    
    @routes.route("/tasks/<int:task_id>", methods=["DELETE"])
    @token_required
    def delete_task(current_user_id, task_id):
        """Delete a task."""
        try:
            task_service.delete_task(task_id)
            return jsonify({"message": "Task deleted"}), 200
        except TaskNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": "Failed to delete task"}), 500
    
    return routes