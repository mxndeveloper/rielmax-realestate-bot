import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv

# Import your routers
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

# Bothost webhook settings
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_DOMAIN = os.getenv("BOTHOST_DOMAIN")  # e.g., "https://your-bot.bothost.ru"
if not WEBHOOK_DOMAIN:
    raise ValueError("BOTHOST_DOMAIN is not set (e.g., https://your-bot.bothost.ru)")

WEBHOOK_URL = f"{WEBHOOK_DOMAIN.rstrip('/')}{WEBHOOK_PATH}"
SECRET_TOKEN = os.getenv("BOTHOST_WEBHOOK_TOKEN")  # optional but recommended
if not SECRET_TOKEN:
    logger.warning("BOTHOST_WEBHOOK_TOKEN not set. Webhook will be insecure.")

# ---------- Bot and Dispatcher ----------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Middlewares
dp.message.middleware(ThrottlingMiddleware(rate_limit=2))
dp.update.middleware(I18nMiddleware())

# Include routers
dp.include_router(start.router)
dp.include_router(listing.router)
dp.include_router(menu.router)
dp.include_router(chat.router)
dp.include_router(language.router)
dp.include_router(search.router)
dp.include_router(admin.router)


# ---------- Startup and Shutdown ----------
async def on_startup(app):
    await init_db()
    # Only set webhook when running on Bothost (production)
    if os.getenv("BOT_ENV") == "production":
        # Set webhook with secret token if provided
        await bot.set_webhook(WEBHOOK_URL, secret_token=SECRET_TOKEN)
        logger.info(f"Webhook set to {WEBHOOK_URL} with secret token")
    else:
        logger.info("Running locally - skipping webhook setup (use polling instead)")


async def on_shutdown(app):
    # Only delete webhook in production
    if os.getenv("BOT_ENV") == "production":
        await bot.delete_webhook()
        logger.info("Webhook deleted")
    else:
        logger.info("Local run - no webhook to delete")


# ---------- Application Setup ----------
def main():
    app = web.Application()
    setup_application(app, dp, bot=bot)

    # Health check endpoint (public, no token required)
    async def health_check(request):
        return web.Response(text="RielAI SuperBot is running ✅")
    app.router.add_get("/", health_check)

    # Register webhook handler
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Bothost passes the port via environment variable PORT (default 8080)
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()