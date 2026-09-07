"""Инициализация БД и наполнение тестовыми данными."""
from datetime import datetime, timedelta
import json

from .extensions import db
from .models import (
    Category, Order, OrderItem, OrderStatus, Product, Review, SellerProfile,
    SellerStatus, User, UserRole,
)


def init_db() -> None:
    """Создаёт таблицы и (если БД пуста) наполняет демо-данными."""
    db.create_all()

    if User.query.first():
        return  # уже инициализировано

    _seed_users()
    _seed_categories()
    _seed_sellers_and_products()
    _seed_reviews()
    _seed_orders()

    db.session.commit()
    print("OK: Database initialized with demo data.")
    print("   admin  / admin123  -- administrator")
    print("   shop1  / seller123 -- approved seller (Магазин «ТехноСила»)")
    print("   shop2  / seller123 -- approved seller (Магазин «Уютный дом»)")
    print("   buyer1 / buyer123  -- customer with order history")
    print("   buyer2 / buyer123  -- customer")


def _seed_users() -> None:
    # Админ
    admin = User(
        username="admin",
        email="admin@encounter.local",
        role=UserRole.ADMIN.value,
        full_name="Администратор",
    )
    admin.set_password("admin123")

    # Продавцы
    shop1 = User(
        username="shop1",
        email="shop1@encounter.local",
        role=UserRole.SELLER.value,
        full_name="Иван Технович",
        phone="+7 900 100-00-01",
        bio="Продаю электронику оптом и в розницу с 2018 года.",
    )
    shop1.set_password("seller123")
    sp1 = SellerProfile(
        user=shop1,
        shop_name="ТехноСила",
        shop_description="Электроника, гаджеты, аксессуары. Быстрая доставка, гарантия.",
        status=SellerStatus.APPROVED.value,
        motivation="Хочу продавать технику, которой сам пользуюсь.",
        applied_at=datetime(2025, 1, 1),
        reviewed_at=datetime(2025, 1, 2),
    )

    shop2 = User(
        username="shop2",
        email="shop2@encounter.local",
        role=UserRole.SELLER.value,
        full_name="Анна Уютнова",
        phone="+7 900 100-00-02",
        bio="Декор, текстиль, всё для уютного дома.",
    )
    shop2.set_password("seller123")
    sp2 = SellerProfile(
        user=shop2,
        shop_name="Уютный дом",
        shop_description="Товары для дома, декоративные мелочи, текстиль ручной работы.",
        status=SellerStatus.APPROVED.value,
        motivation="Занимаюсь рукоделием 5 лет, хочу делиться результатом.",
        applied_at=datetime(2025, 2, 1),
        reviewed_at=datetime(2025, 2, 2),
    )

    # Заявка на рассмотрении
    shop3 = User(
        username="shop3",
        email="shop3@encounter.local",
        role=UserRole.USER.value,
        full_name="Олег Новичков",
    )
    shop3.set_password("seller123")
    sp3 = SellerProfile(
        user=shop3,
        shop_name="Мастерская Олега",
        shop_description="Авторские изделия из дерева.",
        status=SellerStatus.PENDING.value,
        motivation="Делаю деревянные игрушки и предметы интерьера, хочу попробовать продавать.",
    )

    # Покупатели
    buyer1 = User(
        username="buyer1",
        email="buyer1@encounter.local",
        role=UserRole.USER.value,
        full_name="Пётр Иванов",
        phone="+7 900 200-00-01",
    )
    buyer1.set_password("buyer123")

    buyer2 = User(
        username="buyer2",
        email="buyer2@encounter.local",
        role=UserRole.USER.value,
        full_name="Мария Сидорова",
    )
    buyer2.set_password("buyer123")

    db.session.add_all([admin, shop1, shop2, shop3, buyer1, buyer2])
    db.session.flush()


