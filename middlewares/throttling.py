from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Message
import time

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 2.0):
        self.rate_limit = rate_limit
        self.last_message: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        now = time.time()
        if user_id in self.last_message and now - self.last_message[user_id] < self.rate_limit:
            await event.answer("🐢 Не торопись, Riel ещё печатает... Подожди пару секунд.")
            return
        self.last_message[user_id] = now
        return await handler(event, data)