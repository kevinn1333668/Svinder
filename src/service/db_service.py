from typing import List
import jwt
from random import randint 

from src.config import settings
from src.repository.queries import AsyncORM, UserORM, ProfileORM, LikeORM
from src.service.schemas import UserSchema, ProfileSchema, ProfileCreateInternalSchema, LikeSchema


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
        
        user_data = await UserORM.get_user_by_tgid(inviter_tgid)
        user = UserSchema.model_validate(user_data)
        
        if user.invite_code == code and user.invites > 0:
                new_code = ServiceDB.generate_invite_code(inviter_tgid)
                await UserORM.update_invites_and_code_by_tgid(inviter_tgid, user.invites-1, new_code)
                return True
        return False

    
    @staticmethod
    async def is_user_exist_by_tgid(tg_id: int) -> bool:
        user = await UserORM.get_user_by_tgid(tg_id)

        if user is None:
            return False
        return True

    @staticmethod
    async def is_user_exist_by_id(user_id: int) -> bool:
        user = await UserORM.get_user_by_id(user_id)

        if user is None:
            return False
        return True

    @staticmethod
    async def get_user_by_tgid(tg_id: int) -> UserSchema | None:
        user_data = await UserORM.get_user_by_tgid(tg_id)
        user = UserSchema.model_validate(user_data)
        if user is None:
            return None
        return user
    

    @staticmethod
    async def get_invite_info_by_tgid(tg_id: int) -> UserSchema | None:
        user_data = await UserORM.get_user_by_tgid(tg_id)
        user = UserSchema.model_validate(user_data)
        if user is None:
            return None
        return (user.invites, user.invite_code)

    @staticmethod
    async def add_user(tg_id: int):
        invite_token = ServiceDB.generate_invite_code(tg_id)
        await UserORM.create_user(tg_id, 3, invite_token)

    @staticmethod
    async def is_profile_exist_by_tgid(tg_id: int) -> bool:
        profile = await ProfileORM.get_profile_by_tgid(tg_id)
        if profile is None:
            return False
        return True
    
    @staticmethod
    async def add_profile(profile_to_add: ProfileCreateInternalSchema):
        await ProfileORM.create_profile(profile_to_add)

    @staticmethod
    async def update_profile(profile_to_update: ProfileCreateInternalSchema):
        await ProfileORM.update_profile(profile_to_update)

    @staticmethod
    async def search_profile(curr_user_tgid: int) -> ProfileSchema:
        profile = await ProfileORM.get_random_profile_except_tgid(curr_user_tgid)
        return ProfileSchema.model_validate(profile) if profile else None
    
    @staticmethod
    async def get_profile_by_tgid(tgid: int) -> ProfileSchema | None:
        profile = await ProfileORM.get_profile_by_tgid(tgid)
        return ProfileSchema.model_validate(profile) if profile else None
    
    @staticmethod
    async def like_profile(liker_tgid, liked_tgid: int):
        await LikeORM.create_like(liker_tgid, liked_tgid)

    @staticmethod
    async def reject_like(liker_tgid: int, liked_tgid: int): 
        await LikeORM.delete_like(liker_tgid, liked_tgid)

    @staticmethod
    async def accept_like(liker_tgid: int, liked_tgid: int):
        await LikeORM.accept_like(liker_tgid, liked_tgid)

    @staticmethod
    async def get_pending_likes(liked_tgid: int) -> List[LikeSchema]:
        likes_data = await LikeORM.get_all_pending_likes_by_liked_tgid(liked_tgid)

        if likes_data is None:
            return None
        
        likes = [LikeSchema.model_validate(like) for like in likes_data]
            
        return likes
    
    @staticmethod
    async def get_accepted_likes(liker_tgid: int) -> List[LikeSchema]:
        likes_data = await LikeORM.get_all_accepted_likes_by_liker_tgid(liker_tgid)

        if likes_data is None:
            return None
        
        likes = [LikeSchema.model_validate(like) for like in likes_data]
            
        return likes
    