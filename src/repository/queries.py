from sqlalchemy import func, text, select, update
from sqlalchemy.exc import IntegrityError

from src.repository.database import engine, Base, session_maker
from src.repository.models import User, Profile, Like # noqa: F401
from src.service.schemas import ProfileCreateInternalSchema


class AsyncORM:
    @staticmethod
    async def select_version():
        async with session_maker() as session:
            result = await session.execute(text("select version()"))
            version = result.fetchone()
            return version

    @staticmethod
    async def create_tables():
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

class UserORM:
    @staticmethod
    async def create_user(tg_id: int, invites: int, invite_code: str | None):
        async with session_maker() as session:
            new_user = User(
                tg_id = tg_id,
                invites=invites,
                invite_code=invite_code,
            )
            session.add(new_user)
            
            await session.commit()

    @staticmethod
    async def get_user_by_id(user_id: int):
        async with session_maker() as session:
            result = await session.execute(select(User).filter(User.user_id == user_id))
            return result.scalar_one_or_none()
        
    @staticmethod
    async def get_profile_by_id(profile_id: int):
        async with session_maker() as session:
            result = await session.execute(select(Profile).filter(Profile.profile_id == profile_id))
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_tgid(tg_id: int):
        async with session_maker() as session:
            result = await session.execute(select(User).filter(User.tg_id == tg_id))
            return result.scalar_one_or_none()
    
    @staticmethod
    async def update_invites_and_code_by_tgid(tg_id: int, new_invites_count: int, new_invite_code: str):
        async with session_maker() as session:
            result = await session.execute(
                update(User)
                .where(User.tg_id == tg_id)
                .values(
                    invites=new_invites_count,
                    invite_code=new_invite_code,
                )
                .returning(User)
            )
            updated_user = result.scalar_one_or_none()
            
            if updated_user is None:
                return False
                
            await session.commit()
            return True
        
    
class ProfileORM:
    @staticmethod
    async def get_profile_by_tgid(tg_id: int):
        async with session_maker() as session:
            result = await session.execute(select(Profile).filter(Profile.tg_id == tg_id))
            return result.scalar_one_or_none()
        
    @staticmethod
    async def create_profile(profile_data: ProfileCreateInternalSchema):
        async with session_maker() as session:
            
            new_profile = Profile(
                tg_id=profile_data.tg_id,
                name=profile_data.name,
                age=profile_data.age,
                sex=profile_data.sex,
                uni=profile_data.uni,
                description=profile_data.description,
                s3_path=profile_data.s3_path
            )

            session.add(new_profile)
            
            await session.commit()

    @staticmethod
    async def update_profile(profile_data: ProfileCreateInternalSchema):
        async with session_maker() as session:
            stmt = select(Profile).where(Profile.tg_id == profile_data.tg_id)
            result = await session.execute(stmt)
            existing_profile = result.scalars().one_or_none()

            if existing_profile:
                existing_profile.name = profile_data.name
                existing_profile.age = profile_data.age
                existing_profile.sex = profile_data.sex
                existing_profile.uni = profile_data.uni
                existing_profile.description = profile_data.description
                existing_profile.s3_path = profile_data.s3_path

                await session.commit()
                await session.refresh(existing_profile) 
                return True
            else:
                return False
    
    @staticmethod
    async def get_random_profile_except_tgid(curr_user_tgid: int) -> Profile | None:
        async with session_maker() as session:
            stmt = select(Profile).where(
                Profile.tg_id != curr_user_tgid
            ).order_by(
                func.random()
            ).limit(1)

            result = await session.execute(stmt)

            random_profile = result.scalar_one_or_none()

            print("I SEE", random_profile)

            if random_profile is None:
                print("DEBUG: search_profile не нашел других профилей.")
            else:
                print(f"DEBUG: search_profile({curr_user_tgid}) нашел профиль TG ID: {random_profile.tg_id}")

            return random_profile
               

class LikeORM:
    @staticmethod
    async def get_like_by_id(like_id: int):
        async with session_maker() as session:
            result = await session.execute(select(Like).filter(Like.like_id == like_id))
            return result.all_or_none()
        
    @staticmethod
    async def create_like(liker_tgid, liked_tgid):
        async with session_maker() as session:
            try:
                new_like = Like(
                    liker_tgid=liker_tgid,
                    liked_tgid=liked_tgid,
                    is_accepted=False
                )
                session.add(new_like)
                await session.commit()
                return True
            except IntegrityError:
                return False
            
    @staticmethod
    async def delete_like(liker_tgid, liked_tgid):
        async with session_maker() as session:
            try:
                like = await session.execute(
                    select(Like).where(
                        Like.liker_tgid == liker_tgid,
                        Like.liked_tgid == liked_tgid
                    )
                )
                like = like.scalar_one_or_none()
                
                if like:
                    await session.delete(like)
                    await session.commit()
                    return True
                return False
            except Exception:
                await session.rollback()
                return False

    @staticmethod 
    async def get_likes_by_liker_tgid(tg_id: int):
        async with session_maker() as session:
            result = await session.execute(select(Like).filter(Like.liker_tgid == tg_id))
            return result.all_or_none()
        
    @staticmethod
    async def get_likes_by_liked_tgid(tg_id: int):
        async with session_maker() as session:
            result = await session.execute(select(Like).filter(Like.liked_tgid == tg_id))
            return result.scalars().all_or_none()
        
    @staticmethod
    async def get_all_pending_likes_by_liked_tgid(tg_id: int):
        async with session_maker() as session:
            stmt = select(Like).where(
                Like.liked_tgid == tg_id,
                Like.is_accepted == False
            )
            result = await session.execute(stmt)
            return result.scalars().all_or_none()

    @staticmethod
    async def get_all_accepted_likes_by_liker_tgid(tg_id: int):
        async with session_maker() as session:
            stmt = select(Like).where(
                Like.liker_tgid == tg_id,
                Like.is_accepted == True
            )
            result = await session.execute(stmt)
            return result.scalars().all()
        
    @staticmethod
    async def accept_like(like_id: int) -> bool:
        async with session_maker() as session:
            like_to_accept = await LikeORM.get_like_by_id(like_id)
            
            if like_to_accept is None:
                return False
            
            like_to_accept.is_accepted = True
            await session.commit()

        if like_to_accept:
            like_to_accept.is_accepted = True
            await session.commit()
            await session.refresh(like_to_accept)
            return True
        return False
