"""Модели SQLAlchemy для Encounter — маркетплейс + тесты."""
from datetime import datetime
from enum import Enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


# ───────────────── Перечисления ─────────────────

class UserRole(str, Enum):
    """Роли пользователя."""
    USER = "user"
    SELLER = "seller"
    ADMIN = "admin"


class SellerStatus(str, Enum):
    """Статус заявки на продавца."""
    NONE = "none"            # обычный пользователь
    PENDING = "pending"      # заявка подана, ждёт модерации
    APPROVED = "approved"    # одобрен
    REJECTED = "rejected"    # отклонён


class OrderStatus(str, Enum):
    """Статусы заказа."""
    NEW = "new"              # новый, ожидает подтверждения
    CONFIRMED = "confirmed"  # подтверждён продавцом
    SHIPPED = "shipped"      # отправлен
    DELIVERED = "delivered"  # доставлен
    CANCELLED = "cancelled"  # отменён


# ───────────────── Пользователь ─────────────────

class User(UserMixin, db.Model):
    """Пользователь Encounter."""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default=UserRole.USER.value, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Профиль
    full_name = db.Column(db.String(150), default="")
    phone = db.Column(db.String(30), default="")
    avatar = db.Column(db.String(255), default=None)
    bio = db.Column(db.Text, default="")

    # Связи
    test_results = db.relationship(
        "TestResult", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    seller_profile = db.relationship(
        "SellerProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    products = db.relationship(
        "Product", backref="seller", lazy=True, cascade="all, delete-orphan"
    )
    orders = db.relationship(
        "Order", backref="customer", lazy=True, cascade="all, delete-orphan",
        foreign_keys="Order.customer_id",
    )
    cart_items = db.relationship(
        "CartItem", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review", backref="author", lazy=True, cascade="all, delete-orphan"
    )
    favorites = db.relationship(
        "Favorite", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN.value

    @property
    def is_seller(self) -> bool:
        return self.role == UserRole.SELLER.value

    @property
    def is_approved_seller(self) -> bool:
        return (
            self.role == UserRole.SELLER.value
            and self.seller_profile is not None
            and self.seller_profile.status == SellerStatus.APPROVED.value
        )

    def __repr__(self) -> str:
        return f"<User {self.username} role={self.role}>"


# ───────────────── Профиль продавца ─────────────────

class SellerProfile(db.Model):
    """Профиль продавца (заявка + магазин)."""

    __tablename__ = "seller_profile"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False
    )

    # Магазин
    shop_name = db.Column(db.String(120), nullable=False)
    shop_description = db.Column(db.Text, default="")
    banner = db.Column(db.String(255), default=None)  # баннер магазина

    # Заявка
    status = db.Column(
        db.String(20), default=SellerStatus.PENDING.value, nullable=False
    )
    motivation = db.Column(db.Text, default="")  # почему хочет стать продавцом
    rejection_reason = db.Column(db.Text, default="")
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    # Аналитика (денормализация для скорости)
    products_count = db.Column(db.Integer, default=0, nullable=False)
    total_sales = db.Column(db.Integer, default=0, nullable=False)
    rating = db.Column(db.Float, default=0.0, nullable=False)  # 0..5
    reviews_count = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<SellerProfile {self.shop_name!r} status={self.status}>"


# ───────────────── Категории и товары ─────────────────

class Category(db.Model):
    """Категория товаров (дерево)."""

    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    icon = db.Column(db.String(8), default="")  # эмодзи
    parent_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    parent = db.relationship(
        "Category", remote_side=[id], backref=db.backref("children", lazy="dynamic")
    )
    products = db.relationship("Product", backref="category", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Category {self.name!r}>"


class Product(db.Model):
    """Товар."""

    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False, index=True)

    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, index=True)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Float, nullable=False)  # в рублях
    old_price = db.Column(db.Float, nullable=True)  # для скидки
    stock = db.Column(db.Integer, default=0, nullable=False)

    # Модерация
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # продавец скрыл
    is_approved = db.Column(db.Boolean, default=True, nullable=False)  # админ одобрил
    rejection_reason = db.Column(db.Text, default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Денормализация
    views_count = db.Column(db.Integer, default=0, nullable=False)
    sales_count = db.Column(db.Integer, default=0, nullable=False)
    rating = db.Column(db.Float, default=0.0, nullable=False)
    reviews_count = db.Column(db.Integer, default=0, nullable=False)

    # Связи
    images = db.relationship(
        "ProductImage", backref="product", lazy=True, cascade="all, delete-orphan",
        order_by="ProductImage.sort_order"
    )
    reviews = db.relationship(
        "Review", backref="product", lazy=True, cascade="all, delete-orphan"
    )
    favorited_by = db.relationship(
        "Favorite", backref="product", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def main_image(self) -> "ProductImage | None":
        if self.images:
            return self.images[0]
        return None

    @property
    def in_stock(self) -> bool:
        return self.stock > 0 and self.is_active and self.is_approved

    @property
    def discount_percent(self) -> int:
        if self.old_price and self.old_price > self.price:
            return int(round((1 - self.price / self.old_price) * 100))
        return 0

    def __repr__(self) -> str:
        return f"<Product #{self.id} {self.title!r} price={self.price}>"


class ProductImage(db.Model):
    """Изображение товара (несколько на товар)."""

    __tablename__ = "product_image"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ProductImage #{self.id} {self.file_path}>"


# ───────────────── Корзина и заказы ─────────────────

class CartItem(db.Model):
    """Позиция в корзине."""

    __tablename__ = "cart_item"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id"), nullable=False, index=True
    )
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    product = db.relationship("Product", backref="cart_items")

    @property
    def subtotal(self) -> float:
        return (self.product.price or 0) * self.quantity

    def __repr__(self) -> str:
        return f"<CartItem user={self.user_id} product={self.product_id} qty={self.quantity}>"


class Order(db.Model):
    """Заказ (один покупатель — несколько продавцов не смешиваем)."""

    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    status = db.Column(db.String(20), default=OrderStatus.NEW.value, nullable=False)

    # Суммы
    total = db.Column(db.Float, default=0.0, nullable=False)

    # Доставка
    delivery_name = db.Column(db.String(150), nullable=False)
    delivery_phone = db.Column(db.String(30), nullable=False)
    delivery_address = db.Column(db.String(300), nullable=False)
    delivery_comment = db.Column(db.Text, default="")

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    items = db.relationship(
        "OrderItem", backref="order", lazy=True, cascade="all, delete-orphan"
    )
    seller = db.relationship("User", foreign_keys=[seller_id])

    def __repr__(self) -> str:
        return f"<Order #{self.id} status={self.status} total={self.total}>"


class OrderItem(db.Model):
    """Позиция в заказе (снимок цены и названия на момент покупки)."""

    __tablename__ = "order_item"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    product_title = db.Column(db.String(200), nullable=False)  # снимок
    price = db.Column(db.Float, nullable=False)  # снимок
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    product = db.relationship("Product")

    def __repr__(self) -> str:
        return f"<OrderItem {self.product_title!r} x{self.quantity}>"


# ───────────────── Отзывы и избранное ─────────────────

class Review(db.Model):
    """Отзыв на товар."""

    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    rating = db.Column(db.Integer, nullable=False)  # 1..5
    text = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("product_id", "user_id", name="uq_review_product_user"),
    )

    def __repr__(self) -> str:
        return f"<Review {self.rating}/5 for product {self.product_id}>"


