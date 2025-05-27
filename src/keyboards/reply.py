from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.static.text.texts import text_search_profiles, text_edit_profile, text_show_invite_code, text_go_to_deepseek

def welcome_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать")]
        ],
        resize_keyboard=True,
    )


def go_to_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Перейти в главное меню")]
        ],
        resize_keyboard=True,
    )


def go_to_check_token() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сейчас будут документы")]
        ],
        resize_keyboard=True,
    )


def sex_selection_vertical_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Парень")],
            [KeyboardButton(text="Девушка")],
        ],
        resize_keyboard=True,
    )


def sex_selection_horizontal_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[
                KeyboardButton(text="Парень"),
                KeyboardButton(text="Девушка")
        ]],
        resize_keyboard=True,
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text_search_profiles)],
            [KeyboardButton(text=text_edit_profile)],
            [KeyboardButton(text=text_show_invite_code)],
            [KeyboardButton(text=text_go_to_deepseek)],
        ],
        resize_keyboard=True,
    )
