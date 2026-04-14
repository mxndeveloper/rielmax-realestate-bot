from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database import ListingDB
import csv
import io

router = Router()

ADMIN_IDS = [TELEGRAM_BOT_TOKEN]  # Add your ID here

@router.message(Command("add_listings"))
async def add_listings_csv(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("Отправьте CSV файл с объявлениями (title,description,price,district)")

@router.message(F.document)
async def handle_csv_upload(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    document = message.document
    if not document.file_name.endswith('.csv'):
        await message.answer("Пожалуйста, отправьте CSV файл.")
        return

    file = await message.bot.download(document)
    content = file.read().decode('utf-8')

    reader = csv.DictReader(io.StringIO(content))
    added = 0
    for row in reader:
        await ListingDB.add_listing(
            user_id=0,  # system
            title=row.get('title', ''),
            description=row.get('description', ''),
            price=int(row.get('price', 0)),
            district=row.get('district', '')
        )
        added += 1

    await message.answer(f"✅ Добавлено {added} объявлений.")