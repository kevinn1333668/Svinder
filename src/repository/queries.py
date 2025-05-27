from sqlalchemy import text, select, update

from src.repository.database import engine, Base, session_maker
from src.repository.models import User, Profile  # noqa: F401


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
    async def get_user_by_telegram_id(tg_id: int):
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