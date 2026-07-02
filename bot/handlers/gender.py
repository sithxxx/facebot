from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.user_states import AnalysisFlow
from bot.services.payment_service import handle_payment_flow

router = Router()

@router.callback_query(AnalysisFlow.waiting_for_gender, F.data.startswith("gender:"))
async def process_gender(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    
    gender = callback.data.split(":")[1]
    
    gender_text = "👨 Мужской" if gender == "male" else "👩 Женский"
    await callback.message.edit_text(f"Выбран пол: {gender_text}")
    
    data = await state.get_data()
    photo_path = data.get("photo_path")
    
    await state.set_state(AnalysisFlow.waiting_for_payment)
    
    await handle_payment_flow(
        bot=bot,
        message=callback.message,
        user_id=callback.from_user.id,
        state=state,
        photo_path=photo_path,
        gender=gender
    )
