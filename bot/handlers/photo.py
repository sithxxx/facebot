from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.user_states import AnalysisFlow
from bot.locales import get_locale
from bot.services import file_service
from bot.keyboards.gender_kb import gender_keyboard
from bot.database import repository
from face_analysis.validator import validate_image

router = Router()

@router.message(AnalysisFlow.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    lang = await repository.get_user_lang(message.from_user.id)
    L = get_locale(lang)

    # Download the highest resolution version of the photo
    photo = message.photo[-1]
    bot = message.bot
    local_path = await file_service.save_photo(bot, photo.file_id, message.from_user.id)

    is_valid, error_reason = validate_image(local_path)

    if not is_valid:
        error_msg = L.PHOTO_ERRORS.get(error_reason, L.ERROR_GENERAL)
        await message.answer(f"❌ {error_msg}")
        file_service.delete_file(local_path)
        return

    # Keep photo path AND language in the flow state (used down the pipeline).
    await state.update_data(photo_path=local_path, lang=lang or "ru")

    await message.answer(L.GENDER_PROMPT, reply_markup=gender_keyboard(lang or "ru"))
    await state.set_state(AnalysisFlow.waiting_for_gender)


@router.message(AnalysisFlow.waiting_for_photo)
async def handle_not_photo(message: Message, state: FSMContext):
    """Fallback if user sends text instead of photo."""
    L = get_locale(await repository.get_user_lang(message.from_user.id))
    await message.answer(L.PHOTO_PROMPT)
