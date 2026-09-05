# Design notes / 设计说明

[English README](../README.md) · [中文 README](../README.zh-CN.md)

## The problem / 问题

A model can do the wrong work very thoroughly. Increasing reasoning effort does not fix an unclear assignment, and starting more agents can duplicate work or spread an unresolved design decision across several implementations.

This package keeps the main agent responsible for the task and gives children bounded jobs. Model choice and reasoning effort are separate decisions: an inexpensive model at high effort is not automatically the best choice for a simple lookup.

模型可能非常认真地做错方向。提高推理档位不能替代清楚的任务，多开代理也可能重复调查，或把尚未决定的设计扩散到多个实现。这里由主代理负责整体结果，子代理承担明确的局部任务；模型与推理档位分别选择。

## Two presets, one behavior contract / 两套方案，同一套边界

Quality retains the author's prior `xhigh` defaults for four Luna/Terra roles. Balanced sets those same roles to `medium`, while preserving the Sol, Astra and planning defaults. Quality and Balanced are names for these two sets of defaults; they do not describe a measured winner. The lead model is outside the package and is unchanged.

Quality 保留作者原先四个 Luna/Terra 角色的 `xhigh` 默认值；Balanced 将这四个角色设为 `medium`，同时保留 Sol、Astra 与规划角色的默认值。Quality 和 Balanced 是这两套默认值的名称，不代表已测得哪一套更好。主代理模型不属于本项目配置，也不会被改变。

For every delegation, the lead selects the role from the task's evidence. That role's model and effort are fixed together in the selected role file, but model and effort remain separate dimensions of the configuration. This package has a selection guide, not an adaptive-effort controller or runtime router; matching Explore and Worker defaults never require matching selections.

每次委派时，主代理根据任务证据选择角色。被选中角色文件会一并固定模型和推理档位，但模型与推理档位仍是配置中的两个独立维度。本项目只有选择指南，没有自适应推理控制器或运行时路由器；调查与实现角色默认值相同，也不要求两者选择保持一致。

### Author's motivation / 作者的观察

For bounded research or implementation with a capable lead and clear instructions, the author has often found that higher effort takes longer without a noticeable gain. In personal GPT-5.6 use, a larger model or higher effort has sometimes expanded scope, added excessive testing, or introduced regressions. These are anecdotal observations that motivated the two presets, not a benchmark result or a general claim about models or effort.

在主代理能力足够且指令清楚的范围明确的调研或实现中，作者常观察到更高推理档位耗时更长，却没有明显收益。在个人使用 GPT-5.6 的过程中，更大的模型或更高推理档位有时会扩大范围、加入过多测试，或引入回归。这些只是促成两套预设的个人观察，不是基准结果，也不是关于模型或推理档位的普遍结论。

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
