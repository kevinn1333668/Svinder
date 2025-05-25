from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from src.states import StartStates
from src.repository.queries import AsyncORM


commands_router = Router()


@commands_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    await message.answer("start is instanciated")
    # if await AsyncORM.get_user_by_telegram_id(message.from_user.id):
    #     await state.set_state(StartStates.main_menu)
    # else:
    #     await state.set_state(StartStates.get_token)