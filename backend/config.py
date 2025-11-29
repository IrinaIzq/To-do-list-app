import os

class BaseConfig:
    APP_NAME = "To-Do Manager"
    APP_VERSION = "2.0.0"
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ["*"]

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///data.db")

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///data.db")

def get_config(name='development'):
    if name == 'production':
        return ProductionConfig
    return DevelopmentConfig