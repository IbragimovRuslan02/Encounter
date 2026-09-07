# 🛒 Encounter — маркетплейс + психологические тесты

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

<p align="center">
  <a href="https://github.com/IbragimovRuslan02/Encounter/actions/workflows/ci.yml"><img src="https://github.com/IbragimovRuslan02/Encounter/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
  <a href="https://github.com/IbragimovRuslan02/Encounter/releases"><img src="https://img.shields.io/github/v/release/IbragimovRuslan02/Encounter" alt="Latest Release"></a>
  <a href="https://github.com/IbragimovRuslan02/Encounter/commits/main"><img src="https://img.shields.io/github/last-commit/IbragimovRuslan02/Encounter" alt="Last commit"></a>
</p>

> **RU** — Полноценный маркетплейс с каталогом, корзиной, заказами, чатом, отзывами, заявками на продавца, админкой — и психологические тесты в одном приложении.  
> **EN** — A full marketplace with catalog, cart, orders, chat, reviews, seller applications, admin panel — plus psychology quizzes in one app.

**English version below** ⬇️

---

## 📑 Содержание / Table of Contents

- [🇷🇺 Русский](#-русский)
  - [О проекте](#-о-проекте)
  - [Возможности](#-возможности)
  - [Стек](#-стек)
  - [Структура](#-структура)
  - [Быстрый старт](#-быстрый-старт)
  - [Демо-аккаунты](#-демо-аккаунты)
  - [Конфигурация](#-конфигурация)
  - [Команды](#-команды)
  - [Развёртывание](#-развёртывание)
  - [Автор](#-автор)
- [🇬🇧 English](#-english)
- [📄 Лицензия / License](#-лицензия--license)

---

## 🇷🇺 Русский

### 📖 О проекте

**Encounter** — это полноценный e-commerce маркетплейс, расширенный психологическими тестами. Поддерживает три роли пользователей, каталог с категориями, корзину, оформление заказов, чат покупатель-продавец, отзывы с рейтингом, избранное, заявки на продавца с модерацией и административную панель.

### ✨ Возможности

**👤 Покупатель (роль `user`)**
- 📚 Просмотр каталога с фильтрами по категориям и сортировкой
- 🔍 Полнотекстовый поиск по названию и описанию
- 🛒 Корзина с управлением количеством
- 📦 Оформление заказов с доставкой
- ❤ Избранное
- 💬 Чат с продавцами
- ⭐ Отзывы с рейтингом 1-5
- 🧠 Психологические тесты (3 шт.)

**🏪 Продавец (роль `seller`)**
- Заявка на открытие магазина (одобряется админом)
- 📊 Дашборд с выручкой и статистикой
- 📦 Управление товарами: создание, редактирование, удаление, загрузка нескольких фото
- 🏷 Скидки (старая цена)
- 📋 Управление заказами со сменой статусов
- 💬 Чат с покупателями
- 🏪 Настройка профиля магазина (название, описание, баннер)

**⚙ Администратор (роль `admin`)**
- 📊 Полный дашборд со статистикой платформы
- 🏪 Модерация заявок продавцов (одобрение/отклонение с причиной)
- 📦 Управление всеми товарами (скрытие/удаление)
- 📂 Управление категориями (создание, удаление)
- 👥 Управление пользователями (смена ролей)
- 📋 Просмотр всех заказов

**🧠 Психологические тесты**
- «Какой твой тип мышления?» (15 вопросов, 4 шкалы)
- «Какой твой стиль одежды?» (15 вопросов, 4 шкалы)
- «Какое направление карьеры тебе подходит?» (15 вопросов, 4 шкалы)
- История прохождений, детальные результаты

### 🛠 Стек

- **Backend:** Python 3.10+, Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **База данных:** SQLite (по умолчанию), легко переключается на PostgreSQL/MySQL
- **Шаблоны:** Jinja2 + TailwindCSS (CDN)
- **Frontend:** HTML5, Alpine.js (для тестов), ванильный JavaScript
- **Загрузки:** Pillow (ресайз картинок)
- **Безопасность:** CSRF-токены, хеширование паролей (pbkdf2:sha256), разграничение ролей

### 📁 Структура

```
Encounter/
├── app/                       # Пакет приложения
│   ├── __init__.py            #   Application factory
│   ├── config.py              #   Конфигурация (dev/prod)
│   ├── extensions.py          #   SQLAlchemy, Login, CSRF
│   ├── models.py              #   11 моделей БД
│   ├── forms.py               #   WTForms-формы
│   ├── utils.py               #   Утилиты, декораторы, slugify
│   ├── seed.py                #   Начальные данные
│   ├── tests_data.py          #   Каталог психологических тестов
│   ├── templates/             #   Jinja2-шаблоны
│   │   ├── account/           #     Кабинет покупателя
│   │   ├── admin/             #     Админ-панель
│   │   └── seller/            #     Кабинет продавца
│   └── blueprints/            #   Маршруты
│       ├── public.py          #     Главная, каталог, товары
│       ├── auth.py            #     Логин, регистрация
│       ├── user.py            #     Кабинет покупателя
│       ├── seller.py          #     Кабинет продавца
│       ├── admin.py           #     Админ-панель
│       └── api.py             #     API (тесты)
├── static/                    # Изображения
├── instance/                  # БД SQLite (создаётся автоматически)
├── uploads/                   # Загруженные фото (создаётся автоматически)
├── requirements.txt
├── run.py                     # Точка входа
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

### 🚀 Быстрый старт

#### 1. Клонирование
```bash
git clone https://github.com/IbragimovRuslan02/Encounter.git
cd Encounter
```

#### 2. Виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или: venv\Scripts\activate  # Windows
```

#### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 4. Настройка (опционально)
```bash
cp .env.example .env
# Отредактируйте .env — SECRET_KEY, ADMIN_PASSWORD и т.д.
```

#### 5. Запуск
```bash
python run.py
```

Откройте: **http://127.0.0.1:5000**

### 👥 Демо-аккаунты

Приложение создаётся с тестовыми данными (3 продавца, 2 покупателя, 15 товаров, 1 заказ, 4 отзыва):

| Логин | Пароль | Роль | Описание |
|-------|--------|------|----------|
| `admin` | `admin123` | Администратор | Полный доступ |
| `shop1` | `seller123` | Продавец (одобрен) | «ТехноСила» — электроника |
| `shop2` | `seller123` | Продавец (одобрен) | «Уютный дом» — декор/текстиль |
| `shop3` | `seller123` | Заявка | Ожидает одобрения |
| `buyer1` | `buyer123` | Покупатель | С историей заказов |
| `buyer2` | `buyer123` | Покупатель | Без заказов |

### ⚙️ Конфигурация

| Переменная | Назначение | По умолчанию |
|------------|------------|--------------|
| `FLASK_ENV` | Окружение | `development` |
| `SECRET_KEY` | Секретный ключ Flask | случайный |
| `DATABASE_URL` | URI базы данных | SQLite |
| `UPLOAD_FOLDER` | Папка загрузок | `uploads/` |
| `MAX_CONTENT_LENGTH` | Макс. размер файла | 10 МБ |

### 💻 Команды

```bash
# Разработка
python run.py

# Flask CLI
export FLASK_APP=run.py
flask run --host=0.0.0.0 --port=8080
```

### 🌐 Развёртывание

#### Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

#### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

### 👤 Автор

**Ибрагимов Руслан**  
GitHub: [@IbragimovRuslan02](https://github.com/IbragimovRuslan02)

---

## 🇬🇧 English

### 📖 About

**Encounter** is a full-featured e-commerce marketplace extended with psychology quizzes. It supports three user roles, a category-based catalog, shopping cart, order placement, buyer-seller chat, reviews with ratings, favorites, seller applications with admin moderation, and a complete admin panel.

### ✨ Features

**👤 Buyer (`user` role)**
- Catalog browsing with category filters and sorting
- Full-text search by title and description
- Shopping cart with quantity management
- Order placement with delivery details
- Favorites
- Chat with sellers
- Star reviews (1-5)
- 3 psychology quizzes

**🏪 Seller (`seller` role)**
- Store application (admin-approved)
- Dashboard with revenue and statistics
- Product management: create, edit, delete, multiple photo uploads
- Discounts (old price)
- Order management with status workflow
- Chat with buyers
- Store profile customization (name, description, banner)

**⚙ Administrator (`admin` role)**
- Full platform statistics dashboard
- Seller application moderation (approve/reject with reason)
- All-products management (hide/delete)
- Category management (create, delete)
- User management (role changes)
- All-orders view

### 🛠 Tech Stack

- **Backend:** Python 3.10+, Flask 3, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database:** SQLite (default), easy switch to PostgreSQL/MySQL
- **Templates:** Jinja2 + TailwindCSS (CDN)
- **Frontend:** HTML5, Alpine.js (quizzes), vanilla JavaScript
- **Uploads:** Pillow (image resizing)
- **Security:** CSRF tokens, password hashing (pbkdf2:sha256), role-based access

### 📁 Project Structure

```
Encounter/
├── app/                       # App package
│   ├── __init__.py            #   Application factory
│   ├── config.py              #   Configuration
│   ├── extensions.py          #   SQLAlchemy, Login, CSRF
│   ├── models.py              #   11 DB models
│   ├── forms.py               #   WTForms
│   ├── utils.py               #   Utilities, decorators
│   ├── seed.py                #   Demo data
│   ├── tests_data.py          #   Psychology quiz catalog
│   ├── templates/             #   Jinja2 templates
│   └── blueprints/            #   Routes
├── static/                    # Images
├── instance/                  # SQLite DB (auto-created)
├── uploads/                   # User uploads (auto-created)
├── requirements.txt
├── run.py                     # Entry point
└── README.md
```

### 🚀 Quick Start

```bash
git clone https://github.com/IbragimovRuslan02/Encounter.git
cd Encounter
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open **http://127.0.0.1:5000**

### 👥 Demo accounts

| Login | Password | Role |
|-------|----------|------|
| `admin` | `admin123` | Administrator |
| `shop1` | `seller123` | Approved seller (electronics) |
| `shop2` | `seller123` | Approved seller (home goods) |
| `shop3` | `seller123` | Pending seller application |
| `buyer1` | `buyer123` | Customer with order history |
| `buyer2` | `buyer123` | Customer |

### 👤 Author

**Ibragimov Ruslan**  
GitHub: [@IbragimovRuslan02](https://github.com/IbragimovRuslan02)

---

## 📄 Лицензия / License

Проект распространяется под лицензией **MIT** — см. [LICENSE](./LICENSE).  
This project is licensed under the **MIT License** — see [LICENSE](./LICENSE).

---

<div align="center">

**⭐ If this project was useful, please star it on GitHub! ⭐**

</div>
