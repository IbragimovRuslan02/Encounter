"""Публичные маршруты: главная, каталог, карточка товара, поиск."""
from flask import (
    Blueprint, abort, flash, redirect, render_template, request, url_for,
)
from sqlalchemy import or_

from ..extensions import db
from ..forms import ReviewForm
from ..models import (
    Category, Conversation, Favorite, Product, Review, SellerProfile, User,
)
from ..utils import get_user, login_required, recalc_product_rating

bp = Blueprint("public", __name__)


# ─────────────── Главная ───────────────

@bp.route("/")
def home():
    # Популярные товары
    popular_products = (
        Product.query.filter_by(is_active=True, is_approved=True)
        .order_by(Product.sales_count.desc(), Product.rating.desc())
        .limit(8)
        .all()
    )
    # Свежие товары
    new_products = (
        Product.query.filter_by(is_active=True, is_approved=True)
        .order_by(Product.created_at.desc())
        .limit(8)
        .all()
    )
    # Категории верхнего уровня
    top_categories = (
        Category.query.filter_by(parent_id=None)
        .order_by(Category.sort_order)
        .all()
    )
    return render_template(
        "home.html",
        popular_products=popular_products,
        new_products=new_products,
        top_categories=top_categories,
    )


# ─────────────── Каталог ───────────────

@bp.route("/catalog")
def catalog():
    page = request.args.get("page", 1, type=int)
    category_slug = request.args.get("category", "").strip() or None
    search = request.args.get("q", "").strip() or None
    sort = request.args.get("sort", "popular")

    query = Product.query.filter_by(is_active=True, is_approved=True)

    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if not cat:
            abort(404)
        # Включаем подкатегории
        ids = [cat.id] + [c.id for c in cat.children]
        query = query.filter(Product.category_id.in_(ids))

    if search and len(search) >= 2:
        like_q = f"%{search}%"
        query = query.filter(
            or_(Product.title.ilike(like_q), Product.description.ilike(like_q))
        )

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "new":
        query = query.order_by(Product.created_at.desc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc(), Product.reviews_count.desc())
    else:  # popular
        query = query.order_by(
            Product.sales_count.desc(), Product.rating.desc()
        )

    products = query.paginate(page=page, per_page=12, error_out=False)
    all_categories = (
        Category.query.filter_by(parent_id=None)
        .order_by(Category.sort_order)
        .all()
    )
    return render_template(
        "catalog.html",
        products=products,
        categories=all_categories,
        current_category=category_slug,
        current_sort=sort,
        search=search,
    )


# ─────────────── Карточка товара ───────────────

@bp.route("/product/<slug>")
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    product.views_count += 1
    db.session.commit()

    # Похожие товары
    similar = (
        Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.is_active == True,  # noqa: E712
            Product.is_approved == True,  # noqa: E712
        )
        .order_by(Product.rating.desc())
        .limit(4)
        .all()
    )

    # Отзывы
    reviews = (
        Review.query.filter_by(product_id=product.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    # Форма отзыва (если пользователь залогинен, ещё не оставлял и покупал)
    review_form = None
    can_review = False
    user = get_user()
    if user:
        # Уже оставлял?
        already = Review.query.filter_by(
            product_id=product.id, user_id=user.id
        ).first()
        if not already:
            review_form = ReviewForm()
            # Может оставить любой залогиненный (для простоты демо)
            can_review = True

    in_favorites = False
    if user:
        in_favorites = Favorite.query.filter_by(
            user_id=user.id, product_id=product.id
        ).first() is not None

    return render_template(
        "product_detail.html",
        product=product,
        similar=similar,
        reviews=reviews,
        review_form=review_form,
        can_review=can_review,
        in_favorites=in_favorites,
    )


@bp.route("/product/<int:product_id>/review", methods=["POST"])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    user = get_user()
    # Один отзыв от пользователя на товар
    if Review.query.filter_by(product_id=product.id, user_id=user.id).first():
        flash("Вы уже оставляли отзыв на этот товар.", "warning")
        return redirect(url_for("public.product_detail", slug=product.slug))

    form = ReviewForm()
    if form.validate_on_submit():
        r = Review(
            product_id=product.id,
            user_id=user.id,
            rating=form.rating.data,
            text=(form.text.data or "").strip(),
        )
        db.session.add(r)
        db.session.commit()
        recalc_product_rating(product.id)
        flash("Спасибо за отзыв!", "success")
    else:
        flash("Не удалось сохранить отзыв.", "error")
    return redirect(url_for("public.product_detail", slug=product.slug))


@bp.route("/product/<int:product_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(product_id):
    product = Product.query.get_or_404(product_id)
    user = get_user()
    fav = Favorite.query.filter_by(user_id=user.id, product_id=product.id).first()
    if fav:
        db.session.delete(fav)
        flash("Удалено из избранного", "info")
    else:
        db.session.add(Favorite(user_id=user.id, product_id=product.id))
        flash("Добавлено в избранное", "success")
    db.session.commit()
    return redirect(url_for("public.product_detail", slug=product.slug))


# ─────────────── Магазин продавца ───────────────

@bp.route("/shop/<int:seller_id>")
def shop_view(seller_id):
    seller = db.session.get(User, seller_id)
    if not seller or not seller.is_approved_seller:
        abort(404)
    profile = seller.seller_profile
    products = (
        Product.query.filter_by(
            seller_id=seller.id, is_active=True, is_approved=True
        )
        .order_by(Product.created_at.desc())
        .all()
    )
    return render_template("shop.html", seller=seller, profile=profile, products=products)


# ─────────────── Написать продавцу ───────────────

@bp.route("/product/<int:product_id>/contact", methods=["GET", "POST"])
@login_required
def contact_seller(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id == get_user().id:
        flash("Это ваш собственный товар.", "info")
        return redirect(url_for("public.product_detail", slug=product.slug))
    # Создаём или находим диалог
    conv = Conversation.query.filter_by(
        buyer_id=get_user().id,
        seller_id=product.seller_id,
        product_id=product.id,
    ).first()
    if not conv:
        conv = Conversation(
            buyer_id=get_user().id,
            seller_id=product.seller_id,
            product_id=product.id,
        )
        db.session.add(conv)
        db.session.commit()
    return redirect(url_for("user.chat", conversation_id=conv.id))
