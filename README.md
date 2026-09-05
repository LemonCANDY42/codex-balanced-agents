# Codex Balanced Agents

[中文](README.zh-CN.md) · [Install](INSTALL.md) · [Role guide](docs/roles.md) · [Verification](docs/verification.md)

**A personal Codex setup for matching subagents to the task.**

Small, clear jobs go to lighter models. Dense implementation gets a bounded Worker. Ambiguous problems get deeper investigation. A separate Reviewer checks the candidate against the original request.

This repository packages that approach as **14 native Codex roles, two presets, and one installer**. It is for individual developers who want an understandable starting point they can inspect and adapt.

![Architecture: the lead owns scope and final acceptance; Explore, Plan, Worker and Review return bounded results. Quality and Balanced use the same roles with different routine reasoning effort.](assets/architecture.png)

## Start with the task

Start with **Balanced** if you do not have a preference. It gives the four routine Luna/Terra Explore and Worker roles a `medium` reasoning-effort default; **Quality** retains their `xhigh` defaults. The presets otherwise install the same role names, instructions, escalation paths and scope boundaries. The names describe preset choices, not measured quality, cost or speed.

Choose the role again for each delegated outcome. An installed role has a fixed model and reasoning-effort default; this package has no adaptive-effort mechanism or router. Matching Explore and Worker defaults do not require the same model or effort choice across phases, and installing either preset does not change the lead model. [How to read the exact defaults and select a role →](docs/roles.md)

## Install with your agent

Paste this into Codex:

```text
Read https://raw.githubusercontent.com/LemonCANDY42/codex-balanced-agents/main/INSTALL.md
and install Codex Balanced Agents. Let me choose Quality or Balanced.
Ask at most two questions in total. Preserve my existing configuration.
Explain missing models before any installation; never silently substitute them.
```

Or use the terminal with Python 3.11+ and an already installed Codex CLI:

```bash
git clone https://github.com/LemonCANDY42/codex-balanced-agents.git
cd codex-balanced-agents
python3 install.py install
```

The installer asks once for the preset and once to review the installation. If model requirements are missing or cannot be checked, the second question lets you cancel or explicitly install the unchanged files knowing those roles may not run. It never asks model by model.

It installs role files and one routing skill under your Codex home. It does **not** replace your main model, `config.toml`, global `AGENTS.md`, authentication, or MCP configuration. Existing unmanaged role files are conflicts, even when their contents happen to match. [Installation details, updates and removal →](INSTALL.md)

## Uninstall with your agent

Paste this into Codex:

```text
Read https://raw.githubusercontent.com/LemonCANDY42/codex-balanced-agents/main/UNINSTALL.md
and uninstall Codex Balanced Agents from the same Codex home used for installation.
Preview the exact removals first, then remove only verified package-owned files.
Preserve unrelated configuration and user modifications; stop on any conflict.
```

Or, from this repository: `python3 install.py uninstall --yes`.
Use `--dry-run` to preview without changes. [Removal boundaries and recovery →](UNINSTALL.md)

## Use it on a real task

After installation, restart your Codex client and try:

```text
Use $codex-balanced-agents for this bug. Have explore_terra locate the owning
code and return evidence when bounded synthesis is needed. If it establishes a
clear mechanical edit, have worker_luna implement only that edit and validate it.
Have reviewer_sol inspect the finished diff against the original requirement.
Keep integration and final acceptance with you. Preserve unrelated changes.
```

You do not need all 14 roles on every task. Work directly when delegation would add more coordination than value. The installed skill supplies selection guidance; your prompt or project guidance authorizes delegation. There is no background router, custom agent runtime, or mandatory four-stage pipeline.

## What this setup tries to get right

- **Separate uncertainty from execution.** Investigate missing ownership or lifecycle facts before asking a Worker to implement a guess.
- **Make escalation specific.** A concrete blocker or difficult boundary can justify a stronger role. Task size alone does not.
- **Keep scope visible.** Workers have an owning boundary and acceptance checks. A nearby defect is a finding, not permission for extra work.
- **Make review useful.** Reviewers report a location, trigger, evidence and impact. They do not turn style preferences into new requirements.
- **Keep the lead accountable.** Children return results; the lead integrates, resolves findings and verifies the outcome.

[Worked example →](docs/example.md) · [Why these choices and what inspired the packaging →](docs/design.md)

## Limits worth understanding

This is a **personal practice configuration**, not an official OpenAI preset or a proven cost optimizer. More reasoning and more agents can increase latency and token use. We have not run a representative benchmark establishing quality gains, speedups or savings between these presets.

Role instructions do not create a security boundary. In the Codex versions examined here, child permissions and MCP configuration come from the parent; role-local sandbox/delegation settings are not applied. The exported files deliberately omit those ineffective settings. The no-edit and no-further-delegation rules are behavioral instructions. [Versioned evidence and current validation →](docs/verification.md)

Model availability depends on your account, provider and client. The installer checks the CLI's advertised model/effort catalogue; that is not an entitlement or successful-inference test. The app and a separately installed CLI may expose different catalogues.

The role tiers, model choices and reasoning defaults will evolve with model capabilities and hands-on experience, considering completion, rework and latency alongside usage patterns. [How the tiers will evolve →](docs/design.md#how-the-tiers-will-evolve--后续优化与分级)

## Feedback

Found an installation problem, confusing role behavior, or a use case this setup does not cover? [Choose an issue template](https://github.com/LemonCANDY42/codex-balanced-agents/issues/new/choose): bug report, improvement, or question. All templates use English field names and prompts; responses may be in English or Chinese. For agent, CLI or API submissions, follow the same fields in the [issue guide](docs/issues.md). Remove credentials and private information before posting.

Feedback is currently collected through Issues. [MIT licensed](LICENSE).

Community: [LINUX DO](https://linux.do/) — a place to exchange development ideas and experience.
