import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from handlers import start, listing, menu, chat, language, search, admin
from middlewares.throttling import ThrottlingMiddleware
from middlewares.i18n import I18nMiddleware
from database import init_db
from logger import get_logger
from data.update_pipeline import start_listing_updater
from config import FREE_PROXIES  # only used in development

load_dotenv()
logger = get_logger(__name__)

async def main():
    await init_db()

    # Detect environment
    bot_env = os.getenv("BOT_ENV", "development")
    bot = None

    if bot_env == "production":
        # Production: direct connection (Bothost provides clean IP)
        logger.info("🌍 Production mode: using direct connection (no proxy)")
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        me = await bot.get_me()
        logger.info(f"✅ Connected directly as @{me.username}")
    else:
        # Development: try proxies, fallback to direct
        logger.info("🛠️ Development mode: trying proxies...")
        for proxy_url in FREE_PROXIES:
            try:
                session = AiohttpSession(proxy=proxy_url)
                bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"), session=session)
                me = await bot.get_me()
                logger.info(f"✅ Connected via proxy {proxy_url} as @{me.username}")
                break
            except Exception as e:
                logger.warning(f"❌ Proxy {proxy_url} failed: {e}")
                continue

        if bot is None:
            logger.warning("⚠️ All proxies failed, trying direct connection...")
            bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
            me = await bot.get_me()
            logger.info(f"✅ Connected directly as @{me.username}")

    # ----- Dispatcher setup -----
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

    start_listing_updater()
    logger.info("🚀 RielAI SuperBot запущен и готов к работе ❤️")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())