from typing import List
from random import randint 

from src.config import settings
from src.repository.queries import AsyncORM, UserORM, ProfileORM, LikeORM, ComplaintORM, BanORM, DislikeORM
from src.service.schemas import UserSchema, ProfileSchema, ProfileCreateInternalSchema, LikeSchema, BanSchema

from typing import List, Optional


class ServiceDB:

    
    

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
    async def add_user(tg_id: int, username: str | None = None):
        await UserORM.create_user(tg_id, username)

    @staticmethod
    async def get_user_by_usernameORM(username: str):
        return await UserORM.get_user_by_username(username)

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
    async def delete_profile(tg_id: int) -> int:
        return await ProfileORM.delete_profile_by_tg_id(tg_id=tg_id)

    
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
    
    @staticmethod
    async def report_profile(user_id: int, target_id: int):
        await ComplaintORM.add_complaint(user_id=user_id, target_id=target_id)

    @staticmethod
    async def ban_profile(tg_id: int):
        return await BanORM.ban_user(tg_id=tg_id)
    
    @staticmethod
    async def unban_profile(ban_id: int):
        return await BanORM.unban_user(ban_id=ban_id)

    @staticmethod
    async def is_user_banned(tg_id: int):
        return await BanORM.is_banned(tg_id=tg_id)
    
    @staticmethod
    async def get_ban_id(tg_id: int) -> int | None:
        return await BanORM.get_primary_key(tg_id=tg_id)
    
    @staticmethod
    async def get_ban_by_ban_id_ORM(ban_id: int) -> BanSchema:
        return await BanORM.get_ban_by_ban_id(ban_id=ban_id)
    @staticmethod
    async def get_ban_by_tg_id_ORM(tg_id: int) -> BanSchema:
        return await BanORM.get_ban_by_tg_id(tg_id=tg_id)

    @staticmethod
    async def create_dislike(user_id: int, target_id: int) -> bool:
        return await DislikeORM.add_dislike(user_id=user_id, target_id=target_id)

    
    

    