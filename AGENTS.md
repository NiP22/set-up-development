# Development of this skill

This repository packages a Codex skill, templates and vendored engineering skills.
Read `SKILL.md` before changing its workflow. Keep installer behavior deterministic
and dependencies limited to Python's standard library. Use Python 3.11 or newer.

Run `python3 -m unittest discover -s tests -v` after installer changes. If Ruff is
available, run `python3 -m ruff check .` and `python3 -m ruff format --check .`.
Review actual fresh installation, a repeated application and conflict handling;
matching generated prose alone does not validate the workflow.

Keep third-party files under `assets/vendor/` unchanged unless explicitly updating
the recorded upstream snapshot. Preserve licenses and provenance. Adaptation to
Codex belongs in the templates and entry skill. Test against temporary directories,
not personal repositories. Notes and reports belong under `docs/`.

Use independent subagents for bounded implementation or behavioral review when
it materially helps; separate ownership of files and inspect the final result.
