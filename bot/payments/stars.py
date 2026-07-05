from aiogram import Bot
from aiogram.types import LabeledPrice
from bot.locales import get_locale

async def send_stars_invoice(bot: Bot, chat_id: int, price_stars: int, lang: str = "ru"):
    """Sends Telegram Stars invoice."""
    L = get_locale(lang)
    await bot.send_invoice(
        chat_id=chat_id,
        title=L.INVOICE_TITLE,
        description=L.INVOICE_DESCRIPTION,
        payload=f"analysis_{chat_id}",
        provider_token="",  # Empty for Stars
        currency="XTR",
        prices=[LabeledPrice(label=L.INVOICE_LABEL, amount=price_stars)],
    )
