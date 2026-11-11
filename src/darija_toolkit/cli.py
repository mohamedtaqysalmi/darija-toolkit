"""Typer CLI for local use without starting the API."""

from __future__ import annotations

import json

import typer

from darija_toolkit import __version__
from darija_toolkit.detect import detect
from darija_toolkit.normalize import normalize
from darija_toolkit.transliterate import transliterate

app = typer.Typer(
    name="darija-toolkit",
    help="Transliteration, detection and normalization for Moroccan Darija text.",
    no_args_is_help=True,
)


def _read_text(text: str | None) -> str:
    if text is not None:
        return text
    return typer.get_text_stream("stdin").read()


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command("transliterate")
def transliterate_cmd(
    text: str | None = typer.Argument(None, help="Arabizi input; stdin if omitted"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON instead of plain text"),
) -> None:
    """Convert Arabizi to Arabic script."""
    result = transliterate(_read_text(text))
    if json_out:
        payload = {
            "text": result.text,
            "tokens": [
                {
                    "source": t.source,
                    "best": {"text": t.best.text, "score": t.best.score},
                    "alternatives": [{"text": a.text, "score": a.score} for a in t.alternatives],
                }
                for t in result.tokens
            ],
        }
        typer.echo(json.dumps(payload, ensure_ascii=False))
    else:
        typer.echo(result.text)


@app.command("detect")
def detect_cmd(
    text: str | None = typer.Argument(None, help="Input text; stdin if omitted"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON instead of a label"),
) -> None:
    """Label script/language segments."""
    result = detect(_read_text(text))
    if json_out:
        payload = {
            "label": result.label,
            "segments": [
                {"text": s.text, "label": s.label, "score": s.score} for s in result.segments
            ],
        }
        typer.echo(json.dumps(payload, ensure_ascii=False))
    else:
        typer.echo(result.label)


@app.command("normalize")
def normalize_cmd(
    text: str | None = typer.Argument(None, help="Input text; stdin if omitted"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON instead of plain text"),
) -> None:
    """Collapse elongations and common spelling noise."""
    result = normalize(_read_text(text))
    if json_out:
        typer.echo(json.dumps({"text": result.text, "changes": result.changes}))
    else:
        typer.echo(result.text)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
