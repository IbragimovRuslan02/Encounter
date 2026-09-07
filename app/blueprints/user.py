"""Кабинет покупателя: профиль, корзина, заказы, избранное, чат, заявка на продавца."""
from datetime import datetime

from flask import (
    Blueprint, abort, flash, redirect, render_template, request, url_for,
)
from sqlalchemy import or_

from ..extensions import db
from ..forms import (
    ChangePasswordForm, CheckoutForm, MessageForm, ProfileForm,
    SellerApplicationForm,
)
from ..models import (
    CartItem, Conversation, Favorite, Message, Order, OrderItem, OrderStatus,
    Product, SellerProfile, SellerStatus, TestResult, User, UserRole,
)
from ..utils import (
    approved_seller_required, delete_file, get_user, login_required,
    save_image, unique_slug,
)

bp = Blueprint("user", __name__, url_prefix="/account")


# ─────────────── Дашборд ───────────────

@bp.route("/")
@login_required
def dashboard():
    u = get_user()
    cart_count = CartItem.query.filter_by(user_id=u.id).count()
    orders_count = Order.query.filter_by(customer_id=u.id).count()
    favorites_count = Favorite.query.filter_by(user_id=u.id).count()
    recent_orders = (
        Order.query.filter_by(customer_id=u.id)
        .order_by(Order.created_at.desc())
        .limit(3)
        .all()
    )
    return render_template(
        "account/dashboard.html",
        cart_count=cart_count,
        orders_count=orders_count,
        favorites_count=favorites_count,
        recent_orders=recent_orders,
    )


# ─────────────── Профиль ───────────────

@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    u = get_user()
    form = ProfileForm(obj=u)
    pw_form = ChangePasswordForm()

    if request.method == "POST" and "save_profile" in request.form and form.validate_on_submit():
        u.full_name = form.full_name.data.strip()
        u.email = (form.email.data or "").strip() or None
        u.phone = (form.phone.data or "").strip()
        u.bio = (form.bio.data or "").strip()
        if form.avatar.data:
            if u.avatar:
                delete_file(u.avatar)
            path = save_image(form.avatar.data, "avatars")
            if path:
                u.avatar = path
        db.session.commit()
        flash("Профиль обновлён", "success")
        return redirect(url_for("user.profile"))

    if request.method == "POST" and "change_password" in request.form and pw_form.validate_on_submit():
        if not u.check_password(pw_form.old_password.data):
            flash("Неверный текущий пароль", "error")
        else:
            u.set_password(pw_form.new_password.data)
            db.session.commit()
            flash("Пароль изменён", "success")
            return redirect(url_for("user.profile"))

    return render_template("account/profile.html", form=form, pw_form=pw_form)


# ─────────────── Корзина ───────────────

@bp.route("/cart")
@login_required
def cart():
    u = get_user()
    items = (
        CartItem.query.filter_by(user_id=u.id)
        .order_by(CartItem.added_at.desc())
        .all()
    )
    total = sum(it.subtotal for it in items if it.product and it.product.in_stock)
    return render_template("account/cart.html", items=items, total=total)


@bp.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def cart_add(product_id):
    product = Product.query.get_or_404(product_id)
    u = get_user()

    if not product.in_stock:
        flash("Товар недоступен для покупки.", "error")
        return redirect(url_for("public.product_detail", slug=product.slug))

    item = CartItem.query.filter_by(user_id=u.id, product_id=product.id).first()
    if item:
        if item.quantity < product.stock:
            item.quantity += 1
        else:
            flash("Больше нет на складе.", "warning")
    else:
        item = CartItem(user_id=u.id, product_id=product.id, quantity=1)
        db.session.add(item)
    db.session.commit()
    flash(f"«{product.title}» добавлен в корзину", "success")

    # Если из карточки — возвращаемся туда
    next_url = request.form.get("next") or url_for("user.cart")
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect(url_for("user.cart"))


@bp.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
def cart_update(item_id):
    u = get_user()
    item = CartItem.query.filter_by(id=item_id, user_id=u.id).first_or_404()
    qty = request.form.get("quantity", type=int)
    if qty and qty > 0 and qty <= item.product.stock:
        item.quantity = qty
        db.session.commit()
    elif qty and qty > item.product.stock:
        flash("Больше нет на складе.", "warning")
    return redirect(url_for("user.cart"))


