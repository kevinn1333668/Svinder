from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def welcome_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать", callback_data="start_quest")]
        ],
        resize_keyboard=True,
    )


def go_to_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Перейти в главное меню", callback_data="start_quest")]
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
            [KeyboardButton(text="Парень", callback_data="gender_male")],
            [KeyboardButton(text="Девушка", callback_data="gender_female")],
        ],
        resize_keyboard=True,
    )


def sex_selection_horizontal_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[
                KeyboardButton(text="Парень", callback_data="gender_male"),
                KeyboardButton(text="Девушка", callback_data="gender_female")
        ]],
        resize_keyboard=True,
    )
