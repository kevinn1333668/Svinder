from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery 
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.command import CommandObject

from src.service.db_service import ServiceDB
from src.keyboards.inline import moderation_keyboard
from src.states import SearchProfileStates, UserRoadmap
from src.static.text.texts import text_search_profiles
from src.handlers.likes import get_telegram_username_or_name
from src.states import AdminStates

from src.config import settings
import asyncio

admin_router = Router()

broadcast_mode = False

@admin_router.callback_query(F.data.startswith("approve_"))
async def handle_approve(callback_query: CallbackQuery, bot: Bot):
    await callback_query.answer()

    user_tg_id = int(callback_query.data.split("_")[1])
    admin = callback_query.from_user

    username = await get_telegram_username_or_name(bot, user_tg_id)

    admin_mention = f"@{admin.username}" if admin.username else admin.full_name
    user_mention = f"@{username}" if username.startswith('@') else username
    print('123')

    new_text = f"✅ Админ {admin_mention} одобрил пользователя {user_mention}"

    try:
        await callback_query.message.delete()
        await callback_query.message.answer(new_text)

    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")
        await callback_query.message.answer(new_text)

    print(f"Админ {admin.id} одобрил пользователя {user_tg_id}")

@admin_router.callback_query(F.data.startswith("ban_"))
async def handle_ban(callback_query: CallbackQuery, bot: Bot):

    await callback_query.answer()

    action = callback_query.data
    user_tg_id = int(action.split('_')[1])

    if user_tg_id in settings.ADMINS_IDS:
        await callback_query.message.delete()
        await callback_query.message.answer("Нельзя забанить администратора.")
        return

    is_banned = await ServiceDB.is_user_banned(tg_id=user_tg_id)
    print(is_banned)
    if is_banned:
        await callback_query.message.answer(text="Пользователь уже забанен")
        return




    await ServiceDB.ban_profile(tg_id=user_tg_id)

    ban = await ServiceDB.get_ban_by_tg_id_ORM(tg_id=user_tg_id)
    
    admin = callback_query.from_user

    username = await get_telegram_username_or_name(bot, user_tg_id)

    admin_mention = f"@{admin.username}" if admin.username else admin.full_name
    user_mention = f"{username}" if username.startswith('@') else username

    new_text = f"❌ Админ {admin_mention} забанил пользователя {user_mention}. ID бана - {ban.ban_id}"

    try:
        await bot.send_message(
        chat_id=user_tg_id,
        text=f"Вы забаненны по решению администрации. ID бана {ban.ban_id}\n По всем вопросам - @SvinderSupportBot"
    )
    
    except Exception as e:
        print(f"Ошибка при отправки сообщения сообщения: {e}")

    try:
        await callback_query.message.delete()
        await callback_query.message.answer(new_text)

    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")
        await callback_query.message.answer(new_text)

    print(f"Админ {admin.id} забанил пользователя {user_tg_id}")

@admin_router.message(Command("ban"))
async def cmd_ban(message: Message, command: CommandObject):

    if message.from_user.id not in settings.ADMINS_IDS:
        await message.answer("У вас нет прав на это действие.")
        return
    

    

    args = command.args

    if args == '@PaiN7111':
        await message.answer("Нельзя забанить администратора")
        return

    if not args:
        await message.answer("Использование: `/ban @username`", parse_mode="Markdown")
        return
    
    username = args.strip().lstrip('@')
    user = await ServiceDB.get_user_by_usernameORM(username)

    if not user:
        await message.answer(f"❌ Пользователь @{username} не найден.")
        return

    success = await ServiceDB.ban_profile(tg_id=user.tg_id)
    if success:

        ban_id = await ServiceDB.get_ban_id(tg_id=user.tg_id)

        await message.answer(f"✅ Пользователь @{username} забанен. ID бана - {ban_id}")
        try:
            await message.bot.send_message(user.tg_id, f"❌ Вы были забанены по решению администрации. ID бана - {ban_id}\n По всем вопросам обращаться в @SvinderSupportBot")
        except Exception as e:
            print(f"Ошибка при отправке: {e}")
    else:
        await message.answer("❌ Ошибка при бане.")

@admin_router.message(Command("unban"))
async def cmd_unban(message: Message, command: CommandObject):
    
    if message.from_user.id not in settings.ADMINS_IDS:
        await message.answer("У вас нет прав на это действие.")
        return
    
    args = command.args

    if not args:
        await message.answer("Использование: `/unban ID`", parse_mode="Markdown")
        
    try:    
        ban_id = int(args)

    except:
        await message.answer("❌ ID должен быть целыми числом")
        return
    
    ban = await ServiceDB.get_ban_by_ban_id_ORM(ban_id=ban_id)
    success = await ServiceDB.unban_profile(ban_id=ban_id)

    if success:


        await message.answer(f"✅ Пользователь разбанен.")
        try:
            await message.bot.send_message(ban.tg_id, "✅ Вы были разбанены по решению администрации.")
        except Exception as e:
                print(f"Ошибка при отправке: {e}")
    else:
        await message.answer("❌ Ошибка при разбане.")


@admin_router.message(Command('broadcast'))
async def start_broadcast(message: Message, state: FSMContext):
    # Проверка: только админы
    if message.from_user.id not in settings.ADMINS_IDS:
        return  # Или можно отправить "нет прав", если нужно

    # Устанавливаем состояние
    await state.set_state(AdminStates.waiting_broadcast)
    await message.answer("📢 Отправь мне сообщение, которое нужно разослать всем пользователям.")

@admin_router.message(Command('adv'))
async def start_broadcast(message: Message, state: FSMContext):
    # Проверка: только админы
    if message.from_user.id not in settings.ADMINS_IDS:
        return  # Или можно отправить "нет прав", если нужно

    # Устанавливаем состояние
    await state.set_state(AdminStates.waitng_advertisment)
    await message.answer("📢 Отправь мне сообщение, которое нужно разослать всем пользователям.")

@admin_router.message(AdminStates.waiting_broadcast, F.from_user.id.in_(settings.ADMINS_IDS))
async def handle_broadcast(message: Message, bot: Bot, state: FSMContext):
    
    
    await state.clear()
    
    tg_ids = await ServiceDB.get_all_users()

    await message.answer(f"Начинаю рассылку ({len(tg_ids)} пользователям)")

    for tg_id in tg_ids:
        try:
            if message.text:
                await bot.send_message(
                    chat_id=tg_id,
                    text=message.text
                )

            else:
                await bot.copy_message(
                    chat_id=tg_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    caption=message.caption or ''
                )
            await asyncio.sleep(0.05) 

        except Exception as e:
            print(f'Ошибка {tg_id}: {e}')

    await message.answer('✅ Рассылка завершена!')


@admin_router.message(AdminStates.waitng_advertisment, F.from_user.id.in_(settings.ADMINS_IDS))
async def handle_broadcast(message: Message, bot: Bot, state: FSMContext):
    
    
    await state.clear()
    
    tg_ids = await ServiceDB.get_all_users()

    await message.answer(f"Начинаю рассылку ({len(tg_ids)} пользователям)")

    for tg_id in tg_ids:
        try:
            if message.text:
                await bot.send_message(
                    chat_id=tg_id,
                    text=message.text + '\n\n#реклама'
                )

            else:
                await bot.copy_message(
                    chat_id=tg_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    caption=(message.caption or '') + '\n\n#реклама'
                 )
            await asyncio.sleep(0.05) 

        except Exception as e:
            print(f'Ошибка {tg_id}: {e}')

    await message.answer('✅ Рассылка завершена!')