from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import ListingDB, UserDB
from services.parser import search_external_listings
from keyboards import get_main_menu

router = Router()


class SearchStates(StatesGroup):
    waiting_for_query = State()


@router.message(Command("search"))
@router.callback_query(F.data == "search_listings")
async def cmd_search(message_or_callback, state: FSMContext):
    if isinstance(message_or_callback, Message):
        message = message_or_callback
    else:
        message = message_or_callback.message
        await message_or_callback.answer()

    await message.answer(
        "🔍 **Поиск недвижимости**\n\n"
        "Опишите, что вы ищете (район, бюджет, комнаты и т.д.):\n"
        "Примеры:\n"
        "• 2-комнатная квартира в центре до 15 млн\n"
        "• студия Хамовники\n"
        "• однокомнатная у метро"
    )
    await state.set_state(SearchStates.waiting_for_query)


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    query = message.text.strip()
    user_id = message.from_user.id

    await message.answer("🔄 Riel ищет лучшие варианты для вас...")

    try:
        # Get our own listings
        our_listings = await ListingDB.get_all_listings()

        # Get external listings
        external = await search_external_listings(query, limit=12)

        # Combine and prioritize sponsored (in future we will mark some as sponsored)
        all_results = our_listings + external

        if not all_results:
            await message.answer("😔 К сожалению, по вашему запросу ничего не найдено.")
            await state.clear()
            return

        # Show results with sponsored priority simulation
        shown = 0
        for item in all_results[:6]:
            is_sponsored = item.get("is_sponsored", False) or random.random() < 0.2  # 20% chance for demo

            price_str = f"{item.get('price', 0):,}" if item.get('price') else "—"
            district = item.get('district', item.get('address', '—'))
            title = item.get('title', 'Объявление')

            emoji = "⭐ " if is_sponsored else "🏠 "
            text = (
                f"{emoji}**{title}**\n"
                f"💰 {price_str} ₽\n"
                f"📍 {district}\n"
                f"📝 {item.get('description', '')[:110]}..."
            )

            if is_sponsored:
                text = "🔥 **СПОНСОРСКОЕ** 🔥\n" + text

            await message.answer(text)
            shown += 1

        await message.answer(
            f"✅ Показано {shown} лучших вариантов.\n\n"
            "Хотите установить цену-уведомление или **Boost** своё объявление для топа?",
            reply_markup=get_main_menu(is_premium=False)
        )

    except Exception as e:
        await message.answer("⚠️ Ошибка поиска. Попробуйте позже.")
        print(f"Search error: {e}")

    await state.clear()