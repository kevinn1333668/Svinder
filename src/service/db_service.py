import jwt
from random import randint 

from src.config import settings
from src.repository.queries import AsyncORM
from src.service.schemas import UserSchema, ProfileSchema


class ServiceDB:
    @staticmethod
    def generate_invite_code(tg_id: int):
        return jwt.encode({'sub': str(tg_id), 'random': randint(1,1000000000)}, settings.JWT_SECRET, algorithm="HS256")
    
    @staticmethod
    async def is_valid_code(code: str):
        try:
            payload = dict(jwt.decode(code, settings.JWT_SECRET, algorithms=["HS256"]))
        except jwt.exceptions.InvalidTokenError as e:
            print(e)
            return False
        
        print(payload)
        inviter_tgid = int(payload.get("sub"))

        print(inviter_tgid)

        if inviter_tgid is None:
            return False
        
        user_data = await AsyncORM.get_user_by_tgid(inviter_tgid)
        user = UserSchema.model_validate(user_data)
        
        if user.invite_code == code and user.invites > 0:
                new_code = ServiceDB.generate_invite_code(inviter_tgid)
                await AsyncORM.update_invites_and_code_by_tgid(inviter_tgid, user.invites-1, new_code)
                return True
        return False

    
    @staticmethod
    async def is_user_exist_by_tgid(tg_id: int) -> bool:
        user = await AsyncORM.get_user_by_tgid(tg_id)

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
    async def get_user_by_tgid(tg_id: int) -> UserSchema | None:
        user_data = await AsyncORM.get_user_by_tgid(tg_id)
        user = UserSchema.model_validate(user_data)
        if user is None:
            return None
        return user
    

    @staticmethod
    async def get_invite_info_by_tgid(tg_id: int) -> UserSchema | None:
        user_data = await AsyncORM.get_user_by_tgid(tg_id)
        user = UserSchema.model_validate(user_data)
        if user is None:
            return None
        return (user.invites, user.invite_code)

    @staticmethod
    async def add_user(tg_id: int):
        invite_token = ServiceDB.generate_invite_code(tg_id)
        await AsyncORM.create_user(tg_id, 3, invite_token)

    @staticmethod
    async def is_profile_exist_by_tgid(tg_id: int) -> bool:
        profile = await AsyncORM.get_profile_by_tgid(tg_id)
        if profile is None:
            return False
        return True