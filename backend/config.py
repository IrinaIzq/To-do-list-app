import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    APP_NAME = "To-Do Manager"
    APP_VERSION = "2.0.0"
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Always provide a valid default database URI
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    
    CORS_ORIGINS = ["*"]


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Override with env var if set
    if os.getenv("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


class ProductionConfig(Config):
    """Production configuration"""
    # In production, use environment variable or fallback
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///production.db")


def get_config(name):
    """Get configuration class by name"""
    configs = {
        "testing": TestingConfig,
        "production": ProductionConfig,
        "development": Config,
    }
    return configs.get(name, Config)