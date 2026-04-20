import os
import logging
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEBHOOK_PATH = "/webhook"

async def handle_webhook(request):
    """Receive update, log it, and return 200 OK."""
    try:
        data = await request.json()
        logger.info(f"✅ Received update: {data.get('update_id')}")
        # You can also log the message text if present
        if 'message' in data:
            text = data['message'].get('text')
            logger.info(f"   Message: {text}")
    except Exception as e:
        logger.error(f"Error parsing update: {e}")
    return web.Response(status=200, text="OK")

async def health_check(request):
    return web.Response(text="RielAI SuperBot is running ✅")

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get("/", health_check)
    web.run_app(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()