"""Конфигурация Encounter."""
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'encounter.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None):
    env = name or os.environ.get("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)
