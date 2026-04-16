from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_role_keyboard(translations: dict) -> InlineKeyboardMarkup:
    """Role selection keyboard with texts from current language."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=translations["role_realtor"], callback_data="role_realtor")],
        [InlineKeyboardButton(text=translations["role_client"], callback_data="role_client")],
        [InlineKeyboardButton(text=translations["change_language"], callback_data="change_language")],
    ])

def get_main_menu(translations: dict, is_premium: bool = False) -> InlineKeyboardMarkup:
    """Main menu with texts from current language."""
    buttons = [
        [InlineKeyboardButton(text=translations["create_listing"], callback_data="create_listing")],
    ]
    if is_premium:
        buttons.append([InlineKeyboardButton(text=translations["boost_premium"], callback_data="boost_listing")])
    else:
        buttons.append([InlineKeyboardButton(text=translations["boost_teaser"], callback_data="boost_listing")])

    buttons.extend([
        [InlineKeyboardButton(text=translations["search_listings"], callback_data="search_listings")],
        [InlineKeyboardButton(text=translations["mortgage"], callback_data="mortgage")],
        [InlineKeyboardButton(text=translations["sponsored_showcase"], callback_data="sponsored_showcase")],
        [InlineKeyboardButton(text=translations["change_language"], callback_data="change_language")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard – no translations needed (flags + language names)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr"),
         InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kk")],
        [InlineKeyboardButton(text="🇦🇲 Հայերեն", callback_data="lang_hy"),
         InlineKeyboardButton(text="🇬🇪 ქართული", callback_data="lang_ka")],
        [InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh")],
    ])