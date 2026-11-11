from darija_toolkit.detect import Detection, Segment, detect
from darija_toolkit.normalize import Normalization, normalize
from darija_toolkit.transliterate import Candidate, TokenResult, Transliteration, transliterate

__version__ = "0.1.0"

__all__ = [
    "Candidate",
    "Detection",
    "Normalization",
    "Segment",
    "TokenResult",
    "Transliteration",
    "__version__",
    "detect",
    "normalize",
    "transliterate",
]
