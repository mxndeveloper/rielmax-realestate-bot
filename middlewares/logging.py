import logging
import time
from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Logs all incoming updates and their processing time."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Extract user and chat info for context
        user_id = None
        chat_id = None
        update_type = "unknown"

        if event.message:
            user_id = event.message.from_user.id
            chat_id = event.message.chat.id
            update_type = "message"
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            chat_id = event.callback_query.message.chat.id if event.callback_query.message else None
            update_type = "callback_query"
        elif event.inline_query:
            user_id = event.inline_query.from_user.id
            update_type = "inline_query"
        elif event.chat_member:
            user_id = event.chat_member.from_user.id
            update_type = "chat_member"
        elif event.my_chat_member:
            user_id = event.my_chat_member.from_user.id
            update_type = "my_chat_member"

        # Log the incoming update
        logger.info(
            f"📥 Update {update_type} | user={user_id} | chat={chat_id}"
        )

        start_time = time.time()
        try:
            result = await handler(event, data)
            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(
                f"✅ Update processed in {elapsed_ms:.1f}ms | user={user_id}"
            )
            return result
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"❌ Update failed after {elapsed_ms:.1f}ms | user={user_id} | error={type(e).__name__}: {e}",
                exc_info=True
            )
            # Re-raise the exception so other middlewares/handlers can handle it
            raise