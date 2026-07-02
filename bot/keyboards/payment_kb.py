from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def payment_keyboard(price_stars: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"⭐ Оплатить {price_stars} Stars", pay=True)
    )
    builder.row(
        InlineKeyboardButton(text="Не сейчас", callback_data="payment:cancel")
    )
    return builder.as_markup()
