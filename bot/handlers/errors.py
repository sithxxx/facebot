from aiogram import Router
from aiogram.types import ErrorEvent
import logging
from bot.locales import ru

router = Router()

@router.errors()
async def global_error_handler(event: ErrorEvent):
    """Global error handler."""
    logging.error(f"Update: {event.update}\nException: {event.exception}", exc_info=True)
    
    if event.update.message:
        try:
            await event.update.message.answer(ru.ERROR_GENERAL)
        except Exception:
            pass
    elif event.update.callback_query:
        try:
            await event.update.callback_query.message.answer(ru.ERROR_GENERAL)
        except Exception:
            pass
