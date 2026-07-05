from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states.user_states import AnalysisFlow
from bot.locales import get_locale
from bot.keyboards.subscription_kb import payment_choice_keyboard
from bot.config import PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT

router = Router()


@router.callback_query(F.data == "check_subscription")
async def process_subscription_check(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Legacy button from the retired "subscribe for a free analysis" promo.
    Every analysis is paid now — route the user to the payment choice
    (or back to the photo prompt if there is no pending analysis).
    """
    data = await state.get_data()
    L = get_locale(data.get("lang", "ru"))
    await callback.answer(L.PROMO_ENDED)
    if data.get("photo_path") and data.get("gender"):
        await state.set_state(AnalysisFlow.waiting_for_payment)
        await callback.message.edit_text(
            text=L.PAYMENT_CHOICE,
            reply_markup=payment_choice_keyboard(PRICE_STARS, CARD_PRICE_RUB, CRYPTO_PRICE_USDT, data.get("lang", "ru")),
            parse_mode="HTML"
        )
    else:
        await state.set_state(AnalysisFlow.waiting_for_photo)
        await callback.message.edit_text(L.PHOTO_PROMPT)
