from backend.database import db
from backend.models.category import Category

class CategoryValidationError(Exception):
    pass

class CategoryService:

    def create_category(self, name, description):
        if not name or not description:
            raise CategoryValidationError("Missing fields")

        if Category.query.filter_by(name=name).first():
            raise CategoryValidationError("Category already exists")

        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        return category

    def get_all_categories(self):
        return Category.query.all()

    def update_category(self, category_id, name, description):
        category = Category.query.get(category_id)
        if not category:
            raise CategoryValidationError("Category not found")

        category.name = name
        category.description = description
        db.session.commit()
        return category

    def delete_category(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            raise CategoryValidationError("Category not found")
        db.session.delete(category)
        db.session.commit()