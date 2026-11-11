# darija-toolkit

Transliteration, detection and normalization for Moroccan Darija text: a Python package, a FastAPI service and a CLI.

Status: early. Only Arabizi to Arabic-script transliteration exists so far; detection, normalization, the API and the CLI are not built yet.

## Usage

```python
from darija_toolkit import transliterate

result = transliterate("salam labas 3lik")
print(result.text)  # سلام لاباس عليك

# Ambiguous tokens come with ranked alternatives and heuristic scores.
token = transliterate("kan7ebbek").tokens[0]
print(token.best)  # Candidate(text='كنحبك', score=0.384)
print(token.alternatives)  # next-best spellings, best first
```

The transliteration is rule-based: digraphs first (`ch`, `kh`, `gh`, `ou`), chat digits (`2 3 5 6 7 8 9`), elongation collapsing (`mzyaaaan`), and a small word list for frequent words the letter rules handle badly. Short vowels are guessed, so many words come out with a plausible but not the usual spelling. Scores are hand-set weights, not probabilities, and I have not measured accuracy.

The test fixtures in `fixtures/transliteration.json` are drafted examples that are still awaiting native-speaker review. Cases the rules currently get wrong are kept in the file and marked `known_failure`.

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
