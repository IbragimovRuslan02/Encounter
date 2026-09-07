"""Модели SQLAlchemy."""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(db.Model):
    """Пользователь Encounter."""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    results = db.relationship(
        "TestResult", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username} admin={self.is_admin}>"


class TestResult(db.Model):
    """Результат прохождения теста."""

    __tablename__ = "test_result"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )

    test_id = db.Column(db.String(64), nullable=False, index=True)
    test_name = db.Column(db.String(160), nullable=False)

    result_summary = db.Column(db.String(220), nullable=False)
    detailed_answers = db.Column(db.Text, nullable=False)  # JSON string
    date_passed = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<TestResult #{self.id} {self.test_id} -> {self.result_summary!r}>"