class Favorite(db.Model):
    """Избранное."""

    __tablename__ = "favorite"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_favorite_user_product"),
    )

    def __repr__(self) -> str:
        return f"<Favorite user={self.user_id} product={self.product_id}>"


# ───────────────── Чат (минимальный) ─────────────────

class Conversation(db.Model):
    """Диалог между покупателем и продавцом (привязан к товару)."""

    __tablename__ = "conversation"

    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    buyer = db.relationship("User", foreign_keys=[buyer_id])
    seller_rel = db.relationship("User", foreign_keys=[seller_id])
    product = db.relationship("Product")
    messages = db.relationship(
        "Message", backref="conversation", lazy=True, cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    __table_args__ = (
        db.UniqueConstraint("buyer_id", "seller_id", "product_id", name="uq_conv"),
    )


class Message(db.Model):
    """Сообщение в чате."""

    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("conversation.id"), nullable=False, index=True
    )
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id])


# ───────────────── Тесты (как было) ─────────────────

class TestResult(db.Model):
    """Результат прохождения теста."""

    __tablename__ = "test_result"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )

    test_id = db.Column(db.String(64), nullable=False, index=True)
    test_name = db.Column(db.String(160), nullable=False)

    result_summary = db.Column(db.String(220), nullable=False)
    detailed_answers = db.Column(db.Text, nullable=False)  # JSON string
    date_passed = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<TestResult #{self.id} {self.test_id} -> {self.result_summary!r}>"