def _seed_categories() -> None:
    cats = [
        ("Электроника", "electronics", "💻", 1, None),
        ("Смартфоны", "smartfony", "📱", 2, "electronics"),
        ("Ноутбуки", "noutbuki", "💻", 3, "electronics"),
        ("Аксессуары", "aksessuary", "🎧", 4, "electronics"),
        ("Дом и интерьер", "dom-i-interer", "🏠", 5, None),
        ("Текстиль", "tekstil", "🛋️", 6, "dom-i-interer"),
        ("Декор", "dekor", "🖼️", 7, "dom-i-interer"),
        ("Одежда", "odezhda", "👕", 8, None),
        ("Книги", "knigi", "📚", 9, None),
        ("Спорт", "sport", "⚽", 10, None),
    ]
    for name, slug, icon, order, parent_slug in cats:
        parent_id = None
        if parent_slug:
            parent = Category.query.filter_by(slug=parent_slug).first()
            if parent:
                parent_id = parent.id
        db.session.add(Category(
            name=name, slug=slug, icon=icon,
            sort_order=order, parent_id=parent_id,
        ))


def _seed_sellers_and_products() -> None:
    cat = Category.query
    electronics = cat.filter_by(slug="electronics").first()
    smartfony = cat.filter_by(slug="smartfony").first()
    noutbuki = cat.filter_by(slug="noutbuki").first()
    aksessuary = cat.filter_by(slug="aksessuary").first()
    tekstil = cat.filter_by(slug="tekstil").first()
    dekor = cat.filter_by(slug="dekor").first()
    odezhda = cat.filter_by(slug="odezhda").first()
    knigi = cat.filter_by(slug="knigi").first()

    shop1 = User.query.filter_by(username="shop1").first()
    shop2 = User.query.filter_by(username="shop2").first()

    products = [
        # ТехноСила
        (shop1, smartfony, "Смартфон Galaxy X1 128GB", 45990, 52990, 12,
         "Современный смартфон с отличной камерой 50 Мп, AMOLED-экраном 6.5\" и батареей 5000 мАч. Гарантия 12 месяцев."),
        (shop1, smartfony, "Смартфон Lite 8 64GB", 17990, None, 25,
         "Бюджетный, но надёжный: IPS-экран 6.1\", двойная камера, NFC для бесконтактной оплаты."),
        (shop1, noutbuki, "Ноутбук Pro 15 i5/16/512", 79990, 89990, 7,
         "Для работы и учёбы: процессор Intel Core i5, 16 ГБ ОЗУ, SSD 512 ГБ, экран 15.6\" FullHD."),
        (shop1, noutbuki, "Ноутбук Air 14 Ryzen 5/8/256", 54990, None, 10,
         "Лёгкий и компактный, идеален для путешествий. 14\" FHD, AMD Ryzen 5, 8/256."),
        (shop1, aksessuary, "Беспроводные наушники SoundPro", 4990, 5990, 30,
         "Bluetooth 5.3, активное шумоподавление, до 30 часов работы, складная конструкция."),
        (shop1, aksessuary, "Зарядное устройство 65W GaN", 2990, None, 50,
         "Компактное зарядное устройство с технологией GaN: 2 порта USB-C, 1 USB-A. Поддержка Power Delivery и Quick Charge."),
        (shop1, electronics, "Умная колонка Home 2", 7990, 9990, 18,
         "Голосовой помощник, Bluetooth, Wi-Fi, поддержка умного дома. Чёрный и белый цвета."),

        # Уютный дом
        (shop2, tekstil, "Плед шерстяной «Уют» 200x220", 3990, None, 20,
         "Натуральная овечья шерсть, мягкий и тёплый плед. Цвета: бежевый, серый, терракот."),
        (shop2, tekstil, "Набор постельного белья Premium", 6990, 8990, 15,
         "Сатин, 100% хлопок. Размер 2-спальный, 4 наволочки в комплекте. Цвета: белый, молочный, графит."),
        (shop2, dekor, "Картина постер «Горы» 60x80", 2490, None, 35,
         "Печать на холсте, деревянная рама. Стиль: минимализм, скандинавский."),
        (shop2, dekor, "Керамическая ваза ручной работы", 1890, 2490, 12,
         "Уникальная авторская работа, высота 25 см. Каждая ваза немного отличается от фото."),
        (shop2, dekor, "Ароматическая свеча «Сосновый лес»", 890, None, 60,
         "Натуральный соевый воск, хлопковый фитиль, время горения 35 часов. Аромат хвои."),
        (shop2, odezhda, "Худи базовое чёрное", 3490, 3990, 40,
         "100% хлопок плотностью 320 г/м², свободный крой, размеры S–XXL."),
        (shop2, odezhda, "Футболка из органического хлопка", 1290, None, 80,
         "Мягкая, не садится после стирки. Цвета: белый, чёрный, серый, бежевый, хаки."),
        (shop2, knigi, "Книга «Чистый код» (Р. Мартин)", 1490, 1790, 25,
         "Классика для разработчиков: как писать читаемый, поддерживаемый код."),
    ]
    for seller, category, title, price, old, stock, desc in products:
        p = Product(
            seller_id=seller.id,
            category_id=category.id,
            title=title,
            slug="",
            description=desc,
            price=price,
            old_price=old,
            stock=stock,
            is_active=True,
            is_approved=True,
            sales_count=5,
        )
        p.slug = title.lower().replace(" ", "-")[:200]
        db.session.add(p)
    db.session.flush()


