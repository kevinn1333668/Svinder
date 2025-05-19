from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, InviteCode
from src.config import Settings

router = Router()
settings = Settings()

@router.message(Command("invite"))
async def cmd_invite(message: Message, session: AsyncSession):
    # Get user's invite codes
    query = select(InviteCode).where(
        InviteCode.creator_id == message.from_user.id
    )
    result = await session.execute(query)
    invite_codes = result.scalars().all()
    
    # Count active (unused) codes
    active_codes = [code for code in invite_codes if not code.is_used]
    
    if len(active_codes) >= settings.MAX_INVITE_CODES:
        await message.answer(
            "У вас уже максимальное количество активных инвайт-кодов (3).\n"
            "Вы можете отозвать неиспользованные коды командой /revoke_invite"
        )
        return
    
    # Create new invite code
    new_code = InviteCode(creator_id=message.from_user.id)
    session.add(new_code)
    await session.commit()
    
    await message.answer(
        f"🎉 Вот ваш новый инвайт-код: `{new_code.code}`\n\n"
        "Отправьте его другу, чтобы он мог присоединиться к боту.\n"
        "Код можно использовать только один раз.\n\n"
        "У вас осталось {settings.MAX_INVITE_CODES - len(active_codes) - 1} доступных слотов для инвайт-кодов.",
        parse_mode="Markdown"
    )

@router.message(Command("revoke_invite"))
async def cmd_revoke_invite(message: Message, session: AsyncSession):
    # Get user's unused invite codes
    query = select(InviteCode).where(
        InviteCode.creator_id == message.from_user.id,
        InviteCode.is_used == False
    )
    result = await session.execute(query)
    unused_codes = result.scalars().all()
    
    if not unused_codes:
        await message.answer("У вас нет активных инвайт-кодов для отзыва.")
        return
    
    # TODO: Implement code selection and revocation
    await message.answer(
        "Выберите код для отзыва:\n" +
        "\n".join(f"{i+1}. {code.code}" for i, code in enumerate(unused_codes))
    )

@router.message(Command("my_invites"))
async def cmd_my_invites(message: Message, session: AsyncSession):
    # Get all user's invite codes
    query = select(InviteCode).where(
        InviteCode.creator_id == message.from_user.id
    )
    result = await session.execute(query)
    invite_codes = result.scalars().all()
    
    if not invite_codes:
        await message.answer("У вас пока нет инвайт-кодов.")
        return
    
    # Format message
    active_codes = [code for code in invite_codes if not code.is_used]
    used_codes = [code for code in invite_codes if code.is_used]
    
    text = "📋 Ваши инвайт-коды:\n\n"
    
    if active_codes:
        text += "Активные коды:\n"
        for code in active_codes:
            text += f"• `{code.code}`\n"
        text += "\n"
    
    if used_codes:
        text += "Использованные коды:\n"
        for code in used_codes:
            text += f"• `{code.code}` (использован {code.used_at.strftime('%d.%m.%Y')})\n"
    
    await message.answer(text, parse_mode="Markdown") 