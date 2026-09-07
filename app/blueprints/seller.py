"""Маршруты продавца: дашборд, управление товарами, заказы, чат."""
from datetime import datetime, timedelta
from flask import (
    Blueprint, abort, flash, redirect, render_template, request, url_for,
)
from sqlalchemy import func

from ..extensions import db
from ..models import (
    Category, Order, OrderItem, OrderStatus, Product, ProductImage, User,
)
from ..utils import (
    approved_seller_required, delete_file, get_user, login_required,
    save_image, unique_slug,
)

bp = Blueprint("seller", __name__, url_prefix="/seller")


@bp.route("/")
@approved_seller_required
def seller_dashboard():
    u = get_user()
    # Статистика за последние 30 дней
    since = datetime.utcnow() - timedelta(days=30)
    total_products = Product.query.filter_by(seller_id=u.id).count()
    active_products = Product.query.filter_by(
        seller_id=u.id, is_active=True, is_approved=True
    ).count()
    new_orders = Order.query.filter(
        Order.seller_id == u.id, Order.status == OrderStatus.NEW.value
    ).count()
    revenue_30 = db.session.query(func.coalesce(func.sum(Order.total), 0.0)).filter(
        Order.seller_id == u.id,
        Order.created_at >= since,
        Order.status != OrderStatus.CANCELLED.value,
    ).scalar() or 0
    orders_30 = Order.query.filter(
        Order.seller_id == u.id, Order.created_at >= since
    ).count()
    return render_template(
        "seller/dashboard.html",
        total_products=total_products,
        active_products=active_products,
        new_orders=new_orders,
        revenue_30=revenue_30,
        orders_30=orders_30,
    )


# ─────────────── Товары ───────────────

@bp.route("/products")
@approved_seller_required
def products_list():
    u = get_user()
    products = (
        Product.query.filter_by(seller_id=u.id)
        .order_by(Product.created_at.desc())
        .all()
    )
    return render_template("seller/products_list.html", products=products)


@bp.route("/products/new", methods=["GET", "POST"])
@approved_seller_required
def product_new():
    u = get_user()
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        category_id = request.form.get("category_id", type=int)
        try:
            price = float(request.form.get("price") or 0)
        except ValueError:
            price = 0
        try:
            old_price_raw = request.form.get("old_price") or ""
            old_price = float(old_price_raw) if old_price_raw else None
        except ValueError:
            old_price = None
        try:
            stock = int(request.form.get("stock") or 0)
        except ValueError:
            stock = 0
        description = (request.form.get("description") or "").strip()

        if not (title and category_id and price >= 0 and stock >= 0):
            flash("Заполните все обязательные поля корректно.", "error")
        elif not Category.query.get(category_id):
            flash("Неизвестная категория.", "error")
        else:
            p = Product(
                seller_id=u.id,
                category_id=category_id,
                title=title,
                slug=unique_slug(Product, title),
                description=description,
                price=price,
                old_price=old_price,
                stock=stock,
                is_active=True,
                is_approved=True,
            )
            db.session.add(p)
            db.session.flush()
            # Загрузка изображений
            files = request.files.getlist("images")
            for i, f in enumerate(files[:8]):
                if f and f.filename:
                    path = save_image(f, "products")
                    if path:
                        db.session.add(ProductImage(
                            product_id=p.id, file_path=path, sort_order=i,
                        ))
            db.session.commit()
            flash("Товар создан", "success")
            return redirect(url_for("seller.products_list"))

    categories = (
        Category.query.filter_by(parent_id=None)
        .order_by(Category.sort_order)
        .all()
    )
    return render_template("seller/product_form.html", product=None, categories=categories)


@bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@approved_seller_required
def product_edit(product_id):
    u = get_user()
    p = Product.query.filter_by(id=product_id, seller_id=u.id).first_or_404()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        category_id = request.form.get("category_id", type=int)
        try:
            price = float(request.form.get("price") or 0)
        except ValueError:
            price = 0
        try:
            old_price_raw = request.form.get("old_price") or ""
            old_price = float(old_price_raw) if old_price_raw else None
        except ValueError:
            old_price = None
        try:
            stock = int(request.form.get("stock") or 0)
        except ValueError:
            stock = 0
        description = (request.form.get("description") or "").strip()

        if not (title and category_id and price >= 0 and stock >= 0):
            flash("Заполните все поля корректно.", "error")
        else:
            p.title = title
            p.category_id = category_id
            p.price = price
            p.old_price = old_price
            p.stock = stock
            p.description = description
            p.slug = unique_slug(Product, title, exclude_id=p.id)
            p.updated_at = datetime.utcnow()

            # Новые изображения (добавляем к существующим)
            files = request.files.getlist("images")
            existing_count = len(p.images)
            for i, f in enumerate(files[:8]):
                if f and f.filename:
                    path = save_image(f, "products")
                    if path:
                        db.session.add(ProductImage(
                            product_id=p.id, file_path=path, sort_order=existing_count + i,
                        ))
            db.session.commit()
            flash("Товар обновлён", "success")
            return redirect(url_for("seller.products_list"))

    categories = (
        Category.query.filter_by(parent_id=None)
        .order_by(Category.sort_order)
        .all()
    )
    return render_template("seller/product_form.html", product=p, categories=categories)


