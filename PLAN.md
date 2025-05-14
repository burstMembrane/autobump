# PLAN.md — autobump

A CLI tool for automatically determining and applying semantic version bumps based on git commit history across multiple project types.

---

## 🎯 Goals

- Analyse git commit history since the latest tag
- Infer the required semantic version bump (major / minor / patch)
- Update the relevant project file (`pyproject.toml`, `Cargo.toml`, `package.json`, etc.)
- Automate tagging and changelog generation
- Support dry-run and interactive modes
- Be extensible to support multiple project types and version formats
- Different language formats "setup.py", "package.json","Cargo.toml" etc

## Blue Sky

- Add a LLM (local or openAI) to analyze commits in order to infer the version?

---

## 🧱 Stack

**Language**: Python 3.10+

**CLI**: `typer`  
**Git parsing**: `GitPython`  
**Version handling**: `packaging.version`, `semver`  
**TOML parsing**: `tomlkit` (preserves formatting)  
**Optional changelog formatting**: Jinja2 or Markdown string templates

---

## 🔌 Optional Integrations

- `commitizen` (via CLI or vendored logic) for commit parsing
- `cz.toml` detection for user preferences
- Changelog generation in standard Conventional Commits format

---

## 📁 Directory Layout

autobump/
├── main.py       # CLI entry point
├── cli.py            # CLI definitions and commands
├── detect.py         # Detects project type and file
├── versioning.py     # Reads and bumps version numbers
├── gitlog.py         # Commit parsing and bump inference
├── update.py         # File updaters (pyproject.toml, Cargo.toml, etc.)
├── changelog.py      # Optional changelog generation
├── config.py         # User configuration and CLI overrides
└── utils.py

---

## 🧠 Version Inference Rules

Based on [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix                 | Bump Type     |
|------------------------|---------------|
| `fix:`                 | patch         |
| `feat:`                | minor         |
| `BREAKING CHANGE` / `!`| major         |
| Other / unknown prefix | ignored       |

In case of mixed commits:

- `major` > `minor` > `patch` (use the most significant one)

---

## 🧪 CLI Examples

```bash
# Dry run: show what would change
autobump bump --dry-run

# Force a version bump
autobump bump --level minor

# Infer bump from commits and update version
autobump bump

# Apply to a specific project type
autobump bump --project py

# Output changelog to stdout
autobump changelog > CHANGELOG.md

# Tag and push
autobump tag --push


⸻

✅ Milestones

M1: MVP (Python-only)
 ✓ Infer bump from git commit messages
 ✓ Read + bump version in pyproject.toml
 ✓ CLI interface (bump, --dry-run)
 ✓ Git tag support
 ✓ Git commit with user confirmation and message override
 ✓ Push tag and commit with fallback for missing upstream
 ✓ Interactive confirmations (tag, commit) with --yes override

M2: Rust support
 • Support Cargo.toml version updates
 • Auto-detect language based on file presence

M3: Changelog
 • Generate changelog from commit history
 • Output as Markdown

M4: Config and Extensibility
 • User config file (.autobump.toml)
 • Per-project overrides
 • Plugin or adapter system

M5: CI integration
 • GitHub Action to run autobump in PRs or merges

⸻

🧩 Open Questions
 • Should changelogs be optional or required?
 • How opinionated should the commit parsing be (hardcoded vs pluggable)?
 • Should we eventually support monorepos (multi-package detection)?

⸻

🧍‍♂️ Author / Maintainer

Liam Power (liamfpower@gmail.com)

⸻

🏁 Status

✅ M1 complete. Actively extending tagging, changelog, and multi-language support.

Let me know if you'd like the initial `autobump.py` scaffold or if you want to go straight to implementing M1.
