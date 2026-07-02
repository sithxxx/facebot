from aiogram import Bot
from aiogram.types import LabeledPrice
from bot.config import CARD_PROVIDER_TOKEN

async def send_card_invoice(bot: Bot, chat_id: int, price_rub: int):
    """
    Sends Telegram Payments 2.0 invoice (Card).
    """
    await bot.send_invoice(
        chat_id=chat_id,
        title="Разбор лица — полный анализ",
        description="25-страничный PDF с математическим разбором 20 метрик лица",
        payload=f"analysis_{chat_id}",
        provider_token=CARD_PROVIDER_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label="Анализ лица", amount=price_rub * 100)],  # kopecks
        need_email=False,
        need_phone_number=False,
        need_shipping_address=False
    )
