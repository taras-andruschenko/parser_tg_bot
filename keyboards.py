from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


inline_keyboard_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Новий пошук", callback_data="btn_search")],
])

inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("Новий пошук", callback_data="btn_search"),
        InlineKeyboardButton("Так", callback_data="btn_next"),
    ],
])