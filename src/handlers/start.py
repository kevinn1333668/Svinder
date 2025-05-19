from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.models import User, Profile
from src.database import AsyncSession

router = Router()

class Registration(StatesGroup):
    waiting_for_invite = State()
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_university = State()
    waiting_for_bio = State()
    waiting_for_interests = State()

@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    # Check if user exists
    user = await session.get(User, message.from_user.id)
    
    if not user:
        await message.answer(
            "👋 Привет! Я бот для знакомств среди студентов.\n\n"
            "Для регистрации мне нужен инвайт-код. "
            "Попросите его у друга, который уже использует бота."
        )
        # TODO: Implement invite code handling
    else:
        await message.answer(
            f"С возвращением, {user.username}!\n\n"
            "Используйте /profile для просмотра и редактирования профиля\n"
            "/find для поиска собеседника\n"
            "/invite для управления инвайт-кодами"
        )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🤖 Я бот для знакомств среди студентов.\n\n"
        "Основные команды:\n"
        "/start - Начать работу с ботом\n"
        "/profile - Управление профилем\n"
        "/find - Найти собеседника\n"
        "/invite - Управление инвайт-кодами\n"
        "/help - Показать это сообщение"
    ) 