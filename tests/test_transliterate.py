import itertools
import json
import time
from pathlib import Path
from typing import Any

import pytest

from darija_toolkit.rules import LEXICON, rules_as_dict
from darija_toolkit.transliterate import transliterate

FIXTURE_FILE = Path(__file__).parent.parent / "fixtures" / "transliteration.json"
CASES: list[dict[str, Any]] = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))["cases"]


def _param(case: dict[str, Any]) -> Any:
    marks = []
    if case.get("known_failure"):
        marks.append(pytest.mark.xfail(strict=True, reason="rules get this one wrong"))
    return pytest.param(case["input"], case["expected"], id=case["id"], marks=marks)


@pytest.mark.parametrize(("source", "expected"), [_param(c) for c in CASES])
def test_fixture(source: str, expected: str) -> None:
    assert transliterate(source).text == expected


def test_fixture_file_is_well_formed() -> None:
    assert len(CASES) >= 60
    ids = [c["id"] for c in CASES]
    assert len(ids) == len(set(ids))
    assert all(c["reviewed"] is False for c in CASES)
    assert {"greetings", "digits", "ambiguity", "mixed_french", "elongation", "everyday"} <= {
        c["category"] for c in CASES
    }


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("kh", "خ"),
        ("chems", "شمس"),
        ("shkoun", "شكون"),
        ("ghir", "غير"),
        ("3", "3"),
        ("a3", "ا" + "ع"),
        ("7", "7"),
        ("9bl", "قبل"),
        ("5bz", "خبز"),
        ("2", "2"),
        ("cola", "كولا"),
        ("cinema", "سينما"),
        ("chhal", "شحال"),
    ],
)
def test_single_rules(source: str, expected: str) -> None:
    assert transliterate(source).text == expected


def test_empty_string() -> None:
    result = transliterate("")
    assert result.text == ""
    assert result.tokens == ()


def test_whitespace_only_is_preserved() -> None:
    assert transliterate(" \t\n  ").text == " \t\n  "


def test_emoji_and_punctuation_pass_through() -> None:
    assert transliterate("salam 😀!").text == "سلام 😀!"


def test_arabic_input_is_unchanged() -> None:
    source = "سلام لاباس عليك"
    assert transliterate(source).text == source
    assert transliterate(source).tokens == ()


def test_mixed_arabic_and_latin() -> None:
    assert transliterate("سلام daba nji").text == "سلام دابا نجي"


def test_digit_only_tokens_are_kept() -> None:
    assert transliterate("2024 3 7").text == "2024 3 7"


def test_mixed_case() -> None:
    assert transliterate("WACH Bghiti").text == transliterate("wach bghiti").text


def test_long_input_scales_roughly_linearly() -> None:
    unit = "wach bghiti 9ahwa mzyaaaan " * 4
    small = unit * 250
    large = unit * 2500

    start = time.perf_counter()
    transliterate(small)
    t_small = time.perf_counter() - start

    start = time.perf_counter()
    result = transliterate(large)
    t_large = time.perf_counter() - start

    assert result.text.count("واش") == 10000
    assert t_large < max(t_small * 40, 1.0)


def test_one_huge_token_does_not_crash() -> None:
    assert transliterate("a" * 100_000).text != ""
    assert transliterate("b" * 100_000).text == "ب"


def test_alternatives_are_ranked_and_distinct() -> None:
    token = transliterate("kan7ebbek").tokens[0]
    scores = [a.score for a in token.alternatives]
    assert scores == sorted(scores, reverse=True)
    assert token.best.text not in {a.text for a in token.alternatives}
    assert len({a.text for a in token.alternatives}) == len(token.alternatives)
    assert all(a.score <= token.best.score for a in token.alternatives)


def test_max_alternatives_limits_output() -> None:
    assert len(transliterate("kan7ebbek", max_alternatives=1).tokens[0].alternatives) == 1
    assert transliterate("kan7ebbek", max_alternatives=0).tokens[0].alternatives == ()


def test_unambiguous_token_has_no_alternatives() -> None:
    token = transliterate("khouya").tokens[0]
    assert token.alternatives
    assert transliterate("salam").tokens[0].alternatives == ()


def test_lexicon_entries_use_collapsed_keys() -> None:
    for key in LEXICON:
        assert all(a != b for a, b in itertools.pairwise(key)), key


def test_rules_export_is_json_serializable() -> None:
    data = json.loads(json.dumps(rules_as_dict(), ensure_ascii=False))
    assert data["digits"]["3"][0][0] == "ع"
    assert "ch" in data["digraphs"]


def test_str_of_result_is_text() -> None:
    assert str(transliterate("daba")) == "دابا"
