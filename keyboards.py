from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_role_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💼 Риелтор / Realtor", callback_data="role_realtor")],
        [InlineKeyboardButton(text="🏠 Клиент / Client", callback_data="role_client")],
        [InlineKeyboardButton(text="🌐 Сменить язык / Change language", callback_data="change_language")],
    ])

def get_main_menu(is_premium: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="➕ Создать объявление", callback_data="create_listing")],
    ]
    if is_premium:
        buttons.append([InlineKeyboardButton(text="⭐ Boost объявление", callback_data="boost_listing")])
    else:
        buttons.append([InlineKeyboardButton(text="⭐ Boost объявление • 490 Stars", callback_data="boost_listing")])

    buttons.extend([
        [InlineKeyboardButton(text="🔍 Поиск объектов / Search", callback_data="search_listings")],
        [InlineKeyboardButton(text="🏦 Ипотечный калькулятор", callback_data="mortgage")],
        [InlineKeyboardButton(text="⭐ Спонсорские новостройки", callback_data="sponsored_showcase")],
        [InlineKeyboardButton(text="🌐 Сменить язык / Change language", callback_data="change_language")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kk")],
        [InlineKeyboardButton(text="🇦🇲 Հայերեն", callback_data="lang_hy"),
         InlineKeyboardButton(text="🇬🇪 ქართული", callback_data="lang_ka")],
        [InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh")],
    ])