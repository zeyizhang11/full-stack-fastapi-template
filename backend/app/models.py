import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    hexagram_readings: list["HexagramReading"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# ── Liu Yao (六爻) models ──────────────────────────────────────────────────────

class CastMethod(str):
    COIN = "coin"       # 三铜钱法（随机）
    TIME = "time"       # 时间起卦
    NUMBERS = "numbers" # 报数起卦
    MANUAL = "manual"   # 手动指定六爻


class HexagramReadingCreate(SQLModel):
    """三铜钱法起卦（默认）"""
    question: str | None = Field(default=None, max_length=500)
    caster_name: str | None = Field(default=None, max_length=100)
    caster_gender: str | None = Field(default=None, max_length=10)


class CastByTimeRequest(SQLModel):
    """时间起卦"""
    year: int = Field(ge=1900, le=2100)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    hour: int = Field(ge=0, le=23)
    question: str | None = Field(default=None, max_length=500)
    caster_name: str | None = Field(default=None, max_length=100)
    caster_gender: str | None = Field(default=None, max_length=10)


class CastByNumbersRequest(SQLModel):
    """报数起卦：用户随机说三个数（上卦数、下卦数、动爻数）"""
    upper_num: int = Field(ge=1)
    lower_num: int = Field(ge=1)
    changing_num: int = Field(ge=1)
    question: str | None = Field(default=None, max_length=500)
    caster_name: str | None = Field(default=None, max_length=100)
    caster_gender: str | None = Field(default=None, max_length=10)


class CastByManualRequest(SQLModel):
    """手动指定六爻（每爻：6=老阴, 7=少阳, 8=少阴, 9=老阳）"""
    lines: list[int] = Field(min_length=6, max_length=6)
    question: str | None = Field(default=None, max_length=500)
    caster_name: str | None = Field(default=None, max_length=100)
    caster_gender: str | None = Field(default=None, max_length=10)


class HexagramReading(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    reading_number: str = Field(unique=True, index=True, max_length=20)
    cast_method: str = Field(default="coin", max_length=20)
    question: str | None = Field(default=None, max_length=500)
    caster_name: str | None = Field(default=None, max_length=100)
    caster_gender: str | None = Field(default=None, max_length=10)
    lines: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    hexagram_number: int
    changed_hexagram_number: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    owner_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", nullable=True, ondelete="SET NULL"
    )
    owner: Optional["User"] = Relationship(back_populates="hexagram_readings")


class HexagramReadingPublic(SQLModel):
    id: uuid.UUID
    reading_number: str
    cast_method: str
    question: str | None
    caster_name: str | None
    caster_gender: str | None
    lines: list[int]
    hexagram_number: int
    changed_hexagram_number: int | None
    created_at: datetime
    owner_id: uuid.UUID | None


class GanzhiInfo(SQLModel):
    solar: str
    year_gz: str
    month_gz: str
    day_gz: str
    hour_gz: str
    xunkong: list[str]


class YaoInfo(SQLModel):
    liuqin: str       # 六亲：父母/兄弟/妻财/子孙/官鬼
    najia: str        # 纳甲：如 甲子、壬午
    element: str      # 五行：金木水火土
    liushen: str      # 六神：青龙/朱雀/勾陈/腾蛇/白虎/玄武
    is_shi: bool      # 是否世爻
    is_ying: bool     # 是否应爻
    is_xunkong: bool  # 是否旬空
    fuxin: dict | None = None  # 伏神 {"ganzhi": ..., "liuqin": ...}


class HexagramReadingDetail(HexagramReadingPublic):
    """扩展版响应：含干支批注、六神、纳甲、六亲、世应爻、伏神。"""
    ganzhi_info: GanzhiInfo | None = None
    palace: str | None = None
    palace_element: str | None = None
    shi_yao: int | None = None
    ying_yao: int | None = None
    yao_info: list[YaoInfo] | None = None  # 6 items, index 0 = 第一爻
    # 变卦批注
    changed_palace: str | None = None
    changed_shi_yao: int | None = None
    changed_ying_yao: int | None = None
    changed_yao_info: list[YaoInfo] | None = None


class HexagramReadingsPublic(SQLModel):
    data: list[HexagramReadingDetail]
    count: int
