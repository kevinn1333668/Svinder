from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.static.text.texts import (
    text_search_profiles, text_edit_profile,
    text_my_profile,
    text_yes, text_no, text_male, text_female, text_my_likes, text_delete_profile, text_filter_sex,
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
        ]],
        resize_keyboard=True,
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text_search_profiles), KeyboardButton(text=text_edit_profile)],
            [KeyboardButton(text=text_my_likes), KeyboardButton(text=text_my_profile)],
            [KeyboardButton(text=text_filter_sex)],
            [KeyboardButton(text=text_delete_profile)],
        ],
        resize_keyboard=True,
    )
