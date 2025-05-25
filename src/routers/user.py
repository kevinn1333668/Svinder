from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command


user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message):
    await message.answer('Добро пожаловать в бот!')


@user_router.message()
async def user_echo(message: Message):
    if message.text:
        await message.answer(message.text)
