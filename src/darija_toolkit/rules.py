"""Rule tables for Arabizi to Arabic-script transliteration.

Everything here is plain data (strings, numbers, tuples, dicts) so the tables can be exported
to JSON with `rules_as_dict` and reused by a port in another language. The logic that decides
which vowel entry applies lives in `transliterate.py`.

An option is `(arabic_text, weight)`. The first option of a list is the default; the others are
alternatives. Weights are hand-picked heuristics, not measured probabilities. An empty string
means "write nothing", which is how short vowels are usually handled in Darija spelling.
"""

from typing import Final

Option = tuple[str, float]
Options = tuple[Option, ...]

# Matched before single letters, longest first.
DIGRAPHS: Final[dict[str, Options]] = {
    "ch": (("ش", 1.0),),
    "sh": (("ش", 1.0),),
    "kh": (("خ", 1.0),),
    "gh": (("غ", 1.0),),
    "th": (("ث", 0.55), ("ته", 0.45)),
    "dh": (("ذ", 0.55), ("ده", 0.45)),
}

LONG_VOWELS: Final[dict[str, str]] = {
    "ou": "و",
    "oo": "و",
    "uu": "و",
    "aa": "ا",
    "ee": "ي",
    "ii": "ي",
}

CONSONANTS: Final[dict[str, Options]] = {
    "b": (("ب", 1.0),),
    "p": (("ب", 1.0),),
    "t": (("ت", 0.85), ("ط", 0.15)),
    "j": (("ج", 1.0),),
    "d": (("د", 0.85), ("ض", 0.15)),
    "r": (("ر", 1.0),),
    "z": (("ز", 0.85), ("ظ", 0.15)),
    "s": (("س", 0.8), ("ص", 0.2)),
    "f": (("ف", 1.0),),
    "v": (("ف", 1.0),),
    "q": (("ق", 0.85), ("ك", 0.15)),
    "k": (("ك", 1.0),),
    "g": (("ڭ", 0.6), ("گ", 0.3), ("غ", 0.1)),
    "l": (("ل", 1.0),),
    "m": (("م", 1.0),),
    "n": (("ن", 1.0),),
    "h": (("ه", 0.7), ("ح", 0.3)),
    "w": (("و", 1.0),),
    "y": (("ي", 1.0),),
    "x": (("كس", 1.0),),
}

# "c" depends on the next letter: soft before e, i, y, hard otherwise.
C_SOFT: Final[Options] = (("س", 0.7), ("ك", 0.3))
C_HARD: Final[Options] = (("ك", 0.7), ("س", 0.3))
C_SOFT_BEFORE: Final[str] = "eiy"

# Chat digits. A digit with no entry here (0, 1, 4) is left as it is.
DIGITS: Final[dict[str, Options]] = {
    "2": (("ء", 0.7), ("أ", 0.3)),
    "3": (("ع", 1.0),),
    "5": (("خ", 1.0),),
    "6": (("ط", 1.0),),
    "7": (("ح", 1.0),),
    "8": (("غ", 1.0),),
    "9": (("ق", 1.0),),
}
DIGIT_HAMZA_INITIAL: Final[Options] = (("أ", 0.7), ("ء", 0.3))

SHORT_VOWELS: Final[str] = "aeiou"
SEMIVOWELS: Final[str] = "yw"

# Vowel handling by position. Which entry applies is decided in transliterate.py.
VOWELS: Final[dict[str, dict[str, Options]]] = {
    "initial": {
        "a": (("ا", 0.7), ("أ", 0.3)),
        "e": (("ا", 0.7), ("أ", 0.3)),
        "i": (("ا", 0.6), ("إ", 0.4)),
        "o": (("و", 1.0),),
        "u": (("و", 1.0),),
    },
    "final": {
        "a": (("ا", 0.75), ("ة", 0.25)),
        "e": (("", 0.7), ("ا", 0.3)),
        "i": (("ي", 0.85), ("", 0.15)),
        "o": (("و", 0.85), ("", 0.15)),
        "u": (("و", 0.85), ("", 0.15)),
    },
    # "a" in an open or final syllable, before y/w, or next to another vowel.
    "mid_a_long": {"a": (("ا", 0.7), ("", 0.3))},
    "mid_a_short": {"a": (("", 0.6), ("ا", 0.4))},
    "mid": {
        "e": (("", 0.8), ("ي", 0.2)),
        "i": (("ي", 0.8), ("", 0.2)),
        "o": (("و", 0.75), ("", 0.25)),
        "u": (("و", 0.75), ("", 0.25)),
    },
    # A vowel written right after an initial hamza digit ("2ana") adds nothing.
    "after_hamza": dict.fromkeys("aeiou", (("", 0.8), ("ا", 0.2))),
}

# Frequent words where the letter-by-letter rules are known to be weak. Keys are written with
# repeated letters collapsed ("hamdullah" is stored as "hamdulah").
LEXICON: Final[dict[str, str]] = {
    "salam": "سلام",
    "slam": "سلام",
    "chal": "شحال",
    "chokran": "شكرا",
    "shukran": "شكرا",
    "ana": "أنا",
    "mrhba": "مرحبا",
    "bslama": "بسلامة",
    "alah": "الله",
    "inchalah": "إن شاء الله",
    "hamdulah": "الحمد لله",
    "hamdulilah": "الحمد لله",
}


def rules_as_dict() -> dict[str, object]:
    """Return every table as JSON-serializable data."""
    return {
        "digraphs": DIGRAPHS,
        "long_vowels": LONG_VOWELS,
        "consonants": CONSONANTS,
        "c_soft": C_SOFT,
        "c_hard": C_HARD,
        "c_soft_before": C_SOFT_BEFORE,
        "digits": DIGITS,
        "digit_hamza_initial": DIGIT_HAMZA_INITIAL,
        "short_vowels": SHORT_VOWELS,
        "semivowels": SEMIVOWELS,
        "vowels": VOWELS,
        "lexicon": LEXICON,
    }
