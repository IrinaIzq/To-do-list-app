"""
Task service following Single Responsibility Principle.
Handles all task-related business logic with proper error handling.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import case
from backend.database import db, Task, Category


class TaskNotFoundError(Exception):
    """Exception raised when task is not found."""
    pass


class TaskValidationError(Exception):
    """Exception raised when task validation fails."""
    pass


class TaskService:
    """Service class for task operations."""
    
    VALID_PRIORITIES = ['Low', 'Medium', 'High']
    VALID_STATUSES = ['Pending', 'In Progress', 'Completed']
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks sorted by priority criteria.
        
        Returns:
            List of Task objects sorted by:
            1. Due date (earliest first, nulls last)
            2. Priority (High -> Medium -> Low -> None)
            3. Estimated hours (highest first)
        """
        priority_order = case(
            (Task.priority == "High", 1),
            (Task.priority == "Medium", 2),
            (Task.priority == "Low", 3),
            else_=4
        )
        
        return Task.query.order_by(
            Task.due_date.asc().nullslast(),
            priority_order,
            Task.estimated_hours.desc().nullslast()
        ).all()
    
    def get_task_by_id(self, task_id: int) -> Task:
        """
        Get task by ID.
        
        Args:
            task_id: ID of task to retrieve
            
        Returns:
            Task object
            
        Raises:
            TaskNotFoundError: If task not found
        """
        task = Task.query.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")
        return task
    
    def create_task(self, task_data: Dict[str, Any], 
                   category_service: 'CategoryService') -> Task:
        """
        Create a new task.
        
        Args:
            task_data: Dictionary containing task information
            category_service: CategoryService instance for category operations
            
        Returns:
            Created Task object
            
        Raises:
            TaskValidationError: If validation fails
        """
        # Validate required fields
        if not task_data.get('title'):
            raise TaskValidationError("Task title is required")
        
        if not task_data.get('category_name') and not task_data.get('category_id'):
            raise TaskValidationError("Category is required")
        
        # Validate priority if provided
        if task_data.get('priority') and \
           task_data['priority'] not in self.VALID_PRIORITIES:
            raise TaskValidationError(
                f"Priority must be one of: {', '.join(self.VALID_PRIORITIES)}"
            )
        
        # Validate status if provided
        status = task_data.get('status', 'Pending')
        if status not in self.VALID_STATUSES:
            raise TaskValidationError(
                f"Status must be one of: {', '.join(self.VALID_STATUSES)}"
            )
        
        # Validate estimated hours
        estimated_hours = task_data.get('estimated_hours')
        if estimated_hours is not None:
            try:
                estimated_hours = float(estimated_hours)
                if estimated_hours < 0:
                    raise TaskValidationError(
                        "Estimated hours must be non-negative"
                    )
            except (ValueError, TypeError):
                raise TaskValidationError("Estimated hours must be a number")
        
        # Get or create category
        category = self._get_or_create_category(
            task_data, 
            category_service
        )
        
        # Create task
        task = Task(
            title=task_data['title'],
            description=task_data.get('description'),
            estimated_hours=estimated_hours,
            due_date=task_data.get('due_date'),
            priority=task_data.get('priority'),
            status=status,
            category_id=category.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        return task
    
    def update_task(self, task_id: int, task_data: Dict[str, Any],
                   category_service: 'CategoryService') -> Task:
        """
        Update an existing task.
        
        Args:
            task_id: ID of task to update
            task_data: Dictionary containing updated task information
            category_service: CategoryService instance
            
        Returns:
            Updated Task object
            
        Raises:
            TaskNotFoundError: If task not found
            TaskValidationError: If validation fails
        """
        task = self.get_task_by_id(task_id)
        
        # Update fields if provided
        if 'title' in task_data:
            if not task_data['title']:
                raise TaskValidationError("Task title cannot be empty")
            task.title = task_data['title']
        
        if 'description' in task_data:
            task.description = task_data['description']
        
        if 'status' in task_data:
            if task_data['status'] not in self.VALID_STATUSES:
                raise TaskValidationError(
                    f"Status must be one of: {', '.join(self.VALID_STATUSES)}"
                )
            task.status = task_data['status']
        
        if 'priority' in task_data:
            if task_data['priority'] and \
               task_data['priority'] not in self.VALID_PRIORITIES:
                raise TaskValidationError(
                    f"Priority must be one of: {', '.join(self.VALID_PRIORITIES)}"
                )
            task.priority = task_data['priority']
        
        if 'estimated_hours' in task_data:
            if task_data['estimated_hours'] is not None:
                try:
                    hours = float(task_data['estimated_hours'])
                    if hours < 0:
                        raise TaskValidationError(
                            "Estimated hours must be non-negative"
                        )
                    task.estimated_hours = hours
                except (ValueError, TypeError):
                    raise TaskValidationError("Estimated hours must be a number")
            else:
                task.estimated_hours = None
        
        if 'due_date' in task_data:
            task.due_date = task_data['due_date']
        
        # Update category if provided
        if 'category_name' in task_data:
            category = category_service.get_category_by_name(
                task_data['category_name']
            )
            if category:
                task.category_id = category.id
        elif 'category_id' in task_data:
            if task_data['category_id'] is None:
                raise TaskValidationError("Category is required")
            # Verify category exists
            category_service.get_category_by_id(task_data['category_id'])
            task.category_id = task_data['category_id']
        
        db.session.commit()
        return task
    
    def delete_task(self, task_id: int) -> None:
        """
        Delete a task.
        
        Args:
            task_id: ID of task to delete
            
        Raises:
            TaskNotFoundError: If task not found
        """
        task = self.get_task_by_id(task_id)
        db.session.delete(task)
        db.session.commit()
    
    def _get_or_create_category(self, task_data: Dict[str, Any],
                               category_service: 'CategoryService') -> Category:
        """
        Get existing category or create new one.
        
        Args:
            task_data: Task data containing category information
            category_service: CategoryService instance
            
        Returns:
            Category object
        """
        if task_data.get('category_name'):
            category = category_service.get_category_by_name(
                task_data['category_name']
            )
            if not category:
                category = category_service.create_category({
                    'name': task_data['category_name'],
                    'description': 'Auto-created'
                })
            return category
        elif task_data.get('category_id'):
            return category_service.get_category_by_id(task_data['category_id'])
        else:
            raise TaskValidationError("Category is required")
    
    def to_dict(self, task: Task) -> Dict[str, Any]:
        """
        Convert task object to dictionary.
        
        Args:
            task: Task object to convert
            
        Returns:
            Dictionary representation of task
        """
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'estimated_hours': task.estimated_hours,
            'due_date': task.due_date,
            'priority': task.priority,
            'category_id': task.category_id,
            'category': task.category.name if task.category else None
        }