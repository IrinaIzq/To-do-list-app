from backend.database import db
from backend.models.category import Category


class CategoryValidationError(Exception):
    pass


class CategoryService:

    # Required by tests
    CategoryValidationError = CategoryValidationError

    def create_category(self, user_id, name, description=None):
        
        if not name or not name.strip():
            raise CategoryValidationError("Name required")

        existing = Category.query.filter_by(user_id=user_id, name=name).first()
        if existing:
            raise CategoryValidationError("Duplicate category")

        cat = Category(
            name=name.strip(),
            description=description.strip() if description else None,
            user_id=user_id,
        )
        db.session.add(cat)
        db.session.commit()
        return cat

    def get_all_categories(self, user_id):
        return Category.query.filter_by(user_id=user_id).all()

    def update_category(self, category_id, name, description=None):
        cat = db.session.get(Category, category_id)
        if not cat:
            raise CategoryValidationError("Category not found")

        if not name or not name.strip():
            raise CategoryValidationError("Name required")

        cat.name = name.strip()
        cat.description = description.strip() if description else None
        db.session.commit()
        return cat

    def delete_category(self, category_id):
        cat = db.session.get(Category, category_id)
        if not cat:
            raise CategoryValidationError("Category not found")

        db.session.delete(cat)
        db.session.commit()