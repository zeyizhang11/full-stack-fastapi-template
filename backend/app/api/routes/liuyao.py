import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, OptionalCurrentUser, SessionDep
from app.liuyao import (
    HEXAGRAMS,
    cast_by_manual,
    cast_by_numbers,
    cast_by_solar_time,
    cast_hexagram,
    compute_annotations,
    generate_reading_number,
)
from app.models import (
    CastByManualRequest,
    CastByNumbersRequest,
    CastByTimeRequest,
    HexagramReading,
    HexagramReadingCreate,
    HexagramReadingDetail,
    HexagramReadingsPublic,
    Message,
)

router = APIRouter(prefix="/liuyao", tags=["liuyao"])


def _enrich(reading: HexagramReading, year: int, month: int, day: int, hour: int) -> dict:
    ann = compute_annotations(
        reading.hexagram_number, year, month, day, hour,
        changed_hex_num=reading.changed_hexagram_number,
    )
    gz = ann["ganzhi"]
    d = reading.model_dump()
    d["ganzhi_info"] = {
        "solar": gz["solar"], "year_gz": gz["year_gz"],
        "month_gz": gz["month_gz"], "day_gz": gz["day_gz"],
        "hour_gz": gz["hour_gz"], "xunkong": gz["xunkong"],
    }
    d["palace"]               = ann["palace"]
    d["palace_element"]       = ann["palace_element"]
    d["shi_yao"]              = ann["shi_yao"]
    d["ying_yao"]             = ann["ying_yao"]
    d["yao_info"]             = ann["yao_info"]
    d["changed_palace"]       = ann["changed_palace"]
    d["changed_shi_yao"]      = ann["changed_shi_yao"]
    d["changed_ying_yao"]     = ann["changed_ying_yao"]
    d["changed_yao_info"]     = ann["changed_yao_info"]
    return d


def _save_reading(
    session: SessionDep,
    result: dict,
    cast_method: str,
    question: str | None,
    caster_name: str | None,
    caster_gender: str | None,
    owner_id: uuid.UUID | None,
) -> HexagramReading:
    reading = HexagramReading(
        reading_number=generate_reading_number(),
        cast_method=cast_method,
        question=question,
        caster_name=caster_name,
        caster_gender=caster_gender,
        lines=result["lines"],
        hexagram_number=result["hexagram_number"],
        changed_hexagram_number=result["changed_hexagram_number"],
        owner_id=owner_id,
    )
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading


@router.post("/cast", response_model=HexagramReadingDetail)
def cast(*, session: SessionDep, current_user: OptionalCurrentUser, reading_in: HexagramReadingCreate) -> Any:
    """三铜钱法起卦（随机）。无需登录。"""
    result = cast_hexagram()
    reading = _save_reading(session=session, result=result, cast_method="coin",
        question=reading_in.question, caster_name=reading_in.caster_name,
        caster_gender=reading_in.caster_gender,
        owner_id=current_user.id if current_user else None)
    now = datetime.now(timezone.utc)
    return _enrich(reading, now.year, now.month, now.day, now.hour)


@router.post("/cast/time", response_model=HexagramReadingDetail)
def cast_time(*, session: SessionDep, current_user: OptionalCurrentUser, req: CastByTimeRequest) -> Any:
    """时间起卦：根据公历年月日时自动转化为干支在卦。无需登录。"""
    result = cast_by_solar_time(year=req.year, month=req.month, day=req.day, hour_24=req.hour)
    reading = _save_reading(session=session, result=result, cast_method="time",
        question=req.question, caster_name=req.caster_name, caster_gender=req.caster_gender,
        owner_id=current_user.id if current_user else None)
    return _enrich(reading, req.year, req.month, req.day, req.hour)


@router.post("/cast/numbers", response_model=HexagramReadingDetail)
def cast_numbers(*, session: SessionDep, current_user: OptionalCurrentUser, req: CastByNumbersRequest) -> Any:
    """报数起卦。无需登录。"""
    result = cast_by_numbers(upper_num=req.upper_num, lower_num=req.lower_num, changing_num=req.changing_num)
    reading = _save_reading(session=session, result=result, cast_method="numbers",
        question=req.question, caster_name=req.caster_name, caster_gender=req.caster_gender,
        owner_id=current_user.id if current_user else None)
    now = datetime.now(timezone.utc)
    return _enrich(reading, now.year, now.month, now.day, now.hour)


@router.post("/cast/manual", response_model=HexagramReadingDetail)
def cast_manual(*, session: SessionDep, current_user: OptionalCurrentUser, req: CastByManualRequest) -> Any:
    """手动指定六爻（每爻 6/7/8/9）。无需登录。"""
    try:
        result = cast_by_manual(req.lines)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    reading = _save_reading(session=session, result=result, cast_method="manual",
        question=req.question, caster_name=req.caster_name, caster_gender=req.caster_gender,
        owner_id=current_user.id if current_user else None)
    now = datetime.now(timezone.utc)
    return _enrich(reading, now.year, now.month, now.day, now.hour)


@router.get("/", response_model=HexagramReadingsPublic)
def read_history(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 20) -> Any:
    """获取登录用户的起卦历史。"""
    statement = (
        select(HexagramReading)
        .where(HexagramReading.owner_id == current_user.id)
        .order_by(HexagramReading.created_at.desc())  # type: ignore[attr-defined]
        .offset(skip).limit(limit)
    )
    readings = session.exec(statement).all()
    enriched = []
    for r in readings:
        dt = r.created_at
        enriched.append(_enrich(r, dt.year, dt.month, dt.day, dt.hour))
    return HexagramReadingsPublic(data=enriched, count=len(enriched))


@router.get("/hexagrams", response_model=dict)
def get_hexagrams() -> Any:
    """返回六十四卦完整数据。"""
    return HEXAGRAMS


@router.get("/{reading_number}", response_model=HexagramReadingDetail)
def read_reading(reading_number: str, session: SessionDep, current_user: OptionalCurrentUser) -> Any:
    """根据编号查询卦象。"""
    statement = select(HexagramReading).where(HexagramReading.reading_number == reading_number)
    reading = session.exec(statement).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    if reading.owner_id is not None:
        if current_user is None or current_user.id != reading.owner_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    dt = reading.created_at
    return _enrich(reading, dt.year, dt.month, dt.day, dt.hour)


@router.delete("/{reading_id}", response_model=Message)
def delete_reading(reading_id: uuid.UUID, session: SessionDep, current_user: CurrentUser) -> Any:
    """删除卦象记录。仅本人或超级管理员可删除。"""
    reading = session.get(HexagramReading, reading_id)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    if reading.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(reading)
    session.commit()
    return Message(message="Reading deleted successfully")
