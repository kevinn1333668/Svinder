from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from src.states import StartStates
from src.repository.queries import AsyncORM
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
    await state.set_state(StartStates.start)
