# main.py
import re
from pathlib import Path
from typing import Literal

import tomlkit
from git import GitCommandError, Repo
from packaging.version import Version


class NoCommitsError(Exception):
    pass


def get_commits_since_last_tag() -> list[str]:
    repo = Repo(".")

    # Handle case where there are no commits at all
    if not repo.head.is_valid():
        raise NoCommitsError("❌ No commits found in the repository.")

    try:
        latest_tag = repo.git.describe(tags=True, abbrev=0)
        rev_range = f"{latest_tag}..HEAD"
    except GitCommandError:
        # No tags exist yet
        rev_range = "HEAD"

    commits = list(repo.iter_commits(rev_range))
    return [c.message.strip() for c in commits]


def infer_bump(commits: list[str]) -> Literal["major", "minor", "patch"]:
    bump = "patch"
    for msg in commits:
        if "BREAKING CHANGE" in msg or re.match(r"^(feat|fix)!\:", msg):
            return "major"
        elif msg.startswith("feat:"):
            bump = "minor"
    return bump


def compute_new_version(version: str, bump: str) -> str:
    v = Version(version)
    if bump == "major":
        return f"{v.major + 1}.0.0"
    elif bump == "minor":
        return f"{v.major}.{v.minor + 1}.0"
    else:
        return f"{v.major}.{v.minor}.{v.micro + 1}"


def bump_version_from_git(project_file: Path, dry_run: bool = False) -> str:
    doc = tomlkit.parse(project_file.read_text())
    version_str = doc["project"]["version"]

    commits = get_commits_since_last_tag()
    if not commits:
        raise RuntimeError("No new commits found since last tag.")

    bump = infer_bump(commits)
    new_version = compute_new_version(version_str, bump)

    if dry_run:
        return new_version

    doc["project"]["version"] = new_version
    project_file.write_text(tomlkit.dumps(doc))

    return new_version
