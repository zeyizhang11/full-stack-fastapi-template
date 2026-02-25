import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, OptionalCurrentUser, SessionDep
from app.liuyao import HEXAGRAMS, cast_hexagram, generate_reading_number
from app.models import (
    HexagramReading,
    HexagramReadingCreate,
    HexagramReadingPublic,
    HexagramReadingsPublic,
    Message,
)

router = APIRouter(prefix="/liuyao", tags=["liuyao"])


@router.post("/cast", response_model=HexagramReadingPublic)
def cast(
    *,
    session: SessionDep,
    current_user: OptionalCurrentUser,
    reading_in: HexagramReadingCreate,
) -> Any:
    """Cast a hexagram using the three-coin method. Login is optional."""
    result = cast_hexagram()
    reading = HexagramReading(
        reading_number=generate_reading_number(),
        question=reading_in.question,
        lines=result["lines"],
        hexagram_number=result["hexagram_number"],
        changed_hexagram_number=result["changed_hexagram_number"],
        user_id=current_user.id if current_user else None,
    )
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading


@router.get("/", response_model=HexagramReadingsPublic)
def read_history(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 10
) -> Any:
    """Get the logged-in user's reading history."""
    statement = (
        select(HexagramReading)
        .where(HexagramReading.user_id == current_user.id)
        .order_by(HexagramReading.created_at.desc())  # type: ignore[attr-defined]
        .offset(skip)
        .limit(limit)
    )
    readings = session.exec(statement).all()
    return HexagramReadingsPublic(data=list(readings), count=len(readings))


@router.get("/hexagrams", response_model=dict)
def get_hexagrams() -> Any:
    """Return the complete hexagram dataset."""
    return HEXAGRAMS


@router.get("/{reading_number}", response_model=HexagramReadingPublic)
def read_reading(
    reading_number: str,
    session: SessionDep,
    current_user: OptionalCurrentUser,
) -> Any:
    """Look up a reading by its LY-YYYYMMDD-XXXX number.
    
    Anonymous readings are public. User readings require the owner to be logged in.
    """
    statement = select(HexagramReading).where(
        HexagramReading.reading_number == reading_number
    )
    reading = session.exec(statement).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    if reading.user_id is not None:
        if current_user is None or current_user.id != reading.user_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    return reading


@router.delete("/{reading_id}", response_model=Message)
def delete_reading(
    reading_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Delete a reading. Only the owner may delete their reading."""
    reading = session.get(HexagramReading, reading_id)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    if reading.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(reading)
    session.commit()
    return Message(message="Reading deleted successfully")
