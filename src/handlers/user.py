from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from src.repository.queries import AsyncORM
from src.schemas import UserSchema
from src.states import StartStates


user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    if await AsyncORM.get_user_by_telegram_id(message.from_user.id):
        await state.set_state(StartStates.main_menu)
    else:
        await state.set_state(StartStates.get_token)


@user_router.message(StartStates.get_token)
async def user_start(message: Message, state: FSMContext):
    if await AsyncORM.get_user_by_telegram_id(message.from_user.id):
        await state.set_state(StartStates.main_menu)
    else:
        await state.set_state(StartStates.get_token)


@user_router.message()
async def user_echo(message: Message):
    if message.text:
        await message.answer(message.text)
