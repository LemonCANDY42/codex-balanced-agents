---
name: codex-balanced-agents
description: Use the installed Codex Balanced Agents roles when the user requests delegated coding work, or when project guidance calls for independent exploration, bounded implementation, planning, or review. Select task-appropriate roles and keep integration with the lead.
---

# Codex Balanced Agents

Use only installed roles exposed by the current runtime. Do not invent a role, silently substitute its model, or treat a role file as proof that the host loaded it. If a role is missing, report the discrepancy and ask the user to restart the client or choose how to proceed.

## Delegate deliberately

Keep requirements, decisions, integration, and final acceptance with the lead. Work directly on small or tightly coupled tasks. Delegate a concrete independent outcome only when authorized by the user or applicable project guidance and it materially helps. Start with one child; add more only for independent work. Do not duplicate its investigation in the lead. These are selection instructions, not a deterministic router or a token budget enforcer.

Choose the lightest sufficient role:

| Task | Role | Escalate when |
| --- | --- | --- |
| Direct low-risk lookup | `explore_luna` | Bounded synthesis needs `explore_terra` |
| Bounded evidence synthesis | `explore_terra` | Material architecture, ownership, lifecycle, or root-cause uncertainty needs `explore_astra` |
| Difficult investigation | `explore_astra` | A concrete unresolved conflict needs `explore_astra_high` |
| UI investigation | `explore_astra_high` | Return an evidence gap to the lead |
| Non-routine planning | `plan_astra` | A concrete planning blocker needs `plan_astra_xhigh` |
| Clear mechanical implementation | `worker_luna` | Existing logic needs `worker_terra` |
| Established implementation patterns | `worker_terra` | Dense logic within fixed design needs `worker_sol` |
| Dense, bounded implementation | `worker_sol` | Uncertain architecture/lifecycle or difficult root cause needs `worker_astra` |
| Approved difficult design, clear execution | `worker_astra_low` | New material uncertainty needs the lead |
| Difficult implementation/debugging | `worker_astra` | Evidence justifies exceptional depth in `worker_astra_high` |
| UI implementation | `worker_astra_high` | Return a boundary decision to the lead |
| Frozen candidate review | `reviewer_sol` | High-risk cross-layer, lifecycle, concurrency, or root-cause uncertainty needs `reviewer_astra` |

The all-UI-to-Astra-high choice is this preset's quality preference. Do simple UI edits directly when delegation adds no value. Role effort is defined in the selected preset; do not equate the model's name with task-specific superiority.

## Give a complete assignment

Supply the outcome/question, owning modules, non-goals, known facts, acceptance checks, and expected result. Prefer an explicit role and fresh context (for example `fork_turns="none"` when the tool supports it). Give only the context the child needs. Tell a Worker it is not alone and must preserve concurrent changes.

Explore and Plan return evidence or a proposal. Worker implements within its boundary and returns validation. Reviewer reviews one frozen candidate and returns concrete defects with location, trigger, and impact. Children return to the lead rather than starting their own teams. The lead resolves findings within the original authorization; re-review only after a material revision or unresolved risk.

## Check effective permissions

Read-only work and no child delegation are behavioral instructions. Tested Codex versions inherit parent permissions and do not apply role-local sandbox, MCP, or delegation settings. External tools have separate permissions and can remain inherited; no universal MCP denylist is installed. Inspect the actual tool surface and respect the user's permissions. Never describe this package as a security sandbox or an automatic cost optimizer.
