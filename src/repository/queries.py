from operator import sub
from sqlalchemy import func, text, select, update, union, delete, exists, or_, nulls_last
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from src.repository.database import engine, Base, session_maker
from src.repository.models import User, Profile, Like, UserLikesReceived, Complain, Ban, Dislike # noqa: F401
from src.service.schemas import ProfileCreateInternalSchema
from src.repository.types import SexFilterState

from datetime import datetime, timedelta
import random


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
    async def create_user(tg_id: int, username: str | None = None):
        async with session_maker() as session:
            new_user = User(
                tg_id = tg_id,
                username=username
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
    @staticmethod
    async def get_user_by_username(username: str) -> User | None:
        """
        Находит пользователя по username (без учёта регистра).
        :param username: имя пользователя без @, например: "john_doe"
        :return: объект User или None
        """
        async with session_maker() as session:
            result = await session.execute(
                select(User).where(func.lower(User.username) == func.lower(username.strip()))
            )
            return result.scalar_one_or_none()
        
    
class ProfileORM:
    @staticmethod
    async def get_profile_by_tgid(tg_id: int):
        async with session_maker() as session:
            result = await session.execute(select(Profile).filter(Profile.tg_id == tg_id))
            return result.scalar_one_or_none()
        
    @staticmethod
    async def get_all_tg_ids():
        async with session_maker() as session:
            result = await session.execute(select(Profile.tg_id))
            tg_ids = [row[0] for row in result]
            return tg_ids
        
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
                s3_path=profile_data.s3_path,
                sex_filter=0,
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
                existing_profile.sex_filter = profile_data.sex_filter

                await session.commit()
                await session.refresh(existing_profile) 
                return True
            else:
                return False
    
    @staticmethod
    async def get_random_profile(curr_user_tgid: int, sex_filter: SexFilterState) -> Profile | None:
        async with session_maker() as session:

            user_profile = await ProfileORM.get_profile_by_tgid(curr_user_tgid)
            if user_profile is None:
                return None

            # Подзапрос на исключения
            excluded = (
                select(Like.liked_tgid)
                .where(Like.liker_tgid == curr_user_tgid)
                .union_all(
                    # Кого я лайкнул (уже не показываем)
                    select(Like.liked_tgid).where(Like.liker_tgid == curr_user_tgid),
                    # На кого я пожаловался
                    select(Complain.profile_tg_id).where(Complain.user_tg_id == curr_user_tgid),
                    #Если на меня пожаловались
                    select(Complain.user_tg_id).where(Complain.profile_tg_id == curr_user_tgid), 
                    # Кого я дизлайкнул (временно)
                    select(Dislike.profile_id).where(
                        (Dislike.user_id == curr_user_tgid) & (Dislike.until > func.now())
                    ),
                    # Кто лайкнул меня и я принял — он мне больше не нужен
                    select(Like.liker_tgid).where(
                        (Like.liked_tgid == curr_user_tgid) & (Like.is_accepted == True)
                    ),
                )
                .subquery()
            )

                    # Формируем условия WHERE
            conditions = [
                Profile.tg_id != curr_user_tgid,
                ~exists(select(excluded.c.liked_tgid).where(excluded.c.liked_tgid == Profile.tg_id))
            ]

            # Добавляем фильтр по полу только если sex_filter = True
            if sex_filter == SexFilterState.ONLY_GIRLS:
                conditions.append(Profile.sex == "FEMALE")  # замените на ваше значение для женского пола
            elif sex_filter == SexFilterState.ONLY_BOYS:
                conditions.append(Profile.sex == "MALE") 

            # Считаем количество подходящих профилей
            count_stmt = select(func.count()).select_from(Profile).where(*conditions)
            total = (await session.execute(count_stmt)).scalar()

            if not total or total == 0:
                print("DEBUG: search_profile не нашел других профилей.")
                return None

            # Случайный offset
            offset = random.randint(0, total - 1)

            stmt = (
                select(Profile)
                .where(*conditions)
                .offset(offset)
                .limit(1)
            )

            result = await session.execute(stmt)
            random_profile = result.scalar_one_or_none()

            if random_profile is None:
                print("DEBUG: search_profile не нашел других профилей.")
            else:
                print(f"DEBUG: search_profile({curr_user_tgid}) нашел профиль TG ID: {random_profile.tg_id}")

            return random_profile
        


            
    @staticmethod
    async def delete_profile_by_tg_id(tg_id: int):
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.tg_id == tg_id)
                    )
                user = result.scalar()  
                
                if not user:
                    return False


                # 1. Лайки, где пользователь — автор
                await session.execute(
                    delete(Like).where(Like.liker_tgid == tg_id)
                )

                # 2. Лайки, где пользователь — цель
                await session.execute(
                    delete(Like).where(Like.liked_tgid == tg_id)
                )

                await session.execute(
                    delete(UserLikesReceived).where(UserLikesReceived.tg_id == tg_id)
                )

                # 3. Жалобы, где пользователь — автор
                await session.execute(
                    delete(Complain).where(Complain.user_tg_id == tg_id)
                )

                # 4. Жалобы, где пользователь — цель
                await session.execute(
                    delete(Complain).where(Complain.profile_tg_id == tg_id)
                )

                # 5. Дизлайки
                await session.execute(
                    delete(Dislike).where(Dislike.user_id == tg_id)
                )

                await session.execute(
                    delete(Dislike).where(Dislike.profile_id == tg_id)
                )

                # 6. Удаляем профиль
                await session.execute(
                    delete(Profile).where(Profile.tg_id == tg_id)
                )

                # 8. Удаляем пользователя
                await session.delete(user)

            return True
               


    @staticmethod
    async def change_gender_filter_by_tg_id(tg_id: int) -> tuple[bool, bool] | bool:
        async with session_maker() as session:
            profile = await session.execute(select(Profile).where(Profile.tg_id == tg_id))
            profile = profile.scalar_one_or_none()
            
            if profile is None:
                return False
            

            
            current_state = profile.sex_filter
            if current_state == 0:  # OFF
                new_value = 1       # ONLY_GIRLS
            elif current_state == 1: # ONLY_GIRLS
                new_value = 2       # ONLY_BOYS
            else:                   # ONLY_BOYS или любое другое значение
                new_value = 0       # OFF


            profile.sex_filter = new_value
            await session.commit()
            
            print(f"Фильтр изменён: {SexFilterState(new_value)}")
            return (True, new_value)
        
    @staticmethod
    async def get_gender_filter_state(tg_id: int) -> SexFilterState:
        async with session_maker() as session:
            profile = await session.execute(select(Profile).where(Profile.tg_id == tg_id))
            profile = profile.scalar_one_or_none()
            
            if profile is None:
                return SexFilterState.OFF
            
            return SexFilterState(profile.sex_filter)

