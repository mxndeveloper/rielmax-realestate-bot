import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from handlers import start, listing, menu, chat, language, search
from middlewares.throttling import ThrottlingMiddleware
from middlewares.i18n import I18nMiddleware
from database import init_db
from logger import get_logger

load_dotenv()

logger = get_logger(__name__)

async def main():
    await init_db()

    bot = None

    # List of free proxies to try (HTTP)
    free_proxies = [
    "http://20.206.106.192:80",
    "http://185.199.228.220:80",
    "http://38.242.204.27:3128",
    "http://185.198.27.38:3128",
    "http://147.45.186.28:3128",
    "http://167.103.115.102:8800",
    "http://5.250.183.76:3128",
    "http://14.97.89.207:80",
    "http://167.71.5.83:8080",
    "http://192.241.132.32:3128",
    "http://8.213.151.128:3128",
    "http://195.26.224.135:80",
    "http://167.99.236.14:80",
    "http://38.34.179.179:8449",
    "http://41.220.16.218:80",
    "http://111.79.111.126:3128",
    "http://173.245.49.222:80",
    "http://173.245.49.105:80",
    "http://173.245.49.112:80",
    "http://173.245.49.163:80",
    ]

    for proxy_url in free_proxies:
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
            raise RuntimeError("Cannot connect to Telegram. Try mobile hotspot or a different proxy.")

    dp = Dispatcher()

    dp.message.middleware(ThrottlingMiddleware(rate_limit=2))
    dp.update.middleware(I18nMiddleware())

    dp.include_router(start.router)
    dp.include_router(listing.router)
    dp.include_router(menu.router)
    dp.include_router(chat.router)
    dp.include_router(language.router)
    dp.include_router(search.router)

    logger.info("🚀 RielAI SuperBot запущен и готов к работе ❤️")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())