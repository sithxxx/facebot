import asyncio
import logging
import sys
import os

# Ensure WeasyPrint can find its libraries on macOS
if sys.platform == 'darwin':
    os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = '/opt/homebrew/lib:' + os.environ.get('DYLD_FALLBACK_LIBRARY_PATH', '')

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from bot.config import TELEGRAM_BOT_TOKEN, TEMP_DIR, WEBHOOK_URL, WEBHOOK_PORT
from bot.database.connection import init_db
from bot.services.queue_service import start_worker
from bot.middleware.throttling import ThrottlingMiddleware
from bot.handlers import start, photo, gender, payment, subscription, errors
from bot.config import CHANNEL_ID
from face_analysis.beauty_predictor import get_predictor

async def on_startup(bot: Bot):
    # Payments kill-switch guard: impossible to miss in logs.
    if os.getenv("TEST_MODE", "false").lower() == "true":
        logging.warning("=" * 60)
        logging.warning("!!! TEST_MODE=true — ВСЕ ПЛАТЕЖИ ОТКЛЮЧЕНЫ, разборы бесплатны")
        logging.warning("!!! Перед продом установите TEST_MODE=false")
        logging.warning("=" * 60)

    # 2. Create TEMP_DIR if not exists
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # 3. Init DB
    await init_db()
    
    # Check if bot is admin in the subscription channel
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=me.id)
        if member.status not in ["administrator", "creator"]:
            logging.warning(f"Bot is not an admin in channel {CHANNEL_ID}. Subscription checks will fail.")
    except Exception as e:
        logging.warning(f"Could not verify bot admin status in channel {CHANNEL_ID}: {e}")
        
    # Start background workers
    # N_WORKERS: concurrent analyses. Each worker peaks ~1-1.5GB (torch +
    # WeasyPrint), so keep 2 on a 4GB VPS.
    await start_worker(bot, n_workers=int(os.getenv("N_WORKERS", 3)))
    
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(bot: Bot):
    if WEBHOOK_URL:
        await bot.delete_webhook()

def main():
    # 1. Init logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    
    # 4. Init bot and dispatcher
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # 6. Register throttling middleware
    dp.message.middleware(ThrottlingMiddleware(rate_limit=60))
    
    # 5. Register all routers
    dp.include_router(start.router)
    dp.include_router(photo.router)
    dp.include_router(gender.router)
    dp.include_router(payment.router)
    dp.include_router(subscription.router)
    dp.include_router(errors.router)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # 7. Start polling or webhook
    if WEBHOOK_URL:
        # Webhook mode
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path="/webhook")
        setup_application(app, dp, bot=bot)
        
        logging.info(f"Starting web app on port {WEBHOOK_PORT}")
        web.run_app(app, host="0.0.0.0", port=WEBHOOK_PORT)
    else:
        # Polling mode
        logging.info("Starting bot in polling mode")
        asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
