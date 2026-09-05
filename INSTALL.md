# Install Codex Balanced Agents

[中文](INSTALL.zh-CN.md) · [README](README.md)

This guide is also an entrypoint for an agent installing the package on the user's behalf. Install only the package files. Do not replace the user's main model, global instructions, credentials, MCP servers, or unrelated roles.

## For an agent: at most two questions

1. Read the README and inspect `install.py` from this repository. Clone into a new directory; do not overwrite an existing checkout. Use the user's chosen revision when supplied. Otherwise clone the default branch and report the exact commit you inspected.
2. **Question 1**, only if not already answered: Quality or Balanced? Recommend Balanced for routine use. Both have 14 roles; Quality uses `xhigh` for Luna/Terra, Balanced uses `medium` there. Other tiers are unchanged.
3. Verify Python 3.11+ and the actual Codex executable/version. Run `python3 install.py models`, then `python3 install.py install --preset <choice> --dry-run`. Do not treat the catalogue as an account entitlement check. If these commands fail or detect conflicts, report the reason; do not install/upgrade Codex or repair unrelated configuration automatically.
4. **Question 2**: present the target directory and changes together. If any model/effort is missing or unverified, explain the affected roles and offer **cancel (default)** or **install the unchanged preset acknowledging it may not run**. If everything is listed, confirm installation. Do not ask once per model. If the user already authorized these exact changes and chose a preset, omit redundant confirmation.
5. Apply with `python3 install.py install --preset <choice> --yes`. Add `--allow-unverified-models` **only** if the user explicitly selected unchanged installation despite missing/unverified requirements. Never automatically add this flag in response to a failure or silently substitute a model.
6. Run `python3 install.py status`. Tell the user to restart their Codex client, confirm all intended roles are discoverable, and try a bounded task. Distinguish successful file installation, model listing, and actual role execution. Do not launch extra inference just to install.

If a new issue appears after the second question, stop with a concise explanation instead of creating an unbounded interview. A later user-requested repair is a separate operation. Respect any existing user choice; do not ask again because the instructions are being read in a new context.

## Terminal installation

```bash
git clone https://github.com/LemonCANDY42/codex-balanced-agents.git
cd codex-balanced-agents
python3 install.py install
```

Windows users can use `py -3.11` instead of `python3`. The terminal installer asks the same two questions at most. Choosing a preset on the command line skips the first question.

```bash
python3 install.py install --preset balanced --dry-run
python3 install.py install --preset balanced
python3 install.py status
```

Only after explicitly accepting unavailable/unverified models:

```bash
python3 install.py install --preset quality --yes --allow-unverified-models
```

That command installs unchanged files; it does not enable model access.

## What gets installed

The destination defaults to `$CODEX_HOME`, otherwise `~/.codex`. Override it with `--codex-home /path/to/codex-home` **after the subcommand**.

```text
<codex-home>/
  agents/                              14 selected role files
  skills/codex-balanced-agents/SKILL.md role-selection guidance
  codex-balanced-agents/manifest.json  installer ownership and hashes
  codex-balanced-agents/backups/       prior managed versions after updates
```

The installed skill only guides use; it does not automatically start a team. Modern Codex discovers standalone agent TOML files. No `[agents.<role>]` registrations are added to `config.toml`.

The installer checks every target before writing. It refuses unmanaged files, modified managed files, and symlinked package destinations. Existing `config.toml`, `AGENTS.md`, auth and MCP files are not part of its ownership. A dry run does not write package files or state; the invoked Codex process may maintain its own normal cache/log files.

Close active tasks before changing a preset. Do not run simultaneous installers or edit managed files during installation. Managed updates retain a local backup; caught write failures attempt rollback. This is not a crash-proof filesystem transaction. Backups remain local and are not uploaded.

## Models and client versions

`models` queries the `codex` executable on your PATH with its existing account/configuration through stdio `app-server` and `model/list`. It does not log in, send prompts, buy credits, or read credentials itself. `--codex-home` selects the installation destination; it does not change which running account is queried. Use `CODEX_HOME` in the environment when you intend to select a different Codex account/home for the probe.

A desktop-bundled executable and a separate CLI may have different versions and catalogues. Select the executable you actually use through your shell PATH. If a model is not listed, first decide whether to use a suitable client, cancel, or install the unchanged preset for later use. The installer performs no automatic software upgrade.

For offline inspection/testing, `--models-file capture.json` accepts a JSON `model/list` response/result or its `data` array. This trusts the supplied catalogue and does not prove current model access. Do not provide credentials or full account exports.

## Switch, update, remove

Pull changes into a clean checkout, inspect them, and rerun the installer. It only updates files whose hashes still match its ownership record.

```bash
python3 install.py install --preset quality
python3 install.py status
python3 install.py uninstall
```

Uninstall removes only unchanged managed role/skill files and retains backups plus an inactive manifest. If you have edited a managed file, save your customization elsewhere and resolve the reported conflict deliberately; the installer will not overwrite or delete it for you. Do not delete the ownership manifest to force an update.

For a project-only setup, manually copy one preset's TOML files into `.codex/agents/` and the routing skill into `.agents/skills/`. This manual path is not tracked by the global installer. Check the project's trust settings and use its normal version-control process.
