"""API-маршруты: отправка ответов на тесты + страница тестов."""
import json

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from ..extensions import db
from ..models import TestResult
from ..tests_data import TESTS
from ..utils import compute_result_type, get_user, login_required

bp = Blueprint("api", __name__)


@bp.route("/tests")
@login_required
def tests_page():
    """Страница со списком тестов."""
    u = get_user()
    results = (
        TestResult.query.filter_by(user_id=u.id)
        .order_by(TestResult.date_passed.desc())
        .all()
    )
    latest = {}
    for r in results:
        if r.test_id not in latest:
            latest[r.test_id] = r
    return render_template("tests.html", tests=TESTS, latest_results=latest)


@bp.route("/quiz/<test_id>")
@login_required
def quiz(test_id: str):
    if test_id not in TESTS:
        flash("Тест не найден.", "error")
        return redirect(url_for("api.tests_page"))
    return render_template("quiz.html", test_id=test_id, test=TESTS[test_id])


@bp.route("/api/submit/<test_id>", methods=["POST"])
@login_required
def submit(test_id: str):
    if test_id not in TESTS:
        return jsonify({"ok": False, "error": "Тест не найден"}), 404
    payload = request.get_json(silent=True) or {}
    answers = payload.get("answers") or []
    if not isinstance(answers, list) or not answers:
        return jsonify({"ok": False, "error": "Ответы не получены"}), 400
    rtype = compute_result_type(test_id, answers)
    summary = TESTS[test_id]["results"][rtype]
    u = get_user()
    detailed = {"test_id": test_id, "result_type": rtype, "answers": answers}
    tr = TestResult(
        user_id=u.id,
        test_id=test_id,
        test_name=TESTS[test_id]["name"],
        result_summary=summary,
        detailed_answers=json.dumps(detailed, ensure_ascii=False),
    )
    db.session.add(tr)
    db.session.commit()
    return jsonify({"ok": True, "result_id": tr.id})


@bp.route("/result/<int:result_id>")
@login_required
def result_page(result_id: int):
    u = get_user()
    r = db.session.get(TestResult, result_id) or (None,)
    if r is None:
        from flask import abort
        abort(404)
    if r.user_id != u.id and not u.is_admin:
        from flask import abort
        abort(403)
    try:
        detailed = json.loads(r.detailed_answers)
    except (ValueError, TypeError):
        detailed = {"raw": r.detailed_answers}
    return render_template("result.html", r=r, detailed=detailed)
