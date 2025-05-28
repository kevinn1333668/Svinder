from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_action_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
                InlineKeyboardButton(text="♥️", callback_data="like"),
                InlineKeyboardButton(text="👎", callback_data="next"),
                InlineKeyboardButton(text="💤", callback_data="main_menu")
        ]]
    )

# def sex_selection_vertical_keyboard() -> InlineKeyboardMarkup:
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="Парень", callback_data="gender_male")],
#             [InlineKeyboardButton(text="Девушка", callback_data="gender_female")],
#         ]
#     )
