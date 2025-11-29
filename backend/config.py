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
    
    # For Azure: Use in-memory database (data will be lost on restart)
    # This is because Azure Web Apps don't have persistent file storage for SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    
    CORS_ORIGINS = ["*"]


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Production configuration"""
    # For Azure production: use in-memory SQLite or set DATABASE_URL to PostgreSQL/MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///:memory:")


def get_config(name):
    """Get configuration class by name"""
    configs = {
        "testing": TestingConfig,
        "production": ProductionConfig,
        "development": Config,
    }
    return configs.get(name, Config)