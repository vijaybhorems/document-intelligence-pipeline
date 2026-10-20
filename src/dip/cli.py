"""``dip`` command-line entry point. Later phases add subcommands here."""

import typer

from dip import __version__
from dip.config import get_settings

app = typer.Typer(help="Document intelligence pipeline.", no_args_is_help=True)


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command()
def info() -> None:
    """Show the active configuration (secrets masked)."""
    settings = get_settings()
    for key, value in settings.model_dump().items():
        typer.echo(f"{key}: {value}")


if __name__ == "__main__":
    app()
