from typing import Any
from fastapi import APIRouter, HTTPException
from sqlmodel import select, func
from datetime import datetime
import uuid

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Board, BoardCreate, BoardUpdate, BoardPublic, BoardsPublic,
    Message, RepairOrder, RepairStatus
)

router = APIRouter()

@router.get("/", response_model=BoardsPublic)
def read_boards(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """获取板卡列表"""
    count_statement = select(func.count()).select_from(Board)
    count = session.exec(count_statement).one()
    
    statement = select(Board).offset(skip).limit(limit).order_by(Board.created_at.desc())
    boards = session.exec(statement).all()
    
    return BoardsPublic(data=boards, count=count)

@router.get("/stats")
def get_board_stats(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """获取板卡统计信息"""
    total = session.exec(select(func.count(Board.id))).one()
    
    # 根据RepairOrder状态统计
    normal = session.exec(
        select(func.count(Board.id))
        .select_from(Board)
        .outerjoin(RepairOrder)
        .where(RepairOrder.id.is_(None))
    ).one()
    
    new_repairs = session.exec(
        select(func.count(Board.id))
        .select_from(Board)
        .join(RepairOrder)
        .where(RepairOrder.status == RepairStatus.NEW)
    ).one()
    
    diagnosing = session.exec(
        select(func.count(Board.id))
        .select_from(Board)
        .join(RepairOrder)
        .where(RepairOrder.status == RepairStatus.DIAGNOSING)
    ).one()
    
    repaired = session.exec(
        select(func.count(Board.id))
        .select_from(Board)
        .join(RepairOrder)
        .where(RepairOrder.status == RepairStatus.REPAIRED)
    ).one()
    
    scrapped = session.exec(
        select(func.count(Board.id))
        .select_from(Board)
        .join(RepairOrder)
        .where(RepairOrder.status == RepairStatus.SCRAPPED)
    ).one()
    
    return {
        "total": total,
        "normal": normal,
        "faulty": new_repairs,
        "under_repair": diagnosing,
        "repaired": repaired,
        "scrapped": scrapped,
    }

@router.post("/", response_model=BoardPublic)
def create_board(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    board_in: BoardCreate,
) -> Any:
    """创建新板卡"""
    # 检查板卡序列号是否已存在
    existing = session.exec(select(Board).where(Board.sn == board_in.sn)).first()
    if existing:
        raise HTTPException(status_code=400, detail="板卡序列号已存在")
    
    board = Board.model_validate(board_in)
    session.add(board)
    session.commit()
    session.refresh(board)
    return BoardPublic.model_validate(board)

@router.get("/{board_id}", response_model=BoardPublic)
def read_board(
    session: SessionDep,
    current_user: CurrentUser,
    board_id: uuid.UUID,
) -> Any:
    """获取单个板卡信息"""
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return BoardPublic.model_validate(board)

@router.put("/{board_id}", response_model=BoardPublic)
def update_board(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    board_id: uuid.UUID,
    board_in: BoardUpdate,
) -> Any:
    """更新板卡信息"""
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # 如果更新序列号，检查是否重复
    if board_in.sn and board_in.sn != board.sn:
        existing = session.exec(select(Board).where(Board.sn == board_in.sn)).first()
        if existing:
            raise HTTPException(status_code=400, detail="板卡序列号已存在")
    
    update_dict = board_in.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(board, field, value)
    
    session.add(board)
    session.commit()
    session.refresh(board)
    return BoardPublic.model_validate(board)

@router.delete("/{board_id}")
def delete_board(
    session: SessionDep,
    current_user: CurrentUser,
    board_id: uuid.UUID,
) -> Message:
    """删除板卡"""
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    session.delete(board)
    session.commit()
    return Message(message="Board deleted successfully")