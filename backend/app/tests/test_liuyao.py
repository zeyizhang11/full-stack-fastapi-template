"""Unit tests for the Liu Yao divination logic (no database required)."""

from app.liuyao import HEXAGRAMS, cast_hexagram, generate_reading_number


def test_hexagrams_count() -> None:
    assert len(HEXAGRAMS) == 64


def test_hexagram_numbers_complete() -> None:
    numbers = sorted(h["number"] for h in HEXAGRAMS.values())
    assert numbers == list(range(1, 65))


def test_hexagram_required_fields() -> None:
    required = {"number", "name", "pinyin", "english", "judgment"}
    for key, hexagram in HEXAGRAMS.items():
        assert required.issubset(
            hexagram.keys()
        ), f"Hexagram at key {key} is missing fields"


def test_cast_hexagram_structure() -> None:
    result = cast_hexagram()
    assert "lines" in result
    assert "hexagram" in result
    assert "changed_hexagram" in result
    assert "changing_lines" in result
    assert len(result["lines"]) == 6


def test_cast_hexagram_valid_values() -> None:
    for _ in range(20):
        result = cast_hexagram()
        for line in result["lines"]:
            assert line in (6, 7, 8, 9), f"Invalid line value: {line}"
        assert 1 <= result["hexagram"]["number"] <= 64


def test_cast_hexagram_changing_lines() -> None:
    for _ in range(100):
        result = cast_hexagram()
        changing = result["changing_lines"]
        lines = result["lines"]
        for pos in changing:
            assert lines[pos - 1] in (6, 9), f"Line {pos} is not a changing line"


def test_cast_hexagram_changed_hexagram() -> None:
    for _ in range(20):
        result = cast_hexagram()
        if result["changing_lines"]:
            assert result["changed_hexagram"] is not None
            assert 1 <= result["changed_hexagram"]["number"] <= 64
        else:
            assert result["changed_hexagram"] is None


def test_generate_reading_number_format() -> None:
    rn = generate_reading_number()
    parts = rn.split("-")
    assert len(parts) == 3
    assert parts[0] == "LY"
    assert len(parts[1]) == 8  # YYYYMMDD
    assert len(parts[2]) == 4  # 4 chars


def test_generate_reading_numbers_unique() -> None:
    numbers = {generate_reading_number() for _ in range(100)}
    # With 36^4 = 1,679,616 possibilities and only 100 generated, collisions are
    # extremely unlikely
    assert len(numbers) >= 95  # allow for rare collisions in CI
