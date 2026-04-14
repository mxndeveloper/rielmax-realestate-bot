import aiohttp
import feedparser
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import PROXY_LIST  # import your proxy list

router = Router()
PROXY_URL = PROXY_LIST[0]  # use the first working proxy

class SearchStates(StatesGroup):
    waiting_for_query = State()

@router.callback_query(F.data == "search_listings")
async def start_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔍 Введите запрос для поиска (например: 2‑комнатная центр Москва до 20 млн):")
    await state.set_state(SearchStates.waiting_for_query)
    await callback.answer()

@router.message(SearchStates.waiting_for_query)
async def perform_search(message: Message, state: FSMContext):
    query = message.text
    search_q = query.replace(" ", "+")
    url = f"https://www.avito.ru/moskva/kvartiry/prodam/rss?q={search_q}"
    
    # Use aiohttp with proxy to fetch RSS
    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=PROXY_URL, timeout=15) as resp:
            if resp.status != 200:
                await message.answer("Не удалось получить данные. Попробуйте позже.")
                await state.clear()
                return
            xml = await resp.text()
            feed = feedparser.parse(xml)
            if not feed.entries:
                await message.answer("По вашему запросу ничего не найдено. Попробуйте другие ключевые слова.")
            else:
                for entry in feed.entries[:5]:
                    await message.answer(
                        f"🏠 *{entry.title}*\n🔗 [Смотреть]({entry.link})",
                        parse_mode="Markdown"
                    )
    await state.clear()