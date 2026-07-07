from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import CHANNEL_ID
from bot.locales import get_locale


def subscription_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Free-first-analysis funnel:
    Row 1: subscribe to the channel (url)
    Row 2: "I subscribed — check" (verifies membership)
    Row 3: pay without subscribing (falls through to the payment choice)
    """
    L = get_locale(lang)
    channel_url = f"https://t.me/{CHANNEL_ID.lstrip('@')}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=L.SUB_BTN_SUBSCRIBE, url=channel_url)],
            [InlineKeyboardButton(text=L.SUB_BTN_CHECK, callback_data="check_subscription")],
            [InlineKeyboardButton(text=L.SUB_BTN_PAY, callback_data="sub_pay")],
        ]
    )

def payment_choice_keyboard(stars_price: int, card_price_rub: int, crypto_price_usdt: float, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Payment method selection + cancel. Stars are always available; the card
    and crypto buttons appear only when their provider tokens are configured —
    a visible button that errors out is worse than no button.
    """
    from bot.config import CARD_PROVIDER_TOKEN, CRYPTOBOT_TOKEN
    from bot.locales import get_locale
    L = get_locale(lang)

    rows = [[InlineKeyboardButton(text=L.PAY_BTN_STARS.format(price=stars_price), callback_data="pay:stars")]]
    if CARD_PROVIDER_TOKEN:
        rows.append([InlineKeyboardButton(text=L.PAY_BTN_CARD.format(price=card_price_rub), callback_data="pay:card")])
    if CRYPTOBOT_TOKEN:
        rows.append([InlineKeyboardButton(text=L.PAY_BTN_CRYPTO.format(price=crypto_price_usdt), callback_data="pay:crypto")])
    rows.append([InlineKeyboardButton(text=L.PAY_BTN_CANCEL, callback_data="pay:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
