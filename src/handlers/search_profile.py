from aiogram import Router, Bot, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery 
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from src.service.db_service import ServiceDB
from src.keyboards.reply import main_menu_keyboard
from src.keyboards.inline import profile_action_keyboard, confirm_keyboard, moderation_keyboard
from src.states import SearchProfileStates, UserRoadmap
from src.static.text.texts import text_search_profiles
from src.service.schemas import LikeSchema, ProfileSchema
from typing import List, Optional
from src.handlers.likes import get_telegram_username_or_name

from src.config import settings


search_router = Router()

# В БУДУЩЕМ:
# Нужно добавить сюда получение и отображение @username
# telegram_info = await get_telegram_username_or_name(bot, profile.tg_id)
# f"\nTelegram: {telegram_info}"


async def send_next_profile(target_message: Message, curr_user_tgid: int, state: FSMContext, bot: Bot):
    profile = await ServiceDB.search_profile(curr_user_tgid)

    if profile:
        try:
            file_id = profile.s3_path

            await state.update_data(current_viewing_tg_id=profile.tg_id, profile_image=file_id)

            await target_message.answer_photo(
                photo=file_id,
                caption=(
                    f"{profile.name}, {profile.age} лет, {profile.uni}\n"
                    f"{profile.description}"
                ),
                reply_markup=profile_action_keyboard()
            )
            
            await state.set_state(SearchProfileStates.viewing_profile)

        except FileNotFoundError:
             await target_message.answer(f"Ошибка: Файл фото не найден по пути {profile.s3_path}. Пробуем найти следующую анкету.")
             await send_next_profile(target_message, curr_user_tgid, state, bot) 
        except Exception as e:
             await target_message.answer(f"Произошла ошибка при показе фото: {e}. Пробуем найти следующую анкету.")
             print(f"Error sending photo: {e}")
             await send_next_profile(target_message, curr_user_tgid, state, bot)


    else:
        await target_message.answer(
            "Других профилей не найдено 😭",
            reply_markup=main_menu_keyboard()
        )
        await state.set_state(UserRoadmap.main_menu)


@search_router.message(F.text == text_search_profiles)
async def initiate_profile_search_handler(message: Message, state: FSMContext, bot: Bot): # Нужен bot: Bot
     await state.clear() 
     user_profile = await ServiceDB.get_profile_by_tgid(message.from_user.id)
     if user_profile is None:
         await message.answer("Чтобы начать поиск, сначала создайте анкету (/start).")
         return
     await message.answer("Начинаем поиск анкет...", reply_markup=ReplyKeyboardRemove())
     await send_next_profile(message, message.from_user.id, state, bot)


