from typing import Any
from fastapi import APIRouter, HTTPException
from sqlmodel import select, func
from datetime import datetime
import uuid

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    RepairOrder, RepairRecordCreate, RepairRecordUpdate, 
    RepairRecordPublic, RepairRecordsPublic, Message, Board,
    RepairStatus
)

router = APIRouter()

@router.get("/", response_model=RepairRecordsPublic)
def read_repair_records(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """获取维修记录列表"""
    count_statement = select(func.count()).select_from(RepairOrder)
    count = session.exec(count_statement).one()
    
    statement = (
        select(RepairOrder)
        .offset(skip)
        .limit(limit)
        .order_by(RepairOrder.opened_at.desc())
    )
    records = session.exec(statement).all()
    
    # 转换为输出格式
    data = []
    for record in records:
        board = session.get(Board, record.board_id) if record.board_id else None
        data.append(RepairRecordPublic(
            id=record.id,
            board_id=record.board_id,
            status=record.status,
            opened_at=record.opened_at,
            closed_at=record.closed_at,
            board=board
        ))
    
    return RepairRecordsPublic(data=data, count=count)

@router.post("/", response_model=RepairRecordPublic)
def create_repair_record(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    record_in: RepairRecordCreate,
) -> Any:
    """创建维修记录"""
    # 验证板卡存在
    board = session.get(Board, record_in.board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    repair_order = RepairOrder(
        board_id=record_in.board_id,
        status=RepairStatus.NEW
    )
    session.add(repair_order)
    session.commit()
    session.refresh(repair_order)
    
    return RepairRecordPublic(
        id=repair_order.id,
        board_id=repair_order.board_id,
        status=repair_order.status,
        opened_at=repair_order.opened_at,
        closed_at=repair_order.closed_at,
        board=board
    )

@router.get("/{record_id}", response_model=RepairRecordPublic)
def read_repair_record(
    session: SessionDep,
    current_user: CurrentUser,
    record_id: uuid.UUID,
) -> Any:
    """获取单个维修记录"""
    record = session.get(RepairOrder, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Repair record not found")
    
    board = session.get(Board, record.board_id) if record.board_id else None
    
    return RepairRecordPublic(
        id=record.id,
        board_id=record.board_id,
        status=record.status,
        opened_at=record.opened_at,
        closed_at=record.closed_at,
        board=board
    )

@router.put("/{record_id}", response_model=RepairRecordPublic)
def update_repair_record(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    record_id: uuid.UUID,
    record_in: RepairRecordUpdate,
) -> Any:
    """更新维修记录"""
    record = session.get(RepairOrder, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Repair record not found")
    
    update_dict = record_in.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if field == "status" and value:
            setattr(record, field, value)
            if value in [RepairStatus.REPAIRED, RepairStatus.SCRAPPED]:
                record.closed_at = datetime.utcnow()
    
    session.add(record)
    session.commit()
    session.refresh(record)
    
    board = session.get(Board, record.board_id) if record.board_id else None
    
    return RepairRecordPublic(
        id=record.id,
        board_id=record.board_id,
        status=record.status,
        opened_at=record.opened_at,
        closed_at=record.closed_at,
        board=board
    )

@router.delete("/{record_id}")
def delete_repair_record(
    session: SessionDep,
    current_user: CurrentUser,
    record_id: uuid.UUID,
) -> Message:
    """删除维修记录"""
    record = session.get(RepairOrder, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Repair record not found")
    session.delete(record)
    session.commit()
    return Message(message="Repair record deleted successfully")