@bp.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def cart_remove(item_id):
    u = get_user()
    item = CartItem.query.filter_by(id=item_id, user_id=u.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Удалено из корзины", "info")
    return redirect(url_for("user.cart"))


# ─────────────── Оформление заказа ───────────────

@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    u = get_user()
    items = (
        CartItem.query.filter_by(user_id=u.id)
        .all()
    )
    if not items:
        flash("Корзина пуста.", "info")
        return redirect(url_for("user.cart"))

    # Группируем по продавцам
    by_seller: dict[int, list[CartItem]] = {}
    for it in items:
        if it.product and it.product.in_stock:
            by_seller.setdefault(it.product.seller_id, []).append(it)

    if not by_seller:
        flash("Все товары в корзине недоступны.", "info")
        return redirect(url_for("user.cart"))

    form = CheckoutForm()
    if form.validate_on_submit():
        # Создаём заказы: по одному на каждого продавца
        created_orders = []
        for seller_id, seller_items in by_seller.items():
            order = Order(
                customer_id=u.id,
                seller_id=seller_id,
                status=OrderStatus.NEW.value,
                total=sum(it.subtotal for it in seller_items),
                delivery_name=form.delivery_name.data.strip(),
                delivery_phone=form.delivery_phone.data.strip(),
                delivery_address=form.delivery_address.data.strip(),
                delivery_comment=(form.delivery_comment.data or "").strip(),
            )
            db.session.add(order)
            db.session.flush()
            for it in seller_items:
                # Снимок цены
                db.session.add(OrderItem(
                    order_id=order.id,
                    product_id=it.product.id,
                    product_title=it.product.title,
                    price=it.product.price,
                    quantity=it.quantity,
                    subtotal=it.subtotal,
                ))
                # Уменьшаем остаток
                it.product.stock = max(0, it.product.stock - it.quantity)
                it.product.sales_count += it.quantity
            created_orders.append(order)
        # Очищаем корзину
        for it in items:
            db.session.delete(it)
        db.session.commit()
        flash(f"Заказ оформлен! Продавцов: {len(created_orders)}.", "success")
        return redirect(url_for("user.orders"))

    # Предзаполним поля
    if request.method == "GET":
        form.delivery_name.data = u.full_name or u.username
        form.delivery_phone.data = u.phone or ""

    return render_template(
        "account/checkout.html",
        form=form,
        by_seller=by_seller,
        total=sum(it.subtotal for it in items if it.product and it.product.in_stock),
    )


# ─────────────── Мои заказы ───────────────

@bp.route("/orders")
@login_required
def orders():
    u = get_user()
    status = request.args.get("status", "").strip() or None
    query = Order.query.filter_by(customer_id=u.id)
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template("account/orders.html", orders=orders, current_status=status)


@bp.route("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    u = get_user()
    o = Order.query.filter_by(id=order_id, customer_id=u.id).first_or_404()
    return render_template("account/order_detail.html", order=o)


@bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
@login_required
def order_cancel(order_id):
    u = get_user()
    o = Order.query.filter_by(id=order_id, customer_id=u.id).first_or_404()
    if o.status not in (OrderStatus.NEW.value,):
        flash("Этот заказ уже нельзя отменить.", "warning")
        return redirect(url_for("user.order_detail", order_id=o.id))
    o.status = OrderStatus.CANCELLED.value
    o.cancelled_at = datetime.utcnow()
    # Возвращаем остаток
    for it in o.items:
        if it.product:
            it.product.stock += it.quantity
            it.product.sales_count = max(0, it.product.sales_count - it.quantity)
    db.session.commit()
    flash("Заказ отменён", "info")
    return redirect(url_for("user.order_detail", order_id=o.id))


@bp.route("/orders/<int:order_id>/confirm_delivery", methods=["POST"])
@login_required
def order_confirm_delivery(order_id):
    u = get_user()
    o = Order.query.filter_by(id=order_id, customer_id=u.id).first_or_404()
    if o.status != OrderStatus.SHIPPED.value:
        flash("Этот заказ нельзя подтвердить.", "warning")
    else:
        o.status = OrderStatus.DELIVERED.value
        o.delivered_at = datetime.utcnow()
        db.session.commit()
        flash("Спасибо! Заказ отмечен как доставленный.", "success")
    return redirect(url_for("user.order_detail", order_id=o.id))


# ─────────────── Избранное ───────────────

@bp.route("/favorites")
@login_required
def favorites():
    u = get_user()
    favs = (
        Favorite.query.filter_by(user_id=u.id)
        .order_by(Favorite.added_at.desc())
        .all()
    )
    return render_template("account/favorites.html", favorites=favs)


# ─────────────── Стать продавцом ───────────────

@bp.route("/become-seller", methods=["GET", "POST"])
@login_required
def become_seller():
    u = get_user()
    if u.is_admin:
        flash("Администратору не нужно подавать заявку.", "info")
        return redirect(url_for("admin.admin_dashboard"))
    if u.is_approved_seller:
        flash("Вы уже являетесь одобренным продавцом.", "info")
        return redirect(url_for("seller.seller_dashboard"))
    if u.seller_profile and u.seller_profile.status == SellerStatus.PENDING.value:
        flash("Ваша заявка на рассмотрении.", "info")
        return render_template("account/become_seller.html", profile=u.seller_profile, form=None)
    if u.seller_profile and u.seller_profile.status == SellerStatus.REJECTED.value:
        # Можно подать повторно
        db.session.delete(u.seller_profile)
        db.session.commit()

    form = SellerApplicationForm()
    if form.validate_on_submit():
        banner_path = None
        if form.banner.data:
            banner_path = save_image(form.banner.data, "banners")
        sp = SellerProfile(
            user_id=u.id,
            shop_name=form.shop_name.data.strip(),
            shop_description=(form.shop_description.data or "").strip(),
            motivation=form.motivation.data.strip(),
            banner=banner_path,
            status=SellerStatus.PENDING.value,
        )
        db.session.add(sp)
        # Повышаем роль до seller (но он не одобрен)
        u.role = UserRole.SELLER.value
        db.session.commit()
        flash("Заявка отправлена! Мы рассмотрим её в ближайшее время.", "success")
        return redirect(url_for("user.become_seller"))
    return render_template("account/become_seller.html", profile=None, form=form)


# ─────────────── Чат ───────────────

@bp.route("/messages")
@login_required
def messages_list():
    u = get_user()
    # Диалоги, где я — покупатель или продавец
    convs = (
        Conversation.query.filter(or_buyer_seller(u.id))
        .order_by(Conversation.last_message_at.desc())
        .all()
    )
    return render_template("account/messages_list.html", conversations=convs)


@bp.route("/messages/<int:conversation_id>", methods=["GET", "POST"])
@login_required
def chat(conversation_id):
    u = get_user()
    conv = Conversation.query.get_or_404(conversation_id)
    if u.id not in (conv.buyer_id, conv.seller_id):
        abort(403)
    other_id = conv.seller_id if u.id == conv.buyer_id else conv.buyer_id
    other = db.session.get(User, other_id)

    # Помечаем входящие как прочитанные
    for m in conv.messages:
        if m.sender_id != u.id and not m.is_read:
            m.is_read = True
    db.session.commit()

    form = MessageForm()
    if form.validate_on_submit():
        m = Message(
            conversation_id=conv.id,
            sender_id=u.id,
            text=form.text.data.strip(),
        )
        db.session.add(m)
        conv.last_message_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("user.chat", conversation_id=conv.id))

    return render_template("account/chat.html", conv=conv, other=other, form=form)


# Helper: фильтр для диалогов пользователя
def or_buyer_seller(uid):
    return or_(
        Conversation.buyer_id == uid,
        Conversation.seller_id == uid,
    )


# ─────────────── Тесты (в кабинете) ───────────────

@bp.route("/tests")
@login_required
def tests():
    return redirect(url_for("api.tests_page"))


@bp.route("/tests/history")
@login_required
def test_history():
    u = get_user()
    results = (
        TestResult.query.filter_by(user_id=u.id)
        .order_by(TestResult.date_passed.desc())
        .all()
    )
    return render_template("account/test_history.html", results=results)
