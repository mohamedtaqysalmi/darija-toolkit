# Test report — v0.1.0

Local run on Windows before the v0.1.0 release PR.

| Field | Value |
|-------|--------|
| Date | 2026-11-11 |
| Host | Windows 10 (`win32`) |
| Interpreter | CPython 3.15.2 (local); CI matrix is 3.11 and 3.14 |
| Command | `pytest --cov-fail-under=85` |
| Result | **148 passed**, **13 xfailed**, 1 warning |
| Coverage | **98.45%** statements/branches (fail_under 85%) |

## Coverage by module

| Module | Cover |
|--------|-------|
| `__init__.py` | 100% |
| `api.py` | 100% |
| `cli.py` | 96% |
| `detect.py` | 100% |
| `normalize.py` | 100% |
| `rules.py` | 100% |
| `transliterate.py` | 97% |
| **TOTAL** | **98%** |

## Fixture inventory

| File | Cases | Notes |
|------|-------|--------|
| `fixtures/transliteration.json` | 63 | 13 marked `known_failure` → strict xfail |
| `fixtures/detection.json` | 12 | draft labels, `reviewed: false` |
| `fixtures/normalization.json` | 15 | draft expected strings |

## Xfails

The 13 xfails are intentional transliteration misses kept in the suite so regressions on hard cases stay visible. They are not counted as passes. See the `known_failure` entries in `fixtures/transliteration.json` and the Known failures table on the playground.

## Warnings

`StarletteDeprecationWarning` from FastAPI `TestClient` / httpx on this environment. Does not fail the suite; track upstream when upgrading FastAPI/Starlette.

## CI expectation

GitHub Actions runs the same lint, type-check, test, and build steps on Ubuntu for Python 3.11 and 3.14. A green `main` CI run is the release gate alongside this local report.
