"""
Category service following Single Responsibility Principle.
Handles all category-related business logic.
"""
from typing import List, Optional, Dict, Any
from database import db, Category


class CategoryNotFoundError(Exception):
    """Exception raised when category is not found."""
    pass


class CategoryValidationError(Exception):
    """Exception raised when category validation fails."""
    pass


class CategoryService:
    """Service class for category operations."""
    
    def get_all_categories(self) -> List[Category]:
        """
        Get all categories.
        
        Returns:
            List of Category objects
        """
        return Category.query.all()
    
    def get_category_by_id(self, category_id: int) -> Category:
        """
        Get category by ID.
        
        Args:
            category_id: ID of category to retrieve
            
        Returns:
            Category object
            
        Raises:
            CategoryNotFoundError: If category not found
        """
        category = Category.query.get(category_id)
        if not category:
            raise CategoryNotFoundError(
                f"Category with id {category_id} not found"
            )
        return category
    
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """
        Get category by name.
        
        Args:
            name: Name of category to retrieve
            
        Returns:
            Category object if found, None otherwise
        """
        return Category.query.filter_by(name=name).first()
    
    def create_category(self, category_data: Dict[str, Any]) -> Category:
        """
        Create a new category.
        
        Args:
            category_data: Dictionary containing category information
            
        Returns:
            Created Category object
            
        Raises:
            CategoryValidationError: If validation fails
        """
        if not category_data.get('name'):
            raise CategoryValidationError("Category name is required")
        
        # Check if category already exists
        if self.get_category_by_name(category_data['name']):
            raise CategoryValidationError("Category already exists")
        
        category = Category(
            name=category_data['name'],
            description=category_data.get('description')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return category
    
    def update_category(self, category_id: int, 
                       category_data: Dict[str, Any]) -> Category:
        """
        Update an existing category.
        
        Args:
            category_id: ID of category to update
            category_data: Dictionary containing updated category information
            
        Returns:
            Updated Category object
            
        Raises:
            CategoryNotFoundError: If category not found
            CategoryValidationError: If validation fails
        """
        category = self.get_category_by_id(category_id)
        
        if 'name' in category_data:
            if not category_data['name']:
                raise CategoryValidationError("Category name cannot be empty")
            
            # Check if new name conflicts with existing category
            existing = self.get_category_by_name(category_data['name'])
            if existing and existing.id != category_id:
                raise CategoryValidationError("Category name already exists")
            
            category.name = category_data['name']
        
        if 'description' in category_data:
            category.description = category_data['description']
        
        db.session.commit()
        return category
    
    def delete_category(self, category_id: int) -> None:
        """
        Delete a category.
        
        Args:
            category_id: ID of category to delete
            
        Raises:
            CategoryNotFoundError: If category not found
        """
        category = self.get_category_by_id(category_id)
        db.session.delete(category)
        db.session.commit()
    
    def to_dict(self, category: Category) -> Dict[str, Any]:
        """
        Convert category object to dictionary.
        
        Args:
            category: Category object to convert
            
        Returns:
            Dictionary representation of category
        """
        return {
            'id': category.id,
            'name': category.name,
            'description': category.description
        }