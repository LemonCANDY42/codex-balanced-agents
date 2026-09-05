# Verification / 验证记录

[English README](../README.md) · [中文 README](../README.zh-CN.md)

Evidence date: **2026-09-05**. This file separates package checks, client behavior and task-quality evidence.

## Package checks / 文件与安装检查

The two presets contain 14 matching role names. Their only differences are the four documented Luna/Terra reasoning-effort values. Public role files contain only name, description, model, reasoning effort and developer instructions; no personal paths, credentials or MCP inventory are exported.

The offline installer suite uses temporary homes and fake model catalogues. It covers fresh installation, preset switching, idempotency, conflicts before writes, unchanged unrelated configuration, symlink refusal, dry runs, missing-model acknowledgement, at-most-two interactive prompts, uninstall drift and caught-write rollback. Package checks also validate cross-preset invariants and local document links.

两套方案各有 14 个同名角色，仅四个 Luna/Terra 档位不同。安装测试使用临时目录与模拟模型目录，覆盖安装、切换、重复执行、冲突保护、无关配置保留、符号链接、dry run、缺失模型确认、最多两次提问、卸载与写入错误回滚。它们不证明模型推理质量。

Run locally with Python 3.11+:

```bash
python3 -m unittest discover -s tests -v
```

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

The source function remained unchanged. The recorded child permissions inherited the read-only parent. This verifies sampled role loading and execution, not that role instructions can constrain a full-access parent. Other role/model combinations were not individually executed. The test requested roles explicitly and restricted the skill-catalogue budget; it does not verify implicit routing-skill activation. No private session logs or authentication files are included in the repository.

使用桌面捆绑的 0.153.4 在临时 Codex 目录启动了两个新会话，均列出了 14 个自定义角色。子会话记录确认上表模型与档位；示例错误被正确指出，源文件未变。父会话明确设为只读，这不证明角色能限制全权限父会话。未逐一执行全部角色，也未验证技能的隐式触发；仓库没有收录私有会话日志或认证文件。

## Task-quality evidence / 任务效果

No representative A/B benchmark has established that Quality is more accurate or that Balanced saves a particular amount of time or money. The example in this repository is illustrative. Treat preset labels as intended tradeoffs and evaluate them on your own tasks.

目前没有代表性的 A/B 基准证明 Quality 更准确，或 Balanced 节省多少时间与费用。仓库使用示例属于说明性案例，请结合自己的任务选择。
