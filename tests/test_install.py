"""Temporary-directory acceptance tests for the stdlib installer."""

from __future__ import annotations

import asyncio
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))
import install as installer  # noqa: E402


class InstallerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.home = self.root / "codex-home"
        self.models_file = self.root / "model-list.json"
        self._write_catalogue()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_catalogue(self, include_all: bool = True) -> None:
        requirements = []
        for preset in installer.PRESETS:
            _, requirements_for_preset = installer.load_preset(preset)
            requirements.extend(requirements_for_preset)
        catalogue: dict[str, set[str]] = {}
        for requirement in requirements:
            catalogue.setdefault(requirement.model, set()).add(requirement.reasoning_effort)
        if not include_all:
            catalogue.pop(sorted(catalogue)[0])
        payload = {
            "data": [
                {
                    "id": model,
                    "model": model,
                    "supportedReasoningEfforts": [
                        {"reasoningEffort": effort, "description": "fixture"}
                        for effort in sorted(efforts)
                    ],
                }
                for model, efforts in sorted(catalogue.items())
            ],
            "nextCursor": None,
        }
        self.models_file.write_text(json.dumps(payload), encoding="utf-8")

    def invoke(self, *arguments: str) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = installer.main(list(arguments))
        return code, out.getvalue(), err.getvalue()

    def install(self, preset: str, *extra: str) -> tuple[int, str, str]:
        return self.invoke(
            "install",
            "--preset",
            preset,
            "--yes",
            "--codex-home",
            str(self.home),
            "--models-file",
            str(self.models_file),
            *extra,
        )

    def test_install_switch_and_idempotency_preserves_unrelated_config(self) -> None:
        self.home.mkdir()
        config = self.home / "config.toml"
        original_config = b'api_key = "keep-this-private"\n'
        config.write_bytes(original_config)

        code, _, err = self.install("quality")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(config.read_bytes(), original_config)
        manifest_path = self.home / installer.STATE_DIR_NAME / "manifest.json"
        quality_manifest = manifest_path.read_bytes()
        quality_worker = (self.home / "agents" / "worker_terra.toml").read_bytes()

        code, _, err = self.install("balanced")
        self.assertEqual((code, err), (0, ""))
        self.assertNotEqual(
            (self.home / "agents" / "worker_terra.toml").read_bytes(), quality_worker
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["preset"], "balanced")
        self.assertEqual(len(manifest["files"]), 14)
        backups = self.home / installer.STATE_DIR_NAME / "backups"
        self.assertEqual(len(list(backups.iterdir())), 1)

        before_repeat = manifest_path.read_bytes()
        code, output, err = self.install("balanced")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("already installed", output)
        self.assertEqual(manifest_path.read_bytes(), before_repeat)
        self.assertEqual(len(list(backups.iterdir())), 1)
        self.assertNotEqual(quality_manifest, manifest_path.read_bytes())

    def seed_legacy_install(self) -> Path:
        self.assertEqual(self.install("quality")[0], 0)
        skill = self.home / installer.LEGACY_SKILL_REL
        skill.parent.mkdir(parents=True)
        skill.write_bytes(b"legacy managed skill fixture")
        manifest = self.home / installer.STATE_DIR_NAME / "manifest.json"
        data = json.loads(manifest.read_bytes())
        data["files"].append({"path": installer.LEGACY_SKILL_REL,
                              "sha256": installer.sha256_bytes(skill.read_bytes())})
        manifest.write_text(json.dumps(data), encoding="utf-8")
        return skill

    def test_fresh_install_owns_only_fourteen_roles(self) -> None:
        code, output, err = self.install("quality", "--dry-run")
        self.assertEqual((code, err), (0, ""))
        self.assertNotIn("skills/", output)
        self.assertFalse(self.home.exists())
        self.assertEqual(self.install("quality")[0], 0)
        data = json.loads((self.home / installer.STATE_DIR_NAME / "manifest.json").read_bytes())
        self.assertEqual(len(data["files"]), 14)
        self.assertTrue(all(entry["path"].startswith("agents/") for entry in data["files"]))
        self.assertFalse((self.home / "skills").exists())

    def test_roles_only_lifecycle_never_inspects_unrelated_skills(self) -> None:
        skill = self.home / installer.LEGACY_SKILL_REL
        skill.parent.mkdir(parents=True)
        skill.write_bytes(b"unmanaged same-name skill")
        original_lstat = installer._lstat

        def reject_skill_inspection(path):
            if path == self.home / "skills" or self.home / "skills" in path.parents:
                raise AssertionError(f"inspected unrelated skill path: {path}")
            return original_lstat(path)

        with mock.patch.object(installer, "_lstat", side_effect=reject_skill_inspection):
            self.assertEqual(self.install("quality")[0], 0)
            self.assertEqual(self.install("balanced")[0], 0)
            self.assertEqual(self.invoke("status", "--codex-home", str(self.home))[0], 0)
            self.assertEqual(self.invoke("uninstall", "--yes", "--codex-home", str(self.home))[0], 0)
            self.assertEqual(self.install("balanced")[0], 0)
        self.assertEqual(skill.read_bytes(), b"unmanaged same-name skill")

    @unittest.skipIf(os.name == "nt", "symlinks may require Windows privileges")
    def test_roles_only_accepts_unrelated_symlinked_skills_directory(self) -> None:
        self.home.mkdir()
        outside = self.root / "outside-skills"
        outside.mkdir()
        (outside / "keep.txt").write_bytes(b"unrelated")
        (self.home / "skills").symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.install("quality")[0], 0)
        self.assertEqual(self.invoke("uninstall", "--yes", "--codex-home", str(self.home))[0], 0)
        self.assertTrue((self.home / "skills").is_symlink())
        self.assertEqual(list(outside.iterdir()), [outside / "keep.txt"])

    def test_legacy_requires_uninstall_then_roles_only_reinstall(self) -> None:
        skill = self.seed_legacy_install()
        notes = skill.parent / "notes.txt"
        notes.write_bytes(b"personal notes")
        before = self.snapshot()
        code, _, err = self.install("balanced")
        self.assertEqual(code, 2)
        self.assertIn("verified old package first", err)
        self.assertEqual(self.snapshot(), before)
        code, out, err = self.invoke("uninstall", "--dry-run", "--codex-home", str(self.home))
        self.assertEqual((code, err), (0, ""))
        self.assertIn("remove " + installer.LEGACY_SKILL_REL, out)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.invoke("uninstall", "--yes", "--codex-home", str(self.home))[0], 0)
        self.assertFalse(skill.exists())
        self.assertEqual(notes.read_bytes(), b"personal notes")
        self.assertEqual(self.install("balanced")[0], 0)
        self.assertFalse(skill.exists())
        data = json.loads((self.home / installer.STATE_DIR_NAME / "manifest.json").read_bytes())
        self.assertEqual(len(data["files"]), 14)

    def test_modified_legacy_skill_refuses_uninstall_without_deletion(self) -> None:
        skill = self.seed_legacy_install()
        skill.write_bytes(b"user customization")
        before = self.snapshot()
        code, _, err = self.invoke("uninstall", "--yes", "--codex-home", str(self.home))
        self.assertEqual(code, 2)
        self.assertIn("modified", err)
        self.assertEqual(self.snapshot(), before)

    @unittest.skipIf(os.name == "nt", "symlinks may require Windows privileges")
    def test_legacy_uninstall_rejects_each_symlinked_skill_component(self) -> None:
        skill = self.seed_legacy_install()
        for relative in ["skills", "skills/codex-balanced-agents", installer.LEGACY_SKILL_REL]:
            with self.subTest(relative=relative):
                target = self.home / relative
                moved = self.root / "outside"
                target.rename(moved)
                target.symlink_to(moved, target_is_directory=moved.is_dir())
                before = self.snapshot()
                code, _, err = self.invoke("uninstall", "--yes", "--codex-home", str(self.home))
                self.assertEqual(code, 2)
                self.assertIn("symlink", err)
                self.assertEqual(self.snapshot(), before)
                target.unlink()
                moved.rename(target)
        self.assertEqual(skill.read_bytes(), b"legacy managed skill fixture")

    def test_conflict_preflight_does_not_partially_install(self) -> None:
        external = self.home / "agents" / "explore_astra.toml"
        external.parent.mkdir(parents=True)
        external.write_text("owned = 'outside'\n", encoding="utf-8")

        code, _, err = self.install("quality")
        self.assertEqual(code, 2)
        self.assertIn("outside this installer's owner manifest", err)
        self.assertEqual(external.read_text(encoding="utf-8"), "owned = 'outside'\n")
        self.assertFalse((self.home / "skills" / "codex-balanced-agents" / "SKILL.md").exists())
        self.assertFalse((self.home / installer.STATE_DIR_NAME / "manifest.json").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_destination_is_refused_before_writes(self) -> None:
        external_agents = self.root / "external-agents"
        external_agents.mkdir()
        self.home.mkdir()
        os.symlink(external_agents, self.home / "agents")

        code, _, err = self.install("quality")
        self.assertEqual(code, 2)
        self.assertIn("symlink", err)
        self.assertEqual(list(external_agents.iterdir()), [])
        self.assertFalse((self.home / installer.STATE_DIR_NAME).exists())

    def test_missing_models_require_opt_in_for_noninteractive_install(self) -> None:
        self._write_catalogue(include_all=False)
        code, _, err = self.install("quality")
        self.assertEqual(code, 2)
        self.assertIn("--allow-unverified-models", err)
        self.assertFalse((self.home / installer.STATE_DIR_NAME).exists())

        code, output, err = self.install("quality", "--allow-unverified-models")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("installed unchanged with unverified", output)
        self.assertTrue((self.home / installer.STATE_DIR_NAME / "manifest.json").exists())

    def test_dry_run_allows_unavailable_catalogue_without_writes(self) -> None:
        missing = self.root / "missing-model-list.json"
        code, output, err = self.invoke(
            "install",
            "--preset",
            "quality",
            "--yes",
            "--dry-run",
            "--codex-home",
            str(self.home),
            "--models-file",
            str(missing),
        )
        self.assertEqual((code, err), (0, ""))
        self.assertIn("model requirements remain unverified", output)
        self.assertFalse(self.home.exists())

    def test_interactive_install_has_at_most_two_prompts(self) -> None:
        inputs = mock.Mock(side_effect=["balanced", "yes"])
        with mock.patch("builtins.input", inputs):
            code, _, err = self.invoke(
                "install",
                "--codex-home",
                str(self.home),
                "--models-file",
                str(self.models_file),
            )
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(inputs.call_count, 2)

    def test_interactive_missing_model_acknowledgement_is_one_review_prompt(self) -> None:
        self._write_catalogue(include_all=False)
        inputs = mock.Mock(side_effect=["yes"])
        with mock.patch("builtins.input", inputs):
            code, output, err = self.invoke(
                "install",
                "--preset",
                "quality",
                "--codex-home",
                str(self.home),
                "--models-file",
                str(self.models_file),
            )
        self.assertEqual((code, err), (0, ""))
        self.assertIn("installed unchanged with unverified", output)
        self.assertEqual(inputs.call_count, 1)

    def test_confirmation_rechecks_a_new_unmanaged_target_before_writing(self) -> None:
        target = self.home / "agents" / "worker_astra.toml"

        def confirm_and_add_conflict(_: str) -> bool:
            target.parent.mkdir(parents=True)
            target.write_text("owned = 'outside'\n", encoding="utf-8")
            return True

        with mock.patch.object(installer, "_confirm", side_effect=confirm_and_add_conflict):
            code, _, err = self.invoke(
                "install",
                "--preset",
                "quality",
                "--codex-home",
                str(self.home),
                "--models-file",
                str(self.models_file),
            )
        self.assertEqual(code, 2)
        self.assertIn("outside this installer's owner manifest", err)
        self.assertEqual(target.read_text(encoding="utf-8"), "owned = 'outside'\n")
        self.assertFalse((self.home / installer.STATE_DIR_NAME / "manifest.json").exists())

    def test_stalled_app_server_response_becomes_unverified_catalogue(self) -> None:
        class StalledStdout:
            async def readline(self) -> bytes:
                await asyncio.Future()
                return b""  # pragma: no cover - Future never completes

        class StalledProcess:
            stdout = StalledStdout()

        async def stalled_catalogue() -> dict[str, set[str]]:
            deadline = asyncio.get_running_loop().time() + 0.01
            return await installer._read_response(StalledProcess(), 1, deadline)

        with self.assertRaisesRegex(installer.InstallerError, "timed out"):
            asyncio.run(stalled_catalogue())
        with mock.patch.object(installer, "_live_catalog_async", new=stalled_catalogue):
            code, output, err = self.invoke(
                "install",
                "--preset",
                "quality",
                "--yes",
                "--allow-unverified-models",
                "--codex-home",
                str(self.home),
            )
        self.assertEqual((code, err), (0, ""))
        self.assertIn("model verification unavailable", output)
        self.assertIn("installed unchanged with unverified", output)

    def test_uninstall_refuses_drift_without_deleting_files(self) -> None:
        self.assertEqual(self.install("quality")[0], 0)
        target = self.home / "agents" / "worker_astra.toml"
        target.write_text("modified = true\n", encoding="utf-8")

        code, output, err = self.invoke("status", "--codex-home", str(self.home))
        self.assertEqual((code, err), (1, ""))
        self.assertIn("status: drifted", output)

        code, _, err = self.invoke("uninstall", "--yes", "--codex-home", str(self.home))
        self.assertEqual(code, 2)
        self.assertIn("modified", err)
        self.assertEqual(target.read_text(encoding="utf-8"), "modified = true\n")
        self.assertTrue((self.home / installer.STATE_DIR_NAME / "manifest.json").exists())

    def test_uninstall_removes_only_verified_managed_files(self) -> None:
        self.assertEqual(self.install("quality")[0], 0)
        unrelated = self.home / "agents" / "local-role.toml"
        unrelated.write_text("owned = 'outside'\n", encoding="utf-8")

        code, _, err = self.invoke("uninstall", "--yes", "--codex-home", str(self.home))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "owned = 'outside'\n")
        self.assertFalse((self.home / "skills" / "codex-balanced-agents" / "SKILL.md").exists())
        manifest = json.loads(
            (self.home / installer.STATE_DIR_NAME / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertFalse(manifest["installed"])
        self.assertEqual(manifest["files"], [])

    def snapshot(self) -> dict[str, bytes]:
        return {str(p.relative_to(self.home)): p.read_bytes()
                for p in self.home.rglob("*") if p.is_file()}

    def test_uninstall_preview_cancel_repeat_and_reinstall(self) -> None:
        self.assertEqual(self.install("balanced")[0], 0)
        unrelated = {
            "config.toml": b"main configuration",
            "AGENTS.md": b"global instructions",
            "auth.json": b"synthetic auth fixture",
            "mcp.json": b"synthetic mcp fixture",
            "agents/local.toml": b"local role",
            "skills/other/SKILL.md": b"other skill",
            "skills/codex-balanced-agents/my-notes.txt": b"personal notes",
            "codex-balanced-agents/backups/keep.txt": b"backup fixture",
        }
        for relative, content in unrelated.items():
            target = self.home / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        before = self.snapshot()
        with mock.patch.object(installer, "_confirm", side_effect=AssertionError("no prompt")):
            code, out, err = self.invoke("uninstall", "--dry-run", "--codex-home", str(self.home))
        self.assertEqual((code, err), (0, ""))
        self.assertIn("remove agents/worker_astra.toml", out)
        self.assertEqual(self.snapshot(), before)
        with mock.patch.object(installer, "_confirm", return_value=False):
            self.assertEqual(self.invoke("uninstall", "--codex-home", str(self.home))[0], 2)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.invoke("uninstall", "--yes", "--codex-home", str(self.home))[0], 0)
        for relative, content in unrelated.items():
            self.assertEqual((self.home / relative).read_bytes(), content)
        after = self.snapshot()
        self.assertEqual(self.invoke("uninstall", "--yes", "--codex-home", str(self.home))[0], 0)
        self.assertEqual(self.snapshot(), after)
        # Unrelated skill directories neither block nor become owned by installation.
        self.assertEqual(self.install("balanced")[0], 0)

    def test_uninstall_reinstall_without_custom_skill_files(self) -> None:
        self.assertEqual(self.install("quality")[0], 0)
        self.assertEqual(self.invoke("uninstall", "--yes", "--codex-home", str(self.home))[0], 0)
        self.assertEqual(self.install("balanced")[0], 0)

    def test_uninstall_rejects_unrelated_manifest_entry(self) -> None:
        self.assertEqual(self.install("balanced")[0], 0)
        target = self.home / "agents/local.toml"
        target.write_bytes(b"unrelated role")
        manifest = self.home / installer.STATE_DIR_NAME / "manifest.json"
        data = json.loads(manifest.read_bytes())
        data["files"].append({"path": "agents/local.toml", "sha256": installer.sha256_bytes(target.read_bytes())})
        manifest.write_text(json.dumps(data))
        before = self.snapshot()
        code, _, err = self.invoke("uninstall", "--yes", "--codex-home", str(self.home))
        self.assertEqual(code, 2)
        self.assertIn("not in this package", err)
        self.assertEqual(self.snapshot(), before)

    def test_uninstall_rechecks_after_confirmation(self) -> None:
        self.assertEqual(self.install("balanced")[0], 0)
        target = self.home / "agents/worker_astra.toml"
        def change_file(prompt: str) -> bool:
            target.write_bytes(b"user change while reviewing")
            return True
        with mock.patch.object(installer, "_confirm", side_effect=change_file):
            code, _, _ = self.invoke("uninstall", "--codex-home", str(self.home))
        self.assertEqual(code, 2)
        self.assertEqual(target.read_bytes(), b"user change while reviewing")
        self.assertEqual(len(list((self.home / "agents").glob("*.toml"))), 14)

    def test_uninstall_preserves_concurrently_changed_manifest(self) -> None:
        self.assertEqual(self.install("balanced")[0], 0)
        manifest = self.home / installer.STATE_DIR_NAME / "manifest.json"
        before = self.snapshot()
        original = installer._assert_uninstall_current
        count = 0
        replacement = b'{"external": "change"}'
        def change_before_commit(home, state, allowed):
            nonlocal count
            count += 1
            if count == 16:  # initial check + 14 removals + commit check
                manifest.write_bytes(replacement)
            original(home, state, allowed)
        with mock.patch.object(installer, "_assert_uninstall_current", side_effect=change_before_commit):
            code, _, err = self.invoke("uninstall", "--yes", "--codex-home", str(self.home))
        self.assertEqual(code, 2)
        self.assertIn("were restored", err)
        before[f"{installer.STATE_DIR_NAME}/manifest.json"] = replacement
        self.assertEqual(self.snapshot(), before)

    def test_uninstall_write_failure_restores_deleted_files(self) -> None:
        self.assertEqual(self.install("balanced")[0], 0)
        before = self.snapshot()
        with mock.patch.object(installer, "_atomic_write", side_effect=OSError("disk full")):
            code, _, err = self.invoke("uninstall", "--yes", "--codex-home", str(self.home))
        self.assertEqual(code, 2)
        self.assertIn("were restored", err)
        self.assertEqual(self.snapshot(), before)

    def test_uninstall_rollback_preserves_replacement_file(self) -> None:
        self.assertEqual(self.install("balanced")[0], 0)
        target = self.home / "agents/worker_astra.toml"
        def fail_commit(path, content):
            target.write_bytes(b"new user file")
            raise OSError("commit failed")
        with mock.patch.object(installer, "_atomic_write", side_effect=fail_commit):
            code, _, err = self.invoke("uninstall", "--yes", "--codex-home", str(self.home))
        self.assertEqual(code, 2)
        self.assertIn("rollback incomplete", err)
        self.assertEqual(target.read_bytes(), b"new user file")
        self.assertTrue((self.home / "agents/explore_luna.toml").is_file())

    def test_uninstall_missing_file_fails_before_deletion(self) -> None:
        self.assertEqual(self.install("balanced")[0], 0)
        (self.home / "agents/worker_astra.toml").unlink()
        before = self.snapshot()
        self.assertEqual(self.invoke("uninstall", "--yes", "--codex-home", str(self.home))[0], 2)
        self.assertEqual(self.snapshot(), before)

    @unittest.skipIf(os.name == "nt", "symlinks may require Windows privileges")
    def test_uninstall_rejects_symlinked_destination_and_state(self) -> None:
        self.assertEqual(self.install("balanced")[0], 0)
        for relative in ["agents",
                         "agents/worker_astra.toml", "codex-balanced-agents",
                         "codex-balanced-agents/manifest.json"]:
            with self.subTest(relative=relative):
                target = self.home / relative
                moved = self.root / "outside"
                target.rename(moved)
                target.symlink_to(moved, target_is_directory=moved.is_dir())
                before = self.snapshot()
                self.assertEqual(self.invoke("uninstall", "--yes", "--codex-home", str(self.home))[0], 2)
                self.assertEqual(self.snapshot(), before)
                target.unlink()
                moved.rename(target)

    def test_update_rolls_back_if_write_fails(self) -> None:
        self.assertEqual(self.install("quality")[0], 0)
        sources, _ = installer.load_preset("balanced")
        state = installer._preflight_install(self.home, sources)
        old_manifest = (self.home / installer.STATE_DIR_NAME / "manifest.json").read_bytes()
        old_files = {
            relative: (self.home / Path(relative)).read_bytes() for relative in state.files
        }
        original_atomic_write = installer._atomic_write
        failure_target = self.home / "agents" / "worker_terra.toml"

        def fail_on_one_target(path: Path, content: bytes) -> None:
            if path == failure_target:
                raise OSError("simulated full disk")
            original_atomic_write(path, content)

        with mock.patch.object(installer, "_atomic_write", side_effect=fail_on_one_target):
            with self.assertRaises(installer.InstallerError):
                installer.apply_install(self.home, "balanced", sources, state)

        self.assertEqual((self.home / installer.STATE_DIR_NAME / "manifest.json").read_bytes(), old_manifest)
        for relative, content in old_files.items():
            self.assertEqual((self.home / Path(relative)).read_bytes(), content, relative)

    def test_rollback_preserves_manifest_that_appears_before_first_commit(self) -> None:
        sources, _ = installer.load_preset("quality")
        state = installer._preflight_install(self.home, sources)
        manifest = self.home / installer.STATE_DIR_NAME / "manifest.json"
        external_manifest = b'{"created": "outside-this-install"}\n'
        original_assertion = installer._assert_manifest_still_current

        def add_manifest_then_assert(home: Path, current: installer.ManagedState) -> None:
            manifest.write_bytes(external_manifest)
            original_assertion(home, current)

        with mock.patch.object(
            installer, "_assert_manifest_still_current", side_effect=add_manifest_then_assert
        ):
            with self.assertRaisesRegex(installer.InstallerError, "concurrent or changed"):
                installer.apply_install(self.home, "quality", sources, state)

        self.assertEqual(manifest.read_bytes(), external_manifest)
        self.assertFalse((self.home / "agents" / "worker_astra.toml").exists())

    def test_update_rollback_preserves_concurrently_changed_manifest_and_backup(self) -> None:
        self.assertEqual(self.install("quality")[0], 0)
        sources, _ = installer.load_preset("balanced")
        state = installer._preflight_install(self.home, sources)
        original_files = {
            relative: (self.home / Path(relative)).read_bytes() for relative in state.files
        }
        manifest = self.home / installer.STATE_DIR_NAME / "manifest.json"
        external_manifest = b'{"changed": "outside-this-install"}\n'
        original_assertion = installer._assert_manifest_still_current

        def replace_manifest_then_assert(home: Path, current: installer.ManagedState) -> None:
            manifest.write_bytes(external_manifest)
            original_assertion(home, current)

        with mock.patch.object(
            installer, "_assert_manifest_still_current", side_effect=replace_manifest_then_assert
        ):
            with self.assertRaisesRegex(installer.InstallerError, "backup was retained"):
                installer.apply_install(self.home, "balanced", sources, state)

        self.assertEqual(manifest.read_bytes(), external_manifest)
        for relative, content in original_files.items():
            self.assertEqual((self.home / Path(relative)).read_bytes(), content, relative)
        backups = self.home / installer.STATE_DIR_NAME / "backups"
        self.assertEqual(len(list(backups.iterdir())), 1)


if __name__ == "__main__":
    unittest.main()
