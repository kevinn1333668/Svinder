from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from src.states import UserRoadmap
from src.service.db_service import ServiceDB
from src.keyboards.reply import welcome_keyboard, sex_selection_horizontal_keyboard, main_menu_keyboard

from src.static.text.texts import WELCOME_IMAGE, WELCOME_TEXT, text_main_menu







commands_router = Router()


@commands_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):

    await state.clear()

    if not await ServiceDB.is_user_exist_by_tgid(message.from_user.id):
        await ServiceDB.add_user(message.from_user.id, message.from_user.username)
        await message.answer_photo(
            photo=WELCOME_IMAGE,
            caption=WELCOME_TEXT,
            reply_markup=welcome_keyboard(),
            parse_mode="Markdown",
        )
        await state.set_state(UserRoadmap.main_menu)

    else:
        await message.answer(
            text_main_menu,
            reply_markup=main_menu_keyboard(),
        )


    # await state.set_state(StartStates.start)
