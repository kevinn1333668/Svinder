from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession
import random

from src.database.models import User, Profile

router = Router()

@router.message(Command("find"))
async def cmd_find(message: Message, session: AsyncSession):
    # Get user's profile
    query = select(Profile).join(User).where(User.telegram_id == message.from_user.id)
    result = await session.execute(query)
    user_profile = result.scalar_one_or_none()
    
    if not user_profile:
        await message.answer(
            "Для поиска собеседника нужно сначала создать профиль.\n"
            "Используйте команду /profile для создания профиля."
        )
        return
    
    # Find random profile that is not the user's own
    query = select(Profile).join(User).where(
        and_(
            User.telegram_id != message.from_user.id,
            User.is_active == True
        )
    )
    result = await session.execute(query)
    profiles = result.scalars().all()
    
    if not profiles:
        await message.answer(
            "😔 К сожалению, сейчас нет других активных пользователей.\n"
            "Попробуйте позже или пригласите друзей!"
        )
        return
    
    # Select random profile
    random_profile = random.choice(profiles)
    
    # Format profile info
    interests = [interest.name for interest in random_profile.interests]
    
    text = (
        f"👤 Найден собеседник:\n\n"
        f"Имя: {random_profile.name}\n"
        f"Возраст: {random_profile.age}\n"
        f"ВУЗ: {random_profile.university}\n"
        f"О себе: {random_profile.bio}\n"
        f"Интересы: {', '.join(interests)}\n\n"
        "Хотите начать общение?"
    )
    
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Написать", callback_data=f"like_{random_profile.user_id}"),
            InlineKeyboardButton(text="👎 Пропустить", callback_data="skip")
        ]
    ])
    
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("like_"))
async def process_like(callback: CallbackQuery, session: AsyncSession):
    target_user_id = int(callback.data.split("_")[1])
    
    # Get target user's profile
    query = select(Profile).join(User).where(User.id == target_user_id)
    result = await session.execute(query)
    target_profile = result.scalar_one_or_none()
    
    if not target_profile:
        await callback.answer("Пользователь больше не активен.")
        await callback.message.delete()
        return
    
    # Get current user's profile
    query = select(Profile).join(User).where(User.telegram_id == callback.from_user.id)
    result = await session.execute(query)
    current_profile = result.scalar_one_or_none()
    
    # Format message for target user
    target_text = (
        f"👋 Кто-то хочет с вами познакомиться!\n\n"
        f"Имя: {current_profile.name}\n"
        f"Возраст: {current_profile.age}\n"
        f"ВУЗ: {current_profile.university}\n"
        f"О себе: {current_profile.bio}\n\n"
        "Хотите начать общение?"
    )
    
    # Create inline keyboard for target user
    target_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Ответить", callback_data=f"match_{callback.from_user.id}"),
            InlineKeyboardButton(text="👎 Отклонить", callback_data="reject")
        ]
    ])
    
    # Send notification to target user
    await callback.bot.send_message(
        target_profile.user.telegram_id,
        target_text,
        reply_markup=target_keyboard
    )
    
    await callback.answer("Запрос на общение отправлен!")
    await callback.message.delete()

@router.callback_query(F.data == "skip")
async def process_skip(callback: CallbackQuery):
    await callback.answer("Ищем следующего собеседника...")
    await callback.message.delete()
    await cmd_find(callback.message, callback.bot.get("session"))

@router.callback_query(F.data.startswith("match_"))
async def process_match(callback: CallbackQuery, session: AsyncSession):
    target_user_id = int(callback.data.split("_")[1])
    
    # Get both users' profiles
    query = select(Profile).join(User).where(User.id == target_user_id)
    result = await session.execute(query)
    target_profile = result.scalar_one_or_none()
    
    query = select(Profile).join(User).where(User.telegram_id == callback.from_user.id)
    result = await session.execute(query)
    current_profile = result.scalar_one_or_none()
    
    if not target_profile or not current_profile:
        await callback.answer("Один из пользователей больше не активен.")
        await callback.message.delete()
        return
    
    # Notify both users about the match
    match_text = (
        "🎉 У вас взаимная симпатия!\n\n"
        "Теперь вы можете общаться в личных сообщениях.\n"
        "Удачного общения!"
    )
    
    await callback.bot.send_message(target_profile.user.telegram_id, match_text)
    await callback.message.edit_text(match_text)
    
    # TODO: Implement chat functionality or direct message forwarding 