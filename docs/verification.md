# Verification / 验证记录

[English README](../README.md) · [中文 README](../README.zh-CN.md)

Latest package evidence: **2026-09-06**; runtime observations below remain dated **2026-09-05**. This file separates package checks, client behavior and task-quality evidence.

## Package checks / 文件与安装检查

The two presets contain 14 matching role names. Their only differences are the four documented Luna/Terra reasoning-effort values. Public role files contain only name, description, model, reasoning effort and developer instructions; no personal paths, credentials or MCP inventory are exported.

The offline installer suite uses temporary homes and fake model catalogues. It covers fresh installation, preset switching, idempotency, conflicts before writes, unchanged unrelated configuration, symlink refusal, dry runs, missing-model acknowledgement, at-most-two interactive prompts, uninstall drift and caught-write rollback. Package checks also validate cross-preset invariants and local document links.

两套方案各有 14 个同名角色，仅四个 Luna/Terra 档位不同。安装测试使用临时目录与模拟模型目录，覆盖安装、切换、重复执行、冲突保护、无关配置保留、符号链接、dry run、缺失模型确认、最多两次提问、卸载与写入错误回滚。它们不证明模型推理质量。

The initial release passed the suite on Linux, macOS and Windows. GitHub Actions is now disabled and the workflow has been removed; maintainers run checks locally before publishing.

初始发布已通过 Linux、macOS 和 Windows 测试。当前已关闭 GitHub Actions 并移除 workflow，后续发布前由维护者在本地验证。

Run locally with Python 3.11+:

```bash
python3 -m unittest discover -s tests -v
```

## Roles-only update, 2026-09-06 / 仅安装角色更新

The current macOS suite passed **31 tests**. New checks verify 14-role installation without a skills directory, preservation of unrelated and symlinked skill directories across install/update/status/uninstall, refusal to directly update a legacy role-plus-skill installation, verified legacy uninstall followed by roles-only reinstall, and refusal to remove modified or symlinked legacy skill files. No real user installation was removed.

本次 macOS 测试通过 **31 项**。新增验证仅安装 14 个角色且不创建技能目录；安装、更新、状态检查与卸载均保留无关技能及其符号链接目录；旧版“角色加技能”安装不能直接覆盖更新，需验证卸载后重装；修改过的旧技能或符号链接路径会阻止删除。没有卸载真实用户配置。

Both presets also passed a subprocess CLI check starting from the previous published installer: install 15 managed files, refuse direct update without changing the manifest, preview/uninstall the verified legacy package, install 14 roles, check status, and uninstall again. Unrelated configuration remained byte-identical. These checks used temporary homes and a synthetic model catalogue, not live model inference.

两套预设还使用上一版已发布安装器完成子进程 CLI 验证：先安装 15 个受管理文件，确认直接更新拒绝且清单不变，再预览／卸载旧包、安装 14 个角色、检查状态并再次卸载。无关配置逐字节不变。验证使用临时目录与模拟模型目录，没有发起真实模型推理。

All role names, models and reasoning defaults are unchanged. Descriptions and instructions now leave delegation and role/context selection to the lead, while retaining authorization, read-only and verification boundaries. This is source/configuration evidence plus an independent review; the revised prompts have not been benchmarked for model behavior or savings. Linux and Windows have not been rerun for this update.

角色名称、模型与推理默认值均未改变。新版说明把委派及角色／上下文选择交给主代理，并保留授权、只读与验证边界。这些是源码与配置核对及独立审查证据，尚未对新版提示词做行为或节省额度的基准测试；此次更新尚未在 Linux、Windows 重跑。

## Uninstall boundary checks / 卸载边界检查

The 2026-09-05 suite passed 25 tests locally on macOS. New cases cover removal preview and cancellation, preserving unrelated settings/roles/skills/backups and user-added files, repeated uninstall and reinstall, rejection of unrelated manifest paths, modified/missing files, symlinked destinations/state, changes during confirmation, manifest changes before commit, commit failure rollback, and preservation of replacement files during rollback. These checks use temporary Codex homes; no real user installation is removed. The updated uninstall paths have not been rerun on Linux or Windows.

2026-09-05 的测试在 macOS 本机通过，共 25 项。新增覆盖预览与取消、无关配置／角色／技能／备份及额外文件保留、重复卸载与重装、清单越界、文件修改或缺失、符号链接、确认期间的修改、提交前清单变化、提交失败恢复以及恢复时保留后来出现的文件。均使用临时目录，没有卸载真实用户配置；本次更新尚未在 Linux 或 Windows 重跑。

