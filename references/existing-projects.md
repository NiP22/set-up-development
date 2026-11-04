# Existing projects

The bootstrap script is an all-or-nothing copier for missing or identical files.
Its conflict report is input to an agent-led merge, not a request to replace the
repository's settings. Preview is read-only; apply refuses before writing when
any conflict is present. It is not transactional against concurrent writers:
coordinate access to the target while applying.

For an existing target, read each conflicting file and combine only the relevant
pieces. Keep unrelated content, existing model settings, trust/permission choices,
hooks, and user edits. Do not copy project credentials or change approval policies.

Typical merge points:

- `AGENTS.md`: add missing pointers and useful practices; keep project-specific
  instructions authoritative. Avoid repeating global instructions already loaded.
- `.codex/config.toml`: add absent roles with their relative `config_file` paths.
  Preserve existing roles and model choices. Parse the complete file with
  `tomllib` after editing; do not append duplicate TOML tables.
- `.gitignore`: ignore the local graph and generated Graphify skill; keep the
  intended role configs, engineering-skill sources and relative links trackable.
  Do not remove broad existing ignore rules without reviewing their purpose.
- `.graphifyignore`: retain the project's exclusions and exclude vendored skills
  and generated developer artifacts. Do not import another project's data paths.
- `docs/agents`: adapt references to the target's existing tracker/glossary/ADR
  locations. A new glossary, ADR, or task tree is not needed just to fill a template.
- `.agents/skills`: preserve occupied names; resolve conflicts with the user when
  two different skills genuinely compete. Copy the bundled source and license
  before creating relative symlinks. Symlink targets must remain inside the project.

Do not replace an existing Graphify version or custom generated skill automatically.
Inspect `.graphify_version`; reuse a compatible setup or agree on a migration.
The bundled setup script installs hooks through Graphify's native hook manager and
does not overwrite Git aliases. Review `.gitattributes` and Git config changes.

Independent smoke checks belong in a temporary repository. Check both initial
installation and a second application, with pre-existing content and custom hooks.
Report manual merges separately from the copier's exact-match idempotence.
