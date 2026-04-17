import os
import logging
import json
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from database import UserDB
from keyboards import get_role_keyboard, get_main_menu
from dotenv import load_dotenv

load_dotenv()
router = Router()

WELCOME_VIDEO_PATH = "welcome.mp4"
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
        try:
            with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
                translations = json.load(f)
        except FileNotFoundError:
            translations = {"greeting": "Welcome!", "welcome_title": "✨ Welcome", "welcome_subtitle": ""}
    else:
        translations = _

    # Send welcome media (video > photo > text)
    try:
        if os.path.exists(WELCOME_VIDEO_PATH):
            video = FSInputFile(WELCOME_VIDEO_PATH)
            await message.answer_video(
                video=video,
                caption=f"{translations.get('welcome_title', '')}\n{translations.get('welcome_subtitle', '')}",
                parse_mode="Markdown"
            )
        elif os.path.exists(WELCOME_IMAGE_PATH):
            photo = FSInputFile(WELCOME_IMAGE_PATH)
            await message.answer_photo(
                photo=photo,
                caption=f"{translations.get('welcome_title', '')}\n{translations.get('welcome_subtitle', '')}",
                parse_mode="Markdown"
            )
        else:
            await message.answer(translations.get('welcome_title', '✨ Welcome to RielAI ✨'))
    except Exception as e:
        logging.warning(f"Media send error: {e}")
        await message.answer(translations.get('welcome_title', '✨ Welcome to RielAI ✨'))

    # Role selection
    await message.answer(
        translations["greeting"],
        reply_markup=get_role_keyboard(translations)
    )

@router.callback_query(F.data.in_(["role_realtor", "role_client"]))
async def set_role(callback: CallbackQuery, _: dict):
    await callback.answer()  # ✅ IMMEDIATE
    user_id = callback.from_user.id
    role_key = "role_realtor" if callback.data == "role_realtor" else "role_client"
    role_name = _[role_key]
    await UserDB.set_role(user_id, role_name)
    await callback.message.answer(
        _["role_selected"].format(role=role_name),
        reply_markup=get_main_menu(_, is_premium=False)
    )