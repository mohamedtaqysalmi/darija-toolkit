# Test report — v0.1.0

Local gate run used before opening the release PR. CI on GitHub is the public record after merge.

## Environment

| Item | Value |
| --- | --- |
| Date | 2026-11-11 |
| OS | Windows 10 (local) |
| Python | 3.15.2 (local); CI matrix 3.11 and 3.14 |
| Package version | 0.1.0 |
| Install | `pip install -e ".[dev]"` |

## Commands

```bash
ruff check .
ruff format --check .
mypy
pytest
```

## Results

| Gate | Result |
| --- | --- |
| ruff check | pass |
| ruff format --check | pass |
| mypy (strict) | pass |
| pytest | **148 passed**, **13 xfailed**, 0 failed |
| Coverage (branch) | **98.45%** (fail_under 85) |

### Coverage by module (local)

| Module | Cover |
| --- | --- |
| `__init__.py` | 100% |
| `api.py` | 100% |
| `cli.py` | 96% (`if __name__ == "__main__"` uncovered) |
| `detect.py` | 100% |
| `normalize.py` | 100% |
| `rules.py` | 100% |
| `transliterate.py` | 97% |
| **Total** | **98%** |

## Fixtures

| Suite | Cases | Notes |
| --- | --- | --- |
| `fixtures/transliteration.json` | 63 | 13 marked `known_failure` → xfail |
| `fixtures/detection.json` | 12 | heuristic labels, `reviewed: false` |
| `fixtures/normalization.json` | 15 | idempotence also asserted in tests |

## Smoke (library)

```text
transliterate("salam labas 3lik") → سلام لاباس عليك
detect("bonjour wach") → mixed
normalize("saaaafi!!!") → safi!
```

## Warnings

- Starlette deprecation: prefer `httpx2` with `TestClient` in a later dependency bump (non-blocking).

## Not covered here

- GitHub Pages visual QA (see [QA.md](QA.md))
- Demo GIF
- Native-speaker fixture review
