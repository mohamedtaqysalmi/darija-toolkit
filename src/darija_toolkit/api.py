"""Minimal FastAPI app exposing transliterate, detect and normalize."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from darija_toolkit import __version__
from darija_toolkit.detect import detect
from darija_toolkit.normalize import normalize
from darija_toolkit.transliterate import transliterate

app = FastAPI(
    title="darija-toolkit",
    version=__version__,
    description="Transliteration, detection and normalization for Moroccan Darija text.",
)


class TextIn(BaseModel):
    text: str = Field(..., examples=["salam labas 3lik"])


class CandidateOut(BaseModel):
    text: str
    score: float


class TokenOut(BaseModel):
    source: str
    best: CandidateOut
    alternatives: list[CandidateOut]


class TransliterateOut(BaseModel):
    text: str
    tokens: list[TokenOut]


class SegmentOut(BaseModel):
    text: str
    label: str
    score: float


class DetectOut(BaseModel):
    label: str
    segments: list[SegmentOut]


class NormalizeOut(BaseModel):
    text: str
    changes: int


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.post("/transliterate", response_model=TransliterateOut)
def transliterate_endpoint(body: TextIn) -> TransliterateOut:
    result = transliterate(body.text)
    return TransliterateOut(
        text=result.text,
        tokens=[
            TokenOut(
                source=t.source,
                best=CandidateOut(text=t.best.text, score=t.best.score),
                alternatives=[CandidateOut(text=a.text, score=a.score) for a in t.alternatives],
            )
            for t in result.tokens
        ],
    )


@app.post("/detect", response_model=DetectOut)
def detect_endpoint(body: TextIn) -> DetectOut:
    result = detect(body.text)
    return DetectOut(
        label=result.label,
        segments=[SegmentOut(text=s.text, label=s.label, score=s.score) for s in result.segments],
    )


@app.post("/normalize", response_model=NormalizeOut)
def normalize_endpoint(body: TextIn) -> NormalizeOut:
    result = normalize(body.text)
    return NormalizeOut(text=result.text, changes=result.changes)
