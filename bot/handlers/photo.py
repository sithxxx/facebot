from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.user_states import AnalysisFlow
from bot.locales import ru
from bot.services import file_service
from bot.keyboards.gender_kb import gender_keyboard
from face_analysis.validator import validate_image

router = Router()

@router.message(AnalysisFlow.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    # 2. Download the highest resolution version of the photo
    photo = message.photo[-1]
    
    # 3. Save to TEMP_DIR
    bot = message.bot
    local_path = await file_service.save_photo(bot, photo.file_id, message.from_user.id)
    
    # 4. Run validate_image() from Stage 1
    is_valid, error_reason = validate_image(local_path)
    
    if not is_valid:
        # Invalid: send error message, stay in state, delete temp file
        error_msg = ru.PHOTO_ERRORS.get(error_reason, ru.ERROR_GENERAL)
        await message.answer(f"❌ {error_msg}")
        file_service.delete_file(local_path)
        return
        
    # 5. Store photo_path in FSMContext data
    await state.update_data(photo_path=local_path)
    
    # 6. Send gender selection keyboard
    await message.answer(ru.GENDER_PROMPT, reply_markup=gender_keyboard())
    
    # 7. Set state
    await state.set_state(AnalysisFlow.waiting_for_gender)

@router.message(AnalysisFlow.waiting_for_photo)
async def handle_not_photo(message: Message):
    """Fallback if user sends text instead of photo."""
    await message.answer(ru.PHOTO_PROMPT)
