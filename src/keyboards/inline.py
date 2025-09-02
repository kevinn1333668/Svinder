from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_action_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
                InlineKeyboardButton(text="♥️", callback_data="like"),
                InlineKeyboardButton(text="👎", callback_data="next"),
                InlineKeyboardButton(text="🚪", callback_data="main_menu"),
        ],
        [InlineKeyboardButton(text="Пожаловаться", callback_data="complain")],
        [InlineKeyboardButton(text="В черный список 🏴", callback_data=f"blacklist")]]
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
                InlineKeyboardButton(text="Лайкнуть ❤️", callback_data=f"accept_pending_like:{liker_tg_id}"),
                InlineKeyboardButton(text="Отклонить 👎", callback_data=f"reject_pending_like:{liker_tg_id}"),
            ],
            [
                InlineKeyboardButton(text="В черный список 🏴", callback_data=f"Black_list:{liker_tg_id}"),
                InlineKeyboardButton(text="➡️ Следующий", callback_data="next_pending_like"), # Если их много
            ],
            [
                InlineKeyboardButton(text="Меню лайков ☰", callback_data="back_to_view_likes_menu"),
            ]
        ]
    )

def short_pending_like_action_keyboard(liker_tg_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Лайкнуть ❤️", callback_data=f"accept_pending_like:{liker_tg_id}"),
                InlineKeyboardButton(text="Отклонить 👎", callback_data=f"reject_pending_like:{liker_tg_id}"),
            ],
            [
                InlineKeyboardButton(text="В черный список 🏴", callback_data=f"Black_list:{liker_tg_id}"),
            ],
            [
                InlineKeyboardButton(text="Отложить", callback_data="hide_profile"),
            ]
        ]
    )

def confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Неприемлимая анкета", callback_data="complain_all")],
            [InlineKeyboardButton(text="Фотография", callback_data="complain_photo")],
            [InlineKeyboardButton(text="Описание", callback_data="complain_about")],
            [InlineKeyboardButton(text="Выдача себя за другого человека", callback_data="complain_imposter")],
            [InlineKeyboardButton(text="Другое", callback_data="complain_other")],
            [InlineKeyboardButton(text="Назад", callback_data="complain_cancel")]
        ]
    )

def get_confirmation_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="confirm_delete_profile"),
            InlineKeyboardButton(text="Нет", callback_data="cancel_delete_profile")
        ]
    ])

def moderation_keyboard(reported_tg_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{reported_tg_id}"),
            InlineKeyboardButton(text="❌ Забанить", callback_data=f"ban_{reported_tg_id}")]
        ]
    )

def show_profile_keyboard(liker_tg_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Посмотреть профиль ❤️', callback_data=f'show_profile:{liker_tg_id}')]    
        ]
    )