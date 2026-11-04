# Validation — 2026-11-04

Validated on Linux with Python 3.11+ and Graphify 0.9.79.

- Nine installer unit tests pass: fresh install, dry run, identical repeat,
  conflicts before writes, CLI exit codes, dotfiles/vendor metadata, relative
  links surviving relocation, and symlink target/ancestor rejection.
- Ruff check and format check pass; skill frontmatter validator passes.
- Bundled TOML parses. All 81 vendored files match the source installed snapshot.
- Fresh project: all 27 links resolve inside the project, Graphify installs its
  skill and hooks, and a query resolves an actual document heading.
- Second setup leaves identical bootstrap files alone and does not duplicate hooks.
- Independent existing-project exercise: manual merges preserve original
  AGENTS.md content, an existing Codex role, application scripts and a custom
  post-commit hook. Python test passes; Graphify resolves greet() in app.py.

The installer is a copier, not a configuration merger. Existing-project
adaptation was performed by an agent following SKILL.md. OS write failures are
not rolled back. No model inference or benchmark was run by these checks.
