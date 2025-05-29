from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.repository.types import SexEnum


class UserSchema(BaseModel):
    user_id: Annotated[int, Field()]
    tg_id: Annotated[int, Field()]

    invites: Annotated[int, Field()]
    invite_code: Annotated[str, Field()]

    model_config = ConfigDict(from_attributes=True)


class ProfileSchema(BaseModel):
    profile_id: Annotated[int, Field()]
    tg_id: Annotated[int, Field()]

    name: Annotated[str, Field(min_length=1, max_length=100)]
    age: Annotated[int, Field(ge=16, le=80)]
    sex: Annotated[SexEnum, Field()]
    uni: Annotated[str, Field(min_length=2, max_length=100)]
    description: Annotated[str, Field(max_length=1024)]

    is_active: Annotated[bool, Field(default=True)]
    s3_path: Annotated[str | None, Field()]

    created_at: Annotated[datetime, Field()]
    modified_at: Annotated[datetime, Field()]

    model_config = ConfigDict(from_attributes=True)


class ProfileCreateInternalSchema(BaseModel):
    tg_id: int

    name: Annotated[str, Field(min_length=1, max_length=100)]
    age: Annotated[int, Field(ge=16, le=80)]
    sex: Annotated[SexEnum, Field()]
    uni: Annotated[str, Field(min_length=2, max_length=100)]
    description: Annotated[str, Field(max_length=1024)]

    s3_path: Annotated[str | None, Field()]


class LikeSchema(BaseModel):
    like_id: Annotated[int, Field()]
    
    liker_tgid: Annotated[int, Field()]
    liked_tgid: Annotated[int, Field()]

    is_accepted: Annotated[bool, Field(default=True)]

    model_config = ConfigDict(from_attributes=True)
