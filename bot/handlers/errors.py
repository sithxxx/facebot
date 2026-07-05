from aiogram import Router
from aiogram.types import ErrorEvent
import logging
from bot.locales import get_locale
from bot.database import repository

router = Router()

@router.errors()
async def global_error_handler(event: ErrorEvent):
    """Global error handler."""
    logging.error(f"Update: {event.update}\nException: {event.exception}", exc_info=True)

    async def _reply(target, user_id):
        try:
            L = get_locale(await repository.get_user_lang(user_id))
            await target.answer(L.ERROR_GENERAL)
        except Exception:
            pass

    if event.update.message:
        await _reply(event.update.message, event.update.message.from_user.id)
    elif event.update.callback_query:
        await _reply(event.update.callback_query.message, event.update.callback_query.from_user.id)