Both presets also passed subprocess-based CLI install → removal preview → uninstall → status → repeated uninstall checks in temporary homes, with an unrelated configuration file remaining byte-identical.

两套方案还通过了子进程 CLI 的安装 → 卸载预览 → 卸载 → 状态 → 重复卸载检查，全程使用临时目录，无关配置文件逐字节保持一致。

## Version-specific role behavior / 角色加载的版本依据

Examined installed CLI **0.149.1** and desktop-bundled CLI **0.153.4**, and their matching tagged source. Modern CLI discovery accepts standalone agent TOML files without duplicated `config.toml` registrations.

The role loader projects a bounded subset of fields. Role-local sandbox, approval, MCP, apps tables and delegation configuration are not applied; parent authority is preserved. A small set of feature reductions is supported, but this public package does not install tool restrictions. Children are instructed to avoid edits/delegation where appropriate; that is a behavioral contract, not an enforcement claim.

核对版本为独立 CLI **0.149.1** 与桌面捆绑 CLI **0.153.4**。角色加载只应用有限字段，权限和 MCP 来自父会话。公开版因此去掉无效开关，保留清楚的行为要求；不能称为强制只读或禁止派生的安全隔离。

Primary sources:

- [0.153.4 role projection](https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/core/src/agent/role.rs#L37-L127).
- [0.149.1 parent-authority test](https://github.com/openai/codex/blob/rust-v0.149.1/codex-rs/core/src/agent/role_tests.rs#L449-L479).
- [Standalone role discovery](https://github.com/openai/codex/blob/rust-v0.149.1/codex-rs/core/src/config/agent_roles.rs#L20-L109).
- [Official subagent guidance](https://developers.openai.com/codex/subagents). Its broad configuration-layer description differs from the tagged implementation above; use versioned evidence for permission claims.

## Model catalogue checks / 模型目录检查

A live `model/list` probe completed against both installed executables. The separate 0.149.1 CLI did not advertise Astra; the desktop-bundled 0.153.4 executable did. Both listed the GPT-5.6 Luna/Terra/Sol effort combinations used here. This is why an installation explains missing models rather than silently substituting them.

This check reads the CLI's advertised catalogue. It does not verify entitlement, guarantee future availability, or show that every role has completed a task. The installer itself makes no inference calls.

实际查询发现两个客户端的目录不同：0.149.1 未列出 Astra，0.153.4 列出了。目录检查不是账号权限或每个角色运行成功的证明，安装过程也不会发起推理。

## Fresh-session smoke checks / 新会话验证

Using the desktop-bundled 0.153.4 CLI, two fresh sessions ran against isolated temporary Codex homes and a two-line synthetic function. The parent was explicitly read-only. Both reported all 14 custom role types in the active spawn schema, in addition to the built-in types.

The child session records showed:

| Preset | Executed role | Recorded model | Recorded effort | Result |
| --- | --- | --- | --- | --- |
| Balanced | `explore_luna` | `gpt-5.6-luna` | `medium` | Correctly identified the excluded final element |
| Balanced | `reviewer_sol` | `gpt-5.6-sol` | `high` | Reported a concrete trigger, wrong result and requirement violation |
| Quality | `explore_luna` | `gpt-5.6-luna` | `xhigh` | Correctly identified the same error |

The source function remained unchanged. The recorded child permissions inherited the read-only parent. This verifies sampled role loading and execution, not that role instructions can constrain a full-access parent. Other role/model combinations were not individually executed. The test requested roles explicitly and restricted the skill-catalogue budget; it did not verify implicit routing-skill activation (the skill has since been removed from the package). No private session logs or authentication files are included in the repository.

使用桌面捆绑的 0.153.4 在临时 Codex 目录启动了两个新会话，均列出了 14 个自定义角色。子会话记录确认上表模型与档位；示例错误被正确指出，源文件未变。父会话明确设为只读，这不证明角色能限制全权限父会话。未逐一执行全部角色，也未验证当时技能的隐式触发（项目现已移除该技能）；仓库没有收录私有会话日志或认证文件。

## Task-quality evidence / 任务效果

No representative A/B benchmark has established that Quality is more accurate or that Balanced saves a particular amount of time or money. The example in this repository is illustrative. Treat preset labels as intended tradeoffs and evaluate them on your own tasks.

目前没有代表性的 A/B 基准证明 Quality 更准确，或 Balanced 节省多少时间与费用。仓库使用示例属于说明性案例，请结合自己的任务选择。
