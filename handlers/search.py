from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite
from database import DB_PATH, UserDB

router = Router()

class SearchStates(StatesGroup):
    waiting_for_query = State()

@router.callback_query(F.data == "search_listings")
async def start_search(callback: CallbackQuery, state: FSMContext, _: dict):
    await callback.message.answer(
        _["search_prompt"],
        parse_mode="Markdown"
    )
    await state.set_state(SearchStates.waiting_for_query)
    await callback.answer()

@router.message(SearchStates.waiting_for_query)
async def perform_search(message: Message, state: FSMContext, _: dict):
    query = message.text.lower()
    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("""
                SELECT title, price, district, url, source, external_id
                FROM external_listings
                WHERE title LIKE ? OR description LIKE ? OR district LIKE ?
                LIMIT 10
            """, (f"%{query}%", f"%{query}%", f"%{query}%")) as cursor:
                rows = await cursor.fetchall()
    except Exception as e:
        await message.answer(_["no_results"])
        await state.clear()
        return

    if not rows:
        await message.answer(_["no_results"])
    else:
        for row in rows:
            title, price, district, url, source, ext_id = row
            await message.answer(
                f"🏠 *{title}*\n💰 {price:,} ₽\n📍 {district}\n🔗 [Смотреть на {source}]({url})",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text=_["expert_analysis"], callback_data=f"expert_{ext_id}")
                    ]]
                )
            )
    await state.clear()

@router.callback_query(F.data.startswith("expert_"))
async def expert_analysis(callback: CallbackQuery, _: dict):
    ext_id = callback.data.split("_")[1]
    user_lang = await UserDB.get_language(callback.from_user.id) or "ru"
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT title, description, price, district FROM external_listings WHERE external_id = ?",
                (ext_id,)
            ) as cursor:
                listing = await cursor.fetchone()
    except Exception as e:
        await callback.answer(_["listing_not_found"], show_alert=True)
        return

    if not listing:
        await callback.answer(_["listing_not_found"], show_alert=True)
        return

    title, desc, price, district = listing
    # Show typing indicator before calling AI
    await callback.bot.send_chat_action(callback.message.chat.id, "typing")
    from services.ai_client import generate_ai_response
    prompt = f"Дай краткую экспертную оценку (плюсы/минусы, цена за м², ликвидность) для квартиры:\nНазвание: {title}\nОписание: {desc}\nЦена: {price}\nРайон: {district}"
    analysis = await generate_ai_response(prompt, lang=user_lang)
    await callback.message.answer(
        f"📊 *{_['expert_analysis_title']}*\n{analysis}",
        parse_mode="Markdown"
    )
    await callback.answer()