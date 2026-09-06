# Role guide / 角色说明

[English README](../README.md) · [中文 README](../README.zh-CN.md)

## Task-led selection / 按任务判断

The lead decides whether delegation helps, which role fits, how many agents to use, and what context to share. Role descriptions describe capabilities rather than mandatory routes. No task must pass through Explore, Plan, Worker and Review, and a deeper role does not require a failed lower-effort attempt first.

主代理判断是否需要委派、选择哪个角色、需要几个代理，以及传递多少上下文。角色说明描述适用能力，不规定必经路径。任务不必走完调查、规划、实现、审查，也不必先让低档角色失败才能选择更深入的角色。

UI work follows the same judgment: demanding design or interaction work may benefit from Astra high, but UI alone does not require it. Choose the model and reasoning profile for the actual assignment, including its context, uncertainty and verification needs.

UI 工作同样按任务判断：复杂设计或交互可能受益于 Astra high，但不因涉及 UI 就固定使用它。模型与推理档位的选择应结合具体任务、上下文、不确定性与验证需要。

The installed role descriptions provide their capabilities and boundaries; no separate skill is needed. Explore and Plan return evidence or a proposal; Worker implements within authorization; Reviewer checks a candidate when independent review has a concrete benefit. The lead retains scope, integration and acceptance.

已安装角色的说明提供能力定位与边界，无需额外技能。Explore 和 Plan 返回证据或方案；Worker 在授权内实施；独立审查有明确收益时由 Reviewer 检查候选。主代理负责范围、整合与验收。

Installed role files fix the model and default reasoning effort. The lead selects among these profiles; this package does not dynamically change their settings or the lead model. Quality and Balanced retain the same 14 roles and instructions, differing only in four Luna/Terra effort defaults.

已安装角色固定模型和默认推理档位，主代理在这些配置之间选择；本项目不会动态改变角色设置或主模型。Quality 和 Balanced 保留相同的 14 个角色与指令，仅四个 Luna/Terra 推理默认值不同。

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
