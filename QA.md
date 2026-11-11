# QA notes (v0.1.0)

Manual and automated checks before tagging. Automated results live in [TEST_REPORT.md](TEST_REPORT.md).

## Scope

In scope: Arabizi transliteration, heuristic detect, chat normalize, FastAPI, CLI, static Pages playground, CI.

Out of scope for this tag: PyPI publish, auth on the API, native-speaker fixture review, demo GIF recording.

## Automated gate (must be green)

| Check | Command / place |
| --- | --- |
| Lint | `ruff check .` |
| Format | `ruff format --check .` |
| Types | `mypy` |
| Tests + coverage ≥ 85% | `pytest` |
| Wheel build | `python -m build` (CI) |
| CI matrix | Python 3.11 and 3.14 on `ubuntu-latest` |

## Manual checklist (human)

- [ ] Open https://mohamedtaqysalmi.github.io/darija-toolkit/ after Pages deploy
- [ ] Playground: type `salam labas 3lik` → Arabic script appears RTL
- [ ] Sample chips update input and output
- [ ] Known-failures table loads and shows engine vs expected
- [ ] Copy-commands button works in a Chromium browser
- [ ] Dark / light OS theme: text stays readable on hero and panels
- [ ] Mobile width (~375px): hero brand and playground usable, no horizontal scroll
- [ ] `darija-toolkit transliterate "salam"` and `uvicorn darija_toolkit.api:app` against `/health`
- [ ] Record a short demo GIF for the README (not in this tag yet)

## Honesty checks

- README and site say fixtures are unreviewed drafts
- Scores described as hand weights, not probabilities
- Known failures kept as xfails, not deleted

## Sign-off

Automated gate: see TEST_REPORT.md for the local run used at tag time. CI on `main` after squash-merge is the public record.
