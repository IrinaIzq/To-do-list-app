from backend.database import db
from backend.models.category import Category


class CategoryValidationError(Exception):
    """Raised when category validation fails."""
    pass


class CategoryNotFoundError(Exception):
    """Raised when a category is not found."""
    pass


class CategoryService:

    def get_all_categories(self):
        """Return all categories."""
        return Category.query.all()

    def get_category(self, category_id):
        """Return a single category or raise."""
        category = Category.query.get(category_id)
        if not category:
            raise CategoryNotFoundError(f"Category {category_id} not found")
        return category

    def create_category(self, name, user_id=None):
        """Create a new category."""

        if not name or name.strip() == "":
            raise CategoryValidationError("Name is required")

        category = Category(name=name, user_id=user_id)
        db.session.add(category)
        db.session.commit()
        return category

    def delete_category(self, category_id):
        """Delete category or raise if not found."""
        category = Category.query.get(category_id)
        if not category:
            raise CategoryNotFoundError(f"Category {category_id} not found")

        db.session.delete(category)
        db.session.commit()
        return True

    def update_category(self, category_id, **kwargs):
        """Update an existing category."""
        category = Category.query.get(category_id)
        if not category:
            raise CategoryNotFoundError(f"Category {category_id} not found")

        allowed_fields = {"name"}

        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(category, field, value)

        db.session.commit()
        return category
