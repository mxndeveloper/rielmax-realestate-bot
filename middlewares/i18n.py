from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from database import UserDB
import json

class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Extract user_id from the update
        user_id = None
        if event.message and event.message.from_user:
            user_id = event.message.from_user.id
        elif event.callback_query and event.callback_query.from_user:
            user_id = event.callback_query.from_user.id
        elif event.inline_query and event.inline_query.from_user:
            user_id = event.inline_query.from_user.id
        elif event.chosen_inline_result and event.chosen_inline_result.from_user:
            user_id = event.chosen_inline_result.from_user.id
        elif event.chat_member and event.chat_member.from_user:
            user_id = event.chat_member.from_user.id
        elif event.my_chat_member and event.my_chat_member.from_user:
            user_id = event.my_chat_member.from_user.id
        else:
            # No user found – pass through without translations
            return await handler(event, data)

        # Load user's language from DB (default 'ru')
        lang = await UserDB.get_language(user_id)
        try:
            with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
                translations = json.load(f)
        except FileNotFoundError:
            # Fallback to Russian
            with open("locales/ru.json", "r", encoding="utf-8") as f:
                translations = json.load(f)

        # Inject translations into handler data
        data["_"] = translations
        return await handler(event, data)