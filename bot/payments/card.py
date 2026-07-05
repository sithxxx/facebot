from aiogram import Bot
from aiogram.types import LabeledPrice
from bot.config import CARD_PROVIDER_TOKEN
from bot.locales import get_locale

async def send_card_invoice(bot: Bot, chat_id: int, price_rub: int, lang: str = "ru"):
    """Sends Telegram Payments 2.0 invoice (Card)."""
    L = get_locale(lang)
    await bot.send_invoice(
        chat_id=chat_id,
        title=L.INVOICE_TITLE,
        description=L.INVOICE_DESCRIPTION,
        payload=f"analysis_{chat_id}",
        provider_token=CARD_PROVIDER_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label=L.INVOICE_LABEL, amount=price_rub * 100)],  # kopecks
        need_email=False,
        need_phone_number=False,
        need_shipping_address=False
    )
