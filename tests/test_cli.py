import pytest
from typer.testing import CliRunner

from darija_toolkit.cli import app, main

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip().count(".") == 2


def test_transliterate() -> None:
    result = runner.invoke(app, ["transliterate", "salam"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "سلام"


def test_transliterate_json() -> None:
    result = runner.invoke(app, ["transliterate", "salam", "--json"])
    assert result.exit_code == 0
    assert '"text"' in result.stdout


def test_transliterate_stdin() -> None:
    result = runner.invoke(app, ["transliterate"], input="salam")
    assert result.exit_code == 0
    assert result.stdout.strip() == "سلام"


def test_detect() -> None:
    result = runner.invoke(app, ["detect", "wach bghiti"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "darija_arabizi"


def test_detect_json() -> None:
    result = runner.invoke(app, ["detect", "wach bghiti", "--json"])
    assert result.exit_code == 0
    assert '"label"' in result.stdout
    assert "darija_arabizi" in result.stdout


def test_normalize() -> None:
    result = runner.invoke(app, ["normalize", "saaaafi"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "safi"


def test_normalize_json() -> None:
    result = runner.invoke(app, ["normalize", "saaaafi", "--json"])
    assert result.exit_code == 0
    assert '"text"' in result.stdout
    assert '"changes"' in result.stdout


def test_main_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_app() -> None:
        calls.append("called")

    monkeypatch.setattr("darija_toolkit.cli.app", fake_app)
    main()
    assert calls == ["called"]