def _seed_reviews() -> None:
    buyer1 = User.query.filter_by(username="buyer1").first()
    buyer2 = User.query.filter_by(username="buyer2").first()
    products = Product.query.limit(5).all()
    if not (buyer1 and buyer2 and products):
        return
    samples = [
        (buyer1, 5, "Отличный товар! Пришло быстро, качество на высоте. Рекомендую магазин!"),
        (buyer2, 4, "Хороший товар за свою цену. Упаковано нормально, доставка в срок."),
        (buyer1, 5, "Соответствует описанию, продавец общительный, отправил в день заказа."),
        (buyer2, 3, "Нормально, но ожидал чуть лучшего качества. В целом — ок."),
    ]
    for i, (user, rating, text) in enumerate(samples):
        p = products[i % len(products)]
        r = Review(product_id=p.id, user_id=user.id, rating=rating, text=text)
        db.session.add(r)
    db.session.flush()
    # Пересчитаем рейтинги
    for p in products:
        from .utils import recalc_product_rating
        recalc_product_rating(p.id)


def _seed_orders() -> None:
    buyer1 = User.query.filter_by(username="buyer1").first()
    shop1 = User.query.filter_by(username="shop1").first()
    if not (buyer1 and shop1):
        return
    p1 = Product.query.filter_by(title="Беспроводные наушники SoundPro").first()
    p2 = Product.query.filter_by(title="Зарядное устройство 65W GaN").first()
    if not (p1 and p2):
        return
    o = Order(
        customer_id=buyer1.id,
        seller_id=shop1.id,
        status=OrderStatus.DELIVERED.value,
        total=p1.price + p2.price,
        delivery_name="Пётр Иванов",
        delivery_phone="+7 900 200-00-01",
        delivery_address="г. Самара, ул. Ленинградская, д. 25, кв. 12",
        created_at=datetime.utcnow() - timedelta(days=14),
        confirmed_at=datetime.utcnow() - timedelta(days=13),
        shipped_at=datetime.utcnow() - timedelta(days=11),
        delivered_at=datetime.utcnow() - timedelta(days=7),
    )
    db.session.add(o)
    db.session.flush()
    db.session.add(OrderItem(
        order_id=o.id, product_id=p1.id,
        product_title=p1.title, price=p1.price, quantity=1, subtotal=p1.price,
    ))
    db.session.add(OrderItem(
        order_id=o.id, product_id=p2.id,
        product_title=p2.title, price=p2.price, quantity=1, subtotal=p2.price,
    ))
