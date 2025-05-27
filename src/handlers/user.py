from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from src.repository.queries import AsyncORM
from src.states import StartStates


user_router = Router()


@user_router.message(StartStates.start)
async def user_start(message: Message, state: FSMContext):
    pass


@user_router.message(StartStates.get_token)
async def user_get_token(message: Message, state: FSMContext):
    await message.answer(
        "Ты еще не зарегестрирован! Введи инвайт-код и присоединяйся!",
        reply_markup=ReplyKeyboardRemove(),
    )


@user_router.message(StartStates.main_menu)
async def user_main_menu(message: Message, state: FSMContext):
    await message.answer(
        "ГЛАВНОЕ МЕНЮ",
        reply_markup=ReplyKeyboardRemove(),
    )


@user_router.message()
async def user_echo(message: Message):
    if message.text:
        await message.answer(message.text)
