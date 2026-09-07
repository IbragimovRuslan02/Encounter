"""Аутентификация: вход, регистрация, выход."""
from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for,
)

from ..extensions import db
from ..forms import LoginForm, RegisterForm
from ..models import User, UserRole
from ..utils import get_user

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if get_user():
        return redirect(url_for("public.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = (form.email.data or "").strip() or None

        if User.query.filter_by(username=username).first():
            flash("Этот логин уже занят.", "error")
            return render_template("register.html", form=form)
        if email and User.query.filter_by(email=email).first():
            flash("Этот email уже используется.", "error")
            return render_template("register.html", form=form)

        u = User(username=username, email=email, role=UserRole.USER.value)
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()

        session["user_id"] = u.id
        flash("Регистрация успешна! Добро пожаловать.", "success")
        return redirect(url_for("public.home"))

    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if get_user():
        return redirect(url_for("public.home"))

    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data.strip()).first()
        if u and u.check_password(form.password.data):
            session.clear()
            session["user_id"] = u.id
            session.permanent = True
            flash(f"Добро пожаловать, {u.username}!", "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            # Редирект по роли
            if u.is_admin:
                return redirect(url_for("admin.admin_dashboard"))
            if u.is_approved_seller:
                return redirect(url_for("seller.seller_dashboard"))
            return redirect(url_for("public.home"))
        flash("Неверный логин или пароль.", "error")
    return render_template("login.html", form=form)


@bp.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("public.home"))
