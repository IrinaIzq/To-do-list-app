def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "estimated_hours": task.estimated_hours,
        "due_date": task.due_date,
        "priority": task.priority,
        "status": task.status,
        "category_id": task.category_id,
    }

def category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
    }
