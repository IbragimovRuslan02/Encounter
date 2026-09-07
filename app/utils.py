"""Утилиты, декораторы, хелперы для работы с файлами и моделями."""
import os
import re
import secrets
from datetime import datetime
from functools import wraps
from typing import Any

from flask import abort, current_app, flash, redirect, request, session, url_for
from flask_login import current_user
from PIL import Image
from werkzeug.utils import secure_filename

from .extensions import db
from .models import (
    Category, Order, OrderStatus, Product, SellerProfile, SellerStatus, User,
    UserRole,
)


# ─────────────── Slugify ───────────────

def slugify(text: str) -> str:
    """Транслит + безопасный slug."""
    cyrillic_to_latin = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
        "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    text = (text or "").lower().strip()
    out = []
    for ch in text:
        out.append(cyrillic_to_latin.get(ch, ch))
    s = "".join(out)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "item"


def unique_slug(model_cls, base: str, exclude_id: int | None = None) -> str:
    """Генерирует уникальный slug для модели."""
    slug = slugify(base)
    candidate = slug
    i = 1
    while True:
        q = model_cls.query.filter_by(slug=candidate)
        if exclude_id is not None:
            q = q.filter(model_cls.id != exclude_id)
        if not q.first():
            return candidate
        i += 1
        candidate = f"{slug}-{i}"


# ─────────────── Аутентификация ───────────────

def get_user() -> User | None:
    uid = session.get("user_id")
    if not uid:
        return None
    u = db.session.get(User, uid)
    if not u:
        session.clear()
        return None
    return u


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not get_user():
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


def role_required(*roles: str):
    """Декоратор: требует одну из ролей."""
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            u = get_user()
            if not u:
                return redirect(url_for("auth.login", next=request.path))
            if u.role not in roles and not u.is_admin:
                flash("Недостаточно прав.", "error")
                return redirect(url_for("public.home"))
            return view(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        u = get_user()
        if not u:
            return redirect(url_for("auth.login", next=request.path))
        if not u.is_admin:
            flash("Доступ запрещён.", "error")
            return redirect(url_for("public.home"))
        return view(*args, **kwargs)
    return wrapper


def approved_seller_required(view):
    """Требует одобренного продавца."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        u = get_user()
        if not u:
            return redirect(url_for("auth.login", next=request.path))
        if not u.is_approved_seller:
            flash("Чтобы продавать, нужно одобрение магазина.", "warning")
            return redirect(url_for("user.become_seller"))
        return view(*args, **kwargs)
    return wrapper


# ─────────────── Файлы ───────────────

def allowed_file(filename: str, allowed_ext: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_ext


def save_image(file_obj, subfolder: str = "products", max_size=(1200, 1200)) -> str | None:
    """Сохраняет изображение с уникальным именем + делает ресайз.

    Возвращает относительный путь (например 'products/20260908_xxxxx.jpg').
    """
    if not file_obj or not file_obj.filename:
        return None

    ext = file_obj.filename.rsplit(".", 1)[1].lower()
    if ext == "jpeg":
        ext = "jpg"
    if ext not in current_app.config["ALLOWED_IMAGE_EXT"]:
        return None

    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}.{ext}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, secure_filename(unique_name))

    # Ресайз через Pillow
    try:
        img = Image.open(file_obj.stream)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(filepath, quality=85, optimize=True)
    except Exception:
        # Если не картинка — fallback (сохраняем как есть)
        file_obj.stream.seek(0)
        file_obj.save(filepath)

    return os.path.join(subfolder, unique_name)


def delete_file(relative_path: str) -> None:
    if not relative_path:
        return
    full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], relative_path)
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except OSError:
            pass


# ─────────────── Тесты ───────────────

def compute_result_type(test_id: str, answers: list[dict]) -> str:
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


# ─────────────── Форматирование ───────────────

def format_price(value: float) -> str:
    """Форматирует цену: 12 500 ₽"""
    return f"{int(round(value)):,}".replace(",", " ") + " ₽"


def format_date(dt: datetime, fmt: str = "%d.%m.%Y %H:%M") -> str:
    return dt.strftime(fmt) if dt else "—"


def register_template_helpers(app) -> None:
    @app.template_filter("price")
    def _price(v: float) -> str:
        return format_price(v)

    @app.template_filter("dt")
    def _dt(v: datetime, fmt: str = "%d.%m.%Y %H:%M") -> str:
        return format_date(v, fmt)

    @app.template_filter("status_label")
    def _status_label(status: str) -> str:
        labels = {
            OrderStatus.NEW.value: "Новый",
            OrderStatus.CONFIRMED.value: "Подтверждён",
            OrderStatus.SHIPPED.value: "Отправлен",
            OrderStatus.DELIVERED.value: "Доставлен",
            OrderStatus.CANCELLED.value: "Отменён",
        }
        return labels.get(status, status)

    @app.template_filter("role_label")
    def _role_label(role: str) -> str:
        return {
            UserRole.USER.value: "Покупатель",
            UserRole.SELLER.value: "Продавец",
            UserRole.ADMIN.value: "Администратор",
        }.get(role, role)

    @app.template_filter("seller_status_label")
    def _seller_status_label(status: str) -> str:
        return {
            SellerStatus.NONE.value: "—",
            SellerStatus.PENDING.value: "На рассмотрении",
            SellerStatus.APPROVED.value: "Одобрен",
            SellerStatus.REJECTED.value: "Отклонён",
        }.get(status, status)


# ─────────────── Пересчёт рейтингов ───────────────

def recalc_product_rating(product_id: int) -> None:
    """Пересчитывает рейтинг и количество отзывов у товара."""
    from sqlalchemy import func
    from .models import Review
    rating, count = db.session.query(
        func.coalesce(func.avg(Review.rating), 0.0),
        func.count(Review.id),
    ).filter(Review.product_id == product_id).first()
    p = db.session.get(Product, product_id)
    if p:
        p.rating = round(float(rating), 2)
        p.reviews_count = count
        db.session.commit()


def recalc_seller_rating(seller_id: int) -> None:
    """Пересчитывает рейтинг продавца по отзывам на все его товары."""
    from sqlalchemy import func
    from .models import Product, Review
    rating, count = db.session.query(
        func.coalesce(func.avg(Review.rating), 0.0),
        func.count(Review.id),
    ).join(Product, Review.product_id == Product.id).filter(
        Product.seller_id == seller_id
    ).first()
    sp = SellerProfile.query.filter_by(user_id=seller_id).first()
    if sp:
        sp.rating = round(float(rating), 2)
        sp.reviews_count = count
        db.session.commit()
