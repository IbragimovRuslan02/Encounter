"""Маршруты админ-панели."""
from flask import Blueprint, jsonify, render_template

from ..extensions import db
from ..models import TestResult, User
from ..utils import admin_required

bp = Blueprint("admin", __name__)


@bp.route("/admin_dashboard")
@admin_required
def admin_dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    total_results = TestResult.query.count()
    return render_template(
        "admin.html", users=users, total_results=total_results
    )


@bp.route("/admin_dashboard/user/<int:user_id>")
@admin_required
def admin_user_detail(user_id: int):
    u = db.session.get(User, user_id)
    if not u:
        return jsonify({"ok": False, "error": "User not found"}), 404

    results = (
        TestResult.query.filter_by(user_id=u.id)
        .order_by(TestResult.date_passed.desc())
        .all()
    )

    return jsonify({
        "ok": True,
        "user": {
            "id": u.id,
            "username": u.username,
            "is_admin": bool(u.is_admin),
            "created_at": u.created_at.strftime("%d.%m.%Y %H:%M"),
        },
        "results": [
            {
                "id": r.id,
                "test_name": r.test_name,
                "test_id": r.test_id,
                "result_summary": r.result_summary,
                "date_passed": r.date_passed.strftime("%d.%m.%Y %H:%M"),
            }
            for r in results
        ],
    })
