from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def gender_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="👨 Мужской", callback_data="gender:male"),
        InlineKeyboardButton(text="👩 Женский", callback_data="gender:female"),
    )
    return builder.as_markup()
