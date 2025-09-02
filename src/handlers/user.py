import random

from aiogram import F
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.config import settings
from src.service.db_service import ServiceDB
from src.states import SearchProfileStates, UserRoadmap, CreateProfileStates, EditProfileStates




from src.keyboards.reply import (
    go_to_main_menu, 
    main_menu_keyboard, yes_or_no_keyboard,
    understand_keyboard, welcome_keyboard,
)
from src.keyboards.inline import get_confirmation_keyboard, short_pending_like_action_keyboard 

from src.static.text.texts import (
    text_main_menu, text_main_menu_get_back,
    text_search_profiles, text_edit_profile,
    text_my_profile, 
    text_no, text_yes,
    text_profile_create_begin,
    text_search_profiles_start,
    text_delete_profile, text_filter_sex,
    text_top_likers
)


user_router = Router()


@user_router.message(F.text == text_my_profile)
async def get_my_profile(message: Message):
    profile = await ServiceDB.get_profile_by_tgid(message.from_user.id)

    profile_image = profile.s3_path

    await message.answer_photo(
            photo=profile_image,
            caption=(
                f"{profile.name}, {profile.age} лет, {profile.uni}\n"
                f"{profile.sex.value}\n"
                f"{profile.description}"
            )
        )
    
@user_router.message(F.text == text_filter_sex)
async def toggle_gender_filter(message: Message):
    result = await ServiceDB.change_gender_filter(message.from_user.id)

    if result:
        filter_id = result[1]
        if filter_id == 0:
            await message.answer(f'Фильтрация: выключена ❌')

        elif filter_id == 1:
            await message.answer(f'Фильтрация: Девочки 👧')

        elif filter_id == 2:
            await message.answer(f'Фильтрация: Мальчики 👦')

    else:
        await message.answer("Произошла ошибка при смене режима фильтрации")


@user_router.message(F.text == text_top_likers)
async def get_top_likers(message: Message):
    top_users = await ServiceDB.get_top_10()

    text = "🏆 ТОП-10 по лайкам:\n\n"
    for i, (name, count) in enumerate(top_users, 1):
        if i == 1:
            text += f"🥇 {name} 🥇   {count} 🔥\n\n"

        elif i == 2:
            text += f"🥈 {name} — {count}  ❤️\n"

        elif i == 3:
            text += f"🥉 {name} — {count}  ❤️\n"

        else:
            text += f"{i}. {name} — {count}  ❤️\n"

    await message.answer(text)


@user_router.message(F.text == text_delete_profile)
async def delete_my_profile(message: Message):
    await message.answer(
        text="Вы уверены, что хотите удалить свой профиль? Это действие нельзя отменить.",
        reply_markup=get_confirmation_keyboard()
    )


@user_router.callback_query(F.data == "confirm_delete_profile")
async def confirm_delete_profile(callback: CallbackQuery):
    user_tg_id = callback.from_user.id

    try:
        await ServiceDB.delete_profile(tg_id=user_tg_id)
        await callback.message.edit_text(text="Анкета успешно удалена! Нажмите '/start' для перезапуска.")
    except Exception as e:
        await callback.message.edit_text(text="Ошибка при удалении профиля!")

    await callback.answer()  # Убираем "часики" с кнопки


@user_router.callback_query(F.data == "cancel_delete_profile")
async def cancel_delete_profile(callback: CallbackQuery):
    await callback.message.delete()  # Удаляем сообщение с подтверждением
    await callback.answer()  # Убираем индикатор загрузки с кнопки


@user_router.message(F.text == text_edit_profile)
async def user_start_edit_profile(message: Message, state: FSMContext):
    await message.answer(
        "Ну что же, давай отредактируем твою анкету",
        reply_markup=welcome_keyboard(),
    )
    await state.set_state(EditProfileStates.start)



@user_router.message(UserRoadmap.main_menu, F.text == text_yes)
async def user_create_profile(message: Message, state: FSMContext):
    await message.answer(
        text_profile_create_begin,
        reply_markup=understand_keyboard(),
    )
    await state.set_state(CreateProfileStates.start)


@user_router.message(UserRoadmap.main_menu)
async def user_search_profiles(message: Message, state: FSMContext):
    await message.answer(
        "Нужно создать анкету",
        reply_markup=yes_or_no_keyboard()
    )

@user_router.callback_query(F.data.startswith("show_profile"))
async def show_liker_profile(callback_query: CallbackQuery, bot: Bot):

    await callback_query.message.delete()
    
    action = callback_query.data
    liker_tg_id_to_show = int(action.split(':')[1])

    profile_data = await ServiceDB.get_profile_by_tgid(liker_tg_id_to_show)

    if profile_data:
        try:
            file_id = profile_data.s3_path
            
            await bot.send_photo(
                chat_id=callback_query.from_user.id,
                photo=file_id,
                caption=(
                    f"Вам симпатизирует: {profile_data.name}, {profile_data.age} лет, {profile_data.uni}\n"
                    f"{(profile_data.description)}\n\n"
                ),
                reply_markup=short_pending_like_action_keyboard(liker_tg_id=liker_tg_id_to_show)
            )

        except FileNotFoundError:
            await bot.send_message(chat_id=callback_query.from_user.id ,text=f"Не удалось загрузить фото для профиля {profile_data.name}. Пропускаем...")
        except Exception as e:
            await bot.send_message(chat_id=callback_query.from_user.id ,text=f"Произошла ошибка при показе профиля: {e}. Пропускаем...")
            print(f"Error sending pending like profile: {e}")






