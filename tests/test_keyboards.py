import pytest
from keyboards import get_role_keyboard, get_main_menu, get_language_keyboard

def test_role_keyboard():
    mock_translations = {
        "role_realtor": "Realtor",
        "role_client": "Client",
        "change_language": "Change language"
    }
    kb = get_role_keyboard(mock_translations)
    buttons = kb.inline_keyboard
    assert len(buttons) == 3
    assert buttons[0][0].callback_data == "role_realtor"

def test_main_menu():
    mock_translations = {
        "create_listing": "Create listing",
        "boost_teaser": "Boost listing • 490 Stars",
        "boost_premium": "Boost listing",
        "search_listings": "Search",
        "mortgage": "Mortgage",
        "sponsored_showcase": "Sponsored",
        "change_language": "Change language"
    }
    kb = get_main_menu(mock_translations, is_premium=False)
    # Check that Boost button shows teaser
    boost_button = kb.inline_keyboard[1][0]
    assert "490 Stars" in boost_button.text

def test_language_keyboard():
    kb = get_language_keyboard()
    assert len(kb.inline_keyboard) == 4