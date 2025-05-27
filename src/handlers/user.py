from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from src.config import settings
from src.repository.queries import AsyncORM
from src.states import UserRoadmap
from src.keyboards.reply import go_to_main_menu


user_router = Router()


@user_router.message(UserRoadmap.start)
async def user_start(message: Message, state: FSMContext):
    pass


@user_router.message(UserRoadmap.get_token)
async def user_get_token(message: Message, state: FSMContext):
    await state.set_state(UserRoadmap.check_token)
    await message.answer(
        "Ты еще не зарегестрирован! Введи инвайт-код и присоединяйся!",
        reply_markup=ReplyKeyboardRemove(),
    )


@user_router.message(UserRoadmap.check_token)
async def user_check_token(message: Message, state: FSMContext):
    if message.text:
        if message.text == settings.ADMIN_TOKEN:
            await state.set_state(UserRoadmap.main_menu)
            await message.answer(
                "Welcome to the club, buddy!",
                reply_markup=go_to_main_menu(),
            )
        else:
            await message.answer("Такого инвайта не существует!")
    else:
        await message.answer("Инвайт-код должен быть текстом!")


@user_router.message(UserRoadmap.main_menu)
async def user_main_menu(message: Message, state: FSMContext):
    await message.answer(
        "ГЛАВНОЕ МЕНЮ",
        reply_markup=ReplyKeyboardRemove(),
    )


@user_router.message()
async def user_echo(message: Message):
    if message.text:
        await message.answer(message.text)
