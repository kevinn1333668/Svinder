from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update, TelegramObject
from typing import Callable, Dict, Any, Awaitable

from src.service.db_service import ServiceDB


class BanCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Поддержка Update, Message, CallbackQuery и др.
        from_user = None
        if hasattr(event, "from_user") and event.from_user:
            from_user = event.from_user
        elif isinstance(event, Update) and event.message and event.message.from_user:
            from_user = event.message.from_user
        elif isinstance(event, Update) and event.callback_query and event.callback_query.from_user:
            from_user = event.callback_query.from_user

        if from_user is None:
            return await handler(event, data)

        user_tg_id = from_user.id
        is_banned = await ServiceDB.is_user_banned(tg_id=user_tg_id)

        if is_banned:
            bot = data.get("bot")
            if isinstance(event, Message):
                await event.answer("❌ Вы забанены и не можете использовать бота.")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ Вы забанены.", show_alert=True)
            return  # Не передаём дальше — обработчик не вызывается

        return await handler(event, data)