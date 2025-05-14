# main.py
import difflib
import re
from pathlib import Path

import semver
import tomlkit
import typer
from commitizen import defaults
from git import GitCommandError, Repo
from rich import print
from rich.console import Console
from rich.text import Text
from rich.theme import Theme


# Utility message functions
def info(msg: str):
    typer.secho(msg, fg=typer.colors.CYAN)


def warn(msg: str):
    typer.secho(msg, fg=typer.colors.YELLOW)


def error(msg: str):
    typer.secho(msg, fg=typer.colors.RED)


def success(msg: str):
    typer.secho(msg, fg=typer.colors.GREEN)


# Rich diff styles
EQUAL_STYLE = "equal"
DELETE_STYLE = "delete"
INSERT_STYLE = "insert"

custom_theme = Theme(
    {
        "equal": "white",
        "delete": "white on dark_red",
        "insert": "white on dark_green",
    }
)


def rich_diff_texts(before: str, after: str, console: Console = None) -> None:
    if console is None:
        console = Console(theme=custom_theme)
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    diff = list(
        difflib.unified_diff(
            before_lines, after_lines, fromfile="before", tofile="after", lineterm=""
        )
    )
    text = Text()
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            text.append(line + "\n", style=INSERT_STYLE)
        elif line.startswith("-") and not line.startswith("---"):
            text.append(line + "\n", style=DELETE_STYLE)
        else:
            text.append(line + "\n", style=EQUAL_STYLE)
    console.print(text)


def compute_new_version(version: str, bump: str) -> str:
    v = semver.VersionInfo.parse(version)
    if bump == "major":
        return str(v.bump_major())
    elif bump == "minor":
        return str(v.bump_minor())
    else:
        return str(v.bump_patch())


class NoCommitsError(Exception):
    pass


class DirtyRepoError(Exception):
    pass


def get_commits_since_last_tag(allow_dirty: bool = False) -> list[dict]:
    repo = Repo(".")

    if not allow_dirty and repo.is_dirty(untracked_files=True):
        raise DirtyRepoError("There are uncommitted changes in your working directory.")
    if allow_dirty and repo.is_dirty(untracked_files=True):
        warn("There are uncommitted changes in your working directory.")
    # Handle case where there are no commits at all
    if not repo.head.is_valid():
        raise NoCommitsError("No commits found in the repository.")

    try:
        latest_tag = repo.git.describe(tags=True, abbrev=0)
        rev_range = f"{latest_tag}..HEAD"
    except GitCommandError:
        # No tags exist yet
        rev_range = "HEAD"

    commits = list(repo.iter_commits(rev_range))
    head_commit = repo.head.commit.hexsha
    current_branch = None
    try:
        current_branch = repo.active_branch.name
    except Exception:
        pass  # Detached HEAD or no branch
    # Map commit hexsha to branch names
    branch_tips = {}
    for branch in repo.branches:
        branch_tips[branch.commit.hexsha] = branch.name

    result = []
    for c in commits:
        decorations = []
        if c.hexsha == head_commit:
            if current_branch and branch_tips.get(c.hexsha) == current_branch:
                decorations.append(
                    f"[bold cyan]HEAD -> [/bold cyan] [bold green]{current_branch}[/bold green]"
                )
            else:
                decorations.append("[bold cyan]HEAD[/bold cyan]")
        if c.hexsha in branch_tips:
            # Avoid duplicate if already added as HEAD -> branch
            if not (
                current_branch
                and c.hexsha == head_commit
                and branch_tips[c.hexsha] == current_branch
            ):
                decorations.append(branch_tips[c.hexsha])
        decoration_str = f" ({', '.join(decorations)})" if decorations else ""
        result.append(
            {
                "message": c.message.strip(),
                "short_hash": c.hexsha[:7],
                "author": c.author.name,
                "date": c.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "decoration": decoration_str,
            }
        )
    return result


def infer_bump(commits: list[dict]) -> str:
    bump_order = ["patch", "minor", "major"]
    highest_bump = "patch"

    for commit in commits:
        message = commit["message"]
        for pattern, level in defaults.bump_map.items():
            if re.match(pattern, message):
                # Map Commitizen's level to your bump levels
                level = level.lower()
                if bump_order.index(level) > bump_order.index(highest_bump):
                    highest_bump = level
                break  # Stop checking other patterns if a match is found

    return highest_bump


def pretty_print_commits(commits: list[dict]) -> None:
    for commit in commits:
        print(
            f"* [yellow]{commit['short_hash']}[/yellow] {commit['decoration']} {commit['message']}"
        )


def bump_version_from_git(
    project_file: Path,
    allow_dirty: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
    yes: bool = False,
) -> str:
    original_content = project_file.read_text()
    doc = tomlkit.parse(original_content)
    current_version = doc["project"]["version"]
    if verbose:
        typer.secho(f"Current version: {current_version}", fg=typer.colors.YELLOW)
    commits = get_commits_since_last_tag(allow_dirty=allow_dirty)
    if not commits:
        raise RuntimeError("No new commits found since last tag.")
    typer.secho(f"Found {len(commits)} commits since last tag.", fg=typer.colors.YELLOW)
    pretty_print_commits(commits)
    bump = infer_bump(commits)
    new_version = compute_new_version(current_version, bump)

    doc["project"]["version"] = new_version
    updated_content = tomlkit.dumps(doc)

    typer.secho(
        f"These changes will be applied to {project_file}\n", fg=typer.colors.CYAN
    )
    rich_diff_texts(original_content, updated_content)

    if not yes and not dry_run:
        confirm = typer.confirm(
            f"\nDo you want to apply these changes and bump the version to {new_version}?"
        )
        if not confirm:
            typer.secho("Version bump aborted by user.", fg=typer.colors.RED)
            raise typer.Abort()

    if not dry_run:
        project_file.write_text(updated_content)

    return current_version, new_version
