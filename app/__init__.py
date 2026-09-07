"""Application factory."""
import os

from flask import Flask

from .config import get_config
from .extensions import db
from .utils import get_user


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config(config_name))

    # Instance-папка для SQLite
    instance_dir = os.path.dirname(
        app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    )
    os.makedirs(instance_dir, exist_ok=True)

    db.init_app(app)

    @app.context_processor
    def inject_globals():
        u = get_user()
        return {
            "is_logged_in": bool(u),
            "is_admin": bool(u.is_admin) if u else False,
            "nav_user": u,
        }

    from .blueprints import admin_bp, api_bp, auth_bp, public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app
