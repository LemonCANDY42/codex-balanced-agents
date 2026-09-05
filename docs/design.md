# Design notes / 设计说明

[English README](../README.md) · [中文 README](../README.zh-CN.md)

## The problem / 问题

A model can do the wrong work very thoroughly. Increasing reasoning effort does not fix an unclear assignment, and starting more agents can duplicate work or spread an unresolved design decision across several implementations.

This package keeps the main agent responsible for the task and gives children bounded jobs. Model choice and reasoning effort are separate decisions: an inexpensive model at high effort is not automatically the best choice for a simple lookup.

模型可能非常认真地做错方向。提高推理档位不能替代清楚的任务，多开代理也可能重复调查，或把尚未决定的设计扩散到多个实现。这里由主代理负责整体结果，子代理承担明确的局部任务；模型与推理档位分别选择。

## Two presets, one behavior contract / 两套方案，同一套边界

Quality retains the author's deeper Luna/Terra settings. Balanced changes those four roles to medium, while preserving Sol and Astra settings for denser or more uncertain work. This provides an explicit choice without maintaining two competing workflows. It does not establish that either preset wins on a particular task.

Quality 保留作者原先对 Luna/Terra 使用更多推理的设置；Balanced 将四个日常角色调为 medium，保留较复杂工作的 Sol/Astra 档位。两套共享工作方式，不维护两份不同的流程，也不预先声称哪套效果更好。

The 14 names make escalation choices visible. They are not a target number of agents per run. Keep tightly coupled work with one owner, and delegate independent evidence collection before parallelizing edits.

14 个名称让选择与升级路径可见，不代表每次要启动 14 个代理。紧密耦合的任务保持单一负责人，优先考虑可独立验证的调查工作。

## Official basis / 官方依据

[OpenAI's subagent guidance](https://developers.openai.com/codex/subagents) recommends narrow agents, clear tool and task boundaries, and different models/efforts for different work. It also notes that delegation consumes additional tokens and that parallel writes need care. The principles fit this design; the exact 14-role matrix is a personal choice, not an official recommendation.

[官方指导](https://developers.openai.com/codex/subagents)支持清楚分工、任务边界以及按任务选择模型／推理；同时提醒额外 token 和并行写入的协调成本。这里采用这些原则，具体 14 角色组合属于个人实践。

The documented configuration model and released role-loader implementation differ on permission overrides. See [verification](verification.md) for the versioned source evidence. This package does not carry ineffective role-local permission switches forward.

角色权限的文档描述与已发布实现存在差异，具体见[验证记录](verification.md)。本项目没有继续保留已确认无效的角色权限开关。

## Packaging references / 仓库表达参考

- [Superpowers](https://github.com/obra/superpowers): explain what happens during a task, then provide a short installation path.
- [Claude Code Best Practice](https://github.com/shanraisshan/claude-code-best-practice): make examples and reference material easy to navigate.
- [ECC](https://github.com/affaan-m/ECC): explicit onboarding and multilingual entrypoints.
- [Trail of Bits Codex Config](https://github.com/trailofbits/codex-config): label opinionated defaults and distinguish component installation from blanket config replacement.

These are presentation references, not dependencies or endorsements. No third-party role or installer code was copied from them. Public files were authored for this package from the author's own role configuration and the cited runtime behavior.

以上仅作为结构与表达参考，不是依赖或背书；没有复制它们的角色或安装代码。公开文件基于作者自身配置与核对过的运行时行为编写。
