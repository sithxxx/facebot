import logging

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states.user_states import AnalysisFlow
from bot.locales import get_locale
from bot.keyboards.subscription_kb import payment_choice_keyboard, subscription_keyboard
from bot.config import PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT
from bot.database import repository
from bot.services.subscription_service import check_subscription
from bot.services.payment_service import process_successful_payment

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "check_subscription")
async def process_subscription_check(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Free-first-analysis funnel: verify channel membership; if subscribed,
    run the analysis for free (once per user) — otherwise re-show the offer.
    """
    data = await state.get_data()
    lang = data.get("lang", "ru")
    L = get_locale(lang)
    user_id = callback.from_user.id

    photo_path = data.get("photo_path")
    gender = data.get("gender")
    if not (photo_path and gender):
        # Button pressed from an old message with no pending analysis.
        await callback.answer()
        await state.set_state(AnalysisFlow.waiting_for_photo)
        await callback.message.edit_text(L.PHOTO_PROMPT)
        return

    # Guard against double-claiming (e.g. old promo message pressed again).
    user = await repository.get_user(user_id)
    if user and (user.subscription_used or user.total_analyses > 0):
        await callback.answer(L.PROMO_ENDED)
        await state.set_state(AnalysisFlow.waiting_for_payment)
        await callback.message.edit_text(
            text=L.PAYMENT_CHOICE,
            reply_markup=payment_choice_keyboard(PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT, lang),
            parse_mode="HTML"
        )
        return

    is_subscribed = await check_subscription(bot, user_id)

    if not is_subscribed:
        await callback.answer()
        await callback.message.edit_text(
            text=L.SUB_NOT_VERIFIED,
            reply_markup=subscription_keyboard(lang)
        )
        return

    # Subscribed: consume the one-time promo and start the free analysis.
    await callback.answer()
    await repository.set_subscription_used(user_id)
    logger.info("Sub promo: free analysis for user %s (subscribed)", user_id)

    await callback.message.edit_text(L.SUB_VERIFIED)
    await state.set_state(AnalysisFlow.processing)
    await process_successful_payment(
        bot, user_id, callback.message.chat.id,
        method="sub_promo", amount="0",
        photo_path=photo_path, gender=gender, lang=lang,
    )


@router.callback_query(F.data == "sub_pay")
async def sub_pay(callback: CallbackQuery, state: FSMContext):
    """User declined the subscription promo — show the payment choice."""
    data = await state.get_data()
    lang = data.get("lang", "ru")
    L = get_locale(lang)
    await callback.answer()
    await state.set_state(AnalysisFlow.waiting_for_payment)
    await callback.message.edit_text(
        text=L.PAYMENT_CHOICE,
        reply_markup=payment_choice_keyboard(PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT, lang),
        parse_mode="HTML"
    )
