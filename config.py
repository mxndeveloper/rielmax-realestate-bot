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

# Proxy list for CIAN and Telegram connection
FREE_PROXIES = [
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