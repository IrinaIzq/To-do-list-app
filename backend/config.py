import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    APP_NAME = "To-Do Manager"
    APP_VERSION = "2.0.0"
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Always use in-memory database for Azure
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    
    CORS_ORIGINS = ["*"]


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Production configuration"""
    # In-memory database - data is temporary but works on Azure
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


def get_config(name):
    """Get configuration class by name"""
    configs = {
        "testing": TestingConfig,
        "production": ProductionConfig,
        "development": Config,
    }
    return configs.get(name, Config)