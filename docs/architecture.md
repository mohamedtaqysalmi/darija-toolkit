# Architecture

darija-toolkit is a small offline pre-processor for Moroccan Darija chat text: rule tables as data, thin Python APIs (library, CLI, FastAPI), and a static JS playground that loads the same tables.

## Context diagram

```
Arabizi / mixed chat
        │
        ├─► normalize() ──► cleaned Latin / punctuation
        ├─► detect()    ──► segments + label
        └─► transliterate() ──► Arabic script + alternatives
                │
                ├─ Python package / Typer CLI / FastAPI
                └─ site/ JS engine (rules.json)
```

## ADR-001: Rules as data, not a trained model

**Status:** Accepted (v0.1.0)

**Context:** Arabizi → Arabic needs something that installs fast, runs offline, and can be explained in an interview. A fine-tuned model would likely score better on free text.

**Decision:** Encode digraphs, chat digits, vowel options and a tiny lexicon in `rules.py`, export JSON for the playground, and keep scoring as explicit hand weights.

**Consequences:** Explainable and portable; short vowels and edge spellings stay weak. Accuracy is only claimed against fixtures.

## ADR-002: Shared fixtures with honest xfails

**Status:** Accepted (v0.1.0)

**Context:** Silent wrong “passes” hide the hard cases. Draft fixtures will be wrong until a native speaker reviews them.

**Decision:** Keep expected strings in JSON under `fixtures/`. Mark known bad engine outputs `known_failure` and assert them as strict xfails. Detection/normalization cases carry `reviewed: false` until checked by hand.

**Consequences:** CI stays green without lying. Fixture drift between Python and the Pages failure table is visible in public.

## ADR-003: Heuristic detection before ML

**Status:** Accepted (v0.1.0)

**Context:** A chatbot pre-filter needs to know whether a segment is Arabizi, Darija Arabic, MSA or French. Training data and a model ops story are out of scope for 0.1.0.

**Decision:** Tokenize on whitespace, score Latin vs Arabic with small cue lists and script markers (`ڭگپڤ`), merge adjacent same-label tokens, return `mixed` when labels disagree.

**Consequences:** Fast and dependency-free; short or code-switched messages will be wrong often. Scores are relative weights inside one segment.

## ADR-004: Thin FastAPI + Typer over one library

**Status:** Accepted (v0.1.0)

**Context:** Portfolio use wants a callable API and a CLI without duplicating logic.

**Decision:** Implement behavior once in `detect` / `normalize` / `transliterate`. Wrap with FastAPI Pydantic models and Typer commands that optionally emit JSON matching the API shapes.

**Consequences:** One place to fix bugs. No auth, rate limits or persistence in 0.1.0 — local demo only.

## ADR-005: Static Pages playground, not a hosted API

**Status:** Accepted (v0.1.0)

**Context:** A live demo should not require paying for always-on Python hosting for a portfolio site.

**Decision:** Ship a JS port under `site/` that fetches `rules.json` and fixtures client-side. Deploy with GitHub Actions Pages from `/site`.

**Consequences:** Zero runtime cost and works offline after first load. Python and JS can drift if exports are not refreshed when rules change — treat that as a release checklist item.
