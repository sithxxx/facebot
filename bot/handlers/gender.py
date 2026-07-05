from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.user_states import AnalysisFlow
from bot.locales import get_locale
from bot.services.payment_service import handle_payment_flow

router = Router()

@router.callback_query(AnalysisFlow.waiting_for_gender, F.data.startswith("gender:"))
async def process_gender(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    gender = callback.data.split(":")[1]

    data = await state.get_data()
    lang = data.get("lang", "ru")
    L = get_locale(lang)

    gender_text = L.GENDER_MALE if gender == "male" else L.GENDER_FEMALE
    await callback.message.edit_text(L.GENDER_CHOSEN.format(gender=gender_text))

    photo_path = data.get("photo_path")

    await state.set_state(AnalysisFlow.waiting_for_payment)

    await handle_payment_flow(
        bot=bot,
        message=callback.message,
        user_id=callback.from_user.id,
        state=state,
        photo_path=photo_path,
        gender=gender,
        lang=lang,
    )
