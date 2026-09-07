"""Регистрация blueprints."""
from .public import bp as public_bp
from .auth import bp as auth_bp
from .user import bp as user_bp
from .seller import bp as seller_bp
from .admin import bp as admin_bp
from .api import bp as api_bp

__all__ = ["public_bp", "auth_bp", "user_bp", "seller_bp", "admin_bp", "api_bp"]
