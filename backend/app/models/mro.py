from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
import enum

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


# —— 枚举 —— #
class RepairStatus(str, enum.Enum):
    NEW = "NEW"
    DIAGNOSING = "DIAGNOSING"
    WAITING_PARTS = "WAITING_PARTS"
    REPAIRED = "REPAIRED"
    SCRAPPED = "SCRAPPED"


class DiagnosticTool(str, enum.Enum):
    NEO = "NEO"
    ECU_TALK = "ECUTALK"
    OTHER = "OTHER"


# —— 表 —— #
class Board(SQLModel, table=True):
    __tablename__ = "boards"
    __table_args__ = (UniqueConstraint("sn", name="uq_boards_sn"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    sn: str = Field(index=True, nullable=False, description="板卡序列号")
    model: Optional[str] = Field(default=None, index=True)
    vendor: Optional[str] = Field(default="Knorr-Bremse", index=True)
    project: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # 关系
    repair_orders: List["RepairOrder"] = Relationship(back_populates="board")


class Fault(SQLModel, table=True):
    __tablename__ = "faults"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True, nullable=False, description="DTC/自定义故障码")
    name: str = Field(nullable=False)
    category: Optional[str] = None
    description: Optional[str] = None


class RepairOrder(SQLModel, table=True):
    __tablename__ = "repair_orders"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    board_id: UUID = Field(foreign_key="boards.id", index=True, nullable=False)
    status: RepairStatus = Field(default=RepairStatus.NEW, index=True)
    fault_id: Optional[int] = Field(default=None, foreign_key="faults.id")
    opened_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    closed_at: Optional[datetime] = None

    # 关系
    board: Optional[Board] = Relationship(back_populates="repair_orders")
    diagnostics: List["Diagnostic"] = Relationship(back_populates="repair_order")
    part_usages: List["PartUsage"] = Relationship(back_populates="repair_order")


class Diagnostic(SQLModel, table=True):
    __tablename__ = "diagnostics"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    order_id: UUID = Field(foreign_key="repair_orders.id", index=True, nullable=False)

    tool: DiagnosticTool = Field(default=DiagnosticTool.OTHER, index=True)
    ecu_type: Optional[str] = Field(default=None, index=True)
    sw_version: Optional[str] = Field(default=None)
    config_version: Optional[str] = Field(default=None)

    # 诊断/测试得到的故障码、EOL 测试记录等，先存 JSON，后续可细化结构
    dtc_codes: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    result: Optional[str] = None  # 例如 "READ_OK" / "EOL_PASS" / "EOL_FAIL"
    attachment_key: Optional[str] = None  # 日志/报告在对象存储里的 key

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # 关系
    repair_order: Optional[RepairOrder] = Relationship(back_populates="diagnostics")


class SparePart(SQLModel, table=True):
    __tablename__ = "spare_parts"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    spec: Optional[str] = None
    stock: int = Field(default=0)

    # 关系
    usages: List["PartUsage"] = Relationship(back_populates="spare_part")


class PartUsage(SQLModel, table=True):
    __tablename__ = "part_usages"

    id: int | None = Field(default=None, primary_key=True)
    order_id: UUID = Field(foreign_key="repair_orders.id", index=True, nullable=False)
    part_id: int = Field(foreign_key="spare_parts.id", index=True, nullable=False)
    qty: int = Field(default=1)

    # 关系
    repair_order: Optional[RepairOrder] = Relationship(back_populates="part_usages")
    spare_part: Optional[SparePart] = Relationship(back_populates="usages")