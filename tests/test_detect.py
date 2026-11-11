import json
from pathlib import Path
from typing import Any

import pytest

from darija_toolkit.detect import detect

FIXTURE_FILE = Path(__file__).parent.parent / "fixtures" / "detection.json"
CASES: list[dict[str, Any]] = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize(
    "case",
    [pytest.param(c, id=c["id"]) for c in CASES],
)
def test_fixture(case: dict[str, Any]) -> None:
    result = detect(case["input"])
    assert result.label == case["expected_label"]
    if "expected_segments" in case:
        assert [s.label for s in result.segments] == case["expected_segments"]


def test_empty_and_whitespace() -> None:
    assert detect("").label == "mixed"
    assert detect("   ").segments == ()


def test_emoji_alone_yields_mixed_with_no_segments() -> None:
    assert detect("😀!!").label == "mixed"
    assert detect("😀!!").segments == ()


def test_long_input_does_not_crash() -> None:
    text = ("wach bghiti " * 2000) + ("bonjour merci " * 500)
    result = detect(text)
    assert result.segments
    assert result.label in {"mixed", "darija_arabizi", "french"}


def test_darija_arabic_marker_letter() -> None:
    result = detect("ڭال")
    assert result.label == "darija_arabic"
    assert result.segments[0].score >= 0.9


def test_digit_only_token_skipped() -> None:
    result = detect("wach 2024 bghit")
    assert result.label == "darija_arabizi"
    assert all(s.text != "2024" for s in result.segments)


def test_str_returns_label() -> None:
    assert str(detect("bonjour")) == "french"


def test_punctuation_only_token_skipped() -> None:
    result = detect("...")
    assert result.label == "mixed"
    assert result.segments == ()
