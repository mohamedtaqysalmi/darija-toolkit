import re
from dataclasses import dataclass
from functools import lru_cache

from darija_toolkit import rules

_TOKEN = re.compile(r"[A-Za-z0-9]+")
_REPEAT = re.compile(r"(.)\1+")
_ELONGATION = re.compile(r"(.)\1{2,}")

_VOWEL = "V"
_LONG = "L"
_CONSONANT = "C"
_OTHER = "X"


@dataclass(frozen=True)
class Candidate:
    text: str
    score: float


@dataclass(frozen=True)
class TokenResult:
    source: str
    best: Candidate
    alternatives: tuple[Candidate, ...]


@dataclass(frozen=True)
class Transliteration:
    text: str
    tokens: tuple[TokenResult, ...]

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class _Unit:
    text: str
    kind: str
    options: rules.Options


def _collapse_elongation(token: str) -> str:
    def shrink(m: re.Match[str]) -> str:
        ch = m.group(1)
        if ch in rules.SHORT_VOWELS:
            return ch * 2
        if ch == "h":
            return "hhh"
        return ch

    return _ELONGATION.sub(shrink, token)


def _segment(token: str) -> list[_Unit]:
    units: list[_Unit] = []
    i = 0
    while i < len(token):
        pair = token[i : i + 2]
        ch = token[i]
        if pair in rules.LONG_VOWELS:
            units.append(_Unit(pair, _LONG, ((rules.LONG_VOWELS[pair], 1.0),)))
            i += 2
        elif pair in rules.DIGRAPHS:
            units.append(_Unit(pair, _CONSONANT, rules.DIGRAPHS[pair]))
            i += 2
        elif ch in rules.SHORT_VOWELS:
            units.append(_Unit(ch, _VOWEL, ()))
            i += 1
        elif ch == "c":
            soft = token[i + 1 : i + 2] != "" and token[i + 1] in rules.C_SOFT_BEFORE
            units.append(_Unit(ch, _CONSONANT, rules.C_SOFT if soft else rules.C_HARD))
            i += 1
        elif ch in rules.CONSONANTS:
            units.append(_Unit(ch, _CONSONANT, rules.CONSONANTS[ch]))
            i += 1
        elif ch in rules.DIGITS:
            options = rules.DIGITS[ch]
            if ch == "2" and not units:
                options = rules.DIGIT_HAMZA_INITIAL
            units.append(_Unit(ch, _CONSONANT, options))
            i += 1
        else:
            units.append(_Unit(ch, _OTHER, ((ch, 1.0),)))
            i += 1
    return units


def _is_vowelish(unit: _Unit) -> bool:
    return unit.kind in (_VOWEL, _LONG)


def _a_is_long(units: list[_Unit], k: int) -> bool:
    if k + 1 >= len(units):
        return True
    nxt = units[k + 1]
    if _is_vowelish(nxt) or nxt.text in rules.SEMIVOWELS:
        return True
    if k + 2 == len(units):
        return True
    return _is_vowelish(units[k + 2])


def _vowel_options(units: list[_Unit], k: int) -> rules.Options:
    letter = units[k].text
    last = k == len(units) - 1
    if k == 0:
        return rules.VOWELS["initial"][letter]
    if k == 1 and units[0].text == "2":
        return rules.VOWELS["after_hamza"][letter]
    if last:
        return rules.VOWELS["final"][letter]
    if letter == "a":
        key = "mid_a_long" if _a_is_long(units, k) else "mid_a_short"
        return rules.VOWELS[key]["a"]
    return rules.VOWELS["mid"][letter]


def _slots(token: str) -> list[rules.Options]:
    units = _segment(token)
    slots: list[rules.Options] = []
    for k, unit in enumerate(units):
        slots.append(_vowel_options(units, k) if unit.kind == _VOWEL else unit.options)
    return slots


def _build(
    slots: list[rules.Options], max_alternatives: int
) -> tuple[Candidate, tuple[Candidate, ...]]:
    best_text = "".join(options[0][0] for options in slots)
    best_score = 1.0
    for options in slots:
        best_score *= options[0][1]

    found: dict[str, float] = {}
    for i, options in enumerate(slots):
        for text, weight in options[1:]:
            variant = "".join(o[0][0] for o in slots[:i]) + text
            variant += "".join(o[0][0] for o in slots[i + 1 :])
            score = best_score / options[0][1] * weight
            if variant != best_text and score > found.get(variant, 0.0):
                found[variant] = score

    ranked = sorted(found.items(), key=lambda kv: (-kv[1], kv[0]))[:max_alternatives]
    alternatives = tuple(Candidate(t, round(s, 3)) for t, s in ranked)
    return Candidate(best_text, round(best_score, 3)), alternatives


@lru_cache(maxsize=8192)
def _convert_token(token: str, max_alternatives: int) -> TokenResult | None:
    if token.isdigit():
        return None
    lowered = token.lower()
    lexicon_hit = rules.LEXICON.get(_REPEAT.sub(r"\1", lowered))
    if lexicon_hit is not None:
        return TokenResult(token, Candidate(lexicon_hit, 1.0), ())
    normalized = _collapse_elongation(lowered)
    normalized = re.sub(r"([a-z])\1", _undouble, normalized)
    best, alternatives = _build(_slots(normalized), max_alternatives)
    return TokenResult(token, best, alternatives)


def _undouble(m: re.Match[str]) -> str:
    ch = m.group(1)
    # Vowel pairs are long vowels ("aa", "ee", "ii", "oo", "uu"); "h" runs are laughter.
    if ch in rules.SHORT_VOWELS or ch == "h":
        return m.group(0)
    return ch


def transliterate(text: str, *, max_alternatives: int = 3) -> Transliteration:
    """Convert Latin-script (Arabizi) Darija in `text` to Arabic script.

    Only runs of ASCII letters and digits are converted. Whitespace, punctuation, emoji, text
    already in Arabic script and tokens that are only digits are returned unchanged. Each
    converted token carries its best output plus up to `max_alternatives` alternatives.
    """
    results: list[TokenResult] = []

    def replace(m: re.Match[str]) -> str:
        result = _convert_token(m.group(0), max_alternatives)
        if result is None:
            return m.group(0)
        results.append(result)
        return result.best.text

    converted = _TOKEN.sub(replace, text)
    return Transliteration(converted, tuple(results))
