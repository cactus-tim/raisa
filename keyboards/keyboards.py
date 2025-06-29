from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_end_ikb() -> InlineKeyboardMarkup:
    ikb = [
        [InlineKeyboardButton(text="Закончить создание вакансии", callback_data="end_search")]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def fb_ikb() -> InlineKeyboardMarkup:
    ikb = [
        [InlineKeyboardButton(text="Резюме хорошее", callback_data="fb_yes"),
         InlineKeyboardButton(text="Резюме плохое", callback_data="fb_no")]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard
