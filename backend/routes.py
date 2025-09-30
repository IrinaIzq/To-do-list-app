from flask import Blueprint, request, jsonify
from database import db
from models import Task, Category
from utils import task_to_dict, category_to_dict

routes = Blueprint("routes", __name__)

# Tasks routes

@routes.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task_to_dict(t) for t in tasks])

@routes.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    new_task = Task(
        title=data.get("title"),
        description=data.get("description"),
        estimated_hours=data.get("estimated_hours"),
        due_date=data.get("due_date"),
        priority=data.get("priority"),
        status=data.get("status", "pending"),
        category_id=data.get("category_id"),
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created", "id": new_task.id}), 201

@routes.route("/tasks/<int:task_id>", methods=["PUT"])
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

@routes.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})

# Category routes

@routes.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify([category_to_dict(c) for c in categories])

@routes.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    new_category = Category(
        name=data.get("name"),
        description=data.get("description"),
    )
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Category created", "id": new_category.id}), 201

@routes.route("/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    category.name = data.get("name", category.name)
    category.description = data.get("description", category.description)
