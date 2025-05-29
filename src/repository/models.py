from typing import Annotated, List
from datetime import datetime, timezone

from sqlalchemy import text, Boolean, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.repository.types import TgID, Str100, Str256, Str1024, SexEnum
from src.repository.database import Base


created_at_type = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        nullable=False
    )
]

modified_at_type = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=text("TIMEZONE('utc', now())"), # onupdate=text("TIMEZONE('utc', now())"), # АЛЬТЕРНАТИВНЫЙ, более явный вариант для onupdate
        nullable=False
    )
]


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[TgID] = mapped_column(nullable=False, unique=True)
    invites: Mapped[int] = mapped_column(Integer, nullable=False, server_default="3")
    invite_code: Mapped[Str256] = mapped_column(nullable=True)

    profile: Mapped["Profile"] = relationship(
        back_populates="user",
    )


class Profile(Base):
    __tablename__ = "profiles"

    profile_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[TgID] = mapped_column(ForeignKey("users.tg_id"))

    name: Mapped[Str100] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[SexEnum] = mapped_column(nullable=False)
    uni: Mapped[Str100] = mapped_column(nullable=False)
    description: Mapped[Str1024] = mapped_column(nullable=False)
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=True, server_default=text("true")
    )

    s3_path: Mapped[Str1024] = mapped_column(nullable=False, unique=True)

    created_at: Mapped[created_at_type]
    modified_at: Mapped[modified_at_type]

    user: Mapped["User"] = relationship(
        back_populates="profile",
    )


class Like(Base):
    __tablename__ = "likes"

    like_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    liker_tgid: Mapped[TgID] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    liked_tgid: Mapped[TgID] = mapped_column(ForeignKey("users.tg_id"), nullable=False)

    is_accepted: Mapped[bool] = mapped_column(
        Boolean, nullable=True, server_default=text("false")
    )

    __table_args__ = (
        UniqueConstraint("liker_tgid", "liked_tgid", name="uq_liker_liked"),
    )
