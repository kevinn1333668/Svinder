from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_action_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
                InlineKeyboardButton(text="♥️", callback_data="like"),
                InlineKeyboardButton(text="👎", callback_data="next"),
                InlineKeyboardButton(text="🚪", callback_data="main_menu")
        ],
        [InlineKeyboardButton(text="Пожаловаться", callback_data="complain")]]
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

def confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="complain_confirm")],
            [InlineKeyboardButton(text="Нет", callback_data="complain_cancel")]
        ]
    )

def moderation_keyboard(reported_tg_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{reported_tg_id}"),
            InlineKeyboardButton(text="❌ Забанить", callback_data=f"ban_{reported_tg_id}")]
        ]
    )