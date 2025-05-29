from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.static.text.texts import (
    text_search_profiles, text_edit_profile,
    text_show_invite_code, text_go_to_deepseek,
    text_yes, text_no, text_male, text_female, text_my_likes
)


def welcome_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать")]
        ],
        resize_keyboard=True,
    )


def understand_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Понял!")]
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
            [KeyboardButton(text=text_male)],
            [KeyboardButton(text=text_female)],
        ],
        resize_keyboard=True,
    )


def sex_selection_horizontal_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[
                KeyboardButton(text=text_male),
                KeyboardButton(text=text_female)
        ]],
        resize_keyboard=True,
    )


def yes_or_no_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[
                KeyboardButton(text=text_yes),
                KeyboardButton(text=text_no)
        ]],
        resize_keyboard=True,
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text_search_profiles)],
            [KeyboardButton(text=text_edit_profile)],
            [KeyboardButton(text=text_show_invite_code)],
            [KeyboardButton(text=text_my_likes), KeyboardButton(text=text_go_to_deepseek)],
        ],
        resize_keyboard=True,
    )
