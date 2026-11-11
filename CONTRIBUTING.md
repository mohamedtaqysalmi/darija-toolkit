# Contributing

This is a solo-maintained project. Issues and pull requests are welcome, but replies may take
a few days.

## Setup

You need Python 3.11 or newer.

```bash
git clone https://github.com/mohamedtaqysalmi/darija-toolkit.git
cd darija-toolkit
python -m venv .venv
.venv/Scripts/activate        # Windows; on Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Running the checks

CI runs the same commands on Python 3.11 and 3.14:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

`pytest` reports coverage and fails below 85%.

## Branches and commits

- Branch from `main` with a prefix that matches the change: `feat/`, `fix/`, `docs/`, `chore/`,
  `test/` or `refactor/`, for example `fix/arabizi-digit-handling`.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/),
  for example `fix: handle 9 as qaf in word-initial position`.
- Nothing is pushed straight to `main`; changes go through a pull request.

## Pull requests

- Keep a PR to one change. Add or update tests for behavior you touch.
- Fill in the PR template: what changed, why, and how you tested it.
- CI must be green. I squash-merge, so the PR title becomes the commit message and should follow
  Conventional Commits too.
- Update `CHANGELOG.md` under "Unreleased" for user-visible changes.

## Test data

Use invented examples only. Do not paste real chat logs, names, phone numbers or other
personal data into tests, issues or PRs.
