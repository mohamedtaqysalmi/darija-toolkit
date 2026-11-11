import json
from pathlib import Path
from typing import Any

import pytest

from darija_toolkit.normalize import normalize

FIXTURE_FILE = Path(__file__).parent.parent / "fixtures" / "normalization.json"
CASES: list[dict[str, Any]] = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize(
    "case",
    [pytest.param(c, id=c["id"]) for c in CASES],
)
def test_fixture(case: dict[str, Any]) -> None:
    assert normalize(case["input"]).text == case["expected"]


@pytest.mark.parametrize(
    "case",
    [pytest.param(c, id=c["id"]) for c in CASES],
)
def test_idempotent(case: dict[str, Any]) -> None:
    once = normalize(case["input"]).text
    twice = normalize(once).text
    assert once == twice


def test_empty() -> None:
    assert normalize("").text == ""
    assert normalize("").changes == 0


def test_emoji_and_arabic_pass_through() -> None:
    assert normalize("سلام 😀").text == "سلام 😀"


def test_very_long_input() -> None:
    text = "saaaafi!!!! " * 5000
    result = normalize(text)
    assert "safi" in result.text
    assert "!!!!" not in result.text


def test_str_returns_text() -> None:
    assert str(normalize("saaaafi")) == "safi"


def test_capitalized_variant() -> None:
    assert normalize("Wash").text == "Wach"
