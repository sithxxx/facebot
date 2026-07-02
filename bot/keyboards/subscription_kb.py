from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.locales.ru import SUB_OFFER

def subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Two buttons stacked vertically:
    Row 1: "📢 Подписаться на канал" — url button
    Row 2: "✅ Я подписался — проверить" — callback_data="check_subscription"
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url="https://t.me/twitch_s1thxxx")],
            [InlineKeyboardButton(text="✅ Я подписался — проверить", callback_data="check_subscription")]
        ]
    )

def payment_choice_keyboard(stars_price: int, card_price_rub: int, crypto_price_usdt: float) -> InlineKeyboardMarkup:
    """
    Payment method selection + cancel. Stars are always available; the card
    and crypto buttons appear only when their provider tokens are configured —
    a visible button that errors out is worse than no button.
    """
    from bot.config import CARD_PROVIDER_TOKEN, CRYPTOBOT_TOKEN

    rows = [[InlineKeyboardButton(text=f"⭐ {stars_price} Telegram Stars", callback_data="pay:stars")]]
    if CARD_PROVIDER_TOKEN:
        rows.append([InlineKeyboardButton(text=f"💳 {card_price_rub} ₽ картой", callback_data="pay:card")])
    if CRYPTOBOT_TOKEN:
        rows.append([InlineKeyboardButton(text=f"₿ {crypto_price_usdt} USDT крипта", callback_data="pay:crypto")])
    rows.append([InlineKeyboardButton(text="Отмена", callback_data="pay:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
