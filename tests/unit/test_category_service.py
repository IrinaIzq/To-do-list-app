"""Unit tests for CategoryService."""
import pytest
from backend.services.category_service import CategoryService, CategoryValidationError

class TestCategoryService:
    def test_create_category_success(self, app, category_service):
        """Test successful category creation."""
        with app.app_context():
            category = category_service.create_category({
                'name': 'Test',
                'description': 'Test desc'
            })
            
            assert category.name == 'Test'
    
    def test_create_category_without_name(self, app, category_service):
        """Test category creation without name."""
        with app.app_context():
            with pytest.raises(CategoryValidationError):
                category_service.create_category({})