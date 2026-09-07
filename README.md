# 🧠 Encounter — платформа психологических тестов

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> **RU** — Веб-приложение для прохождения психологических тестов с сохранением истории и админ-панелью.  
> **EN** — Web application for taking psychology quizzes with history tracking and an admin panel.

**English version below** ⬇️

---

## 📑 Содержание / Table of Contents

- [🇷🇺 Русский](#-русский)
  - [О проекте](#-о-проекте)
  - [Возможности](#-возможности)
  - [Стек](#-стек)
  - [Структура](#-структура)
  - [Быстрый старт](#-быстрый-старт)
  - [Конфигурация](#-конфигурация)
  - [Команды](#-команды)
  - [Развёртывание](#-развёртывание)
  - [Автор](#-автор)
- [🇬🇧 English](#-english)
  - [About](#-about)
  - [Features](#-features)
  - [Tech Stack](#-tech-stack-1)
  - [Project Structure](#-project-structure-1)
  - [Quick Start](#-quick-start-1)
  - [Configuration](#-configuration-1)
  - [Commands](#-commands-1)
  - [Deployment](#-deployment)
  - [Author](#-author-1)
- [📄 Лицензия / License](#-лицензия--license)

---

## 🇷🇺 Русский

### 📖 О проекте

**Encounter** — это веб-приложение с психологическими тестами, написанное на Flask. Пользователи могут зарегистрироваться, пройти тесты, получить интерпретацию результата и сохранить историю прохождений. Администратор управляет пользователями и видит всю статистику.

**Включённые тесты:**

| ID | Название | О чём |
|----|----------|-------|
| 🧠 `thinking` | Какой твой тип мышления? | Аналитик / Креативщик / Интуит / Практик |
| 👔 `style` | Какой твой стиль одежды? | Casual / Classic / Trendy / Avant‑garde |
| 💼 `career` | Какое направление карьеры тебе подходит? | Корпорация / Творчество / Фриланс / Предпринимательство |

Каждый тест — 15 вопросов с 4 вариантами ответа. Результат определяется по накопленным баллам в каждой шкале.

### ✨ Возможности

**Для пользователей:**
- 🔐 Регистрация и вход (хеширование паролей через `pbkdf2:sha256`)
- 🧩 Прохождение тестов с подсчётом результата на клиенте
- 📚 История прохождений с подробной расшифровкой ответов
- 👤 Личный кабинет (история, последние результаты)
- 🔒 Защита от перебора и небезопасных действий

**Для администратора:**
- 📊 Дашборд со списком пользователей и общим числом результатов
- 🔍 Детальная карточка пользователя через API (история его тестов)
- 🔐 Разграничение ролей (`admin` / `user`)

### 🛠 Стек

- **Backend:** Python 3.10+, Flask 3, Flask‑SQLAlchemy
- **База данных:** SQLite (легко переключается на PostgreSQL/MySQL)
- **Шаблоны:** Jinja2
- **Frontend:** HTML5, TailwindCSS (CDN), ванильный JavaScript
- **Безопасность:** Werkzeug password hashing, разграничение ролей, защита сессий

### 📁 Структура

```
Encounter/
├── app/                       # Пакет приложения
│   ├── __init__.py            #   Application factory
│   ├── config.py              #   Конфигурация (dev/prod)
│   ├── extensions.py          #   SQLAlchemy
│   ├── models.py              #   Модели User, TestResult
│   ├── tests_data.py          #   Каталог тестов (вопросы, шкалы, результаты)
│   ├── utils.py               #   Декораторы login_required/admin_required
│   ├── seed.py                #   Инициализация БД (создание админа)
│   └── blueprints/            #   Маршруты
│       ├── public.py          #     Главная, тесты, результаты
│       ├── auth.py            #     Логин/регистрация/выход
│       ├── admin.py           #     Админ-панель
│       └── api.py             #     API отправки ответов
├── templates/                 # Jinja2-шаблоны
├── static/                    # CSS, JS, изображения
├── instance/                  # БД SQLite (создаётся автоматически)
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

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 4. Настройка окружения (опционально)
```bash
cp .env.example .env
# Отредактируйте .env — укажите SECRET_KEY, ADMIN_PASSWORD и т.д.
```

#### 5. Запуск
```bash
python run.py
```

Откройте в браузере:
- 🌐 **Сайт:** http://127.0.0.1:5000
- 🔐 **Админ-панель:** http://127.0.0.1:5000/admin_dashboard
  - Логин: `admin` / Пароль: `admin123`

> ⚠️ **Обязательно смените пароль администратора перед публикацией!**

### ⚙️ Конфигурация

Переменные окружения (см. `.env.example`):

| Переменная | Назначение | По умолчанию |
|------------|------------|--------------|
| `FLASK_ENV` | Окружение (`development` / `production`) | `development` |
| `SECRET_KEY` | Секретный ключ Flask | случайный |
| `DATABASE_URL` | URI базы данных | SQLite в `instance/` |
| `ADMIN_USERNAME` | Логин администратора | `admin` |
| `ADMIN_PASSWORD` | Пароль администратора | `admin123` |

### 💻 Команды

```bash
# Запуск в режиме разработки
python run.py

# Запуск через Flask CLI
export FLASK_APP=run.py
flask run

# Запуск на конкретном порту
flask run --host=0.0.0.0 --port=8080
```

### 🌐 Развёртывание

#### Production на Gunicorn + Nginx
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

#### Docker (пример)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

Для production рекомендуется:
- Заменить SQLite на PostgreSQL
- Установить `SECRET_KEY` через переменные окружения
- Настроить HTTPS (Let's Encrypt)

### 👤 Автор

**Ибрагимов Руслан**  
📧 Через GitHub: [@IbragimovRuslan02](https://github.com/IbragimovRuslan02)

Проект 2025–2026

---

## 🇬🇧 English

### 📖 About

**Encounter** is a Flask web application for taking psychology quizzes. Users can register, complete tests, get their result interpretation, and keep a history of all attempts. The admin manages users and reviews aggregate statistics.

**Included tests:**

| ID | Name | What it measures |
|----|------|------------------|
| 🧠 `thinking` | What is your thinking style? | Analytical / Creative / Intuitive / Practical |
| 👔 `style` | What is your clothing style? | Casual / Classic / Trendy / Avant‑garde |
| 💼 `career` | What career path suits you? | Corporate / Creative / Freelance / Entrepreneur |

Each test is 15 questions × 4 options. The result is calculated from accumulated scores per scale.

### ✨ Features

**For users:**
- 🔐 Registration and login (`pbkdf2:sha256` password hashing)
- 🧩 Take quizzes with client-side scoring
- 📚 Persistent history of attempts with detailed answer breakdown
- 👤 Personal dashboard (history, latest results)

**For admins:**
- 📊 Dashboard with all users and total results count
- 🔍 Per-user API endpoint with full attempt history
- 🔐 Role-based access (`admin` / `user`)

### 🛠 Tech Stack

- **Backend:** Python 3.10+, Flask 3, Flask‑SQLAlchemy
- **Database:** SQLite (easy switch to PostgreSQL/MySQL)
- **Templates:** Jinja2
- **Frontend:** HTML5, TailwindCSS (CDN), vanilla JavaScript
- **Security:** Werkzeug password hashing, role-based access, session protection

### 📁 Project Structure

```
Encounter/
├── app/                       # App package
│   ├── __init__.py            #   Application factory
│   ├── config.py              #   Configuration (dev/prod)
│   ├── extensions.py          #   SQLAlchemy
│   ├── models.py              #   User, TestResult models
│   ├── tests_data.py          #   Tests catalog (questions, scales, results)
│   ├── utils.py               #   login_required / admin_required decorators
│   ├── seed.py                #   DB init (default admin user)
│   └── blueprints/            #   Routes
│       ├── public.py          #     Home, tests, results
│       ├── auth.py            #     Login / register / logout
│       ├── admin.py           #     Admin dashboard
│       └── api.py             #     Quiz submission API
├── templates/                 # Jinja2 templates
├── static/                    # CSS, JS, images
├── instance/                  # SQLite DB (auto-created)
├── requirements.txt
├── run.py                     # Entry point
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

### 🚀 Quick Start

#### 1. Clone
```bash
git clone https://github.com/IbragimovRuslan02/Encounter.git
cd Encounter
```

#### 2. Virtual environment
```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Environment setup (optional)
```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, ADMIN_PASSWORD, etc.
```

#### 5. Run
```bash
python run.py
```

Open in browser:
- 🌐 **Site:** http://127.0.0.1:5000
- 🔐 **Admin:** http://127.0.0.1:5000/admin_dashboard
  - Login: `admin` / Password: `admin123`

> ⚠️ **Change the admin password before deploying to production!**

### ⚙️ Configuration

Environment variables (see `.env.example`):

| Variable | Purpose | Default |
|----------|---------|---------|
| `FLASK_ENV` | Environment (`development` / `production`) | `development` |
| `SECRET_KEY` | Flask secret key | random |
| `DATABASE_URL` | Database URI | SQLite in `instance/` |
| `ADMIN_USERNAME` | Admin login | `admin` |
| `ADMIN_PASSWORD` | Admin password | `admin123` |

### 💻 Commands

```bash
# Development server
python run.py

# Flask CLI
export FLASK_APP=run.py
flask run

# Custom host/port
flask run --host=0.0.0.0 --port=8080
```

### 🌐 Deployment

#### Production with Gunicorn + Nginx
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

#### Docker (example)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

For production we recommend:
- Switch from SQLite to PostgreSQL
- Set `SECRET_KEY` via environment variables
- Configure HTTPS (Let's Encrypt)

### 👤 Author

**Ibragimov Ruslan**  
📧 Via GitHub: [@IbragimovRuslan02](https://github.com/IbragimovRuslan02)

Project 2025–2026

---

## 📄 Лицензия / License

Проект распространяется под лицензией **MIT**. Подробнее — в файле [LICENSE](./LICENSE).  
This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

<div align="center">

**⭐ Если проект оказался полезен — поставьте звезду на GitHub! / If this project was useful, please star it on GitHub! ⭐**

</div>
