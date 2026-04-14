import pytest
from unittest.mock import AsyncMock, patch, mock_open
from middlewares.i18n import I18nMiddleware
from middlewares.throttling import ThrottlingMiddleware
from aiogram.types import Update, Message, User, Chat

@pytest.mark.asyncio
async def test_i18n_middleware():
    # Create a fake update with a message
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=123,
            chat=Chat(id=456, type="private"),
            from_user=User(id=789, is_bot=False, first_name="Test")
        )
    )
    with patch('database.UserDB.get_language', AsyncMock(return_value="en")):
        with patch('builtins.open', mock_open(read_data='{"key": "value"}')):
            middleware = I18nMiddleware()
            handler = AsyncMock()
            data = {}
            await middleware(handler, update, data)

@pytest.mark.asyncio
async def test_throttling_middleware():
    middleware = ThrottlingMiddleware(rate_limit=0.1)
    handler = AsyncMock()
    event = AsyncMock()
    event.from_user.id = 123
    data = {}
    # First call passes
    await middleware(handler, event, data)
    assert handler.called
    handler.reset_mock()
    # Second call within rate limit should be blocked
    await middleware(handler, event, data)
    assert not handler.called
    event.answer.assert_called()