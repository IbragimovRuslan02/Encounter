"""Маршруты админ-панели."""
from datetime import datetime, timedelta
from flask import (
    Blueprint, abort, flash, redirect, render_template, request, url_for,
)
from sqlalchemy import func

from ..extensions import db
from ..models import (
    Category, Conversation, Favorite, Message, Order, OrderStatus, Product,
    Review, SellerProfile, SellerStatus, TestResult, User, UserRole,
)
from ..utils import admin_required, delete_file, get_user, save_image

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def admin_dashboard():
    total_users = User.query.filter(User.role != UserRole.ADMIN.value).count()
    total_sellers = User.query.filter_by(role=UserRole.SELLER.value).count()
    pending_sellers = SellerProfile.query.filter_by(
        status=SellerStatus.PENDING.value
    ).count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    new_orders = Order.query.filter_by(status=OrderStatus.NEW.value).count()
    total_revenue = db.session.query(
        func.coalesce(func.sum(Order.total), 0.0)
    ).filter(Order.status != OrderStatus.CANCELLED.value).scalar() or 0
    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_sellers=total_sellers,
        pending_sellers=pending_sellers,
        total_products=total_products,
        total_orders=total_orders,
        new_orders=new_orders,
        total_revenue=total_revenue,
    )


# ─────────────── Пользователи ───────────────

@bp.route("/users")
@admin_required
def users_list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users_list.html", users=users)


@bp.route("/users/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = db.session.get(User, user_id) or abort(404)
    orders = (
        Order.query.filter_by(customer_id=user.id)
        .order_by(Order.created_at.desc())
        .limit(10)
        .all()
    ) if user.role == UserRole.USER.value else []
    products = (
        Product.query.filter_by(seller_id=user.id)
        .order_by(Product.created_at.desc())
        .limit(10)
        .all()
    ) if user.role == UserRole.SELLER.value else []
    return render_template("admin/user_detail.html", user=user, orders=orders, products=products)


@bp.route("/users/<int:user_id>/role", methods=["POST"])
@admin_required
def user_role_change(user_id):
    user = db.session.get(User, user_id) or abort(404)
    new_role = request.form.get("role")
    if new_role in (UserRole.USER.value, UserRole.SELLER.value, UserRole.ADMIN.value):
        user.role = new_role
        db.session.commit()
        flash("Роль обновлена", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


# ─────────────── Заявки на продавца ───────────────

@bp.route("/sellers")
@admin_required
def sellers_list():
    status = request.args.get("status", SellerStatus.PENDING.value)
    profiles = (
        SellerProfile.query.filter_by(status=status)
        .order_by(SellerProfile.applied_at.desc())
        .all()
    )
    counts = {
        s: SellerProfile.query.filter_by(status=s).count()
        for s in (SellerStatus.PENDING.value, SellerStatus.APPROVED.value, SellerStatus.REJECTED.value)
    }
    return render_template(
        "admin/sellers_list.html",
        profiles=profiles,
        current_status=status,
        counts=counts,
    )


@bp.route("/sellers/<int:profile_id>")
@admin_required
def seller_detail(profile_id):
    sp = db.session.get(SellerProfile, profile_id) or abort(404)
    products = (
        Product.query.filter_by(seller_id=sp.user_id)
        .order_by(Product.created_at.desc())
        .all()
    )
    return render_template("admin/seller_detail.html", profile=sp, products=products)


@bp.route("/sellers/<int:profile_id>/approve", methods=["POST"])
@admin_required
def seller_approve(profile_id):
    sp = db.session.get(SellerProfile, profile_id) or abort(404)
    sp.status = SellerStatus.APPROVED.value
    sp.reviewed_at = datetime.utcnow()
    sp.user.role = UserRole.SELLER.value
    db.session.commit()
    flash(f"Магазин «{sp.shop_name}» одобрен", "success")
    return redirect(url_for("admin.sellers_list"))


@bp.route("/sellers/<int:profile_id>/reject", methods=["POST"])
@admin_required
def seller_reject(profile_id):
    sp = db.session.get(SellerProfile, profile_id) or abort(404)
    reason = (request.form.get("reason") or "").strip()
    sp.status = SellerStatus.REJECTED.value
    sp.reviewed_at = datetime.utcnow()
    sp.rejection_reason = reason
    sp.user.role = UserRole.USER.value  # возвращаем обычную роль
    db.session.commit()
    flash("Заявка отклонена", "info")
    return redirect(url_for("admin.sellers_list"))


# ─────────────── Товары ───────────────

@bp.route("/products")
@admin_required
def products_list():
    products = Product.query.order_by(Product.created_at.desc()).limit(100).all()
    return render_template("admin/products_list.html", products=products)


@bp.route("/products/<int:product_id>/toggle", methods=["POST"])
@admin_required
def product_toggle(product_id):
    p = db.session.get(Product, product_id) or abort(404)
    p.is_approved = not p.is_approved
    db.session.commit()
    flash("Статус товара изменён", "success")
    return redirect(url_for("admin.products_list"))


@bp.route("/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def product_delete(product_id):
    p = db.session.get(Product, product_id) or abort(404)
    for img in p.images:
        delete_file(img.file_path)
    db.session.delete(p)
    db.session.commit()
    flash("Товар удалён", "info")
    return redirect(url_for("admin.products_list"))


# ─────────────── Заказы ───────────────

@bp.route("/orders")
@admin_required
def orders_list():
    status = request.args.get("status", "").strip() or None
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).limit(200).all()
    return render_template("admin/orders_list.html", orders=orders, current_status=status)


# ─────────────── Категории ───────────────

@bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories_list():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        icon = (request.form.get("icon") or "").strip()
        parent_id = request.form.get("parent_id", type=int)
        if name:
            from ..utils import slugify, unique_slug
            slug = unique_slug(Category, name)
            c = Category(name=name, slug=slug, icon=icon, parent_id=parent_id or None)
            db.session.add(c)
            db.session.commit()
            flash("Категория добавлена", "success")
            return redirect(url_for("admin.categories_list"))
    categories = (
        Category.query.filter_by(parent_id=None)
        .order_by(Category.sort_order)
        .all()
    )
    return render_template("admin/categories_list.html", categories=categories)


@bp.route("/categories/<int:cat_id>/delete", methods=["POST"])
@admin_required
def category_delete(cat_id):
    c = db.session.get(Category, cat_id) or abort(404)
    if c.products.count() > 0:
        flash("Нельзя удалить: есть товары в этой категории.", "error")
    else:
        db.session.delete(c)
        db.session.commit()
        flash("Категория удалена", "info")
    return redirect(url_for("admin.categories_list"))
