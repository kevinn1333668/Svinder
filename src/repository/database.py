from sqlalchemy import String, BigInteger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import Enum as SQLAlchemyEnum

from src.config import settings
from src.repository.types import TgID, Str32, Str64, Str100, Str128, Str256, Str1024, SexEnum


engine = create_async_engine(
    settings.database_url,
    echo=False,
)


session_maker = async_sessionmaker(engine)


class Base(DeclarativeBase):
    type_annotation_map = {
        SexEnum: SQLAlchemyEnum(SexEnum, name="SEX"),
        TgID: BigInteger,
        Str1024: String(1024),
        Str256: String(256),
        Str128: String(128),
        Str100: String(100),
        Str64: String(64),
        Str32: String(32),
    }

    repr_cols_num = 5
    repr_cols = tuple()
    
    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
