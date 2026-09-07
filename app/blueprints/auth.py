"""Аутентификация: вход, регистрация, выход."""
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for,
)

from ..extensions import db
from ..models import User
from ..utils import get_user

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if get_user():
        return redirect(url_for("public.tests_page"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        u = User.query.filter_by(username=username).first()
        if u and u.check_password(password):
            session["user_id"] = u.id
            session["username"] = u.username
            session["is_admin"] = bool(u.is_admin)

            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)

            return redirect(
                url_for("admin.admin_dashboard") if u.is_admin
                else url_for("public.tests_page")
            )

        flash("Неверный логин или пароль.", "error")

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if get_user():
        return redirect(url_for("public.tests_page"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        if len(username) < 3:
            flash("Логин минимум 3 символа.", "error")
            return render_template("register.html")
        if len(password) < 4:
            flash("Пароль минимум 4 символа.", "error")
            return render_template("register.html")
        if password != confirm:
            flash("Пароли не совпадают.", "error")
            return render_template("register.html")
        if User.query.filter_by(username=username).first():
            flash("Такой пользователь уже существует.", "error")
            return render_template("register.html")

        u = User(username=username, is_admin=False)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()

        flash("Регистрация успешна. Войдите.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("public.home"))