class LikeORM:
    @staticmethod
    async def get_like_by_id(like_id: int):
        async with session_maker() as session:
            result = await session.execute(select(Like).filter(Like.like_id == like_id))
            return result.all()
        
    @staticmethod
    async def get_like_by_tgids(liker_tgid: int, liked_tgid: int):
        async with session_maker() as session:
            result = await session.execute(select(Like).filter(
                Like.liker_tgid == liker_tgid,
                Like.liked_tgid == liked_tgid
            ))
            return result.scalar_one_or_none()

    @staticmethod
    async def create_like(liker_tgid: int, liked_tgid: int):
        async with session_maker() as session:
            try:
                print(f"✅ Вызван create_like: {liker_tgid} → {liked_tgid}")
                # 1. Пытаемся добавить лайк
                new_like = Like(
                    liker_tgid=liker_tgid,
                    liked_tgid=liked_tgid,
                    is_accepted=False
                )
                session.add(new_like)
                await session.commit()
                print("✅ Лайк добавлен в likes")  # Сохраняем в таблицу likes

            except IntegrityError:
                await session.rollback()
                print("❌ Ошибка IntegrityError при вставке лайка")
                return False  # дубликат или ошибка ссылок

            try:
                # 2. Фиксируем факт получения лайка (только один раз)
                stmt = insert(UserLikesReceived).values(
                    tg_id=liked_tgid,
                    liker_tgid=liker_tgid
                ).on_conflict_do_nothing(
                    index_elements=['tg_id', 'liker_tgid']
                )
                result = await session.execute(stmt)
                print(f"✅ Вставлено в user_likes_received: {result.rowcount} строк")

                await session.execute(stmt)
                await session.commit()
                return True
            
            except Exception as e:
                print(f"❌ Ошибка при вставке в user_likes_received: {type(e).__name__}: {e}") 
                # Маловероятно, но на всякий случай
                await session.rollback()
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
            return result.all()
        
    @staticmethod
    async def get_likes_by_liked_tgid(tg_id: int):
        async with session_maker() as session:
            result = await session.execute(select(Like).filter(Like.liked_tgid == tg_id))
            return result.scalars().all()
        
    @staticmethod
    async def get_all_pending_likes_by_liked_tgid(tg_id: int):
        async with session_maker() as session:
            stmt = select(Like).where(
                Like.liked_tgid == tg_id,
                Like.is_accepted == False,
                ~exists().where((Complain.user_tg_id == tg_id) &           # Я (получатель) жаловался
                (Complain.profile_tg_id == Like.liker_tgid)) # на того, кто лайкнул)
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    async def get_all_accepted_likes_by_liker_tgid(tg_id: int):
        async with session_maker() as session:
            stmt = select(Like).where(
                or_(Like.liker_tgid == tg_id, Like.liked_tgid == tg_id),
                Like.is_accepted == True
            )
            result = await session.execute(stmt)
            return result.scalars().all()
        
    @staticmethod
    async def accept_like(liker_tgid: int, liked_tgid: int) -> bool:
        async with session_maker() as session:
            like = await session.execute(
                select(Like).where(
                    Like.liker_tgid == liker_tgid,
                    Like.liked_tgid == liked_tgid
                )
            )
            like = like.scalar_one_or_none()

            if like is None:
                return False
            
            like.is_accepted = True
            
            await session.commit()
            
    @staticmethod
    async def get_top_likers(limit: int = 10):
        async with session_maker() as session:
            # Подзапрос: количество лайков
            subq = (
                select(
                    UserLikesReceived.tg_id,
                    func.count().label("like_count")
                )
                .group_by(UserLikesReceived.tg_id)
                .subquery()
            )

            # Основной запрос: тянем имя из Profile
            stmt = (
                select(
                    Profile.name,
                    subq.c.like_count
                )
                .join(Profile, Profile.tg_id == subq.c.tg_id)
                .where(Profile.is_active == True)
                .order_by(nulls_last(subq.c.like_count.desc()))
                .limit(limit)
            )

            result = await session.execute(stmt)
            return result.all()
        

    

        
class ComplaintORM:

    @staticmethod
    async def add_complaint(user_id: int, target_id: int) -> bool:
        async with session_maker() as session:
            try:
                complaint = Complain(user_tg_id=user_id, profile_tg_id=target_id)

                session.add(complaint)
                await session.commit()
                return True

            except IntegrityError:
                return False
            

class BanORM:
    @staticmethod
    async def ban_user(tg_id: int) -> bool:
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.tg_id == tg_id)
                    )
                user = result.scalar()  
                
                if not user:
                    return False
                
                existing_ban = await session.execute(select(Ban).where(Ban.tg_id == tg_id))
                if existing_ban.scalar_one_or_none():
                    return True  # Уже в бане


                # 1. Лайки, где пользователь — автор
                await session.execute(
                    delete(Like).where(Like.liker_tgid == tg_id)
                )

                # 2. Лайки, где пользователь — цель
                await session.execute(
                    delete(Like).where(Like.liked_tgid == tg_id)
                )

                # 3. Жалобы, где пользователь — автор
                await session.execute(
                    delete(Complain).where(Complain.user_tg_id == tg_id)
                )

                # 4. Жалобы, где пользователь — цель
                await session.execute(
                    delete(Complain).where(Complain.profile_tg_id == tg_id)
                )

                # 5. Дизлайки
                await session.execute(
                    delete(Dislike).where(Dislike.user_id == tg_id)
                )

                await session.execute(
                    delete(Dislike).where(Dislike.profile_id == tg_id)
                )

                # 6. Удаляем профиль
                await session.execute(
                    delete(Profile).where(Profile.tg_id == tg_id)
                )

                # 7. Добавляем в бан
                session.add(Ban(tg_id=tg_id))

                # 8. Удаляем пользователя
                await session.delete(user)

            return True
    
    @staticmethod
    async def is_banned(tg_id: int) -> bool:
        async with session_maker() as session:
            result = await session.execute(
                select(Ban).where(Ban.tg_id == tg_id)
            )
            return result.scalar_one_or_none() is not None
        
    @staticmethod
    async def unban_user(ban_id: int) -> bool:
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    delete(Ban).where(Ban.ban_id==ban_id)
                )
            return result.rowcount > 0
        
    @staticmethod
    async def get_primary_key(tg_id: int) -> int | None:
        async with session_maker() as session:
            result = await session.execute(
                select(Ban.ban_id).where(Ban.tg_id == tg_id)
            )
            ban_id = result.scalar_one_or_none()
            return ban_id
        
    @staticmethod
    async def get_ban_by_ban_id(ban_id: int) -> Ban:
        async with session_maker() as session:
            result = await session.execute(
                select(Ban).where(Ban.ban_id == ban_id)
            )
            ban = result.scalar_one_or_none()
            return ban

    @staticmethod
    async def get_ban_by_tg_id(tg_id: int) -> Ban:
        async with session_maker() as session:
            result = await session.execute(
                select(Ban).where(Ban.tg_id == tg_id)
            )
            ban = result.scalar_one_or_none()

            return ban   

        

class DislikeORM:
    @staticmethod
    async def add_dislike(user_id: int, target_id: int):
        async with session_maker() as session:
            async with session.begin():

                result = await session.execute(
                    select(Dislike).where(
                    Dislike.user_id == user_id,
                    Dislike.profile_id == target_id
                    )
                )

                existing = result.scalar_one_or_none()

                new_until = datetime.now() + timedelta(minutes=40)

                if existing:
                    existing.until = new_until

                else:
                    dislike = Dislike(
                        user_id=user_id,
                        profile_id=target_id,
                        until=new_until
                    )
                    session.add(dislike)

            return True
                