from aiogram import Router, F
from aiogram.types import Message
from database import UserDB
from services.ai_client import generate_ai_response

router = Router()

@router.message(F.text)
async def handle_chat(message: Message, _: dict):
    if message.text.startswith("/"):
        return

    role = await UserDB.get_role(message.from_user.id)
    if not role:
        await message.answer(_["no_role"])
        return

    user_lang = await UserDB.get_language(message.from_user.id) or "ru"

    user_text = message.text
    prompt = f"Пользователь ({role}): {user_text}"

    await message.bot.send_chat_action(message.chat.id, "typing")
    response = await generate_ai_response(prompt, lang=user_lang)
    await message.answer(response)