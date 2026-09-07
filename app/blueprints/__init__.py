"""Blueprints Encounter."""
from .public import bp as public_bp
from .auth import bp as auth_bp
from .admin import bp as admin_bp
from .api import bp as api_bp

__all__ = ["public_bp", "auth_bp", "admin_bp", "api_bp"]
