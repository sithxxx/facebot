import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, PreCheckoutQuery, Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.states.user_states import AnalysisFlow
from bot.locales import get_locale
from bot.config import PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT
from bot.payments.stars import send_stars_invoice
from bot.payments.card import send_card_invoice
from bot.payments.crypto import create_crypto_invoice, start_invoice_polling
from bot.services.payment_service import process_successful_payment

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(AnalysisFlow.waiting_for_payment, F.data.startswith("pay:"))
async def handle_payment_choice(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    method = callback.data.split(":")[1]
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    data = await state.get_data()
    lang = data.get("lang", "ru")
    L = get_locale(lang)

    if method == "cancel":
        await callback.message.edit_text(L.PAYMENT_CANCELLED)
        await state.set_state(AnalysisFlow.waiting_for_photo)
        await bot.send_message(chat_id, L.PHOTO_PROMPT)
        return

    # First, edit out the keyboard so they can't spam it
    await callback.message.edit_reply_markup(reply_markup=None)

    if method == "stars":
        await send_stars_invoice(bot, chat_id, PRICE_STARS, lang)
    elif method == "card":
        await send_card_invoice(bot, chat_id, CARD_PRICE_RUB, lang)
    elif method == "crypto":
        try:
            photo_path = data.get("photo_path")
            gender = data.get("gender")

            invoice_data = await create_crypto_invoice(CRYPTO_PRICE_USDT, user_id)
            pay_url = invoice_data["pay_url"]
            invoice_id = invoice_data["invoice_id"]

            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=L.CRYPTO_PAY_BUTTON, url=pay_url)
            ]])
            await bot.send_message(chat_id, L.CRYPTO_INVOICE_SENT, reply_markup=kb, parse_mode="HTML")

            asyncio.create_task(start_invoice_polling(bot, invoice_id, user_id, chat_id, photo_path, gender, lang))
            await state.set_state(AnalysisFlow.processing)

        except Exception as e:
            logger.error(f"Crypto error: {e}")
            await bot.send_message(chat_id, L.ERROR_GENERAL)

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    # Always answer OK for both Stars and Card
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    payment_info = message.successful_payment

    currency = payment_info.currency
    if currency == "XTR":
        method = "stars"
        amount = str(payment_info.total_amount)
    else:
        method = "card"
        amount = str(payment_info.total_amount / 100)

    data = await state.get_data()
    photo_path = data.get("photo_path", "")
    gender = data.get("gender", "male")
    lang = data.get("lang", "ru")

    await state.set_state(AnalysisFlow.processing)

    await process_successful_payment(
        bot=bot,
        user_id=user_id,
        chat_id=chat_id,
        method=method,
        amount=amount,
        photo_path=photo_path,
        gender=gender,
        # Needed for refunds (refundStarPayment) and dispute handling.
        telegram_payment_charge_id=payment_info.telegram_payment_charge_id,
        lang=lang,
    )
