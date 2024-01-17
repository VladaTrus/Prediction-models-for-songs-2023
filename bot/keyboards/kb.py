from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

menu = [
    [
        InlineKeyboardButton(text="📝 Оставить отзыв", callback_data="review"),
        InlineKeyboardButton(
            text="🖼 Сгенерировать подборку песен по жанру",
            callback_data="genre_playlist",
        ),
    ],
    [
        InlineKeyboardButton(text="💳 Предсказать жанр песни", callback_data="predict"),
        InlineKeyboardButton(text="Посмотреть статистику бота", callback_data="stats"),
    ],
    [InlineKeyboardButton(text="🔎 Помощь", callback_data="help")],
]
menu_kb = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True
)
iexit_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]
    ]
)
