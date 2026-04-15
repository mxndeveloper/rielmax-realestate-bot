from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database import ListingDB
import csv
import io
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env early in this file too

router = Router()

# Put your real Telegram ID here (you can add multiple admins)
ADMIN_IDS = [int(os.getenv("ADMIN_TELEGRAM_ID", "0"))]   # ← Correct way

@router.message(Command("import_listings"))
async def import_listings(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("Доступ запрещён.")

    await message.answer("Отправьте мне файл listings.csv")

@router.message(F.document)
async def handle_csv_upload(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not message.document.file_name.endswith('.csv'):
        return await message.answer("Пожалуйста, отправьте CSV файл.")

    file = await message.bot.download(message.document)
    content = file.read().decode('utf-8')

    reader = csv.DictReader(io.StringIO(content))
    added = 0

    for row in reader:
        await ListingDB.add_listing(
            user_id=0,   # system added
            title=row.get('title', ''),
            description=row.get('description', ''),
            price=int(row.get('price', 0)),
            district=row.get('district', ''),
            address=row.get('address', '')
        )
        added += 1

    await message.answer(f"✅ Успешно добавлено {added} объявлений из CSV.")