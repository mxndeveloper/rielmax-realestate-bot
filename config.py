import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN missing")

# YandexGPT
YANDEX_API_KEY = os.getenv("YANDEXGPT_API_KEY")
YANDEX_CATALOG_ID = os.getenv("YANDEX_GPT_CATALOG_ID") or os.getenv("YANDEX_FOLDER_ID")
if not YANDEX_CATALOG_ID:
    raise ValueError("YANDEX_GPT_CATALOG_ID missing")

# Proxy list – all working SOCKS5 from your table
PROXY_LIST = [
    "socks5://ausqwjbz:ddtwqy04h3po@31.59.20.176:6754",
    "socks5://ausqwjbz:ddtwqy04h3po@23.95.150.145:6114",
    "socks5://ausqwjbz:ddtwqy04h3po@198.23.239.134:6540",
    "socks5://ausqwjbz:ddtwqy04h3po@45.38.107.97:6014",
]

# Rate limiting (messages per second per user)
RATE_LIMIT = 2