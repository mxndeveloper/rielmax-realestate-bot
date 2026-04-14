from keyboards import get_role_keyboard, get_main_menu, get_language_keyboard

def test_role_keyboard():
    kb = get_role_keyboard()
    buttons = kb.inline_keyboard
    assert len(buttons) == 3  # Realtor, Client, Change language
    assert buttons[0][0].callback_data == "role_realtor"

def test_main_menu():
    kb = get_main_menu(is_premium=False)
    # Check that Boost button shows price
    boost_button = kb.inline_keyboard[1][0]
    assert "490 Stars" in boost_button.text

def test_language_keyboard():
    kb = get_language_keyboard()
    # Should have 4 rows (ru/en, tr/kk, hy/ka, zh)
    assert len(kb.inline_keyboard) == 4
    assert kb.inline_keyboard[0][0].callback_data == "lang_ru"