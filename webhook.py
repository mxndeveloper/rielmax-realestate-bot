import os
from dotenv import load_dotenv
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from handlers import start, listing, menu, chat, language, search, admin
from middlewares.throttling import ThrottlingMiddleware
from middlewares.i18n import I18nMiddleware
from database import init_db
from logger import get_logger

load_dotenv()
logger = get_logger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing in .env")

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://rielaibot.bothost.ru/webhook"   # Your exact Bothost domain

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(ThrottlingMiddleware(rate_limit=2))
dp.update.middleware(I18nMiddleware())

dp.include_router(start.router)
dp.include_router(listing.router)
dp.include_router(menu.router)
dp.include_router(chat.router)
dp.include_router(language.router)
dp.include_router(search.router)
dp.include_router(admin.router)

async def on_startup(app):
    await init_db()
    
    # Only set webhook when running on Bothost (production)
    if os.getenv("BOT_ENV") == "production":
        try:
            await bot.set_webhook(WEBHOOK_URL)
            logger.info(f"✅ Webhook successfully set to {WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    else:
        logger.info("Running locally - skipping webhook setup")

    logger.info("🚀 RielAI SuperBot started")

async def on_shutdown(app):
    if os.getenv("BOT_ENV") == "production":
        await bot.delete_webhook()
    logger.info("Shutdown complete")

def main():
    app = web.Application()
    setup_application(app, dp, bot=bot)
    
    app.router.add_get("/", lambda r: web.Response(text="RielAI SuperBot is running ✅"))
    
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    web.run_app(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()