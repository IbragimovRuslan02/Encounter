"""Публичные маршруты (главная, тесты, результаты)."""
from flask import Blueprint, abort, flash, redirect, render_template, url_for

from ..extensions import db
from ..models import TestResult
from ..tests_data import TESTS
from ..utils import get_user, login_required

bp = Blueprint("public", __name__)


@bp.route("/")
def home():
    """Главная страница."""
    return render_template("home.html", show_categories=True)


@bp.route("/profile")
def profile_entry():
    """Иконка профиля: логин/регистрация для гостей, история для авторизованных."""
    u = get_user()
    if not u:
        return redirect(url_for("auth.login", next=url_for("public.profile_entry")))
    if u.is_admin:
        return redirect(url_for("admin.admin_dashboard"))
    return redirect(url_for("public.my_results"))


@bp.route("/tests")
@login_required
def tests_page():
    """Список доступных тестов."""
    u = get_user()
    results = (
        TestResult.query.filter_by(user_id=u.id)
        .order_by(TestResult.date_passed.desc())
        .all()
    )
    latest: dict[str, TestResult] = {}
    for r in results:
        if r.test_id not in latest:
            latest[r.test_id] = r
    return render_template("tests.html", tests=TESTS, latest_results=latest)


@bp.route("/quiz/<test_id>")
@login_required
def quiz(test_id: str):
    """Страница прохождения конкретного теста."""
    if test_id not in TESTS:
        flash("Тест не найден.", "error")
        return redirect(url_for("public.tests_page"))
    return render_template("quiz.html", test_id=test_id, test=TESTS[test_id])


@bp.route("/result/<int:result_id>")
@login_required
def result_page(result_id: int):
    """Детальная страница результата."""
    import json

    u = get_user()
    r = db.session.get(TestResult, result_id)
    if not r:
        abort(404)
    if r.user_id != u.id and not u.is_admin:
        abort(403)

    try:
        detailed = json.loads(r.detailed_answers)
    except (ValueError, TypeError):
        detailed = {"raw": r.detailed_answers}

    return render_template("result.html", r=r, detailed=detailed)


@bp.route("/my_results")
@login_required
def my_results():
    """История прохождений пользователя."""
    u = get_user()
    results = (
        TestResult.query.filter_by(user_id=u.id)
        .order_by(TestResult.date_passed.desc())
        .all()
    )
    return render_template("my_results.html", results=results)
