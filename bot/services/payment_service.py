import logging
import os
from aiogram import Bot
from aiogram.fsm.context import FSMContext

from bot.database import repository
from bot.locales import get_locale
from bot.keyboards.subscription_kb import payment_choice_keyboard
from bot.config import PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT, is_free_user
from bot.services.queue_service import add_job

logger = logging.getLogger(__name__)

# DANGER: bypasses ALL payments — every analysis becomes free.
# Local testing only; must be false in production.
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"


async def handle_payment_flow(bot, message, user_id, state, photo_path, gender, lang: str = "ru"):
    """
    Master payment decision function. Called after gender is selected.
    Every analysis is paid: always show the payment method choice.
    """
    L = get_locale(lang)

    if TEST_MODE:
        logger.warning("TEST_MODE is ON — payment skipped for user %s. NEVER enable in production.", user_id)
        await process_successful_payment(bot, user_id, message.chat.id, "test", "0", photo_path, gender, lang=lang)
        return

    # Whitelisted friends analyze for free (FREE_USERS in .env: @usernames/ids).
    user = await repository.get_user(user_id)
    username = user.username if user else None
    if is_free_user(user_id, username):
        logger.info("FREE_USERS whitelist: free analysis for user %s (@%s)", user_id, username)
        await process_successful_payment(bot, user_id, message.chat.id, "whitelist", "0", photo_path, gender, lang=lang)
        return

    await state.update_data(photo_path=photo_path, gender=gender, lang=lang)

    await bot.send_message(
        chat_id=message.chat.id,
        text=L.PAYMENT_CHOICE,
        reply_markup=payment_choice_keyboard(PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT, lang),
        parse_mode="HTML"
    )


async def process_successful_payment(bot: Bot, user_id: int, chat_id: int, method: str, amount: str,
                                     photo_path: str, gender: str,
                                     telegram_payment_charge_id: str | None = None,
                                     lang: str = "ru"):
    """
    Called after any payment method succeeds.
    telegram_payment_charge_id is required for refunds (refundStarPayment) —
    always persist it when Telegram provides one.
    """
    L = get_locale(lang)

    await repository.create_payment(
        user_id=user_id,
        telegram_payment_charge_id=telegram_payment_charge_id,
        amount=amount,
        method=method
    )

    msg = await bot.send_message(chat_id, L.PAYMENT_SUCCESS)

    db_job = await repository.create_analysis_job(user_id, gender)

    job_dict = {
        "user_id": user_id,
        "chat_id": chat_id,
        "photo_path": photo_path,
        "gender": gender,
        "lang": lang,
        "message_id": msg.message_id,
        "db_job_id": db_job.id
    }
    await add_job(job_dict)
