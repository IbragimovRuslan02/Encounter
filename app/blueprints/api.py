"""API-маршруты (отправка ответов на тест)."""
import json

from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import TestResult
from ..tests_data import TESTS
from ..utils import compute_result_type, get_user, login_required

bp = Blueprint("api", __name__)


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
    detailed = {
        "test_id": test_id,
        "result_type": rtype,
        "answers": answers,
    }

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
