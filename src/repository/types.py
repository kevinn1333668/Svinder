from enum import Enum
from typing import NewType


TgID = NewType("TgID", int)
Str1024 = NewType("Str1024", str)
Str256 = NewType("Str256", str)
Str128 = NewType("Str128", str)
Str100 = NewType("Str100", str)
Str64 = NewType("Str64", str)
Str32 = NewType("Str32", str)


class SexEnum(Enum):
    MALE = "male"
    FEMALE = "female"