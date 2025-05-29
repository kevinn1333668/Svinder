import logging
import sys
import logging
import sys
import asyncio


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings

from src.handlers.user import user_router
from src.handlers.commands import commands_router
from src.handlers.profile import profile_router
from src.handlers.search_profile import search_router
from src.handlers.edit_profile import edit_router
from src.handlers.likes import likes_router

from src.repository.queries import AsyncORM


async def main():
    await AsyncORM.create_tables()
    
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_routers(commands_router, profile_router, search_router, edit_router, likes_router, user_router)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())