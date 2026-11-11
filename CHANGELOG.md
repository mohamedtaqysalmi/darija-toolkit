# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-11-11

### Added

- Rule-based Arabizi → Arabic-script transliteration with ranked alternatives (`darija_toolkit.transliterate`, `darija_toolkit.rules`).
- Heuristic script/language detection (`detect`): `darija_arabizi`, `darija_arabic`, `msa`, `french`, `mixed`.
- Chat normalizer (`normalize`): elongations, punctuation runs, common Arabizi spelling variants; idempotent on fixture outputs.
- FastAPI app (`darija_toolkit.api`) with `/health`, `/transliterate`, `/detect`, `/normalize`.
- Typer CLI (`darija-toolkit`) with matching commands and `--json` where useful.
- Fixture suites: transliteration (60+ cases, known failures as xfails), detection, normalization.
- Static GitHub Pages site under `site/` with an in-browser transliteration playground.
- Docs: architecture ADRs, QA checklist, test report; community files and CI already on `main`.

### Notes

- Fixture expected values are drafts pending native-speaker review.
- Transliteration scores are hand-set weights, not calibrated probabilities.
