import aiohttp
import asyncio
import json
from functools import lru_cache
from config import YANDEX_API_KEY, YANDEX_CATALOG_ID
from logger import get_logger

logger = get_logger(__name__)

# Simple in‑memory cache (use Redis for production)
_cache = {}

async def generate_ai_response(prompt: str, lang: str = "ru") -> str:
    key = f"{prompt}_{lang}"
    if key in _cache:
        return _cache[key]

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "x-folder-id": YANDEX_CATALOG_ID,
        "Content-Type": "application/json"
    }

    # Optimised system prompt – short and direct
    system_prompt = f"You are Riel, a real estate AI. Answer in {lang}. Be brief, helpful, use emojis."

    payload = {
        "modelUri": f"gpt://{YANDEX_CATALOG_ID}/yandexgpt-lite/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.5,      # lower = faster
            "maxTokens": 300         # reduce for speed
        },
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": prompt}
        ]
    }

    for attempt in range(2):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = data["result"]["alternatives"][0]["message"]["text"]
                        _cache[key] = response
                        return response
                    else:
                        logger.warning(f"YandexGPT API error {resp.status}: {await resp.text()}")
        except asyncio.TimeoutError:
            logger.warning(f"YandexGPT timeout attempt {attempt+1}")
        except Exception as e:
            logger.warning(f"YandexGPT attempt {attempt+1} failed: {e}")

    # Fallback message (in user’s language)
    fallback = {
        "ru": "😔 Извини, Riel временно перегружен. Попробуй через минуту.",
        "en": "😔 Sorry, Riel is temporarily overloaded. Please try again in a minute.",
        "tr": "😔 Üzgünüm, Riel geçici olarak aşırı yüklendi. Lütfen bir dakika sonra tekrar deneyin.",
        "kk": "😔 Кешір, Riel уақытша шамадан тыс жүктелген. Бір минуттан кейін қайталап көріңіз.",
        "hy": "😔 Ներեցեք, Riel-ը ժամանակավորապես ծանրաբեռնված է: Խնդրում ենք մեկ րոպեից նորից փորձել:",
        "ka": "😔 უკაცრავად, Riel დროებით გადატვირთულია. გთხოვთ, სცადოთ ერთ წუთში.",
        "zh": "😔 抱歉，Riel暂时过载。请一分钟后再试。"
    }
    return fallback.get(lang, fallback["ru"])