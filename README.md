# darija-toolkit

Transliteration, detection and normalization for Moroccan Darija text: a Python package, a FastAPI service and a CLI.

Status: early scaffold, nothing usable yet. The package currently only exposes its version.

## Development setup

Requires Python 3.11 or newer.

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows; on Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

Run the checks:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

## License

MIT, see [LICENSE](LICENSE).
