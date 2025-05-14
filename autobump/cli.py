# cli.py
from pathlib import Path

import typer

from autobump.main import (
    DirtyRepoError,
    NoCommitsError,
    NoCommitsSinceLastTagError,
    bump_version_from_git,
)

app = typer.Typer()


@app.command()
def bump(
    project_file: Path = typer.Option("pyproject.toml", help="Path to pyproject.toml"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show version change without writing"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show verbose output"),
    allow_dirty: bool = typer.Option(
        False, "--allow-dirty", help="Allow uncommitted changes"
    ),
    commit: bool = typer.Option(False, "--commit", "-c", help="Commit the changes"),
    commit_message: str | None = typer.Option(
        None, "--commit-message", "-m", help="Commit message"
    ),
    tag: bool | None = typer.Option(
        None, "--tag", "-t", help="Create a git tag for the new version"
    ),
    push: bool = typer.Option(
        False, "--push", "-p", help="Push the changes to the remote repository"
    ),
    tag_name: str | None = typer.Option(None, "--tag-name", "-n", help="Tag name"),
):
    """
    Bump version based on git commit history.
    """
    try:
        current_version, new_version = bump_version_from_git(
            project_file,
            dry_run=dry_run,
            verbose=verbose,
            allow_dirty=allow_dirty,
            commit=commit,
            commit_message=commit_message,
            tag=tag,
            push=push,
            tag_name=tag_name,
        )
        if dry_run:
            typer.secho(
                f"Dry run. Would bump: {current_version} -> {new_version}",
                fg=typer.colors.YELLOW,
            )
        else:
            typer.secho(
                f"Bumped: {current_version} -> {new_version}", fg=typer.colors.GREEN
            )
    except (NoCommitsError, DirtyRepoError, NoCommitsSinceLastTagError) as e:
        typer.secho(str(e), fg=typer.colors.RED)


if __name__ == "__main__":
    app()