@bp.route("/products/<int:product_id>/delete", methods=["POST"])
@approved_seller_required
def product_delete(product_id):
    u = get_user()
    p = Product.query.filter_by(id=product_id, seller_id=u.id).first_or_404()
    # Удалим файлы изображений
    for img in p.images:
        delete_file(img.file_path)
    db.session.delete(p)
    db.session.commit()
    flash("Товар удалён", "info")
    return redirect(url_for("seller.products_list"))


@bp.route("/products/<int:product_id>/delete-image/<int:image_id>", methods=["POST"])
@approved_seller_required
def product_image_delete(product_id, image_id):
    u = get_user()
    p = Product.query.filter_by(id=product_id, seller_id=u.id).first_or_404()
    img = ProductImage.query.filter_by(id=image_id, product_id=p.id).first_or_404()
    delete_file(img.file_path)
    db.session.delete(img)
    db.session.commit()
    flash("Фото удалено", "info")
    return redirect(url_for("seller.product_edit", product_id=p.id))


# ─────────────── Заказы продавца ───────────────

@bp.route("/orders")
@approved_seller_required
def orders_list():
    u = get_user()
    status = request.args.get("status", "").strip() or None
    query = Order.query.filter_by(seller_id=u.id)
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template("seller/orders_list.html", orders=orders, current_status=status)


@bp.route("/orders/<int:order_id>")
@approved_seller_required
def order_detail(order_id):
    u = get_user()
    o = Order.query.filter_by(id=order_id, seller_id=u.id).first_or_404()
    return render_template("seller/order_detail.html", order=o)


@bp.route("/orders/<int:order_id>/status", methods=["POST"])
@approved_seller_required
def order_status_change(order_id):
    u = get_user()
    o = Order.query.filter_by(id=order_id, seller_id=u.id).first_or_404()
    new_status = request.form.get("status")
    allowed = [
        OrderStatus.CONFIRMED.value, OrderStatus.SHIPPED.value,
        OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value,
    ]
    if new_status not in allowed:
        flash("Недопустимый статус.", "error")
    else:
        o.status = new_status
        if new_status == OrderStatus.CONFIRMED.value:
            o.confirmed_at = datetime.utcnow()
        elif new_status == OrderStatus.SHIPPED.value:
            o.shipped_at = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED.value:
            o.delivered_at = datetime.utcnow()
        elif new_status == OrderStatus.CANCELLED.value:
            o.cancelled_at = datetime.utcnow()
            # Возвращаем остаток
            for it in o.items:
                if it.product:
                    it.product.stock += it.quantity
                    it.product.sales_count = max(0, it.product.sales_count - it.quantity)
        db.session.commit()
        flash(f"Статус изменён: {new_status}", "success")
    return redirect(url_for("seller.order_detail", order_id=o.id))


# ─────────────── Чат продавца ───────────────

@bp.route("/messages")
@approved_seller_required
def messages_list():
    from ..models import Conversation
    from sqlalchemy import or_
    u = get_user()
    convs = (
        Conversation.query.filter(
            or_(Conversation.buyer_id == u.id, Conversation.seller_id == u.id)
        )
        .order_by(Conversation.last_message_at.desc())
        .all()
    )
    return render_template("seller/messages_list.html", conversations=convs)


@bp.route("/messages/<int:conversation_id>")
@approved_seller_required
def message_view(conversation_id):
    from ..models import Conversation
    u = get_user()
    conv = Conversation.query.get_or_404(conversation_id)
    if u.id not in (conv.buyer_id, conv.seller_id):
        abort(403)
    other_id = conv.seller_id if u.id == conv.buyer_id else conv.buyer_id
    other = db.session.get(User, other_id)
    for m in conv.messages:
        if m.sender_id != u.id and not m.is_read:
            m.is_read = True
    db.session.commit()
    return render_template("seller/message_view.html", conv=conv, other=other)


@bp.route("/messages/<int:conversation_id>/send", methods=["POST"])
@approved_seller_required
def message_send(conversation_id):
    from ..models import Conversation, Message
    u = get_user()
    conv = Conversation.query.get_or_404(conversation_id)
    if u.id not in (conv.buyer_id, conv.seller_id):
        abort(403)
    text = (request.form.get("text") or "").strip()
    if text:
        m = Message(conversation_id=conv.id, sender_id=u.id, text=text)
        db.session.add(m)
        conv.last_message_at = datetime.utcnow()
        db.session.commit()
    return redirect(url_for("seller.message_view", conversation_id=conv.id))


# ─────────────── Профиль магазина ───────────────

@bp.route("/profile", methods=["GET", "POST"])
@approved_seller_required
def shop_profile():
    u = get_user()
    sp = u.seller_profile
    if request.method == "POST":
        sp.shop_name = (request.form.get("shop_name") or sp.shop_name).strip()
        sp.shop_description = (request.form.get("shop_description") or "").strip()
        if request.files.get("banner") and request.files["banner"].filename:
            if sp.banner:
                delete_file(sp.banner)
            sp.banner = save_image(request.files["banner"], "banners")
        db.session.commit()
        flash("Профиль магазина обновлён", "success")
        return redirect(url_for("seller.shop_profile"))
    return render_template("seller/shop_profile.html", profile=sp)
