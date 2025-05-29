import asyncio
from typing import List, Optional

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from src.service.db_service import ServiceDB
from src.keyboards.reply import main_menu_keyboard
from src.keyboards.inline import view_likes_menu_keyboard, pending_like_action_keyboard
from src.states import ViewLikesStates, UserRoadmap
from src.service.schemas import ProfileSchema, LikeSchema


async def get_telegram_username_or_name(bot: Bot, user_tg_id: int) -> str:
    try:
        chat = await bot.get_chat(user_tg_id)
        if chat.username:
            return f"@{chat.username}"
        else:
            name_parts = [chat.first_name, chat.last_name]
            full_name = " ".join(filter(None, name_parts))
            return full_name if full_name else f"User ID: {user_tg_id}"
    except Exception:
        return f"User ID: {user_tg_id}"


likes_router = Router()

@likes_router.message(F.text == "Мои лайки ❤️")
async def my_likes_menu_entry(message: Message, state: FSMContext):
    await state.set_state(ViewLikesStates.choose_view_type)

    await message.answer(
        "Переходим в меню лайков...",
        reply_markup=ReplyKeyboardRemove() 
    )
    
    await message.answer(
        "Здесь ты можешь посмотреть, кто проявил к тебе симпатию или ответил на твою.",
        reply_markup=view_likes_menu_keyboard() 
    )

