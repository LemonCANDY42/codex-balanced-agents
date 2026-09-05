# Role guide / 角色说明

[English README](../README.md) · [中文 README](../README.zh-CN.md)

The same 14 role names and instructions are installed by both presets. Only the four Luna/Terra effort values differ. / 两套使用同样的 14 个角色与指令，仅四个 Luna/Terra 角色的推理档位不同。

| Role | Model | Quality | Balanced |
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

## Selection boundaries / 选择边界

The self-contained [routing skill](../skills/codex-balanced-agents/SKILL.md) is the maintained selection table. Every role also contains its own scope and handoff rules. / 选择逻辑维护在自包含的[使用技能](../skills/codex-balanced-agents/SKILL.md)中，每个角色也有自己的范围和交接要求。

- **Explore / 调查**: Luna for direct lookup; Terra for bounded synthesis; Astra for difficult ownership, lifecycle or root-cause investigation. UI exploration uses Astra high.
- **Plan / 规划**: Astra high for non-routine planning; xhigh only after a concrete unresolved planning blocker. Return acceptance criteria with the plan.
- **Worker / 实现**: Luna for clear mechanical work; Terra for established patterns; Sol for dense logic inside an accepted design; Astra for difficult implementation. Astra low is for executing an already-understood difficult design. UI implementation uses Astra high.
- **Review / 审查**: Sol high for a bounded frozen candidate; Astra medium for high-risk cross-layer, lifecycle, concurrency or root-cause uncertainty. Review does not authorize repair or redesign.

The all-UI-to-Astra-high rule is a personal preference for delegated UI work, not an official requirement or a claim that simple UI tasks need an expensive model. The lead can complete small tasks directly. / 将委派的 UI 工作交给 Astra high 是个人质量偏好，并非官方要求；简单任务可以由主代理直接完成。

These roles are separate options, not a sequence that must run from Luna to Astra. When evidence already establishes a difficult boundary, choose the appropriate role directly. / 角色是可选分工，并非必须逐级跑完的流程；已有证据证明难度时可直接选合适角色。
