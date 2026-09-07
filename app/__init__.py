"""Application factory."""
import os

from flask import Flask

from .config import get_config
from .extensions import csrf, db, login_manager
from .utils import get_user, register_template_helpers


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config(config_name))

    # Создаём нужные папки
    instance_dir = os.path.dirname(
        app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    )
    os.makedirs(instance_dir, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    for sub in ("products", "avatars", "banners"):
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], sub), exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(uid: str):
        from .models import User
        return db.session.get(User, int(uid))

    @app.context_processor
    def inject_globals():
        from .models import CartItem
        u = get_user()
        cart_count = 0
        if u:
            cart_count = CartItem.query.filter_by(user_id=u.id).count()
        return {
            "is_logged_in": bool(u),
            "is_admin": u.is_admin if u else False,
            "is_seller": u.is_seller if u else False,
            "is_approved_seller": u.is_approved_seller if u else False,
            "nav_user": u,
            "cart_count": cart_count,
        }

    register_template_helpers(app)

    # Blueprints
    from .blueprints import admin_bp, api_bp, auth_bp, public_bp, seller_bp, user_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found(_e):
        from flask import render_template
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(_e):
        from flask import render_template
        return render_template("403.html"), 403

    return app
