# Example: a small bug with a tempting extra change

[English README](../README.md) · [中文 README](../README.zh-CN.md)

This is an illustrative assignment, not a recorded benchmark result.

Suppose a CSV importer accidentally discards rows with a blank optional note. The same module also contains an old parsing abstraction someone would like to replace.

1. The lead defines the outcome: retain rows with an empty optional note; preserve invalid required-field rejection. Replacing the parser is out of scope.
2. If evidence gathering is useful, `explore_terra` identifies the owning predicate and the direct consumers, then returns the relevant paths and uncertainty.
3. A bounded `worker_terra` assignment changes the predicate and checks both the blank-note case and invalid-required-field case. If the change instead requires a schema migration, it returns that decision to the lead.
4. `reviewer_sol` reviews the finished candidate against those requirements. A demonstrated regression is a finding. A preference for a new parsing framework is not a defect in the candidate.
5. The lead resolves findings, integrates the result and runs the appropriate final checks.

The value being sought is easy to inspect: one agreed outcome, bounded edits, evidence-based review and one owner of acceptance. The role files cannot guarantee those behaviors; verify them on your own tasks.

---

本例用于说明如何分工，不是已经记录的基准结果。

假设 CSV 导入器错误地丢弃了“可选备注为空”的行，同一个模块里又恰好有一套大家想替换的旧解析抽象。

1. 主代理明确目标：保留可选备注为空的行，但继续拒绝必填字段不合法的行。替换解析器不在范围内。
2. 确有调查价值时，`explore_terra` 定位判断条件和直接使用方，返回路径与不确定性。
3. `worker_terra` 在限定范围内修改条件，并验证正反两个行为。如果发现必须迁移数据结构，返回主代理决定。
4. `reviewer_sol` 对照原需求检查最终候选。可以复现的回归是问题；更喜欢另一个框架，不是候选缺陷。
5. 主代理处理发现、整合结果并完成最终检查。

希望得到的价值是可以检查的：一个明确目标、有限改动、有证据的审查，以及一个验收负责人。角色文件不能保证这些行为，需要在自己的任务中观察。
