import pytest
from unittest.mock import patch, AsyncMock, mock_open
from handlers.start import cmd_start, set_role
from handlers.language import set_language
from handlers.chat import handle_chat
from database import UserDB

@pytest.fixture
def translations():
    return {
        "no_role": "Please /start",
        "role_selected_realtor": "You are a realtor",
        "role_selected_client": "You are a client",
        "role_realtor": "Realtor",
        "role_client": "Client",
        "greeting": "Welcome",
        "stats_header": "Stats: {users} users, {listings} listings",
        "welcome_title": "Welcome",
        "welcome_subtitle": "Subtitle",
        "change_language": "Change language",
        "role_selected": "You selected role: {role}",
        "create_listing": "Create listing",
        "search_listings": "Search properties",
        "mortgage": "Mortgage",
        "sponsored_showcase": "Sponsored new builds",
        "boost_teaser": "Boost listing • 490 Stars",
        "boost_premium": "Boost listing",
        "sponsored_text": "Sponsored text",
        "mortgage_prompt": "Send price and down payment",
        "mortgage_result": "Monthly payment: {monthly}"
    }

@pytest.mark.asyncio
async def test_start_command(db, mock_message, translations):
    mock_message.text = "/start"
    with patch.object(UserDB, 'get_language', AsyncMock(return_value='ru')):
        await cmd_start(mock_message, translations)
    mock_message.answer_photo.assert_called_once()

@pytest.mark.asyncio
async def test_set_role(db, mock_callback, translations):
    mock_callback.data = "role_realtor"
    with patch.object(UserDB, 'set_role', AsyncMock()) as mock_set:
        await set_role(mock_callback, translations)
        mock_set.assert_called_once_with(123, translations["role_realtor"])
        mock_callback.message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_set_language(db, mock_callback):
    mock_callback.data = "lang_en"
    # Provide a mock translation dict that includes all keys get_role_keyboard expects
    mock_translations = {
        "greeting": "Hello",
        "role_realtor": "Realtor",
        "role_client": "Client",
        "change_language": "Change language",
        "role_selected_realtor": "You are a realtor",
        "role_selected_client": "You are a client"
    }
    with patch.object(UserDB, 'set_language', AsyncMock()):
        with patch('builtins.open', mock_open(read_data='{"greeting": "Hello"}')):
            with patch('json.load', return_value=mock_translations):
                await set_language(mock_callback)
    mock_callback.message.answer.assert_called()

@pytest.mark.asyncio
async def test_handle_chat_no_role(db, mock_message, translations):
    mock_message.text = "Hello"
    with patch.object(UserDB, 'get_role', AsyncMock(return_value=None)):
        await handle_chat(mock_message, translations)
    mock_message.answer.assert_called_with(translations["no_role"])

@pytest.mark.asyncio
async def test_handle_chat_with_role(db, mock_message, translations):
    mock_message.text = "Hello"
    with patch.object(UserDB, 'get_role', AsyncMock(return_value="Риелтор")):
        with patch.object(UserDB, 'get_language', AsyncMock(return_value="en")):
            with patch('handlers.chat.generate_ai_response', AsyncMock(return_value="AI reply")):
                await handle_chat(mock_message, translations)
    mock_message.answer.assert_called_with("AI reply")