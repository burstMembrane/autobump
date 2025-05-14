# cli.py
from pathlib import Path

import typer

from autobump.main import NoCommitsError, bump_version_from_git

app = typer.Typer()


@app.command()
def bump(
    project_file: Path = typer.Option("pyproject.toml", help="Path to pyproject.toml"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show version change without writing"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose output"),
):
    """
    Bump version based on git commit history.
    """
    try:
        new_version = bump_version_from_git(
            project_file, dry_run=dry_run, verbose=verbose
        )
        typer.secho(f"New version: {new_version}", fg=typer.colors.GREEN)
    except NoCommitsError:
        typer.secho("No commits found in the repository.", fg=typer.colors.RED)


if __name__ == "__main__":
    app()
