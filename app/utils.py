"""Вспомогательные функции и декораторы."""
from functools import wraps

from flask import flash, redirect, request, session, url_for

from .extensions import db
from .models import User


def get_user() -> User | None:
    """Возвращает текущего пользователя по сессии или None."""
    uid = session.get("user_id")
    if not uid:
        return None
    u = db.session.get(User, uid)
    if not u:
        session.clear()
        return None
    return u


def login_required(view):
    """Декоратор: требуется залогиненный пользователь."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not get_user():
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    """Декоратор: требуется администратор."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        u = get_user()
        if not u:
            return redirect(url_for("auth.login", next=request.path))
        if not u.is_admin:
            flash("Доступ запрещён.", "error")
            return redirect(url_for("public.tests_page"))
        return view(*args, **kwargs)

    return wrapper


def compute_result_type(test_id: str, answers: list[dict]) -> str:
    """Подсчитывает самый частый тип ответа. Возвращает ключ результата."""
    from .tests_data import TESTS

    counts: dict[str, int] = {}
    for a in answers:
        t = a.get("type")
        if not t:
            continue
        counts[t] = counts.get(t, 0) + 1

    if not counts:
        return next(iter(TESTS[test_id]["results"].keys()))

    max_count = max(counts.values())
    for k in counts.keys():
        if counts[k] == max_count:
            return k

    return next(iter(TESTS[test_id]["results"].keys()))
