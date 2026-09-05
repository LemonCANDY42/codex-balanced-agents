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
        self.assertEqual(len(manifest["files"]), 15)
        backups = self.home / installer.STATE_DIR_NAME / "backups"
        self.assertEqual(len(list(backups.iterdir())), 1)

        before_repeat = manifest_path.read_bytes()
        code, output, err = self.install("balanced")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("already installed", output)
        self.assertEqual(manifest_path.read_bytes(), before_repeat)
        self.assertEqual(len(list(backups.iterdir())), 1)
        self.assertNotEqual(quality_manifest, manifest_path.read_bytes())

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
