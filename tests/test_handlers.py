"""
RielAI SuperBot - Basic Tests
Run with: pytest tests/ -v
"""

import pytest
from aiogram.types import InlineKeyboardMarkup
from unittest.mock import AsyncMock, patch, MagicMock

# Import your modules
from keyboards import get_role_keyboard, get_main_menu, get_language_keyboard
from handlers import start, language


def test_keyboards_return_correct_type():
    """All keyboard functions must return InlineKeyboardMarkup"""
    assert isinstance(get_role_keyboard(), InlineKeyboardMarkup)
    assert isinstance(get_main_menu(), InlineKeyboardMarkup)
    assert isinstance(get_language_keyboard(), InlineKeyboardMarkup)
    print("✅ Keyboards: All functions return correct type")


def test_start_handler_has_router():
    """start handler should expose a router"""
    assert hasattr(start, "router")
    assert hasattr(start, "cmd_start")
    print("✅ start.py: Router and cmd_start exist")


def test_language_handler_has_router():
    """language handler should expose a router"""
    assert hasattr(language, "router")
    print("✅ language.py: Router exists")


def test_main_menu_contains_monetization():
    """Main menu must include Boost button (business model)"""
    keyboard = get_main_menu(is_premium=False)
    button_texts = [btn.text for row in keyboard.inline_keyboard for btn in row]
    assert any("Boost" in text for text in button_texts)
    print("✅ Main menu contains Boost button")


@pytest.mark.asyncio
async def test_start_command_runs_without_crash():
    """Test that /start handler executes without raising exceptions"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 123456789
    message.from_user.language_code = "ru"
    message.answer = AsyncMock()
    message.answer_photo = AsyncMock()

    # Mock database and file operations
    with patch("handlers.start.UserDB.get_language", return_value="ru"), \
         patch("handlers.start.UserDB.set_language", return_value=None), \
         patch("handlers.start.UserDB.get_role", return_value=None), \
         patch("builtins.open") as mock_open:

        # Make open return a proper file-like object with json content
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = '{"greeting": "Test greeting"}'
        mock_open.return_value = mock_file

        await start.cmd_start(message)

        # At least one response should be sent
        assert message.answer.called or message.answer_photo.called
        print("✅ /start handler executed successfully")


if __name__ == "__main__":
    pytest.main(["-v", __file__])