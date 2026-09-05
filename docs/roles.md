# Role guide / 角色说明

[English README](../README.md) · [中文 README](../README.zh-CN.md)

## Choose per delegation / 每次委派单独选择

Choose a role for the concrete result you need now, then make the next choice from the evidence that returns. Explore, Plan, Worker and Review are options with different responsibilities, not stages that must use a matching model or reasoning effort. The lead may work directly when delegation would not help.

每次根据当前要交付的具体结果选择角色，再依据返回的证据决定下一步。Explore、Plan、Worker 和 Review 是职责不同的选项，不是必须使用相同模型或推理档位的阶段；委派没有帮助时，主代理可以直接完成工作。

The installed role files fix both a model and a reasoning-effort default. The matrix below separates those dimensions so a role choice is not mistaken for an effort choice alone. The package supplies guidance, not an adaptive-effort mechanism or a runtime router, and neither preset changes the lead model.

安装后的角色文件同时固定模型和默认推理档位。下表把两项分开列出，避免把选角色误解为只选推理档位。本项目提供的是选择指导，不含自适应推理机制或运行时路由器；任一预设都不会改变主代理模型。

Both presets install the same 14 role names and instructions. Quality and Balanced are names for two sets of defaults; only the four Luna/Terra reasoning-effort defaults differ. / 两套都安装相同的 14 个角色名称与指令。Quality 和 Balanced 是两套默认值的名称；仅四个 Luna/Terra 角色的默认推理档位不同。

## Selection boundaries / 选择边界

The self-contained [routing skill](../skills/codex-balanced-agents/SKILL.md) is the maintained selection table. Every role also contains its own scope and handoff rules. / 选择逻辑维护在自包含的[使用技能](../skills/codex-balanced-agents/SKILL.md)中，每个角色也有自己的范围和交接要求。

- **Explore / 调查**: Luna for direct lookup; Terra for bounded synthesis; Astra for difficult ownership, lifecycle or root-cause investigation. UI exploration uses Astra high.
- **Plan / 规划**: Astra high for non-routine planning; xhigh only after a concrete unresolved planning blocker. Return acceptance criteria with the plan.
- **Worker / 实现**: Luna for clear mechanical work; Terra for established patterns; Sol for dense logic inside an accepted design; Astra for difficult implementation. Astra low is for executing an already-understood difficult design. UI implementation uses Astra high.
- **Review / 审查**: Sol high for a bounded frozen candidate; Astra medium for high-risk cross-layer, lifecycle, concurrency or root-cause uncertainty. Review does not authorize repair or redesign.

### Short handoff example / 简短交接示例

If a bug report needs bounded synthesis across callers, ask `explore_terra` to identify the owning condition and return evidence. If that evidence leaves one clear mechanical edit, use `worker_luna` for the implementation. If the implementation instead relies on an established pattern and needs more judgment, use `worker_terra`; dense, bounded existing logic can justify `worker_sol`. The Worker follows the implementation task, not the Explore role's model or effort.

如果一个 bug 报告需要综合多个调用方的证据，可让 `explore_terra` 找到归属条件并返回证据。若证据表明只需一项明确的机械改动，实施时选 `worker_luna`；若实现依赖既有模式且需要更多判断，选 `worker_terra`；对范围明确的密集既有逻辑，可选 `worker_sol`。Worker 的选择取决于实现任务本身，而不是前一个 Explore 角色的模型或推理档位。

The all-UI-to-Astra-high rule is a personal preference for delegated UI work, not an official requirement or a claim that simple UI tasks need an expensive model. The lead can complete small tasks directly. / 将委派的 UI 工作交给 Astra high 是个人质量偏好，并非官方要求；简单任务可以由主代理直接完成。

These roles are separate options, not a sequence that must run from Luna to Astra. When evidence already establishes a difficult boundary, choose the appropriate role directly. / 角色是可选分工，并非必须逐级跑完的流程；已有证据证明难度时可直接选合适角色。

## Fixed models and reasoning effort defaults / 固定模型与推理档位默认值

The model column is the role's fixed model. The two reasoning-effort columns are the exact defaults installed by each preset. / “模型”列是角色固定使用的模型；两个“推理档位默认值”列是两套预设安装的精确默认值。

| Role | Model | Quality effort | Balanced effort |
| --- | --- | --- | --- |
| `explore_astra` | `gpt-6-astra` | `medium` | `medium` |
| `explore_astra_high` | `gpt-6-astra` | `high` | `high` |
| `explore_luna` | `gpt-5.6-luna` | `xhigh` | `medium` |
| `explore_terra` | `gpt-5.6-terra` | `xhigh` | `medium` |
| `plan_astra` | `gpt-6-astra` | `high` | `high` |
| `plan_astra_xhigh` | `gpt-6-astra` | `xhigh` | `xhigh` |
| `reviewer_astra` | `gpt-6-astra` | `medium` | `medium` |
| `reviewer_sol` | `gpt-5.6-sol` | `high` | `high` |
| `worker_astra` | `gpt-6-astra` | `medium` | `medium` |
| `worker_astra_high` | `gpt-6-astra` | `high` | `high` |
| `worker_astra_low` | `gpt-6-astra` | `low` | `low` |
| `worker_luna` | `gpt-5.6-luna` | `xhigh` | `medium` |
| `worker_sol` | `gpt-5.6-sol` | `high` | `high` |
| `worker_terra` | `gpt-5.6-terra` | `xhigh` | `medium` |

Quality keeps the prior `xhigh` defaults for the four Luna/Terra roles; Balanced uses `medium` for those same roles. Equal values in Explore and Worker are defaults for separate role files, not an instruction to pair them. / Quality 保留四个 Luna/Terra 角色原有的 `xhigh` 默认值；Balanced 将这四个角色设为 `medium`。调查和实现角色出现相同数值，是各自角色文件的默认值，并不要求把它们配对使用。
