from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from sqlmodel import select

from app.api.deps import SessionDep, CurrentUser
from app.models import Diagnostic, DiagnosticTool, RepairOrder


class DiagnosticIn(BaseModel):
    order_id: UUID
    tool: DiagnosticTool = DiagnosticTool.OTHER
    ecu_type: Optional[str] = None
    sw_version: Optional[str] = None
    config_version: Optional[str] = None
    dtc_codes: Optional[list[str]] = None
    result: Optional[str] = None
    attachment_key: Optional[str] = None


class DiagnosticOut(BaseModel):
    id: UUID
    order_id: UUID
    tool: DiagnosticTool
    ecu_type: Optional[str]
    sw_version: Optional[str]
    config_version: Optional[str]
    dtc_codes: Optional[list[str]]
    result: Optional[str]
    attachment_key: Optional[str]
    created_at: str  # 返回字符串格式的时间


router = APIRouter()


@router.get("/", response_model=list[DiagnosticOut])
def list_diagnostics(
    session: SessionDep, 
    current_user: CurrentUser,
    order_id: UUID | None = None
):
    """获取诊断记录列表"""
    stmt = select(Diagnostic)
    if order_id:
        stmt = stmt.where(Diagnostic.order_id == order_id)
    
    diagnostics = session.exec(stmt).all()
    
    # 转换为输出格式
    result = []
    for diag in diagnostics:
        result.append(DiagnosticOut(
            id=diag.id,
            order_id=diag.order_id,
            tool=diag.tool,
            ecu_type=diag.ecu_type,
            sw_version=diag.sw_version,
            config_version=diag.config_version,
            dtc_codes=diag.dtc_codes,
            result=diag.result,
            attachment_key=diag.attachment_key,
            created_at=diag.created_at.isoformat()
        ))
    
    return result


@router.post("/", response_model=DiagnosticOut)
def create_diagnostic(
    *,
    data: DiagnosticIn, 
    session: SessionDep,
    current_user: CurrentUser
):
    """创建诊断记录"""
    # 验证维修工单存在
    order = session.get(RepairOrder, data.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 创建诊断记录
    diagnostic = Diagnostic(**data.model_dump())
    session.add(diagnostic)
    session.commit()
    session.refresh(diagnostic)
    
    # 返回格式化结果
    return DiagnosticOut(
        id=diagnostic.id,
        order_id=diagnostic.order_id,
        tool=diagnostic.tool,
        ecu_type=diagnostic.ecu_type,
        sw_version=diagnostic.sw_version,
        config_version=diagnostic.config_version,
        dtc_codes=diagnostic.dtc_codes,
        result=diagnostic.result,
        attachment_key=diagnostic.attachment_key,
        created_at=diagnostic.created_at.isoformat()
    )


@router.get("/{diagnostic_id}", response_model=DiagnosticOut)
def get_diagnostic(
    diagnostic_id: UUID,
    session: SessionDep,
    current_user: CurrentUser
):
    """获取单个诊断记录"""
    diagnostic = session.get(Diagnostic, diagnostic_id)
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    
    return DiagnosticOut(
        id=diagnostic.id,
        order_id=diagnostic.order_id,
        tool=diagnostic.tool,
        ecu_type=diagnostic.ecu_type,
        sw_version=diagnostic.sw_version,
        config_version=diagnostic.config_version,
        dtc_codes=diagnostic.dtc_codes,
        result=diagnostic.result,
        attachment_key=diagnostic.attachment_key,
        created_at=diagnostic.created_at.isoformat()
    )


@router.put("/{diagnostic_id}", response_model=DiagnosticOut)
def update_diagnostic(
    diagnostic_id: UUID,
    data: DiagnosticIn,
    session: SessionDep,
    current_user: CurrentUser
):
    """更新诊断记录"""
    diagnostic = session.get(Diagnostic, diagnostic_id)
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    
    # 更新字段
    update_dict = data.model_dump(exclude_unset=True, exclude={"order_id"})  # 不允许修改order_id
    for field, value in update_dict.items():
        setattr(diagnostic, field, value)
    
    session.add(diagnostic)
    session.commit()
    session.refresh(diagnostic)
    
    return DiagnosticOut(
        id=diagnostic.id,
        order_id=diagnostic.order_id,
        tool=diagnostic.tool,
        ecu_type=diagnostic.ecu_type,
        sw_version=diagnostic.sw_version,
        config_version=diagnostic.config_version,
        dtc_codes=diagnostic.dtc_codes,
        result=diagnostic.result,
        attachment_key=diagnostic.attachment_key,
        created_at=diagnostic.created_at.isoformat()
    )


@router.delete("/{diagnostic_id}")
def delete_diagnostic(
    diagnostic_id: UUID,
    session: SessionDep,
    current_user: CurrentUser
):
    """删除诊断记录"""
    diagnostic = session.get(Diagnostic, diagnostic_id)
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    
    session.delete(diagnostic)
    session.commit()
    
    return {"message": "Diagnostic deleted successfully"}