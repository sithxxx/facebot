import aiohttp
import asyncio
import logging
from bot.config import CRYPTOBOT_TOKEN

logger = logging.getLogger(__name__)

CRYPTOBOT_API_URL = "https://pay.crypt.bot/api"

async def create_crypto_invoice(amount_usdt: float, user_id: int) -> dict:
    """
    Creates invoice via CryptoBot API.
    """
    headers = {
        "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN
    }
    payload = {
        "asset": "USDT",
        "amount": str(amount_usdt),
        "description": "Разбор лица — Face Analysis Bot",
        "payload": str(user_id),
        "expires_in": 3600
    }
    # Optional fields for paid_btn can be added if bot username is known
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{CRYPTOBOT_API_URL}/createInvoice", headers=headers, json=payload) as resp:
            data = await resp.json()
            if data.get("ok"):
                return data["result"]
            else:
                logger.error(f"CryptoBot createInvoice error: {data}")
                raise ValueError("Failed to create crypto invoice")

async def check_crypto_invoice(invoice_id: int) -> str:
    """
    Checks invoice status via CryptoBot API.
    Returns status: "active" | "paid" | "expired"
    """
    headers = {
        "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN
    }
    params = {
        "invoice_ids": str(invoice_id)
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{CRYPTOBOT_API_URL}/getInvoices", headers=headers, params=params) as resp:
            data = await resp.json()
            if data.get("ok") and data["result"]["items"]:
                return data["result"]["items"][0]["status"]
            return "expired"

async def start_invoice_polling(bot, invoice_id: int, user_id: int, chat_id: int, photo_path: str, gender: str, lang: str = "ru"):
    """
    Polls check_crypto_invoice() every 10 seconds.
    Timeout: 3600 seconds.
    """
    from bot.services.payment_service import process_successful_payment
    from bot.locales import get_locale
    L = get_locale(lang)

    max_retries = 360  # 1 hour (360 * 10s)
    for _ in range(max_retries):
        try:
            status = await check_crypto_invoice(invoice_id)
            if status == "paid":
                await process_successful_payment(bot, user_id, chat_id, method="crypto", amount="USDT", photo_path=photo_path, gender=gender, lang=lang)
                return
            elif status == "expired":
                await bot.send_message(chat_id, L.CRYPTO_EXPIRED)
                return
        except Exception as e:
            logger.error(f"Error polling crypto invoice {invoice_id}: {e}")

        await asyncio.sleep(10)

    # If timeout
    await bot.send_message(chat_id, L.CRYPTO_EXPIRED)
