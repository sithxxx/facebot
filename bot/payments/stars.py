from aiogram import Bot
from aiogram.types import LabeledPrice

async def send_stars_invoice(bot: Bot, chat_id: int, price_stars: int):
    """
    Sends Telegram Stars invoice.
    """
    await bot.send_invoice(
        chat_id=chat_id,
        title="Разбор лица — полный анализ",
        description="25-страничный PDF с математическим разбором 20 метрик лица",
        payload=f"analysis_{chat_id}",
        provider_token="",  # Empty for Stars
        currency="XTR",
        prices=[LabeledPrice(label="Анализ лица", amount=price_stars)],
    )
