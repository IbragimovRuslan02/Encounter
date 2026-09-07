"""Инициализация БД и сид-данные."""
from .extensions import db
from .models import User


def init_db() -> None:
    """Создаёт таблицы и админа по умолчанию."""
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
