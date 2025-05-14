# autobump

Automatically bump version numbers for your project based on git commit history and semantic versioning rules.

---

## What is autobump?

**autobump** is a CLI tool that analyzes your git commit history, infers the appropriate semantic version bump (major, minor, patch), and updates your project version in `pyproject.toml` (and, in the future, other project files like `Cargo.toml` or `package.json`). It can also automate git tagging, changelog generation, and pushing changes to your remote repository.

- **Zero config**: Works out of the box for Python projects using `pyproject.toml`.
- **Conventional Commits**: Uses commit messages to infer version bumps.
- **Safe & Interactive**: Supports dry-run, confirmation prompts, and can be run non-interactively.
- **Extensible**: Designed to support multiple languages and project types.

---

## Features

- Analyze git commit history since the latest tag
- Infer semantic version bump (major / minor / patch) using [Conventional Commits](https://www.conventionalcommits.org/)
- Update `pyproject.toml` version (Python projects)
- Optional: commit, tag, and push changes
- Dry-run and interactive confirmation modes
- Rich, colored diffs of version changes
- Extensible for other project types (Rust, JS, etc.)

---

## Installation

```bash
pip install autobump
```

Or clone and install locally:

```bash
git clone https://github.com/burstMembrane/autobump.git
cd autobump
pip install .
```

---

## Usage

### Bump version (auto-infer from commits)

```bash
autobump bump
```

### Dry run (show what would change, but do not write)

```bash
autobump bump --dry-run
```

### Commit, tag, and push

```bash
autobump bump --commit --tag --push
```

### Custom commit message and tag name

```bash
autobump bump --commit-message "chore: release v1.2.0" --tag-name v1.2.0
```

### Allow uncommitted changes

```bash
autobump bump --allow-dirty
```

---

## How does it work?

- **Commit Analysis**: Scans git commits since the last tag. Uses [Conventional Commits](https://www.conventionalcommits.org/) to determine if the bump should be major, minor, or patch.
- **Version Update**: Updates the version in `pyproject.toml` (preserving formatting).
- **Git Integration**: Optionally commits the change, creates a tag, and pushes to your remote.
- **Safety**: Interactive confirmation by default, with `--yes` for automation. Dry-run mode shows all changes and git operations that would be performed.
- **Rich Diffs**: Uses `rich` to show colored diffs of the version change.

---

## Extensibility

- Designed to support other project types (Rust, JS, etc.) via modular file updaters.
- Commit parsing can be extended or replaced (e.g., with `commitizen`).
- Changelog generation and config file support planned.

---

## Example Workflow

```bash
git commit -m "feat: add new API endpoint"
git commit -m "fix: correct typo in docs"
autobump bump --dry-run
# Shows: Would bump 1.2.3 -> 1.3.0, shows diff, and lists git operations

autobump bump --commit --tag --push
# Applies the bump, commits, tags, and pushes
```

---

## Project Structure

- `autobump/main.py` — Core logic for version bumping, commit analysis, and git operations
- `autobump/cli.py` — CLI commands and argument parsing (using Typer)

---

## Development

- Python 3.10+

---

## Rationale

See [PLAN.md](./PLAN.md) for full goals and design. In short:

- Automate the tedious, error-prone process of version bumping and tagging
- Enforce semantic versioning and commit hygiene
- Make it easy to integrate with CI/CD and support multiple languages
- Provide a safe, interactive, and extensible tool for all your versioning needs

---

## 📄 License

MIT

---

## 👤 Author

Liam Power (<info@liampower.dev>)
