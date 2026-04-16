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
SUPPORTED_LANGUAGES = ["ru", "en", "tr", "kk", "hy", "ka", "zh"]

@router.message(Command("start"))
async def cmd_start(message: Message, _: dict):
    user_id = message.from_user.id
    
    # Get or auto-detect language
    lang = await UserDB.get_language(user_id)
    if not lang or lang not in SUPPORTED_LANGUAGES:
        detected = message.from_user.language_code or "ru"
        lang = detected if detected in SUPPORTED_LANGUAGES else "ru"
        await UserDB.set_language(user_id, lang)
        # Reload translations for this response (since middleware ran with old language)
        try:
            with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
                translations = json.load(f)
        except FileNotFoundError:
            translations = {"greeting": "Welcome! Please select your role."}
    else:
        translations = _  # use already injected translations

    # Send welcome photo
    try:
        photo = FSInputFile(WELCOME_IMAGE_PATH)
        await message.answer_photo(
            photo=photo,
            caption=f"{translations.get('welcome_title', '')}\n{translations.get('welcome_subtitle', '')}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.warning(f"Welcome photo error: {e}")
        await message.answer(translations.get('welcome_title', '✨ Welcome to RielAI ✨'))

    # Show role selection using the correct translations
    await message.answer(
        translations["greeting"],
        reply_markup=get_role_keyboard(translations)
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
async def set_role(callback: CallbackQuery, _: dict):
    user_id = callback.from_user.id
    role_key = "role_realtor" if callback.data == "role_realtor" else "role_client"
    role_name = _[role_key]  # get translated role name from injected dict
    
    await UserDB.set_role(user_id, role_name)
    
    await callback.message.answer(
        _["role_selected"].format(role=role_name),
        reply_markup=get_main_menu(_, is_premium=False)
    )
    await callback.answer()

@router.message(Command("getid"))
async def get_id(message: Message):
    await message.answer(f"Your Telegram ID: `{message.from_user.id}`", parse_mode="Markdown")