from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_action_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
                InlineKeyboardButton(text="♥️", callback_data="like"),
                InlineKeyboardButton(text="👎", callback_data="next"),
                InlineKeyboardButton(text="💤", callback_data="main_menu")
        ]]
    )


def view_likes_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Кто меня лайкнул 👀", callback_data="view_who_liked_me"),
            ],
            [
                InlineKeyboardButton(text="Мои взаимные лайки ❤️", callback_data="view_my_mutual_likes"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="likes_to_main_menu"),
            ]
        ]
    )


def pending_like_action_keyboard(liker_tg_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Лайкнуть в ответ ❤️", callback_data=f"accept_pending_like:{liker_tg_id}"),
                InlineKeyboardButton(text="Отклонить 👎", callback_data=f"reject_pending_like:{liker_tg_id}"),
            ],
            [
                 InlineKeyboardButton(text="➡️ Следующий", callback_data="next_pending_like"), # Если их много
            ],
            [
                InlineKeyboardButton(text="Меню лайков ☰", callback_data="back_to_view_likes_menu"),
            ]
        ]
    )
