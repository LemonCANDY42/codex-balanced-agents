#!/usr/bin/env python3
"""Install the Codex balanced-agent presets without changing Codex settings.

This program intentionally uses only the Python 3.11 standard library.  It owns
only the files recorded in its manifest; it never writes config.toml, AGENTS.md,
authentication, or MCP configuration.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
import tomllib


ROOT = Path(__file__).resolve().parent
PRESETS = ("quality", "balanced")
SKILL_REL = "skills/codex-balanced-agents/SKILL.md"
STATE_DIR_NAME = "codex-balanced-agents"
MANIFEST_VERSION = 1
CLIENT_INFO = {"name": "codex_balanced_agents", "version": "0.1.0"}
TOTAL_APP_SERVER_TIMEOUT_SECONDS = 20.0


class InstallerError(RuntimeError):
    """An expected, actionable installer failure."""


class ConflictError(InstallerError):
    """A target is not safely owned by this installer."""


@dataclass(frozen=True)
class SourceFile:
    relative_path: str
    content: bytes


@dataclass(frozen=True)
class ModelRequirement:
    source_name: str
    model: str
    reasoning_effort: str


@dataclass(frozen=True)
class ManagedState:
    exists: bool
    installed: bool
    preset: str | None
    files: dict[str, str]
    raw: bytes | None


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _lstat(path: Path) -> os.stat_result | None:
    try:
        return path.lstat()
    except FileNotFoundError:
        return None


def _is_symlink(path: Path) -> bool:
    stat = _lstat(path)
    return stat is not None and path.is_symlink()


def _require_regular_file(path: Path, description: str) -> bytes:
    if _is_symlink(path):
        raise ConflictError(f"refusing symlink {description}: {path}")
    stat = _lstat(path)
    if stat is None:
        raise InstallerError(f"missing {description}: {path}")
    if not path.is_file():
        raise InstallerError(f"{description} is not a regular file: {path}")
    return path.read_bytes()


def _assert_no_symlink_components(path: Path, description: str) -> None:
    """Reject a symlink at the supplied destination boundary.

    Platform temporary locations may legitimately have a system-owned symlink
    ancestor (for example macOS /var -> /private/var).  Derived destinations are
    checked independently, so this deliberately does not reject those ancestors.
    """
    if _is_symlink(path):
        raise ConflictError(f"refusing symlink in {description}: {path}")


def normalize_home(value: str | None) -> Path:
    raw = value or os.environ.get("CODEX_HOME") or "~/.codex"
    home = Path(raw).expanduser().absolute()
    _assert_no_symlink_components(home, "--codex-home")
    stat = _lstat(home)
    if stat is not None and not home.is_dir():
        raise InstallerError(f"--codex-home is not a directory: {home}")
    return home


def _safe_relative(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise InstallerError(f"invalid manifest path: {value!r}")
    return path.as_posix()


def _destination(home: Path, relative_path: str) -> Path:
    safe = _safe_relative(relative_path)
    return home.joinpath(*PurePosixPath(safe).parts)


def _is_generic_owned_relative(relative_path: str) -> bool:
    try:
        safe = _safe_relative(relative_path)
    except InstallerError:
        return False
    if safe == SKILL_REL:
        return True
    parts = PurePosixPath(safe).parts
    return len(parts) == 2 and parts[0] == "agents" and parts[1].endswith(".toml")


def _manifest_path(home: Path) -> Path:
    return home / STATE_DIR_NAME / "manifest.json"


def _read_manifest(home: Path, allowed_paths: set[str] | None = None) -> ManagedState:
    state_dir = home / STATE_DIR_NAME
    if _is_symlink(state_dir):
        raise ConflictError(f"refusing symlink installer state directory: {state_dir}")
    if state_dir.exists() and not state_dir.is_dir():
        raise ConflictError(f"installer state path is not a directory: {state_dir}")

    manifest = _manifest_path(home)
    if _is_symlink(manifest):
        raise ConflictError(f"refusing symlink manifest: {manifest}")
    if not manifest.exists():
        if state_dir.exists():
            raise ConflictError(
                f"installer state directory already exists without an owner manifest: {state_dir}"
            )
        return ManagedState(False, False, None, {}, None)
    raw = _require_regular_file(manifest, "owner manifest")
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallerError(f"invalid owner manifest: {manifest}") from exc
    if not isinstance(decoded, dict) or decoded.get("version") != MANIFEST_VERSION:
        raise InstallerError(f"unsupported owner manifest: {manifest}")

    installed = decoded.get("installed", True)
    preset = decoded.get("preset")
    entries = decoded.get("files")
    if not isinstance(installed, bool) or preset not in PRESETS or not isinstance(entries, list):
        raise InstallerError(f"invalid owner manifest fields: {manifest}")

    files: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise InstallerError(f"invalid owner manifest entry: {manifest}")
        relative = entry.get("path")
        digest = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(digest, str):
            raise InstallerError(f"invalid owner manifest entry: {manifest}")
        relative = _safe_relative(relative)
        if not _is_generic_owned_relative(relative):
            raise InstallerError(f"manifest path is outside installer ownership: {relative}")
        if allowed_paths is not None and relative not in allowed_paths:
            raise InstallerError(f"manifest path is not in this package: {relative}")
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise InstallerError(f"invalid manifest digest for {relative}")
        if relative in files:
            raise InstallerError(f"duplicate manifest path: {relative}")
        files[relative] = digest

    if installed and not files:
        raise InstallerError(f"installed owner manifest has no files: {manifest}")
    if not installed and files:
        raise InstallerError(f"uninstalled owner manifest has files: {manifest}")
    return ManagedState(True, installed, preset, files, raw)


def _source_path(preset: str) -> Path:
    return ROOT / "presets" / preset / "agents"


def _validate_source_layout() -> dict[str, list[Path]]:
    layouts: dict[str, list[Path]] = {}
    expected_names: set[str] | None = None
    for preset in PRESETS:
        directory = _source_path(preset)
        if _is_symlink(directory):
            raise InstallerError(f"preset directory must not be a symlink: {directory}")
        if not directory.is_dir():
            raise InstallerError(f"missing preset directory: {directory}")
        files = sorted(directory.glob("*.toml"), key=lambda item: item.name)
        if len(files) != 14:
            raise InstallerError(f"preset {preset} must contain exactly 14 agent TOML files")
        for file in files:
            if _is_symlink(file) or not file.is_file():
                raise InstallerError(f"preset agent must be a regular file: {file}")
            if "/" in file.name or file.name in ("", ".", ".."):
                raise InstallerError(f"unsafe preset filename: {file.name!r}")
        names = {file.name for file in files}
        if expected_names is None:
            expected_names = names
        elif names != expected_names:
            raise InstallerError("quality and balanced presets must contain the same agent filenames")
        layouts[preset] = files
    return layouts


def _model_requirement(source_name: str, content: bytes) -> ModelRequirement:
    try:
        parsed = tomllib.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise InstallerError(f"invalid TOML in {source_name}") from exc
    model = parsed.get("model")
    # Codex agent TOML uses model_reasoning_effort.  Accept the shorter spelling
    # for a deliberately hand-authored offline fixture, but never infer one.
    reasoning_effort = parsed.get("model_reasoning_effort", parsed.get("reasoning_effort"))
    if not isinstance(model, str) or not model:
        raise InstallerError(f"{source_name} must declare a non-empty model")
    if not isinstance(reasoning_effort, str) or not reasoning_effort:
        raise InstallerError(f"{source_name} must declare a non-empty model_reasoning_effort")
    return ModelRequirement(source_name, model, reasoning_effort)


def load_preset(preset: str) -> tuple[list[SourceFile], list[ModelRequirement]]:
    if preset not in PRESETS:
        raise InstallerError(f"unknown preset: {preset}")
    layouts = _validate_source_layout()
    files: list[SourceFile] = []
    requirements: list[ModelRequirement] = []
    for source in layouts[preset]:
        content = _require_regular_file(source, "preset agent")
        relative = f"agents/{source.name}"
        files.append(SourceFile(relative, content))
        requirements.append(_model_requirement(source.name, content))

    skill_source = ROOT / "skills" / "codex-balanced-agents" / "SKILL.md"
    content = _require_regular_file(skill_source, "installer skill")
    files.append(SourceFile(SKILL_REL, content))
    return files, requirements


def _catalog_from_result(payload: Any) -> dict[str, set[str]]:
    """Parse the app-server model/list result shape, without inventing models."""
    if isinstance(payload, dict) and "result" in payload:
        payload = payload["result"]
    if not isinstance(payload, dict):
        raise InstallerError("models file must contain a model/list result object")
    data = payload.get("data")
    if not isinstance(data, list):
        raise InstallerError("model/list result has no data array")
    result: dict[str, set[str]] = {}
    for item in data:
        if not isinstance(item, dict):
            raise InstallerError("model/list data contains a non-object entry")
        model = item.get("model", item.get("id"))
        efforts = item.get("supportedReasoningEfforts")
        if not isinstance(model, str) or not model or not isinstance(efforts, list):
            raise InstallerError("model/list entry is missing model/id or supportedReasoningEfforts")
        parsed_efforts: set[str] = set()
        for effort in efforts:
            if not isinstance(effort, dict) or not isinstance(effort.get("reasoningEffort"), str):
                raise InstallerError("supportedReasoningEfforts entries must contain reasoningEffort")
            parsed_efforts.add(effort["reasoningEffort"])
        result.setdefault(model, set()).update(parsed_efforts)
    return result


def catalog_from_file(path_value: str) -> dict[str, set[str]]:
    path = Path(path_value).expanduser()
    raw = _require_regular_file(path, "models file")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallerError(f"invalid models file: {path}") from exc
    return _catalog_from_result(payload)


async def _read_response(
    process: asyncio.subprocess.Process, request_id: int, deadline: float
) -> dict[str, Any]:
    if process.stdout is None:
        raise InstallerError("Codex app-server did not provide stdout")
    loop = asyncio.get_running_loop()
    while True:
        remaining = deadline - loop.time()
        if remaining <= 0:
            raise InstallerError("Codex app-server model/list timed out")
        try:
            line = await asyncio.wait_for(process.stdout.readline(), timeout=remaining)
        except asyncio.TimeoutError as exc:
            raise InstallerError("Codex app-server model/list timed out") from exc
        if not line:
            raise InstallerError("Codex app-server closed before model/list completed")
        try:
            message = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(message, dict) or message.get("id") != request_id:
            continue
        error = message.get("error")
        if error is not None:
            raise InstallerError(f"Codex app-server request failed: {error}")
        result = message.get("result")
        if not isinstance(result, dict):
            raise InstallerError("Codex app-server returned an invalid result")
        return result


async def _write_json_line(
    process: asyncio.subprocess.Process, payload: dict[str, Any], deadline: float
) -> None:
    if process.stdin is None:
        raise InstallerError("Codex app-server did not provide stdin")
    try:
        process.stdin.write((json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8"))
        remaining = deadline - asyncio.get_running_loop().time()
        if remaining <= 0:
            raise asyncio.TimeoutError
        await asyncio.wait_for(process.stdin.drain(), timeout=remaining)
    except (asyncio.TimeoutError, BrokenPipeError, ConnectionResetError, OSError) as exc:
        raise InstallerError("Codex app-server transport failed while requesting model/list") from exc


async def _live_catalog_async() -> dict[str, set[str]]:
    if shutil.which("codex") is None:
        raise InstallerError("Codex CLI was not found; use --models-file or --allow-unverified-models")
    process = await asyncio.create_subprocess_exec(
        "codex",
        "app-server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    loop = asyncio.get_running_loop()
    deadline = loop.time() + TOTAL_APP_SERVER_TIMEOUT_SECONDS
    try:
        await _write_json_line(
            process,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"clientInfo": CLIENT_INFO},
            },
            deadline,
        )
        await _read_response(process, 1, deadline)
        await _write_json_line(
            process,
            {"jsonrpc": "2.0", "method": "initialized", "params": {}},
            deadline,
        )

        catalogue: dict[str, set[str]] = {}
        cursor: str | None = None
        request_id = 2
        while True:
            params: dict[str, Any] = {"includeHidden": False}
            if cursor is not None:
                params["cursor"] = cursor
            await _write_json_line(
                process,
                {"jsonrpc": "2.0", "id": request_id, "method": "model/list", "params": params},
                deadline,
            )
            page = await _read_response(process, request_id, deadline)
            parsed = _catalog_from_result(page)
            for model, efforts in parsed.items():
                catalogue.setdefault(model, set()).update(efforts)
            next_cursor = page.get("nextCursor", page.get("next_cursor"))
            if next_cursor is None:
                break
            if not isinstance(next_cursor, str) or not next_cursor:
                raise InstallerError("Codex app-server returned an invalid model/list cursor")
            cursor = next_cursor
            request_id += 1
        return catalogue
    finally:
        if process.returncode is None:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()


def live_catalog() -> dict[str, set[str]]:
    try:
        return asyncio.run(_live_catalog_async())
    except FileNotFoundError as exc:
        raise InstallerError("Codex CLI was not found; use --models-file or --allow-unverified-models") from exc
    except (asyncio.TimeoutError, OSError) as exc:
        raise InstallerError("Codex app-server model/list failed") from exc


def requested_model_issues(
    requirements: Iterable[ModelRequirement], catalogue: dict[str, set[str]]
) -> list[str]:
    issues: list[str] = []
    seen: set[tuple[str, str]] = set()
    for requirement in requirements:
        key = (requirement.model, requirement.reasoning_effort)
        if key in seen:
            continue
        seen.add(key)
        available = catalogue.get(requirement.model)
        if available is None:
            issues.append(f"missing model {requirement.model}")
        elif requirement.reasoning_effort not in available:
            issues.append(
                f"{requirement.model} does not support reasoning_effort {requirement.reasoning_effort}"
            )
    return issues


def _format_verification(issues: list[str], unavailable: str | None) -> str:
    if unavailable is not None:
        return f"model verification unavailable: {unavailable}"
    if issues:
        return "model verification failed: " + "; ".join(issues)
    return "model verification passed"


def _choose_preset() -> str:
    try:
        answer = input("Choose preset [quality/balanced] (default: cancel): ").strip().lower()
    except EOFError as exc:
        raise InstallerError("installation cancelled; no preset was supplied") from exc
    choices = {"quality": "quality", "q": "quality", "balanced": "balanced", "b": "balanced"}
    if answer not in choices:
        raise InstallerError("installation cancelled; select quality or balanced")
    return choices[answer]


def _confirm(prompt: str) -> bool:
    try:
        return input(prompt).strip().lower() in {"y", "yes"}
    except EOFError:
        return False


def _assert_destination_layout(home: Path, state: ManagedState) -> None:
    _assert_no_symlink_components(home, "--codex-home")
    for directory in (home / "agents", home / "skills", home / "skills" / "codex-balanced-agents"):
        if _is_symlink(directory):
            raise ConflictError(f"refusing symlink destination directory: {directory}")
        if directory.exists() and not directory.is_dir():
            raise ConflictError(f"destination path is not a directory: {directory}")
    if not state.installed and (home / "skills" / "codex-balanced-agents").exists():
        raise ConflictError(
            "skill destination already exists outside this installer's owner manifest: "
            f"{home / 'skills' / 'codex-balanced-agents'}"
        )


def _validate_existing_owned_files(home: Path, state: ManagedState) -> None:
    if not state.installed:
        return
    for relative, digest in state.files.items():
        target = _destination(home, relative)
        content = _require_regular_file(target, f"managed file {relative}")
        if sha256_bytes(content) != digest:
            raise ConflictError(
                f"managed file was modified: {target}; restore it or remove the installer state manually"
            )


def _preflight_install(home: Path, sources: list[SourceFile]) -> ManagedState:
    desired = {source.relative_path for source in sources}
    state = _read_manifest(home, desired)
    _assert_destination_layout(home, state)
    _validate_existing_owned_files(home, state)

    for source in sources:
        target = _destination(home, source.relative_path)
        if _is_symlink(target):
            raise ConflictError(f"refusing symlink destination file: {target}")
        if target.exists() and source.relative_path not in state.files:
            raise ConflictError(
                f"destination already exists outside this installer's owner manifest: {target}"
            )
    backup_dir = home / STATE_DIR_NAME / "backups"
    if _is_symlink(backup_dir):
        raise ConflictError(f"refusing symlink backup directory: {backup_dir}")
    if backup_dir.exists() and not backup_dir.is_dir():
        raise ConflictError(f"backup path is not a directory: {backup_dir}")
    return state


def _assert_target_still_owned_or_absent(home: Path, relative: str, state: ManagedState) -> None:
    """Check a target again at the point an install would mutate it."""
    target = _destination(home, relative)
    if relative in state.files:
        content = _require_regular_file(target, f"managed file {relative}")
        if sha256_bytes(content) != state.files[relative]:
            raise ConflictError(f"managed file changed during install: {target}")
    elif target.exists() or _is_symlink(target):
        raise ConflictError(
            f"destination appeared outside this installer's owner manifest: {target}"
        )


def _assert_manifest_still_current(home: Path, state: ManagedState) -> None:
    manifest = _manifest_path(home)
    if state.raw is None:
        if manifest.exists() or _is_symlink(manifest):
            raise ConflictError(f"owner manifest appeared during install: {manifest}")
        return
    current = _require_regular_file(manifest, "owner manifest")
    if current != state.raw:
        raise ConflictError(f"owner manifest changed during install: {manifest}")


def _ensure_directory(path: Path, created: list[Path]) -> None:
    if path.exists():
        if _is_symlink(path) or not path.is_dir():
            raise ConflictError(f"unsafe destination directory: {path}")
        return
    parent = path.parent
    if parent != path:
        _ensure_directory(parent, created)
    path.mkdir()
    created.append(path)


def _atomic_write(path: Path, content: bytes) -> None:
    if _is_symlink(path):
        raise ConflictError(f"refusing symlink destination file: {path}")
    if path.exists() and not path.is_file():
        raise ConflictError(f"destination is not a regular file: {path}")
    fd, temporary_name = tempfile.mkstemp(prefix=".codex-balanced-agents-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _manifest_bytes(preset: str, files: dict[str, str], installed: bool = True) -> bytes:
    payload = {
        "version": MANIFEST_VERSION,
        "installed": installed,
        "preset": preset,
        "files": [
            {"path": path, "sha256": files[path]}
            for path in sorted(files)
        ],
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _backup_previous(home: Path, state: ManagedState, created: list[Path]) -> Path | None:
    if not state.installed:
        return None
    backup_root = home / STATE_DIR_NAME / "backups"
    _ensure_directory(backup_root, created)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    candidate = backup_root / stamp
    sequence = 1
    while candidate.exists():
        candidate = backup_root / f"{stamp}-{sequence}"
        sequence += 1
    _ensure_directory(candidate, created)
    if state.raw is None:
        raise InstallerError("owner manifest bytes are unavailable")
    _atomic_write(candidate / "manifest.json", state.raw)
    for relative in sorted(state.files):
        target = _destination(home, relative)
        _assert_target_still_owned_or_absent(home, relative, state)
        backup_file = candidate / "files" / relative
        _ensure_directory(backup_file.parent, created)
        _atomic_write(backup_file, target.read_bytes())
    return candidate


def _cleanup_created_directories(created: list[Path]) -> None:
    for directory in reversed(created):
        try:
            directory.rmdir()
        except OSError:
            pass


def apply_install(home: Path, preset: str, sources: list[SourceFile], state: ManagedState) -> None:
    """Apply a preflighted install and restore managed bytes if an operation fails."""
    refreshed_state = _preflight_install(home, sources)
    if refreshed_state != state:
        raise ConflictError("installer state changed after review; rerun installation")
    state = refreshed_state
    source_map = {source.relative_path: source.content for source in sources}
    original_files = {
        relative: _destination(home, relative).read_bytes()
        for relative in state.files
    }
    old_manifest = state.raw
    created_directories: list[Path] = []
    written_files: dict[str, bytes] = {}
    removed: set[str] = set()
    backup_path: Path | None = None
    written_manifest: bytes | None = None
    manifest = _manifest_path(home)
    try:
        _ensure_directory(home, created_directories)
        _ensure_directory(home / "agents", created_directories)
        _ensure_directory(home / "skills", created_directories)
        _ensure_directory(home / "skills" / "codex-balanced-agents", created_directories)
        _ensure_directory(home / STATE_DIR_NAME, created_directories)
        backup_path = _backup_previous(home, state, created_directories)

        for relative in sorted(source_map):
            _assert_target_still_owned_or_absent(home, relative, state)
            _atomic_write(_destination(home, relative), source_map[relative])
            written_files[relative] = source_map[relative]
        for relative in sorted(set(state.files) - set(source_map)):
            target = _destination(home, relative)
            _assert_target_still_owned_or_absent(home, relative, state)
            target.unlink()
            removed.add(relative)
        digests = {relative: sha256_bytes(content) for relative, content in source_map.items()}
        _assert_manifest_still_current(home, state)
        manifest_content = _manifest_bytes(preset, digests)
        _atomic_write(manifest, manifest_content)
        written_manifest = manifest_content
    except Exception as exc:
        rollback_errors: list[str] = []
        for relative in sorted(set(written_files) | removed):
            target = _destination(home, relative)
            try:
                if relative in written_files:
                    if _is_symlink(target) or not target.is_file():
                        rollback_errors.append(f"{relative}: target changed after this install wrote it")
                        continue
                    if target.read_bytes() != written_files[relative]:
                        rollback_errors.append(f"{relative}: target changed after this install wrote it")
                        continue
                    if relative in original_files:
                        _atomic_write(target, original_files[relative])
                    else:
                        target.unlink()
                elif not target.exists():
                    _atomic_write(target, original_files[relative])
                else:
                    rollback_errors.append(f"{relative}: target was recreated after this install removed it")
            except Exception as rollback_exc:  # pragma: no cover - exceptional disk failure path
                rollback_errors.append(f"{relative}: {rollback_exc}")
        try:
            if written_manifest is not None:
                if _is_symlink(manifest) or not manifest.is_file():
                    rollback_errors.append("manifest: changed after this install wrote it")
                elif manifest.read_bytes() != written_manifest:
                    rollback_errors.append("manifest: changed after this install wrote it")
                elif old_manifest is not None:
                    _atomic_write(manifest, old_manifest)
                else:
                    manifest.unlink()
            elif old_manifest is None:
                if manifest.exists() or _is_symlink(manifest):
                    rollback_errors.append("manifest: appeared outside this install")
            elif _is_symlink(manifest) or not manifest.is_file() or manifest.read_bytes() != old_manifest:
                rollback_errors.append("manifest: changed outside this install")
        except Exception as rollback_exc:  # pragma: no cover - exceptional disk failure path
            rollback_errors.append(f"manifest: {rollback_exc}")
        if backup_path is not None and not rollback_errors:
            try:
                shutil.rmtree(backup_path)
            except OSError:
                pass
        _cleanup_created_directories(created_directories)
        message = f"installation failed and previous managed files were restored: {exc}"
        if rollback_errors:
            message = f"installation failed; concurrent or changed files were left in place: {exc}"
            if backup_path is not None:
                message += "; backup was retained for recovery: "
            else:
                message += "; manual recovery may be needed: "
            message += "; ".join(rollback_errors)
        raise InstallerError(message) from exc


def command_install(args: argparse.Namespace) -> int:
    if args.yes and not args.preset:
        raise InstallerError("--yes requires --preset")
    preset = args.preset or _choose_preset()
    home = normalize_home(args.codex_home)
    sources, requirements = load_preset(preset)
    state = _preflight_install(home, sources)

    catalogue: dict[str, set[str]] | None = None
    unavailable: str | None = None
    try:
        catalogue = catalog_from_file(args.models_file) if args.models_file else live_catalog()
    except InstallerError as exc:
        unavailable = str(exc)
    issues = requested_model_issues(requirements, catalogue) if catalogue is not None else []
    verification = _format_verification(issues, unavailable)
    print(verification)

    if args.dry_run:
        print(f"dry run: would install preset {preset} to {home}")
        for source in sources:
            print(f"  {source.relative_path}")
        if unavailable is not None:
            print("dry run: no files were written; model requirements remain unverified")
        return 0

    unverified = unavailable is not None or bool(issues)
    if args.yes:
        if unverified and not args.allow_unverified_models:
            raise InstallerError(
                "refusing unverified model requirements; rerun with --allow-unverified-models "
                "only to install the preset unchanged"
            )
    elif unverified:
        if not _confirm(
            "Install the preset unchanged acknowledging that unavailable model requirements may not run? [y/N]: "
        ):
            raise InstallerError("installation cancelled")
    elif not _confirm(f"Install preset {preset} to {home}? [y/N]: "):
        raise InstallerError("installation cancelled")

    refreshed_sources, _ = load_preset(preset)
    if refreshed_sources != sources:
        raise ConflictError("package source changed after review; rerun installation")
    refreshed_state = _preflight_install(home, refreshed_sources)
    if refreshed_state != state:
        raise ConflictError("installer state changed after review; rerun installation")
    sources = refreshed_sources
    state = refreshed_state
    desired_hashes = {source.relative_path: sha256_bytes(source.content) for source in sources}
    if state.installed and state.preset == preset and state.files == desired_hashes:
        print(f"preset {preset} is already installed and matches its owner manifest")
        return 0
    apply_install(home, preset, sources, state)
    if unverified:
        print("installed unchanged with unverified model requirements; no model substitutions were made")
    else:
        print(f"installed preset {preset} to {home}")
    return 0


def command_status(args: argparse.Namespace) -> int:
    home = normalize_home(args.codex_home)
    try:
        state = _read_manifest(home)
    except InstallerError as exc:
        print(f"status: drifted ({exc})")
        return 1
    if not state.exists or not state.installed:
        print("status: not installed")
        return 0
    try:
        _assert_destination_layout(home, state)
        _validate_existing_owned_files(home, state)
    except InstallerError as exc:
        print(f"status: drifted ({exc})")
        return 1
    print(f"status: installed preset {state.preset}; {len(state.files)} managed files match manifest")
    return 0


def _uninstalled_manifest_bytes(preset: str) -> bytes:
    return _manifest_bytes(preset, {}, installed=False)


def command_uninstall(args: argparse.Namespace) -> int:
    home = normalize_home(args.codex_home)
    state = _read_manifest(home)
    if not state.exists or not state.installed:
        print("uninstall: nothing installed")
        return 0
    _assert_destination_layout(home, state)
    _validate_existing_owned_files(home, state)
    if not args.yes and not _confirm(f"Remove preset {state.preset} from {home}? [y/N]: "):
        raise InstallerError("uninstall cancelled")

    original_files = {relative: _destination(home, relative).read_bytes() for relative in state.files}
    manifest = _manifest_path(home)
    try:
        for relative in sorted(state.files):
            target = _destination(home, relative)
            if _is_symlink(target) or sha256_bytes(target.read_bytes()) != state.files[relative]:
                raise ConflictError(f"managed file changed during uninstall: {target}")
            target.unlink()
        skill_directory = home / "skills" / "codex-balanced-agents"
        try:
            skill_directory.rmdir()
        except OSError:
            pass
        _atomic_write(manifest, _uninstalled_manifest_bytes(state.preset or "balanced"))
    except Exception as exc:
        rollback_errors: list[str] = []
        for relative, content in original_files.items():
            target = _destination(home, relative)
            if not target.exists():
                try:
                    _ensure_directory(target.parent, [])
                    _atomic_write(target, content)
                except Exception as rollback_exc:  # pragma: no cover - exceptional disk failure path
                    rollback_errors.append(f"{relative}: {rollback_exc}")
        message = f"uninstall failed and managed files were restored: {exc}"
        if rollback_errors:
            message += "; manual recovery may be needed: " + "; ".join(rollback_errors)
        raise InstallerError(message) from exc
    print("uninstalled managed preset files; backups and inactive owner manifest were retained locally")
    return 0


def command_models(args: argparse.Namespace) -> int:
    catalogue = catalog_from_file(args.models_file) if args.models_file else live_catalog()
    print("Model catalogue (advisory; it does not verify account entitlement):")
    for model in sorted(catalogue):
        efforts = ", ".join(sorted(catalogue[model])) or "none"
        print(f"  {model}: {efforts}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", default=None, help="Codex home (default: CODEX_HOME or ~/.codex)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    install = subparsers.add_parser("install", help="install a preset")
    install.add_argument("--codex-home", dest="codex_home", default=argparse.SUPPRESS)
    install.add_argument("--preset", choices=PRESETS)
    install.add_argument("--yes", action="store_true", help="skip the one installation review prompt")
    install.add_argument("--dry-run", action="store_true", help="validate and show planned files without writing")
    install.add_argument("--allow-unverified-models", action="store_true")
    install.add_argument("--models-file", help="offline JSON capture of a model/list result")
    install.set_defaults(handler=command_install)

    status = subparsers.add_parser("status", help="check manifest and managed file hashes")
    status.add_argument("--codex-home", dest="codex_home", default=argparse.SUPPRESS)
    status.set_defaults(handler=command_status)

    uninstall = subparsers.add_parser("uninstall", help="remove verified managed files")
    uninstall.add_argument("--codex-home", dest="codex_home", default=argparse.SUPPRESS)
    uninstall.add_argument("--yes", action="store_true", help="skip the removal review prompt")
    uninstall.set_defaults(handler=command_uninstall)

    models = subparsers.add_parser("models", help="list the advisory local model catalogue")
    models.add_argument("--codex-home", dest="codex_home", default=argparse.SUPPRESS)
    models.add_argument("--models-file", help="offline JSON capture of a model/list result")
    models.set_defaults(handler=command_models)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except InstallerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
