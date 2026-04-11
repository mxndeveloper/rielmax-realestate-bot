import aiohttp
import asyncio
import json
from config import YANDEX_API_KEY, YANDEX_CATALOG_ID
from logger import get_logger

logger = get_logger(__name__)

# Map language codes to system prompts (you can store these in locale files if you prefer)
SYSTEM_PROMPTS = {
    "ru": "Ты — Riel, дружелюбный AI-помощник по недвижимости в России. Отвечай **только по-русски**, полезно, кратко и с эмодзи. Используй ❤️.",
    "en": "You are Riel, a friendly AI real estate assistant in Russia. Answer **only in English**, helpfully, concisely, with emojis. Use ❤️.",
    "tr": "Sen Riel'sin, Rusya'da dost canlısı bir gayrimenkul asistanı. **Sadece Türkçe** cevap ver, faydalı, kısa ve emojilerle. ❤️ kullan.",
    "kk": "Сен Riel, Ресейдегі мейірімді жылжымайтын мүлік көмекшісі. **Тек қазақ тілінде** жауап бер, пайдалы, қысқа және эмодзилермен. ❤️ қолдан.",
    "hy": "Դու Riel-ն ես՝ Ռուսաստանում բարեկամական անշարժ գույքի օգնական: **Պատասխանիր միայն հայերեն**, օգտակար, հակիրճ, էմոջիներով: Օգտագործիր ❤️:",
    "ka": "შენ ხარ Riel, მეგობრული AI უძრავი ქონების ასისტენტი რუსეთში. **უპასუხე მხოლოდ ქართულად**, სასარგებლოდ, მოკლედ, ემოჯით. გამოიყენე ❤️.",
    "zh": "你是Riel，俄罗斯友好的房地产AI助手。**仅用中文回答**，有用、简洁、带表情符号。使用❤️。"
}

async def generate_ai_response(prompt: str, lang: str = "ru", max_retries: int = 2) -> str:
    """
    Call YandexGPT API and force response in the user's language.
    """
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "x-folder-id": YANDEX_CATALOG_ID,
        "Content-Type": "application/json"
    }

    # Use the appropriate system prompt for the requested language
    system_text = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["ru"])

    payload = {
        "modelUri": f"gpt://{YANDEX_CATALOG_ID}/yandexgpt-lite/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 500
        },
        "messages": [
            {"role": "system", "text": system_text},
            {"role": "user", "text": prompt}
        ]
    }

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        logger.info(f"API Response: {data}")
                        return data["result"]["alternatives"][0]["message"]["text"]
                    else:
                        error_text = await resp.text()
                        logger.warning(f"YandexGPT API error {resp.status}: {error_text}")
        except asyncio.TimeoutError:
            logger.warning(f"YandexGPT timeout attempt {attempt+1}")
        except Exception as e:
            logger.warning(f"YandexGPT attempt {attempt+1} failed: {e}")

        if attempt == max_retries - 1:
            # Return error message in the user's language
            error_msgs = {
                "ru": "😔 Извини, Riel временно перегружен. Попробуй через минуту.",
                "en": "😔 Sorry, Riel is temporarily overloaded. Please try again in a minute.",
                "tr": "😔 Üzgünüm, Riel geçici olarak aşırı yüklendi. Lütfen bir dakika sonra tekrar deneyin.",
                "kk": "😔 Кешір, Riel уақытша шамадан тыс жүктелген. Бір минуттан кейін қайталап көріңіз.",
                "hy": "😔 Ներեցեք, Riel-ը ժամանակավորապես ծանրաբեռնված է: Խնդրում ենք մեկ րոպեից նորից փորձել:",
                "ka": "😔 უკაცრავად, Riel დროებით გადატვირთულია. გთხოვთ, სცადოთ ერთ წუთში.",
                "zh": "😔 抱歉，Riel暂时过载。请一分钟后再试。"
            }
            return error_msgs.get(lang, error_msgs["ru"])
        await asyncio.sleep(1)

    return "❌ Ошибка. Напиши позже."