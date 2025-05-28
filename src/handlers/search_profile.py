from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext

from src.service.db_service import ServiceDB
from src.keyboards.reply import main_menu_keyboard
from src.keyboards.inline import profile_action_keyboard
from src.states import SearchProfileStates, UserRoadmap


search_router = Router()


@search_router.message(SearchProfileStates.get_profile)
async def profile_start(message: Message, state: FSMContext):
    profile = await ServiceDB.search_profile(message.from_user.id)

    profile_image = FSInputFile(str(profile.s3_path))

    if profile:
        await message.answer_photo(
            photo=profile_image,
            caption=f"{profile.name}, {profile.age} лет, {profile.uni}\n{profile.description}",
            reply_markup=profile_action_keyboard()
        )
        await state.set_state(SearchProfileStates.get_profile)
    else:
        await message.answer(
            "Других профилей не найдено 😭",
            reply_markup=main_menu_keyboard()
        )
        await state.set_state(UserRoadmap.main_menu)
