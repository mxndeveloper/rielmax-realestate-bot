import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv

from handlers import start, listing, menu, chat, language, search, admin
from middlewares.throttling import ThrottlingMiddleware
from middlewares.i18n import I18nMiddleware
from database import init_db

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Configuration ----------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN missing")

WEBHOOK_PATH = "/webhook"
WEBHOOK_DOMAIN = os.getenv("BOTHOST_DOMAIN")
if not WEBHOOK_DOMAIN:
    raise ValueError("BOTHOST_DOMAIN environment variable not set")
WEBHOOK_URL = f"{WEBHOOK_DOMAIN.rstrip('/')}{WEBHOOK_PATH}"

# Optional secret token for extra security
SECRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- Middlewares ----------
dp.message.middleware(ThrottlingMiddleware(rate_limit=2))
dp.update.middleware(I18nMiddleware())

# ---------- Routers ----------
dp.include_router(start.router)
dp.include_router(listing.router)
dp.include_router(menu.router)
dp.include_router(chat.router)
dp.include_router(language.router)
dp.include_router(search.router)
dp.include_router(admin.router)

# ---------- Webhook Security Middleware (Optional) ----------
@dp.update.outer_middleware()
async def verify_secret_token(handler, event, data):
    request = data.get("request")
    if request and SECRET_TOKEN:
        token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if token != SECRET_TOKEN:
            return web.Response(status=403, text="Forbidden")
    return await handler(event, data)

# ---------- Startup & Shutdown ----------
async def on_startup(app):
    await init_db()
    await bot.set_webhook(WEBHOOK_URL, secret_token=SECRET_TOKEN)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    logger.info("Webhook deleted")

# ---------- Web Application ----------
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