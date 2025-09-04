import uuid
from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

# ================================
# 用户和物品模型（保持原有）
# ================================

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)

class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)

class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)

class UserPublic(UserBase):
    id: uuid.UUID

class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)

class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="items")

class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID

class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int

# ================================
# MRO 系统模型
# ================================

class RepairStatus(str, Enum):
    NEW = "NEW"
    DIAGNOSING = "DIAGNOSING"
    WAITING_PARTS = "WAITING_PARTS"
    REPAIRED = "REPAIRED"
    SCRAPPED = "SCRAPPED"

class DiagnosticTool(str, Enum):
    NEO = "NEO"
    ECUTALK = "ECUTALK"
    OTHER = "OTHER"

# Board 模型
class Board(SQLModel, table=True):
    __tablename__ = "boards"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sn: str = Field(unique=True, index=True, description="序列号")
    model: str | None = Field(default=None, description="型号")
    vendor: str | None = Field(default="Knorr-Bremse", description="供应商")
    project: str | None = Field(default=None, description="项目")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    repair_orders: list["RepairOrder"] = Relationship(back_populates="board")

# RepairOrder 模型
class RepairOrder(SQLModel, table=True):
    __tablename__ = "repair_orders"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    board_id: uuid.UUID = Field(foreign_key="boards.id", index=True)
    status: RepairStatus = Field(default=RepairStatus.NEW, index=True)
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: datetime | None = Field(default=None)
    
    # 关系
    board: Board | None = Relationship(back_populates="repair_orders")
    diagnostics: list["Diagnostic"] = Relationship(back_populates="repair_order")

# Diagnostic 模型
class Diagnostic(SQLModel, table=True):
    __tablename__ = "diagnostics"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="repair_orders.id", index=True)
    tool: DiagnosticTool = Field(default=DiagnosticTool.OTHER)
    ecu_type: str | None = Field(default=None)
    sw_version: str | None = Field(default=None)
    config_version: str | None = Field(default=None)
    dtc_codes: list[str] | None = Field(default=None)
    result: str | None = Field(default=None)
    attachment_key: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    repair_order: RepairOrder | None = Relationship(back_populates="diagnostics")

# ================================
# API 兼容模型
# ================================

class BoardCreate(SQLModel):
    sn: str = Field(description="板卡序列号")
    model: str | None = Field(default=None, description="板卡型号")
    vendor: str | None = Field(default="Knorr-Bremse", description="供应商")
    project: str | None = Field(default=None, description="项目")

class BoardUpdate(SQLModel):
    sn: str | None = Field(default=None)
    model: str | None = Field(default=None)
    vendor: str | None = Field(default=None)
    project: str | None = Field(default=None)

class BoardPublic(SQLModel):
    id: uuid.UUID
    sn: str
    model: str | None
    vendor: str | None
    project: str | None
    created_at: datetime
    
    @property
    def board_id(self) -> str:
        return self.sn
    
    @property
    def status(self) -> str:
        return "NORMAL"
    
    @property
    def location(self) -> str:
        return self.project or "未指定"
    
    @property
    def description(self) -> str | None:
        return f"{self.vendor} {self.model}" if self.model else self.vendor
    
    @property
    def updated_at(self) -> datetime:
        return self.created_at

class BoardsPublic(SQLModel):
    data: list[BoardPublic]
    count: int

class RepairRecordCreate(SQLModel):
    board_id: uuid.UUID = Field(description="关联板卡ID")
    fault_description: str = Field(description="故障描述")

class RepairRecordUpdate(SQLModel):
    status: RepairStatus | None = None

class RepairRecordPublic(SQLModel):
    id: uuid.UUID
    board_id: uuid.UUID
    status: RepairStatus
    opened_at: datetime
    closed_at: datetime | None
    board: BoardPublic | None = None
    
    @property
    def fault_description(self) -> str:
        return f"维修工单 - 状态: {self.status}"
    
    @property
    def created_at(self) -> datetime:
        return self.opened_at

class RepairRecordsPublic(SQLModel):
    data: list[RepairRecordPublic]
    count: int

# ================================
# 通用模型
# ================================

class Message(SQLModel):
    message: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: str | None = None

class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)