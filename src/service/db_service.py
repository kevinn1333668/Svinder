from src.repository.queries import AsyncORM
from src.service.schemas import UserSchema, ProfileSchema


class AsyncServiceDB:
    @staticmethod
    async def is_user_exist_by_telegram_id(tg_id: int) -> bool:
        user = await AsyncORM.get_user_by_telegram_id(tg_id)

        if user is None:
            return False
        return True

    @staticmethod
    async def is_user_exist_by_id(user_id: int) -> bool:
        user = await AsyncORM.get_user_by_id(user_id)

        if user is None:
            return False
        return True

    @staticmethod
    async def get_user_by_telegram_id(tg_id: int):
        pass