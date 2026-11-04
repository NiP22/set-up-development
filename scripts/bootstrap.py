#!/usr/bin/env python3
"""Copy the portable development setup after checking every destination."""

from __future__ import annotations

import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path


class ConflictError(ValueError):
    """The target needs manual merging before the installer can proceed."""


@dataclass(frozen=True)
class Entry:
    path: Path
    kind: str
    source: Path | None = None
    link: str | None = None


def _inventory(template: Path, vendor: Path) -> list[Entry]:
    entries: dict[Path, Entry] = {Path("."): Entry(Path("."), "directory")}

    for source_root, destination_root in (
        (template, Path(".")),
        (vendor, Path("docs/skills/mattpocock")),
    ):
        if source_root.is_symlink() or not source_root.is_dir():
            raise ValueError(f"Expected a source directory: {source_root}")

        for source in [source_root, *sorted(source_root.rglob("*"))]:
            relative = destination_root / source.relative_to(source_root)
            if source.is_symlink():
                raise ValueError(f"Source symlinks are unsupported: {source}")
            if source.is_dir():
                entry = Entry(relative, "directory")
            elif source.is_file():
                entry = Entry(relative, "file", source=source)
            else:
                raise ValueError(f"Expected a regular source file: {source}")

            if relative in entries and entries[relative] != entry:
                raise ValueError(f"Overlapping source assets: {relative}")
            entries[relative] = entry

    for skill in sorted(vendor.iterdir()):
        if skill.is_dir() and (skill / "SKILL.md").is_file():
            relative = Path(".agents/skills") / skill.name
            if relative in entries:
                raise ValueError(f"Overlapping source assets: {relative}")
            link = f"../../docs/skills/mattpocock/{skill.name}"
            entries[relative] = Entry(relative, "link", link=link)

    for relative in list(entries):
        for parent in relative.parents:
            existing = entries.get(parent)
            if existing is not None and existing.kind != "directory":
                raise ValueError(f"Source assets require a directory: {parent}")
            entries.setdefault(parent, Entry(parent, "directory"))

    return sorted(entries.values(), key=lambda entry: (len(entry.path.parts), str(entry.path)))


def _preflight(target: Path, entries: list[Entry]) -> list[Entry]:
    conflicts: set[Path] = set()
    changes: list[Entry] = []

    # Check lexical ancestors before inspecting children. Resolving paths here
    # would hide a symlink and allow writes outside the requested directory.
    for ancestor in reversed([target, *target.parents]):
        if ancestor.is_symlink() or (ancestor.exists() and not ancestor.is_dir()):
            raise ConflictError(f"Unsafe target ancestor (no files written): {ancestor}")

    for entry in entries:
        destination = target / entry.path
        unsafe_parent = False
        parents = [parent for parent in destination.parents if parent.is_relative_to(target)]
        for parent in reversed(parents):
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                conflicts.add(parent)
                unsafe_parent = True
                break
        if unsafe_parent:
            continue

        exists = os.path.lexists(destination)
        if not exists:
            changes.append(entry)
            continue

        if entry.kind == "directory":
            identical = not destination.is_symlink() and destination.is_dir()
        elif entry.kind == "link":
            identical = destination.is_symlink() and os.readlink(destination) == entry.link
        else:
            identical = (
                not destination.is_symlink()
                and destination.is_file()
                and destination.read_bytes() == entry.source.read_bytes()
            )
        if not identical:
            conflicts.add(destination)

    if conflicts:
        paths = "\n".join(f"  {path}" for path in sorted(conflicts))
        raise ConflictError(f"Conflicting paths (no files written):\n{paths}")
    if any(entry.kind == "link" for entry in changes) and not hasattr(os, "symlink"):
        raise ValueError("This platform cannot create the required skill symlinks.")
    return changes


def bootstrap(target: Path, template: Path, vendor: Path, *, apply: bool = False) -> list[str]:
    """Return planned changes; apply them only after a conflict-free preflight."""
    target = Path(os.path.abspath(Path(target).expanduser()))
    entries = _inventory(Path(template), Path(vendor))
    changes = _preflight(target, entries)
    descriptions = []

    for entry in changes:
        destination = target / entry.path
        detail = f" -> {entry.link}" if entry.kind == "link" else ""
        descriptions.append(f"CREATE {entry.kind}: {destination}{detail}")
        if not apply:
            continue

        if entry.kind == "directory":
            destination.mkdir(parents=True, exist_ok=True)
        elif entry.kind == "file":
            shutil.copy2(entry.source, destination)
        else:
            try:
                destination.symlink_to(entry.link, target_is_directory=True)
            except OSError as exc:
                raise OSError(f"Cannot create skill symlink {destination}: {exc}") from exc

    return descriptions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="repository directory to prepare")
    parser.add_argument("--apply", action="store_true", help="write the displayed changes")
    args = parser.parse_args()
    assets = Path(__file__).resolve().parents[1] / "assets"

    try:
        changes = bootstrap(
            args.target, assets / "template", assets / "vendor/mattpocock", apply=args.apply
        )
    except (ValueError, OSError) as exc:
        parser.exit(2, f"{exc}\n")

    print("Apply:" if args.apply else "Dry run (use --apply to write):")
    print("\n".join(changes) if changes else "No changes; existing files and links are identical.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