@likes_router.callback_query(ViewLikesStates.choose_view_type, F.data == "view_who_liked_me")
async def process_view_who_liked_me(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    user_tg_id = callback_query.from_user.id

    pending_likes: List[LikeSchema] = await ServiceDB.get_pending_likes(liked_tgid=user_tg_id)

    if not pending_likes:
        await callback_query.message.answer("У тебя пока нет лайков.")
        await state.set_state(ViewLikesStates.choose_view_type)
        await callback_query.message.answer("Выберите опцию:", reply_markup=view_likes_menu_keyboard())
        return

    liker_ids = [like.liker_tgid for like in pending_likes]
    await state.update_data(pending_liker_ids=liker_ids, current_pending_index=0)
    await state.set_state(ViewLikesStates.viewing_pending_likes)
    
    await callback_query.message.edit_text("Загружаю анкеты тех, кто вас лайкнул...")
    await show_next_pending_like_profile(callback_query.message, state, bot)


async def show_next_pending_like_profile(target_message: Message, state: FSMContext, bot: Bot):
    user_tg_id = target_message.chat.id
    data = await state.get_data()
    pending_liker_ids: List[int] = data.get("pending_liker_ids", [])
    current_index: int = data.get("current_pending_index", 0)

    if not pending_liker_ids or current_index >= len(pending_liker_ids):
        await target_message.answer("Вы просмотрели все анкеты, которые вас лайкнули в этой сессии.", reply_markup=view_likes_menu_keyboard())
        await state.set_state(ViewLikesStates.choose_view_type)
        return

    liker_tg_id_to_show = pending_liker_ids[current_index]
    
    profile_data: Optional[ProfileSchema] = await ServiceDB.get_profile_by_tgid(liker_tg_id_to_show)

    if profile_data:
        try:
            profile_image = FSInputFile(str(profile_data.s3_path))
            telegram_user_info = await get_telegram_username_or_name(bot, liker_tg_id_to_show)
            
            await target_message.answer_photo(
                photo=profile_image,
                caption=(
                    f"Вам симпатизирует: {profile_data.name}, {profile_data.age} лет, {profile_data.uni}\n"
                    f"{profile_data.description}\n\n"
                    f"Telegram: {telegram_user_info}"
                ),
                reply_markup=pending_like_action_keyboard(liker_tg_id=liker_tg_id_to_show)
            )
            await state.update_data(currently_viewed_pending_liker_id=liker_tg_id_to_show)
        except FileNotFoundError:
            await target_message.answer(f"Не удалось загрузить фото для профиля {profile_data.name}. Пропускаем...")
            await state.update_data(current_pending_index=current_index + 1)
            await show_next_pending_like_profile(target_message, state, bot)
        except Exception as e:
            await target_message.answer(f"Произошла ошибка при показе профиля: {e}. Пропускаем...")
            print(f"Error sending pending like profile: {e}")
            await state.update_data(current_pending_index=current_index + 1)
            await show_next_pending_like_profile(target_message, state, bot)
    else:
        await target_message.answer(f"Не удалось найти профиль для пользователя с ID {liker_tg_id_to_show}. Пропускаем...")
        await state.update_data(current_pending_index=current_index + 1)
        await show_next_pending_like_profile(target_message, state, bot)


@likes_router.callback_query(ViewLikesStates.viewing_pending_likes, F.data.startswith("accept_pending_like:"))
async def process_accept_pending_like(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer("Лайк принят! ❤️")
    
    liker_tg_id_str = callback_query.data.split(":")[1]
    liker_tg_id = int(liker_tg_id_str)
    current_user_tg_id = callback_query.from_user.id

    await ServiceDB.accept_like(liker_tg_id, current_user_tg_id)

    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    current_index = data.get("current_pending_index", 0)
    await state.update_data(current_pending_index=current_index + 1)
    await show_next_pending_like_profile(callback_query.message, state, bot)


@likes_router.callback_query(ViewLikesStates.viewing_pending_likes, F.data.startswith("reject_pending_like:"))
async def process_reject_pending_like(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer("Лайк отклонен. 👎")
    
    liker_tg_id_str = callback_query.data.split(":")[1]
    liker_tg_id = int(liker_tg_id_str)
    current_user_tg_id = callback_query.from_user.id

    await ServiceDB.reject_like(liker_tg_id, current_user_tg_id)
    
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    current_index = data.get("current_pending_index", 0)
    await state.update_data(current_pending_index=current_index + 1)
    await show_next_pending_like_profile(callback_query.message, state, bot)


@likes_router.callback_query(ViewLikesStates.viewing_pending_likes, F.data == "next_pending_like")
async def process_next_pending_like_button(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    try:
        await callback_query.message.delete() 
    except TelegramBadRequest:
        pass
        
    data = await state.get_data()
    current_index = data.get("current_pending_index", 0)
    await state.update_data(current_pending_index=current_index + 1)
    await show_next_pending_like_profile(callback_query.message, state, bot)


@likes_router.callback_query(ViewLikesStates.choose_view_type, F.data == "view_my_mutual_likes")
async def process_view_my_mutual_likes(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    user_tg_id = callback_query.from_user.id

    accepted_likes_i_gave: List[LikeSchema] = await ServiceDB.get_accepted_likes(liker_tgid=user_tg_id)

    if not accepted_likes_i_gave:
        await callback_query.message.answer("У тебя пока нет взаимных лайков...", reply_markup=view_likes_menu_keyboard())
        await state.set_state(ViewLikesStates.choose_view_type)
        return

    await callback_query.message.edit_text("Ваши взаимные симпатии:")
    
    for like_info in accepted_likes_i_gave:
        mutual_profile_tg_id = like_info.liked_tgid 
        profile_data: Optional[ProfileSchema] = await ServiceDB.get_profile_by_tgid(mutual_profile_tg_id)

        if profile_data:
            try:
                profile_image = FSInputFile(str(profile_data.s3_path))
                telegram_user_info = await get_telegram_username_or_name(bot, mutual_profile_tg_id)
                
                await callback_query.message.answer_photo(
                    photo=profile_image,
                    caption=(
                        f"Взаимная симпатия с: {profile_data.name}, {profile_data.age}\n"
                        f"Университет: {profile_data.uni}\n"
                        f"О себе: {profile_data.description}\n\n"
                        f"Связь: {telegram_user_info}"
                    )
                )
            except FileNotFoundError:
                await callback_query.message.answer(f"Не удалось загрузить фото для профиля {profile_data.name} (ID: {mutual_profile_tg_id}). Telegram: {await get_telegram_username_or_name(bot, mutual_profile_tg_id)}")
            except Exception as e:
                await callback_query.message.answer(f"Произошла ошибка при показе профиля {profile_data.name} (ID: {mutual_profile_tg_id}). Telegram: {await get_telegram_username_or_name(bot, mutual_profile_tg_id)}. Ошибка: {e}")
                print(f"Error sending mutual like profile: {e}")
        else:
            await callback_query.message.answer(f"Не удалось найти профиль для пользователя с ID {mutual_profile_tg_id}. Telegram: {await get_telegram_username_or_name(bot, mutual_profile_tg_id)}")
        
        await asyncio.sleep(0.5)

    await callback_query.message.answer("🔼 Вот все твои взаимные лайки 🔼", reply_markup=view_likes_menu_keyboard())
    await state.set_state(ViewLikesStates.choose_view_type)


@likes_router.callback_query(F.data.in_({"likes_to_main_menu", "back_to_view_likes_menu"}))
async def process_back_buttons_likes(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    action = callback_query.data

    if action == "likes_to_main_menu":
        await state.clear()
        await callback_query.message.edit_text(
            "Возвращаемся в главное меню.",
            # reply_markup=main_menu_keyboard()
        )

        await callback_query.message.answer("Окей, возвращаю!", reply_markup=main_menu_keyboard())
        await state.set_state(UserRoadmap.main_menu)

    elif action == "back_to_view_likes_menu":
        await state.set_state(ViewLikesStates.choose_view_type)
        await callback_query.message.edit_text(
            "Меню лайков:",
            reply_markup=view_likes_menu_keyboard()
        )