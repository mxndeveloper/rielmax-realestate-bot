import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from services.mortgage_calc import calculate_monthly_payment
import aiosqlite

router = Router()

ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

@router.callback_query(F.data == "sponsored_showcase")
async def sponsored_showcase(callback: CallbackQuery, _: dict):
    await callback.message.answer(_["sponsored_text"])
    await callback.answer()

@router.callback_query(F.data == "mortgage")
async def mortgage_menu(callback: CallbackQuery, _: dict):
    await callback.message.answer(_["mortgage_prompt"], parse_mode="Markdown")
    await callback.answer()

@router.message(F.text.regexp(r"^\d+\s+\d+$"))
async def calculate_mortgage(message: Message, _: dict):
    parts = message.text.split()
    price = float(parts[0])
    down = float(parts[1])
    monthly = calculate_monthly_payment(price, down, annual_rate=21.0, years=30)
    await message.answer(
        _["mortgage_result"].format(price=price, down=down, monthly=monthly),
        parse_mode="Markdown"
    )

@router.message(Command("stats"))
async def admin_stats(message: Message, _: dict):
    if message.from_user.id != ADMIN_ID:
        return
    async with aiosqlite.connect("riel_bot.db") as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            user_count = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM listings") as cur:
            listing_count = (await cur.fetchone())[0]
    await message.answer(
        _["stats_header"].format(users=user_count, listings=listing_count)
    )