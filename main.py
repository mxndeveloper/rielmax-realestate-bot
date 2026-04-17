import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import start, listing, menu, chat, language, search, admin
from middlewares.throttling import ThrottlingMiddleware
from middlewares.i18n import I18nMiddleware
from database import init_db
from logger import get_logger

load_dotenv()
logger = get_logger(__name__)

async def main():
    await init_db()
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    me = await bot.get_me()
    logger.info(f"✅ Connected as @{me.username}")

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

    logger.info("🚀 RielAI SuperBot запущен и готов к работе ❤️")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())