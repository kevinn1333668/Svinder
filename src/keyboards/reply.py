from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


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
            [KeyboardButton(text="Смотреть анкеты 🔎")],
            [KeyboardButton(text="Редактировать свою анкету 🪞")],
            [KeyboardButton(text="Инвайт-код для друга 💎")],
            [KeyboardButton(text="Мне никто не пишет. . .")],
        ],
        resize_keyboard=True,
    )
