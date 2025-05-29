from aiogram import Router, Bot, F
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile, CallbackQuery 
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from src.service.db_service import ServiceDB
from src.keyboards.reply import main_menu_keyboard
from src.keyboards.inline import profile_action_keyboard
from src.states import SearchProfileStates, UserRoadmap


search_router = Router()

# В БУДУЩЕМ:
# Нужно добавить сюда получение и отображение @username
# telegram_info = await get_telegram_username_or_name(bot, profile.tg_id)
# f"\nTelegram: {telegram_info}"


async def send_next_profile(target_message: Message, curr_user_tgid: int, state: FSMContext, bot: Bot):
    profile = await ServiceDB.search_profile(curr_user_tgid)

    if profile:
        await state.update_data(current_viewing_tg_id=profile.tg_id)

        try:
            profile_image = FSInputFile(str(profile.s3_path)) 
            
            await target_message.answer_photo(
                photo=profile_image,
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


@search_router.message(SearchProfileStates.start)
async def initiate_profile_search_handler(message: Message, state: FSMContext, bot: Bot): # Нужен bot: Bot
     await state.clear() 
     await message.answer("Начинаем поиск анкет...", reply_markup=ReplyKeyboardRemove())
     await send_next_profile(message, message.from_user.id, state, bot)


@search_router.callback_query(SearchProfileStates.viewing_profile, F.data.in_(["like", "next", "main_menu"]))
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
        await send_next_profile(callback_query.message, user_tg_id, state, bot)

    elif action == "next":
        print(f"Пропускаем профиль: {user_tg_id} -> {viewed_tg_id}")
        await send_next_profile(callback_query.message, user_tg_id, state, bot)

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