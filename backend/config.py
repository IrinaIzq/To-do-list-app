import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    APP_NAME = "To-Do Manager"
    APP_VERSION = "2.0.0"
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default DB for dev - always provide a valid URI
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///dev.db"
    )

    CORS_ORIGINS = ["*"]


class TestingConfig(Config):
    TESTING = True
    # In-memory database for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    # In production, DATABASE_URL must be set or fall back to a file
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///production.db"
    )


def get_config(name):
    if name == "testing":
        return TestingConfig
    if name == "production":
        return ProductionConfig
    return Config