import random

from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from src.config import settings
from src.service.db_service import ServiceDB
from src.states import UserRoadmap
from src.keyboards.reply import go_to_main_menu, go_to_check_token


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
        if message.text == settings.ADMIN_TOKEN or await ServiceDB.is_valid_code(message.text):
            try:
                await ServiceDB.add_user(message.from_user.id)
                await state.set_state(UserRoadmap.main_menu)
                await message.answer(
                    "Welcome to the club, buddy!",
                    reply_markup=go_to_main_menu(),
                )
            except Exception:
                await state.clear()
                await message.answer("Smth is wrong")
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



user_messages_mm = [
    "Рад снова тебя видеть! 😈",
    "Зачем ты удалил наш чат!? Ну ладно, заходи, я соскучился 🥹",
    "Какие люди в Голливуде! Проходи!",
    "Залетай ✈️",
]


@user_router.message()
async def user_message(message: Message, state: FSMContext):
    if await ServiceDB.is_user_exist_by_tgid(message.from_user.id):
        await message.answer(
            random.choice(user_messages_mm),
            reply_markup=go_to_main_menu(),
        )
        await state.set_state(UserRoadmap.main_menu)
    else:
        await message.answer(
            "Сюда вход только по приглашению, ну-ка документики пожалуйста 🕵🏿‍♂️",
            reply_markup=go_to_check_token(),
        )
        await state.set_state(UserRoadmap.get_token)