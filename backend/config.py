import os

class BaseConfig:
    SECRET_KEY = "dev-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prod.db")


def get_config(name: str = "default"):
    """
    Tests expect this function, and expect it to work with NO arguments.
    """
    if name == "testing":
        return TestingConfig()
    elif name == "development":
        return DevelopmentConfig()
    elif name == "production":
        return ProductionConfig()
    else:
        # default fallback
        env = os.getenv("FLASK_ENV", "production")

        if env == "development":
            return DevelopmentConfig()
        elif env == "testing":
            return TestingConfig()
        else:
            return ProductionConfig()