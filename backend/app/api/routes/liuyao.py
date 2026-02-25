import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

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

# Build an O(1) reverse-lookup dict: hexagram number → hexagram data
_HEXAGRAM_BY_NUMBER: dict[int, dict] = {
    h["number"]: h for h in HEXAGRAMS.values()
}
_FALLBACK_HEXAGRAM = {"name": "?", "english": "?", "judgment": "?"}


def _to_public(reading: HexagramReading) -> HexagramReadingPublic:
    """Convert a DB HexagramReading to the public response model."""
    base_hex_by_num = _HEXAGRAM_BY_NUMBER.get(reading.hexagram_number, _FALLBACK_HEXAGRAM)
    changed_hex_by_num = (
        _HEXAGRAM_BY_NUMBER.get(reading.changed_hexagram_number)
        if reading.changed_hexagram_number
        else None
    )

    lines: list[int] = reading.lines if isinstance(reading.lines, list) else []
    changing_lines: list[int] = []
    for i, line in enumerate(lines):
        if line in (6, 9):
            changing_lines.append(i + 1)

    return HexagramReadingPublic(
        id=reading.id,
        reading_number=reading.reading_number,
        question=reading.question,
        lines=lines,
        hexagram_number=reading.hexagram_number,
        hexagram_name=base_hex_by_num.get("name", "?"),
        hexagram_english=base_hex_by_num.get("english", "?"),
        hexagram_judgment=base_hex_by_num.get("judgment", ""),
        changed_hexagram_number=reading.changed_hexagram_number,
        changed_hexagram_name=(
            changed_hex_by_num.get("name") if changed_hex_by_num else None
        ),
        changing_lines=changing_lines,
        created_at=reading.created_at,
        user_id=reading.user_id,
    )


def _bits_from_lines(lines: list[int]) -> int:
    bits = 0
    for i, line in enumerate(lines):
        if line in (7, 9):
            bits |= 1 << i
    return bits


@router.post("/cast", response_model=HexagramReadingPublic)
def cast_new_hexagram(
    *,
    session: SessionDep,
    current_user: OptionalCurrentUser,
    reading_in: HexagramReadingCreate,
) -> Any:
    """
    Cast a new hexagram reading.  Works for both authenticated and anonymous users.
    """
    result = cast_hexagram()
    hexagram = result["hexagram"]
    changed_hexagram = result["changed_hexagram"]

    reading = HexagramReading(
        reading_number=generate_reading_number(),
        question=reading_in.question,
        lines=result["lines"],
        hexagram_number=hexagram["number"],
        changed_hexagram_number=(
            changed_hexagram["number"] if changed_hexagram else None
        ),
        user_id=current_user.id if current_user else None,
    )
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return _to_public(reading)


@router.get("/", response_model=HexagramReadingsPublic)
def read_my_readings(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """
    Retrieve the current user's hexagram readings (requires login).
    """
    count_stmt = (
        select(func.count())
        .select_from(HexagramReading)
        .where(HexagramReading.user_id == current_user.id)
    )
    count = session.exec(count_stmt).one()
    stmt = (
        select(HexagramReading)
        .where(HexagramReading.user_id == current_user.id)
        .order_by(HexagramReading.created_at.desc())  # type: ignore[attr-defined]
        .offset(skip)
        .limit(limit)
    )
    readings = session.exec(stmt).all()
    return HexagramReadingsPublic(
        data=[_to_public(r) for r in readings], count=count
    )


@router.get("/{reading_number}", response_model=HexagramReadingPublic)
def read_hexagram_by_number(
    session: SessionDep,
    current_user: OptionalCurrentUser,
    reading_number: str,
) -> Any:
    """
    Retrieve a hexagram reading by its reading number.
    Anonymous readings are accessible to anyone who knows the number.
    User-owned readings are accessible to the owner (or admins).
    """
    stmt = select(HexagramReading).where(
        HexagramReading.reading_number == reading_number
    )
    reading = session.exec(stmt).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")

    # If the reading belongs to a user, only that user (or superuser) can view it
    if reading.user_id is not None:
        if current_user is None:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        if not current_user.is_superuser and reading.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return _to_public(reading)


@router.delete("/{reading_id}", response_model=Message)
def delete_reading(
    session: SessionDep,
    current_user: CurrentUser,
    reading_id: uuid.UUID,
) -> Any:
    """
    Delete a hexagram reading (must be the owner or superuser).
    """
    reading = session.get(HexagramReading, reading_id)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    if not current_user.is_superuser and reading.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(reading)
    session.commit()
    return Message(message="Reading deleted successfully")
