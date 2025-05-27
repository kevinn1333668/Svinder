from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from src.states import UserRoadmap
from src.service.db_service import ServiceDB
from src.keyboards.reply import welcome_keyboard, sex_selection_horizontal_keyboard


WELCOME_TEXT = """
*Виват, студент!* 🇧🇾  

*Сустрэча* - это бот для знакомств среди учащихся вузов — находи друзей, единомышленников или даже вторую половинку!  

✨ *Что тут можно делать?*  
• Смотреть анкеты других ребят 🕵🏿‍♂️
• Найти интересных людей 🎓
• Общаться с виртуальным собеседником 🥶 

_Нажми *"Начать"*, чтобы создать свою анкету или посмотреть другие!_ 
"""


WELCOME_IMAGE = FSInputFile("src/static/bot/welcome.jpeg")


commands_router = Router()


@commands_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    await message.answer_photo(
        photo=WELCOME_IMAGE,
        caption=WELCOME_TEXT,
        reply_markup=welcome_keyboard(),
        parse_mode="Markdown",
    )

    if await ServiceDB.is_user_exist_by_telegram_id(message.from_user.id):
        await state.set_state(UserRoadmap.main_menu)
    else:
        await state.set_state(UserRoadmap.get_token)
    # await state.set_state(StartStates.start)
