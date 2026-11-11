# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-11

### Added

- Rule-based Arabizi to Arabic-script transliteration (`darija_toolkit.transliterate`) with ranked alternatives for ambiguous tokens, and rule tables as plain data in `darija_toolkit.rules`.
- Heuristic script/language detection (`darija_toolkit.detect`) with segment labels: `darija_arabizi`, `darija_arabic`, `msa`, `french`, `mixed`.
- Chat-oriented normalizer (`darija_toolkit.normalize`) for elongations, common Arabizi variants, and punctuation/whitespace noise.
- FastAPI app (`darija_toolkit.api`) with `/health`, `/transliterate`, `/detect`, `/normalize`.
- Typer CLI entry point `darija-toolkit` (`transliterate`, `detect`, `normalize`, `version`).
- Draft fixtures: `fixtures/transliteration.json` (63 cases, 13 known failures), `fixtures/detection.json`, `fixtures/normalization.json`.
- Static GitHub Pages playground under `site/` (JS port of the rule tables) and deploy workflow.
- Architecture notes (`docs/architecture.md`), QA checklist (`QA.md`), and local test report (`TEST_REPORT.md`).
- Project scaffold: package layout, tooling, community files, CI (Python 3.11 / 3.14), CodeQL, Dependabot.

### Notes

- Fixtures are drafted and not native-speaker reviewed.
- Detection and transliteration scores are relative heuristic weights, not probabilities.
- Package is not published to PyPI in this release.

[Unreleased]: https://github.com/mohamedtaqysalmi/darija-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mohamedtaqysalmi/darija-toolkit/releases/tag/v0.1.0
