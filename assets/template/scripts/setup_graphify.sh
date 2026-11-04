#!/usr/bin/env bash
# Project-local setup; Graphify itself is a separate developer tool.
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$project_dir"
graphify_requirement="graphifyy==0.9.79"
expected_version="${graphify_requirement#graphifyy==}"

if [[ "$(git rev-parse --show-toplevel)" != "$project_dir" ]]; then
    printf '%s\n' 'Run this script from a project with its own Git root.' >&2
    exit 1
fi
if ! command -v graphify >/dev/null 2>&1; then
    printf 'Install the developer tool: uv tool install "%s"\n' "$graphify_requirement" >&2
    exit 1
fi
if [[ "$(graphify --version)" != "graphify $expected_version" ]]; then
    printf 'Expected Graphify %s. Preserve the existing installation until a version change is agreed.\n' "$expected_version" >&2
    exit 1
fi

for path in .agents .agents/skills .agents/skills/graphify graphify-out; do
    if [[ -L "$path" ]]; then
        printf 'Review the existing symlink before setup: %s\n' "$path" >&2
        exit 1
    fi
done

skill_dir=.agents/skills/graphify
if [[ -e "$skill_dir" ]]; then
    if [[ ! -f "$skill_dir/.graphify_version" ]] || [[ "$(cat "$skill_dir/.graphify_version")" != "$expected_version" ]]; then
        printf 'Existing Graphify skill needs manual review: %s\n' "$skill_dir" >&2
        exit 1
    fi
else
    graphify install --project --platform agents
fi

if [[ -d graphify-out/memory ]]; then
    mkdir -p graphify-out/private-memory
    archive_dir="$(mktemp -d graphify-out/private-memory/archive.XXXXXX)"
    mv -- graphify-out/memory "$archive_dir/memory"
    printf 'Preserved local memory in %s/memory\n' "$archive_dir"
fi

graphify hook install
PYTHONHASHSEED=0 graphify update .
graphify hook status
