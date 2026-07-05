from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.locales import get_locale

def gender_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    L = get_locale(lang)
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text=L.GENDER_MALE, callback_data="gender:male"),
        InlineKeyboardButton(text=L.GENDER_FEMALE, callback_data="gender:female"),
    )
    return builder.as_markup()
