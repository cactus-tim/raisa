from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_new_vacancy_kb() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Новая вакансия')]
        ],
        resize_keyboard=True
    )
    return keyboard


def fb_ikb() -> InlineKeyboardMarkup:
    ikb = [
        [InlineKeyboardButton(text="Резюме хорошее", callback_data="fb_yes"),
         InlineKeyboardButton(text="Резюме плохое", callback_data="fb_no")]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard
