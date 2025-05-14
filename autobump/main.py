# main.py
import re
from pathlib import Path
from typing import Literal

import semver
import tomlkit
import typer
from git import GitCommandError, Repo
from rich import print


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


def get_commits_since_last_tag() -> list[dict]:
    repo = Repo(".")

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


def infer_bump(commits: list[dict]) -> Literal["major", "minor", "patch"]:
    bump = "patch"
    for c in commits:
        msg = c["message"]
        if "BREAKING CHANGE" in msg or re.match(r"^(feat|fix)!:", msg):
            return "major"
        elif msg.startswith("feat:"):
            bump = "minor"
    return bump


def pretty_print_commits(commits: list[dict]) -> None:
    for commit in commits:
        print(
            f"* [yellow]{commit['short_hash']}[/yellow] {commit['decoration']} {commit['message']}"
        )


def bump_version_from_git(
    project_file: Path, dry_run: bool = False, verbose: bool = False
) -> str:
    doc = tomlkit.parse(project_file.read_text())
    version_str = doc["project"]["version"]
    if verbose:
        typer.secho(f"Current version: {version_str}", fg=typer.colors.YELLOW)
    commits = get_commits_since_last_tag()
    if not commits:
        raise RuntimeError("No new commits found since last tag.")
    if verbose:
        typer.secho(
            f"Found {len(commits)} commits since last tag.", fg=typer.colors.YELLOW
        )
        pretty_print_commits(commits)
    bump = infer_bump(commits)
    new_version = compute_new_version(version_str, bump)

    if dry_run:
        return new_version

    doc["project"]["version"] = new_version
    project_file.write_text(tomlkit.dumps(doc))

    return new_version
