import os
import logging
import json
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from database import UserDB
from keyboards import get_role_keyboard, get_main_menu, get_language_keyboard
from dotenv import load_dotenv

load_dotenv()
router = Router()

WELCOME_MP4_PATH = "welcome.mp4"
WELCOME_IMAGE_PATH = "welcome.jpg"
SUPPORTED_LANGUAGES = ["ru", "en", "tr", "kk", "hy", "ka", "zh"]

@router.message(Command("start"))
async def cmd_start(message: Message, _: dict):
    user_id = message.from_user.id
    lang = await UserDB.get_language(user_id)
    if not lang or lang not in SUPPORTED_LANGUAGES:
        detected = message.from_user.language_code or "ru"
        lang = detected if detected in SUPPORTED_LANGUAGES else "ru"
        await UserDB.set_language(user_id, lang)
        # Load fresh translations for this response (since middleware might have used default)
        try:
            with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
                translations = json.load(f)
        except FileNotFoundError:
            translations = {"greeting": "Welcome!", "welcome_title": "✨ Welcome", "welcome_subtitle": ""}
    else:
        translations = _

    # Send welcome media (video > photo > text)
    sent = False
    try:
        if os.path.exists(WELCOME_MP4_PATH):
            video = FSInputFile(WELCOME_MP4_PATH)
            await message.answer_video(
                video=video,
                caption=f"{translations.get('welcome_title', '')}\n{translations.get('welcome_subtitle', '')}",
                parse_mode="Markdown"
            )
            sent = True
        elif os.path.exists(WELCOME_IMAGE_PATH):
            photo = FSInputFile(WELCOME_IMAGE_PATH)
            await message.answer_photo(
                photo=photo,
                caption=f"{translations.get('welcome_title', '')}\n{translations.get('welcome_subtitle', '')}",
                parse_mode="Markdown"
            )
            sent = True
        else:
            await message.answer(translations.get('welcome_title', '✨ Welcome to RielAI ✨'))
            sent = True
    except Exception as e:
        logging.warning(f"Media send error: {e}")
        await message.answer(translations.get('welcome_title', '✨ Welcome to RielAI ✨'))

    # Show role selection
    await message.answer(
        translations["greeting"],
        reply_markup=get_role_keyboard(translations)
    )