from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from database import UserDB
from keyboards import get_language_keyboard, get_main_menu, get_role_keyboard
import json

router = Router()

@router.message(Command("language"))
async def change_language(message: Message):
    await message.answer(
        "🌐 **Выберите язык / Choose language**",
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await UserDB.set_language(user_id, lang)

    # Load translations
    try:
        with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
            t = json.load(f)
    except Exception:
        t = {"greeting": "Language changed."}

    # Try to edit original message (if it's a bot message)
    try:
        await callback.message.edit_text(
            f"✅ Language set to {lang.upper()}"
        )
    except Exception:
        await callback.message.answer(f"✅ Language set to {lang.upper()}")

    # Show appropriate menu after language change
    role = await UserDB.get_role(user_id)
    if role:
        greeting = t.get("role_selected_realtor" if role == "Риелтор" else "role_selected_client", t.get("greeting", ""))
        await callback.message.answer(greeting, reply_markup=get_main_menu(is_premium=False))
    else:
        await callback.message.answer(t.get("greeting", "Выберите роль:"), reply_markup=get_role_keyboard())

    await callback.answer()