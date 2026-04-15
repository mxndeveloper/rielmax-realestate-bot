import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.types import Update
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
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_DOMAIN = os.getenv("BOTHOST_DOMAIN")
if not WEBHOOK_DOMAIN:
    raise ValueError("BOTHOST_DOMAIN is not set")
WEBHOOK_URL = f"{WEBHOOK_DOMAIN.rstrip('/')}{WEBHOOK_PATH}"

BOT_ENV = os.getenv("BOT_ENV", "development")
BEARER_TOKEN = os.getenv("BOTHOST_BEARER_TOKEN")

if BOT_ENV == "production" and not BEARER_TOKEN:
    raise ValueError("BOTHOST_BEARER_TOKEN is required in production (get it from Bothost dashboard)")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Middlewares
dp.message.middleware(ThrottlingMiddleware(rate_limit=2))
dp.update.middleware(I18nMiddleware())

# Routers
dp.include_router(start.router)
dp.include_router(listing.router)
dp.include_router(menu.router)
dp.include_router(chat.router)
dp.include_router(language.router)
dp.include_router(search.router)
dp.include_router(admin.router)


# ---------- Bearer Token Verification Middleware (only in production) ----------
if BOT_ENV == "production":
    @dp.update.outer_middleware()
    async def verify_bearer_token(handler, event: Update, data: dict):
        request = data.get("request")
        if request is None:
            return await handler(event, data)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return web.Response(status=401, text="Unauthorized: missing Bearer token")
        token = auth_header.split(" ")[1]
        if token != BEARER_TOKEN:
            return web.Response(status=403, text="Forbidden: invalid token")
        return await handler(event, data)


# ---------- Startup & Shutdown ----------
async def on_startup(app):
    await init_db()
    if BOT_ENV == "production":
        await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"Webhook set to {WEBHOOK_URL}")
    else:
        logger.info("Running locally - skipping webhook setup")

async def on_shutdown(app):
    if BOT_ENV == "production":
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

    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()