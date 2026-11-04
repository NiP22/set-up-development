"""Filesystem checks for the bootstrap installer, using synthetic assets only."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/bootstrap.py"
SPEC = importlib.util.spec_from_file_location("development_bootstrap", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
bootstrap = MODULE.bootstrap
ConflictError = MODULE.ConflictError


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.template = self.root / "source/assets/template"
        self.vendor = self.root / "source/assets/vendor/mattpocock"
        self.target = self.root / "target"
        self.write(self.template / "AGENTS.md", "Generic instructions\n")
        self.write(self.template / ".codex/config.toml", "[agents]\n")
        self.write(self.template / ".gitignore", "local-cache/\n")
        self.write(self.vendor / "research/SKILL.md", "Research instructions\n")
        self.write(self.vendor / "research/reference.md", "Reference\n")
        self.write(self.vendor / "LICENSE", "Fixture license\n")
        self.write(self.vendor / "installation.json", "{}\n")

    @staticmethod
    def write(path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def install(self, *, apply: bool = True):
        return bootstrap(self.target, self.template, self.vendor, apply=apply)

    def snapshot(self, root: Path):
        result = {}
        for path in [root, *sorted(root.rglob("*"))]:
            if path.is_symlink():
                value = ("link", os.readlink(path))
            elif path.is_file():
                value = ("file", path.read_bytes())
            else:
                value = ("directory",)
            result[str(path.relative_to(root))] = (value, path.lstat().st_mtime_ns)
        return result

    def test_dry_run_does_not_create_target(self):
        changes = self.install(apply=False)
        self.assertTrue(changes)
        self.assertFalse(self.target.exists())
        self.assertTrue(any("CREATE link:" in line for line in changes))

    def test_blank_install_retains_dotfiles_and_vendor(self):
        self.install()
        self.assertEqual((self.target / ".codex/config.toml").read_text(), "[agents]\n")
        self.assertEqual((self.target / ".gitignore").read_text(), "local-cache/\n")
        self.assertEqual(
            (self.target / "docs/skills/mattpocock/LICENSE").read_text(), "Fixture license\n"
        )
        self.assertTrue((self.target / "docs/skills/mattpocock/installation.json").is_file())

    def test_identical_repeat_performs_no_writes(self):
        self.install()
        before = self.snapshot(self.target)
        with (
            patch.object(MODULE.shutil, "copy2", side_effect=AssertionError("unexpected copy")),
            patch.object(Path, "mkdir", side_effect=AssertionError("unexpected mkdir")),
            patch.object(Path, "symlink_to", side_effect=AssertionError("unexpected link")),
        ):
            self.assertEqual(self.install(), [])
        self.assertEqual(self.snapshot(self.target), before)

    def test_conflict_prevents_all_writes(self):
        self.write(self.target / "AGENTS.md", "Existing user instructions\n")
        before = self.snapshot(self.target)
        with self.assertRaisesRegex(ConflictError, "AGENTS.md"):
            self.install()
        self.assertEqual(self.snapshot(self.target), before)
        self.assertFalse((self.target / ".codex").exists())

    def test_different_existing_skill_link_is_conflict(self):
        link = self.target / ".agents/skills/research"
        link.parent.mkdir(parents=True)
        link.symlink_to("missing-location")
        before = self.snapshot(self.target)
        with self.assertRaisesRegex(ConflictError, "research"):
            self.install()
        self.assertEqual(self.snapshot(self.target), before)

    def test_symlink_directory_cannot_redirect_install_outside_target(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.target.mkdir()
        (self.target / "docs").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ConflictError, "docs"):
            self.install()
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_symlink_ancestor_of_target_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(outside, target_is_directory=True)
        self.target = alias / "new-repo"
        with self.assertRaisesRegex(ConflictError, "Unsafe target ancestor"):
            self.install()
        self.assertEqual(list(outside.iterdir()), [])

    def test_links_use_copied_vendor_after_source_is_moved(self):
        self.install()
        link = self.target / ".agents/skills/research"
        self.assertFalse(Path(os.readlink(link)).is_absolute())
        self.assertEqual(os.readlink(link), "../../docs/skills/mattpocock/research")
        self.template.parents[1].rename(self.root / "source-moved")
        self.assertEqual((link / "SKILL.md").read_text(), "Research instructions\n")

    def test_cli_defaults_to_dry_run_and_conflicts_exit_two(self):
        bundled_script = self.root / "source/scripts/bootstrap.py"
        bundled_script.parent.mkdir()
        shutil.copy2(SCRIPT, bundled_script)
        command = [sys.executable, str(bundled_script), str(self.target)]

        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Dry run", result.stdout)
        self.assertFalse(self.target.exists())

        self.write(self.target / "AGENTS.md", "User instructions\n")
        before = self.snapshot(self.target)
        result = subprocess.run([*command, "--apply"], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("AGENTS.md", result.stderr)
        self.assertIn("no files written", result.stderr)
        self.assertEqual(self.snapshot(self.target), before)


if __name__ == "__main__":
    unittest.main()