@search_router.callback_query(SearchProfileStates.viewing_profile, F.data.in_(["like", "next", "main_menu", "complain"]))
async def handle_profile_action(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()

    action = callback_query.data
    user_tg_id = callback_query.from_user.id
    state_data = await state.get_data()
    viewed_tg_id = state_data.get("current_viewing_tg_id")

    print(f"DEBUG: handle_profile_action вызван пользователем TG ID: {user_tg_id}")
    print(f"DEBUG: Из FSM состояния получен viewed_tg_id: {viewed_tg_id}")

    if not viewed_tg_id:
        await callback_query.message.answer("Ошибка состояния. Попробуйте начать поиск заново.")
        await state.clear()
        return

    print(f"User {user_tg_id} pressed '{action}' on profile TG ID {viewed_tg_id}")

    if action == "like":
        print(f"Лайк! {user_tg_id} -> {viewed_tg_id}")

        await ServiceDB.like_profile(user_tg_id, viewed_tg_id)
        await callback_query.message.answer("👍")

        pending_likes: List[LikeSchema] = await ServiceDB.get_pending_likes(liked_tgid=user_tg_id)
        liker_ids = [like.liker_tgid for like in pending_likes]

        if viewed_tg_id in liker_ids:
            await ServiceDB.accept_like(viewed_tg_id, user_tg_id)
            await ServiceDB.accept_like(user_tg_id, viewed_tg_id)
            profile_data_viewed: Optional[ProfileSchema] = await ServiceDB.get_profile_by_tgid(viewed_tg_id)
            profile_data_user: Optional[ProfileSchema] = await ServiceDB.get_profile_by_tgid(user_tg_id)

            if profile_data_viewed:
                try:
                    profile_viewed_image = profile_data_viewed.s3_path
                    profile_user_image = profile_data_user.s3_path

                    telegram_viewed_info = await get_telegram_username_or_name(bot, viewed_tg_id)
                    telegram_user_info = await get_telegram_username_or_name(bot, user_tg_id)
                    
                    await callback_query.message.answer_photo(
                        photo=profile_viewed_image,
                        caption=(
                            f"Взаимная симпатия с: {profile_data_viewed.name}, {profile_data_viewed.age}\n"
                            f"Город: {profile_data_viewed.uni}\n"
                            f"О себе: {profile_data_viewed.description}\n\n"
                            f"Связь: {telegram_viewed_info}"
                        )
                    )

                    await bot.send_photo(
                        chat_id=viewed_tg_id,
                        photo=profile_user_image,
                        caption=(
                            f"Взаимная симпатия с: {profile_data_user.name}, {profile_data_user.age}\n"
                            f"Город: {profile_data_user.uni}\n"
                            f"О себе: {profile_data_user.description}\n\n"
                            f"Связь: {telegram_user_info}"
                        )
                    )

                except FileNotFoundError:
                    await callback_query.message.answer(f"Не удалось загрузить фото для профиля {profile_data_viewed.name} (ID: {viewed_tg_id}). Telegram: {await get_telegram_username_or_name(bot, viewed_tg_id)}")
                except Exception as e:
                    await callback_query.message.answer(f"Произошла ошибка при показе профиля {profile_data_viewed.name} (ID: {viewed_tg_id}). Telegram: {await get_telegram_username_or_name(bot, viewed_tg_id)}. Ошибка: {e}")
                    print(f"Error sending mutual like profile: {e}")
            else:
                await callback_query.message.answer(f"Не удалось найти профиль для пользователя с ID {viewed_tg_id}. Telegram: {await get_telegram_username_or_name(bot, viewed_tg_id)}")
        await send_next_profile(callback_query.message, user_tg_id, state, bot)

    elif action == "next":
        print(f"Пропускаем профиль: {user_tg_id} -> {viewed_tg_id}")

        await ServiceDB.create_dislike(user_id=user_tg_id, target_id=viewed_tg_id)

        await send_next_profile(callback_query.message, user_tg_id, state, bot)

    elif action == 'complain':
        await state.update_data(
            previous_message_text=callback_query.message.caption,
            previous_keyboard=callback_query.message.reply_markup
        )

        try:
            await callback_query.message.edit_caption(
                caption="Вы уверены?",
                reply_markup=confirm_keyboard()
            )
            return

        except Exception as e:
            print(f"Ошибка при редактировании сообщения: {e}")
            await callback_query.message.answer("Произошла ошибка. Попробуйте еще раз.")

    elif action == "main_menu":
        await callback_query.message.answer(
            "Возвращаемся в главное меню.",
            reply_markup=main_menu_keyboard()
        )
        await state.set_state(UserRoadmap.main_menu)

    try:
         await callback_query.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest as e:
         print(f"Telegram API error editing/deleting message: {e}")
    except Exception as e:
         print(f"Не удалось убрать клавиатуру из сообщения: {e}")


@search_router.callback_query(F.data.in_(["complain_confirm", "complain_cancel"]))
async def handle_complain_confirmation(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()

    action = callback_query.data
    state_data = await state.get_data()
    viewed_tg_id = state_data.get("current_viewing_tg_id")
    profile_photo = state_data.get("profile_image")
    previous_message_text = state_data.get("previous_message_text", "")
    previous_keyboard = state_data.get("previous_keyboard", None)

    if action == "complain_confirm":
        user_tg_id = callback_query.from_user.id
        
        await ServiceDB.report_profile(user_id=user_tg_id, target_id=viewed_tg_id)

        await bot.send_photo(
            chat_id=settings.ADMIN_CHAT_ID,
            photo=profile_photo,
            caption=previous_message_text,
            reply_markup=moderation_keyboard(viewed_tg_id)
        )

        await callback_query.message.answer("👍")
        print(f"Пользователь {user_tg_id} пожаловался на {viewed_tg_id}")



        await send_next_profile(callback_query.message, user_tg_id, state, bot)

    elif action == "complain_cancel":
        try:
            await callback_query.message.edit_caption(
                caption=previous_message_text,
                reply_markup=previous_keyboard
            )
        except Exception as e:
            print(f"Ошибка при восстановлении сообщения: {e}")
            await callback_query.message.answer("Возврат к предыдущему профилю.")

        await state.update_data(
            previous_message_text=None,
            previous_keyboard=None
        )

