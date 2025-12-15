# cli.py
from pathlib import Path
from typing import Optional

import typer

from autobump.language_detection import (
    UnsupportedLanguageError,
    detect_language,
    get_config_file_for_language,
    get_supported_languages,
)
from autobump.main import (
    DirtyRepoError,
    NoCommitsError,
    NoCommitsSinceLastTagError,
    bump_version_from_git,
)
from autobump.parsers import get_parser

app = typer.Typer()


@app.command()
def bump(
    config_file: str = typer.Option(
        "", "--config-file", "-f", help="Path to config file (auto-detected if not provided)"
    ),
    language: str = typer.Option(
        "", "--language", "-l", help="Programming language (node/python/rust/go)"
    ),
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
    Auto-detects language and config file if not specified.
    """
    try:
        # Auto-detect or use provided language/config
        if not language and not config_file:
            detected_language, detected_config_file = detect_language()
            if verbose:
                typer.secho(
                    f"Auto-detected {detected_language} project with {detected_config_file.name}",
                    fg=typer.colors.CYAN
                )
            language = detected_language
            config_file_path = detected_config_file
        elif language and not config_file:
            config_file_path = get_config_file_for_language(language)
        elif not language and config_file:
            config_file_path = Path(config_file)
            # Try to infer language from config file name
            if config_file_path.name == "package.json":
                language = "node"
            elif config_file_path.name in ["pyproject.toml", "setup.py"]:
                language = "python"
            elif config_file_path.name == "Cargo.toml":
                language = "rust"
            elif config_file_path.name == "go.mod":
                language = "go"
            else:
                raise UnsupportedLanguageError(
                    f"Could not infer language from {config_file_path.name}. Please specify --language"
                )
        else:
            config_file_path = Path(config_file)
        
        # Create the appropriate parser
        config_parser = get_parser(language, config_file_path)
        
        current_version, new_version = bump_version_from_git(
            config_parser,
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
    except (NoCommitsError, DirtyRepoError, NoCommitsSinceLastTagError, UnsupportedLanguageError, FileNotFoundError, ValueError, KeyError) as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
