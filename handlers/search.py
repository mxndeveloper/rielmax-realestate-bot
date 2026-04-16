from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite
from database import DB_PATH

router = Router()

class SearchStates(StatesGroup):
    waiting_for_query = State()

@router.callback_query(F.data == "search_listings")
async def start_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🔍 Введите параметры поиска (например: *2‑комнатная в центре до 20 млн*)",
        parse_mode="Markdown"
    )
    await state.set_state(SearchStates.waiting_for_query)
    await callback.answer()

@router.message(SearchStates.waiting_for_query)
async def perform_search(message: Message, state: FSMContext):
    query = message.text.lower()
    # Simple keyword search across title, description, district
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT title, price, district, url, source, external_id
            FROM external_listings
            WHERE title LIKE ? OR description LIKE ? OR district LIKE ?
            LIMIT 10
        """, (f"%{query}%", f"%{query}%", f"%{query}%")) as cursor:
            rows = await cursor.fetchall()
    if not rows:
        await message.answer("По вашему запросу ничего не найдено. Попробуйте другие ключевые слова.")
    else:
        for row in rows:
            title, price, district, url, source, ext_id = row
            await message.answer(
                f"🏠 *{title}*\n💰 {price:,} ₽\n📍 {district}\n🔗 [Смотреть на {source}]({url})",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text="📊 Экспертная оценка", callback_data=f"expert_{ext_id}")
                    ]]
                )
            )
    await state.clear()

# Optional: expert analysis callback (using YandexGPT)
@router.callback_query(F.data.startswith("expert_"))
async def expert_analysis(callback: CallbackQuery):
    ext_id = callback.data.split("_")[1]
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT title, description, price, district FROM external_listings WHERE external_id = ?", (ext_id,)) as cursor:
            listing = await cursor.fetchone()
    if not listing:
        await callback.answer("Объявление не найдено", show_alert=True)
        return
    title, desc, price, district = listing
    # Call YandexGPT to generate expert analysis
    from services.ai_client import generate_ai_response
    prompt = f"Дай краткую экспертную оценку (плюсы/минусы, цена за м², ликвидность) для квартиры:\nНазвание: {title}\nОписание: {desc}\nЦена: {price}\nРайон: {district}"
    analysis = await generate_ai_response(prompt, lang="ru")
    await callback.message.answer(f"📊 *Экспертная оценка Riel:*\n{analysis}", parse_mode="Markdown")
    await callback.answer()