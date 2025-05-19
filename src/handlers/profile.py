from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Profile, Interest
from src.config import Settings

router = Router()
settings = Settings()

class ProfileEdit(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_university = State()
    waiting_for_bio = State()
    waiting_for_interests = State()

@router.message(Command("profile"))
async def cmd_profile(message: Message, session: AsyncSession):
    # Get user profile
    query = select(Profile).join(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()
    
    if not profile:
        await message.answer(
            "У вас пока нет профиля. Давайте создадим его!\n\n"
            "Отправьте мне ваше имя:"
        )
        await ProfileEdit.waiting_for_name.set()
        return
    
    # Format profile info
    interests = [interest.name for interest in profile.interests]
    
    text = (
        f"👤 Ваш профиль:\n\n"
        f"Имя: {profile.name}\n"
        f"Возраст: {profile.age}\n"
        f"ВУЗ: {profile.university}\n"
        f"О себе: {profile.bio}\n"
        f"Интересы: {', '.join(interests)}\n\n"
        "Для редактирования используйте команды:\n"
        "/edit_name - изменить имя\n"
        "/edit_age - изменить возраст\n"
        "/edit_university - изменить ВУЗ\n"
        "/edit_bio - изменить описание\n"
        "/edit_interests - изменить интересы"
    )
    
    await message.answer(text)

@router.message(Command("edit_name"))
async def cmd_edit_name(message: Message, state: FSMContext):
    await message.answer("Отправьте мне ваше новое имя:")
    await ProfileEdit.waiting_for_name.set()

@router.message(ProfileEdit.waiting_for_name)
async def process_name(message: Message, state: FSMContext, session: AsyncSession):
    name = message.text.strip()
    
    if len(name) < 2 or len(name) > 50:
        await message.answer("Имя должно быть от 2 до 50 символов. Попробуйте еще раз:")
        return
    
    # Update or create profile
    query = select(Profile).join(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()
    
    if profile:
        profile.name = name
    else:
        user = await session.get(User, message.from_user.id)
        profile = Profile(
            user_id=user.id,
            name=name
        )
        session.add(profile)
    
    await session.commit()
    await state.clear()
    
    await message.answer(
        f"✅ Имя успешно обновлено!\n\n"
        "Продолжите заполнение профиля, отправив мне ваш возраст (18-30):"
    )
    await ProfileEdit.waiting_for_age.set()

@router.message(ProfileEdit.waiting_for_age)
async def process_age(message: Message, state: FSMContext, session: AsyncSession):
    try:
        age = int(message.text.strip())
        if age < settings.MIN_AGE or age > settings.MAX_AGE:
            await message.answer(
                f"Возраст должен быть от {settings.MIN_AGE} до {settings.MAX_AGE} лет. "
                "Попробуйте еще раз:"
            )
            return
    except ValueError:
        await message.answer("Пожалуйста, введите число. Попробуйте еще раз:")
        return
    
    # Update profile
    query = select(Profile).join(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()
    
    if profile:
        profile.age = age
        await session.commit()
    
    await state.clear()
    
    await message.answer(
        "✅ Возраст успешно обновлен!\n\n"
        "Теперь отправьте мне название вашего ВУЗа:"
    )
    await ProfileEdit.waiting_for_university.set()

# TODO: Implement other profile edit handlers (university, bio, interests) 