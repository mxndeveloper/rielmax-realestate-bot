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
from config import FREE_PROXIES  # shared proxy list

load_dotenv()
logger = get_logger(__name__)

async def main():
    await init_db()

    # ----- Bot creation with proxy fallback -----
    bot = None
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
        logger.error("❌ All proxies failed. Trying direct connection...")
        try:
            bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
            me = await bot.get_me()
            logger.info(f"✅ Connected directly as @{me.username}")
        except Exception as e:
            logger.error(f"Direct connection also failed: {e}")
            raise RuntimeError("Cannot connect to Telegram. Check network or proxies.")

    # ----- Dispatcher setup -----
    dp = Dispatcher()
    dp.message.middleware(ThrottlingMiddleware(rate_limit=2))
    dp.update.middleware(I18nMiddleware())

    # Include all routers
    dp.include_router(start.router)
    dp.include_router(listing.router)
    dp.include_router(menu.router)
    dp.include_router(chat.router)
    dp.include_router(language.router)
    dp.include_router(search.router)
    dp.include_router(admin.router)

    # Start the background listing updater (runs every 6 hours)
    start_listing_updater()

    logger.info("🚀 RielAI SuperBot запущен и готов к работе ❤️")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())