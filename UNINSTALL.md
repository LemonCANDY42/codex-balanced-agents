# Uninstall Codex Balanced Agents

[中文](UNINSTALL.zh-CN.md) · [README](README.md)

## One command

From an inspected, current checkout, with Python 3.11+:

```bash
python3 install.py uninstall --yes
```

This skips the confirmation prompt, **not** ownership or integrity checks. It does not need Codex, account access, model availability or a network connection. Windows users can use `py -3.11` instead of `python3`.

The destination is `$CODEX_HOME`, otherwise `~/.codex`. If you installed into a custom directory, use that same destination:

```bash
python3 install.py uninstall --codex-home /path/to/codex-home --dry-run
python3 install.py uninstall --codex-home /path/to/codex-home --yes
```

`--dry-run` verifies and lists the exact removal paths without modifying files or invoking Codex. Omit `--yes` for an interactive review. Close active tasks and do not run another installer or edit managed files during removal. Restart the Codex client afterward so it refreshes role discovery and removes any legacy skill from its catalogue.

## For an agent

1. Use a clean checkout of this repository and inspect `install.py`; report the exact revision used. If the checkout is gone, clone to a new temporary directory without overwriting existing files. Do not install or upgrade Codex just to uninstall this package.
2. Identify the same Codex home used for installation. If the destination is ambiguous, resolve that before removal; do not scan and delete matching files from other homes or projects.
3. Run `python3 install.py uninstall --codex-home <home> --dry-run` and review the target paths. If the user authorized package removal and this is the intended home, run the same command with `--yes` instead of `--dry-run` without redundant questions.
4. Run `python3 install.py status --codex-home <home>`. Report removed files, retained local state, and any conflicts; ask the user to restart Codex. Never claim successful removal when the command failed.
5. On a conflict, stop and explain it. Do not use recursive deletion, modify hashes, delete the manifest, revert customizations, or remove unrelated configuration to force success.

## Removal boundary

- A file must be recorded in the local ownership manifest **and** belong to this checkout's 14 packaged role paths or the legacy `skills/codex-balanced-agents/SKILL.md` path. New installations contain only roles; that skill path is retained solely for uninstalling older packages. Unlisted files are not adopted, even when their contents match.
- Every recorded file must be regular, present, and match its recorded SHA-256. Modified or missing files, invalid manifests and symlinked package destinations stop preflight before deletion. A record naming an unrelated role is rejected even with a matching hash.
- The installer rechecks destination directories and the manifest during removal, and checks each file immediately before deleting it. It never recursively removes `agents/`, `skills/`, or Codex home. For a legacy installation, it removes the old package skill directory only if empty.
- Main `config.toml`, global `AGENTS.md`, authentication, MCP settings, other roles/skills, and user-added files are preserved. Backups and an inactive ownership manifest remain locally so the removal is recorded. These are not active roles and are not automatically purged.
- If a caught error interrupts removal, the installer attempts to restore only files it actually deleted, using exclusive creation so it cannot overwrite replacement files. Incomplete recovery is reported. This is not a crash-proof transaction or protection against a malicious concurrent filesystem writer; do not edit files concurrently.
- Repeated removal is a no-op after success. An installation made by manually copying files has no ownership record and is not removed. Custom files left in a legacy skill directory remain untouched and do not block a new roles-only installation.

If you want to keep a customized role, save it separately first and decide how to resolve the conflict. The uninstaller will not guess which edits you intended to retain. Do not delete the ownership manifest to bypass the checks.

## Project-only manual installations

`install.py uninstall` does not remove manually copied project files. Use the installation commit or recorded diff to identify which `.codex/agents/<role>.toml` files were actually added. The [14 role names](docs/roles.md#fixed-models-and-reasoning-effort-defaults--固定模型与推理档位默认值) identify candidate filenames, not proof of ownership.

Review each candidate against the exact preset revision originally copied. Remove only unchanged files demonstrably added by that installation, using the project's normal version-control process. Preserve pre-existing roles, user modifications, unrelated changes, and `.codex` configuration; do not delete the entire agents directory or blindly revert a commit containing other work. If provenance is missing or a file differs, stop that removal and resolve it explicitly with the user. Review the resulting diff and restart Codex after removal.
