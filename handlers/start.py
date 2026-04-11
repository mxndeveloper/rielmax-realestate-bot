from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from database import UserDB
from keyboards import get_role_keyboard, get_main_menu, get_language_keyboard
import logging
import json
from dotenv import load_dotenv

load_dotenv()

router = Router()

WELCOME_IMAGE_PATH = "welcome.jpg"
SUPPORTED_LANGUAGES = ["ru", "en", "tr", "kk", "hy", "ka", "zh"]  # added all

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    # Get or auto-detect language
    lang = await UserDB.get_language(user_id)
    if not lang or lang not in SUPPORTED_LANGUAGES:
        detected = message.from_user.language_code or "ru"
        lang = detected if detected in SUPPORTED_LANGUAGES else "ru"
        await UserDB.set_language(user_id, lang)
    
    # Load translations
    try:
        with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
            t = json.load(f)
    except FileNotFoundError:
        logging.error(f"Locale file locales/{lang}.json not found")
        t = {"greeting": "Welcome! Please select your role."}

    # Send welcome photo
    try:
        photo = FSInputFile(WELCOME_IMAGE_PATH)
        await message.answer_photo(
            photo=photo,
            caption=f"{t.get('welcome_title', '')}\n{t.get('welcome_subtitle', '')}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.warning(f"Welcome photo error: {e}")
        await message.answer(t.get('welcome_title', '✨ Welcome to RielAI ✨'))

    # Show role selection
    await message.answer(
        t.get('greeting', 'Привет! 👋 Выберите роль, чтобы начать:'),
        reply_markup=get_role_keyboard()
    )

@router.callback_query(F.data == "change_language")
async def change_language_prompt(callback: CallbackQuery):
    await callback.message.answer(
        "🌐 **Выберите язык / Choose language**\n"
        "🇷🇺 Русский • 🇬🇧 English • 🇹🇷 Türkçe • 🇰🇿 Қазақша • 🇦🇲 Հայերեն • 🇬🇪 ქართული • 🇨🇳 中文",
        reply_markup=get_language_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.in_(["role_realtor", "role_client"]))
async def set_role(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await UserDB.get_language(user_id) or "ru"
    
    try:
        with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
            t = json.load(f)
    except Exception:
        t = {}

    role_key = "role_realtor" if callback.data == "role_realtor" else "role_client"
    role_name = t.get(role_key, "Риелтор" if callback.data == "role_realtor" else "Клиент")

    await UserDB.set_role(user_id, role_name)

    await callback.message.answer(
        t.get(f"role_selected_{'realtor' if callback.data == 'role_realtor' else 'client'}", 
              f"Отлично! Вы выбрали роль: {role_name}"),
        reply_markup=get_main_menu(is_premium=False)
    )
    await callback.answer()

@router.message(Command("getid"))
async def get_id(message: Message):
    await message.answer(f"Your Telegram ID: `{message.from_user.id}`", parse_mode="Markdown")