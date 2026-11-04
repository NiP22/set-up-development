---
name: set-up-development
description: Prepare a new or existing repository for development with Codex using project instructions, worker and scout roles, bundled engineering skills, local task documentation, and Graphify. Use when asked to bootstrap agent development conventions or transfer this setup to another project.
---

# Set up development

Prepare the target project using the portable resources beside this file. Resolve
all resource paths relative to this skill's directory, never a previous checkout.
The initial templates are in Russian; adapt project-facing guidance to the project's
language and existing conventions. The bundled third-party skills stay unchanged.

## Inspect and choose the smallest setup

1. Identify the target and read its applicable instructions, Git status, build/test
   manifests, existing `.agents/skills`, `.codex`, documentation, and Graphify setup.
   Preserve unrelated edits. An empty directory needs no invented architecture.
2. Reuse existing conventions. The default for a new project is `docs/tasks` for
   local tasks and `docs/agents` for agent guidance; create glossary and ADR files
   only when there is content for them. Existing issue trackers take precedence.
3. Keep project paths, service credentials, experiments, generated graphs, and
   benchmark-specific policies out of the reusable setup. Select real verification
   commands from the target project's manifests rather than importing another
   project's Python environment or test commands.

## Install and adapt

Run the installer first as a read-only preview:

```bash
python3 /path/to/set-up-development/scripts/bootstrap.py /path/to/target
```

It plans files from `assets/template`, bundles all 27 engineering skills from
`assets/vendor/mattpocock`, and creates relative links under `.agents/skills`.
It neither installs packages nor changes Git settings. For a fresh target, apply:

```bash
python3 /path/to/set-up-development/scripts/bootstrap.py /path/to/target --apply
```

An identical repeat is a no-op. Any differing destination or symlink ancestor
stops the entire apply before writes. This is deliberately not a config merger.
For an existing project, inspect the reported conflicts and merge relevant pieces
with ordinary file edits, preserving the existing content. Copy missing resources
and create the relative links directly. Do not delete files to make the installer
accept a project. A later run may still report intentional differences; that is
not a failed manual integration. See [existing projects](references/existing-projects.md).

Review the resulting `AGENTS.md` and `.codex/config.toml` against the actual project.
Keep existing role/model choices; the bundled worker/scout models are an example
from the source setup, not a guarantee of account availability. Check the available
models before enabling them, and adapt or omit model overrides when needed.
For a non-Codex assistant, explain that `.codex` role settings require adaptation.

## Set up Graphify

Use the installed `graphifyy==0.9.79`. If missing, install it with
`uv tool install 'graphifyy==0.9.79'` when package installation is within the request.
If a different version is already installed, preserve it until the user chooses
replacement or a separately managed installation. Do not change the main project's
Python dependencies just to install a developer tool.

In a Git repository run `bash scripts/setup_graphify.sh`. The script checks the
version, installs the project skill if absent, installs project Git hooks and merge
driver, and builds a structural code/Markdown graph without model calls. Existing
user hooks are preserved by Graphify; existing Git aliases are left alone.

For a target without Git, either initialize a local repository when requested or
leave hooks pending. Do not create a remote or publish code as a side effect of
this skill. The default graph is local and ignored; regenerate it from the target.
Semantic enrichment is a separate operation, not part of this bootstrap.

## Verify and hand over

- Check that all skill links resolve inside the target, licenses accompany the
  bundled skills, TOML parses, and no source-machine paths or secrets were copied.
- Review instructions for relevance and conflicting conventions; detect existing
  ignore rules that hide the intended `.codex`, `.agents` links, or `docs` files.
- Check `graphify --version`, `graphify hook status`, graph existence and a query
  using a real symbol or document heading. Distinguish indexing bootstrap docs
  from indexing application code that does not yet exist.
- Inspect the final diff or file inventory. Report what was installed, preserved,
  manually merged, and left pending. Do not call configuration setup a successful
  application run. Repository creation, publishing, and inference require their
  own user-requested scope.

Bundled provenance and licenses: [third-party notices](docs/THIRD_PARTY_NOTICES.md).
