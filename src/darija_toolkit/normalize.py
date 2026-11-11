"""Chat-oriented normalizer for Arabizi Darija text.

Goals: collapse elongations, strip noisy punctuation runs, map a few spelling variants,
and leave Arabic script alone. Designed so a second pass does not change the result
(idempotent on the outputs we care about).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ELONG_VOWEL = re.compile(r"([aeiouAEIOU])\1{2,}")
_ELONG_CONS = re.compile(r"([b-df-hj-np-tv-zB-DF-HJ-NP-TV-Z])\1{2,}")
_LAUGH_H = re.compile(r"[hH]{4,}")
_PUNCT_RUN = re.compile(r"([!?.,])\1{1,}")
_SPACE_RUN = re.compile(r"[ \t\u00a0]{2,}")

# Common Arabizi spelling variants seen in Moroccan chat. Keys are already lowercased
# and elongation-collapsed forms.
_VARIANTS: dict[str, str] = {
    "wach": "wach",
    "wash": "wach",
    "chhal": "chhal",
    "shhal": "chhal",
    "chal": "chhal",
    "mzyan": "mzyan",
    "mezian": "mzyan",
    "mezyan": "mzyan",
    "bghit": "bghit",
    "bgheet": "bghit",
    "b9hit": "bghit",
    "saafi": "safi",
    "saaaafi": "safi",
    "safi": "safi",
    "labas": "labas",
    "lbas": "labas",
    "salam": "salam",
    "slam": "salam",
    "slm": "salam",
    "chokran": "chokran",
    "shukran": "chokran",
    "merci": "chokran",
    "inchallah": "inchalah",
    "inshallah": "inchalah",
    "inchalah": "inchalah",
    "hamdulillah": "hamdulah",
    "hamdullah": "hamdulah",
    "hamdulilah": "hamdulah",
    "alhamdulillah": "hamdulah",
}

_TOKEN = re.compile(r"[A-Za-z0-9]+|[^A-Za-z0-9]+")


@dataclass(frozen=True)
class Normalization:
    text: str
    changes: int

    def __str__(self) -> str:
        return self.text


def _collapse_token(token: str) -> str:
    if not token or not token[0].isascii() or not token[0].isalnum():
        return token
    out = _LAUGH_H.sub("hh", token)
    out = _ELONG_VOWEL.sub(r"\1\1", out)
    out = _ELONG_CONS.sub(r"\1", out)
    key = re.sub(r"(.)\1+", r"\1", out.lower()) if out.isalpha() else out.lower()
    # Soft key: keep single doubles (shhal), collapse 3+ consonant runs only.
    soft = re.sub(r"([aeiou])\1+", r"\1\1", out.lower())
    soft = re.sub(r"([^aeiou\d])\1{2,}", r"\1", soft)
    mapped = _VARIANTS.get(soft) or _VARIANTS.get(key)
    if mapped is None:
        return out
    # Preserve rough capitalization of the first letter only.
    if out[:1].isupper():
        return mapped[:1].upper() + mapped[1:]
    return mapped


def normalize(text: str) -> Normalization:
    """Return a cleaned version of `text` and how many replacements were applied."""
    if text == "":
        return Normalization("", 0)

    changes = 0
    parts: list[str] = []
    for piece in _TOKEN.findall(text):
        cleaned = _collapse_token(piece)
        if cleaned != piece:
            changes += 1
        parts.append(cleaned)
    out = "".join(parts)
    squeezed = _PUNCT_RUN.sub(r"\1", out)
    if squeezed != out:
        changes += len(_PUNCT_RUN.findall(out))
        out = squeezed
    spaced = _SPACE_RUN.sub(" ", out)
    if spaced != out:
        changes += 1
        out = spaced
    # Strip leading/trailing spaces and tabs per line without a multiline regex
    # (CodeQL flags alternation + unbounded repeats on user text as ReDoS risk).
    edged = "\n".join(line.strip(" \t") for line in out.split("\n"))
    if edged != out:
        changes += 1
        out = edged
    return Normalization(out, changes)
