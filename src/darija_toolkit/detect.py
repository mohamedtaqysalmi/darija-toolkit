"""Heuristic script/language detection for Darija chat text.

Labels returned per segment:
- darija_arabizi: Latin letters with chat digits or Darija markers
- darija_arabic: Arabic script with Darija-leaning letter choices (ڭ, گ, پ, ڤ) or known words
- msa: Arabic script without those markers
- french: Latin letters matching French word patterns, no chat digits
- mixed: the whole input spans more than one of the above

This is a lightweight chatbot pre-filter, not a trained classifier. Scores are relative
weights inside one segment, not calibrated probabilities.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

Label = str

_ARABIC = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")
# Allow a leading chat digit so tokens like "3lik" / "7it" are scored.
_LATIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9']*")
_CHAT_DIGIT = re.compile(r"[235679]")
_DIGIT_ONLY = re.compile(r"\d+")
_DARIJA_AR_MARKERS = set("ڭگپڤ")
_WHITESPACE_SPLIT = re.compile(r"(\s+)")

# Short lists on purpose. Enough to tip short messages; not a dictionary.
_DARIJA_ARABIZI_CUES = {
    "wach",
    "wash",
    "bghit",
    "bghiti",
    "daba",
    "bzaf",
    "safi",
    "saafi",
    "kayn",
    "kayen",
    "fin",
    "mzyan",
    "mezian",
    "labas",
    "salam",
    "kifach",
    "chhal",
    "shhal",
    "3lik",
    "3ndi",
    "ma3ndich",
    "ghir",
    "ghadi",
    "nji",
    "njiw",
}
_FRENCH_CUES = {
    "bonjour",
    "salut",
    "merci",
    "oui",
    "non",
    "avec",
    "pour",
    "dans",
    "je",
    "tu",
    "il",
    "elle",
    "nous",
    "vous",
    "les",
    "des",
    "une",
    "est",
    "pas",
    "s'il",
    "svp",
    "aujourd",
}
_MSA_CUES = {
    "في",
    "من",
    "إلى",
    "على",
    "هذا",
    "هذه",
    "ذلك",
    "التي",
    "الذي",
    "كان",
    "يكون",
    "أن",
    "إن",
}
_DARIJA_AR_CUES = {
    "واش",
    "بغيت",
    "دابا",
    "بزاف",
    "سافي",
    "كاين",
    "فين",
    "مزيان",
    "لاباس",
    "كيفاش",
    "شحال",
    "غير",
    "غادي",
}


@dataclass(frozen=True)
class Segment:
    text: str
    label: Label
    score: float


@dataclass(frozen=True)
class Detection:
    label: Label
    segments: tuple[Segment, ...]

    def __str__(self) -> str:
        return self.label


_DARIJA_DIGRAPH = re.compile(r"(ch|kh|gh|sh)")


def _score_latin(token: str) -> tuple[Label, float]:
    lower = token.lower()
    has_digit = bool(_CHAT_DIGIT.search(lower))
    darija = 0.2 if has_digit else 0.0
    french = 0.0
    if lower in _DARIJA_ARABIZI_CUES:
        darija += 0.6
    elif _DARIJA_DIGRAPH.search(lower):
        # Digraphs like ch/kh/gh are common in Arabizi; "ou" alone is not (too many French hits).
        darija += 0.45
    if lower in _FRENCH_CUES or lower.endswith(("tion", "ment", "eux", "euse")):
        french += 0.6
    if has_digit:
        return "darija_arabizi", min(0.95, 0.5 + darija)
    if french > darija and french > 0:
        return "french", min(0.9, french)
    if darija > 0:
        return "darija_arabizi", min(0.9, darija)
    # Bare Latin with no cue: lean French for Western European chat, weak score.
    return "french", 0.35


def _score_arabic(token: str) -> tuple[Label, float]:
    if any(ch in _DARIJA_AR_MARKERS for ch in token):
        return "darija_arabic", 0.9
    if token in _DARIJA_AR_CUES:
        return "darija_arabic", 0.85
    if token in _MSA_CUES:
        return "msa", 0.8
    # Default Arabic script without markers: MSA with a soft score.
    return "msa", 0.45


def _classify_token(token: str) -> Segment | None:
    if _ARABIC.fullmatch(token):
        label, score = _score_arabic(token)
        return Segment(token, label, score)
    if _DIGIT_ONLY.fullmatch(token):
        return None
    if _LATIN.fullmatch(token):
        label, score = _score_latin(token)
        return Segment(token, label, score)
    return None


def _merge_adjacent(segments: list[Segment]) -> list[Segment]:
    if not segments:
        return []
    merged: list[Segment] = [segments[0]]
    for seg in segments[1:]:
        prev = merged[-1]
        if seg.label == prev.label:
            merged[-1] = Segment(
                prev.text + " " + seg.text,
                prev.label,
                round((prev.score + seg.score) / 2, 3),
            )
        else:
            merged.append(seg)
    return merged


def _overall(segments: list[Segment]) -> Label:
    if not segments:
        return "mixed"
    labels = {s.label for s in segments}
    if len(labels) == 1:
        return next(iter(labels))
    return "mixed"


def detect(text: str) -> Detection:
    """Split `text` into language/script segments and label each one."""
    if not text or not text.strip():
        return Detection("mixed", ())

    pieces: list[Segment] = []
    for part in _WHITESPACE_SPLIT.split(text.strip()):
        if not part or part.isspace():
            continue
        # Keep punctuation glued words simple: strip outer punctuation for scoring,
        # but keep the original token text in the segment.
        core = part.strip(".,!?;:\"'()[]{}…")
        if not core:
            continue
        classified = _classify_token(core)
        if classified is None:
            continue
        pieces.append(Segment(part, classified.label, classified.score))

    merged = _merge_adjacent(pieces)
    return Detection(_overall(merged), tuple(merged))
