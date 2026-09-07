"""Все формы приложения."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import (
    BooleanField, DecimalField, IntegerField, PasswordField, SelectField,
    StringField, SubmitField, TextAreaField,
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp,
)


# ─────────────── Auth ───────────────

class RegisterForm(FlaskForm):
    username = StringField(
        "Логин",
        validators=[
            DataRequired(),
            Length(min=3, max=80),
            Regexp(r"^[A-Za-z0-9_]+$", message="Только латиница, цифры и _"),
        ],
    )
    email = StringField("Email", validators=[Optional(), Email()])
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(), Length(min=4, max=128)],
    )
    confirm = PasswordField(
        "Повторите пароль",
        validators=[DataRequired(), EqualTo("password", message="Пароли не совпадают")],
    )
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


# ─────────────── Профиль пользователя ───────────────

class ProfileForm(FlaskForm):
    full_name = StringField("Полное имя", validators=[Optional(), Length(max=150)])
    email = StringField("Email", validators=[Optional(), Email()])
    phone = StringField("Телефон", validators=[Optional(), Length(max=30)])
    bio = TextAreaField("О себе", validators=[Optional(), Length(max=1000)])
    avatar = FileField(
        "Аватар",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Только изображения")],
    )
    submit = SubmitField("Сохранить")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Текущий пароль", validators=[DataRequired()])
    new_password = PasswordField(
        "Новый пароль", validators=[DataRequired(), Length(min=4, max=128)]
    )
    confirm = PasswordField(
        "Повторите новый пароль",
        validators=[DataRequired(), EqualTo("new_password", message="Пароли не совпадают")],
    )
    submit = SubmitField("Сменить пароль")


# ─────────────── Заявка на продавца ───────────────

class SellerApplicationForm(FlaskForm):
    shop_name = StringField(
        "Название магазина",
        validators=[DataRequired(), Length(min=2, max=120)],
    )
    shop_description = TextAreaField(
        "Описание магазина",
        validators=[Optional(), Length(max=2000)],
    )
    motivation = TextAreaField(
        "Почему вы хотите стать продавцом?",
        validators=[DataRequired(), Length(min=20, max=2000)],
    )
    banner = FileField(
        "Баннер магазина (опционально)",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Только изображения")],
    )
    submit = SubmitField("Подать заявку")


# ─────────────── Товары ───────────────

class ProductForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired(), Length(min=3, max=200)])
    category_id = SelectField("Категория", coerce=int, validators=[DataRequired()])
    price = DecimalField(
        "Цена (₽)",
        validators=[DataRequired(), NumberRange(min=0, max=10_000_000)],
    )
    old_price = DecimalField(
        "Старая цена (₽, опционально, для скидки)",
        validators=[Optional(), NumberRange(min=0, max=10_000_000)],
    )
    stock = IntegerField(
        "Остаток на складе",
        validators=[DataRequired(), NumberRange(min=0, max=1_000_000)],
    )
    description = TextAreaField(
        "Описание", validators=[Optional(), Length(max=5000)]
    )
    images = MultipleFileField(
        "Фотографии (можно несколько, первая станет главной)",
        validators=[Optional()],
    )
    submit = SubmitField("Сохранить")


# ─────────────── Оформление заказа ───────────────

class CheckoutForm(FlaskForm):
    delivery_name = StringField(
        "ФИО получателя", validators=[DataRequired(), Length(min=3, max=150)]
    )
    delivery_phone = StringField(
        "Телефон", validators=[DataRequired(), Length(min=5, max=30)]
    )
    delivery_address = StringField(
        "Адрес доставки", validators=[DataRequired(), Length(min=5, max=300)]
    )
    delivery_comment = TextAreaField(
        "Комментарий к заказу (опционально)",
        validators=[Optional(), Length(max=1000)],
    )
    submit = SubmitField("Подтвердить заказ")


# ─────────────── Отзыв ───────────────

class ReviewForm(FlaskForm):
    rating = SelectField(
        "Оценка",
        choices=[(5, "⭐⭐⭐⭐⭐ Отлично"), (4, "⭐⭐⭐⭐ Хорошо"),
                 (3, "⭐⭐⭐ Нормально"), (2, "⭐⭐ Плохо"),
                 (1, "⭐ Ужасно")],
        coerce=int,
        validators=[DataRequired()],
    )
    text = TextAreaField("Отзыв", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Оставить отзыв")


# ─────────────── Чат ───────────────

class MessageForm(FlaskForm):
    text = TextAreaField(
        "Сообщение", validators=[DataRequired(), Length(min=1, max=2000)]
    )
    submit = SubmitField("Отправить")


# ─────────────── Поиск (форма для navbar) ───────────────

class SearchForm(FlaskForm):
    q = StringField("Поиск", validators=[Optional(), Length(max=120)])
