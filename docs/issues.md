# Filing an issue / 提交 Issue

[Open the issue chooser / 选择 Issue 类型](https://github.com/LemonCANDY42/codex-balanced-agents/issues/new/choose)

Use English or Chinese. Pick **Bug report**, **Improvement**, or **Question**. Give the issue a specific title (for example, `[Bug] Balanced install stops on an unmanaged role file`) and keep one topic per issue. Search existing issues first and add new evidence there when it is the same problem.

可用中文或英文。选择**问题报告**、**改进建议**或**使用疑问**，标题说明具体问题（例如 `[Bug] 安装 Balanced 时遇到非托管角色文件后停止`），每条 Issue 聚焦一个主题。先搜索已有 Issue；如果是相同问题，请在原帖补充新证据。

Provide facts you observed. Mark unknowns, hypotheses and untested suggestions explicitly. A minimal example is enough; a complete root-cause analysis is not required. Remove credentials, private paths, account identifiers and private project content before posting. Do not attach full configuration files or session logs.

提供实际观察到的事实，明确标注未知信息、推测和未经验证的建议。最小示例即可，不要求先完成根因分析。发布前移除凭据、私人路径、账号标识和私有项目内容，不要附完整配置文件或会话日志。

## Agents, CLI and API / 通过 agent、CLI 或 API 提交

The YAML forms in [`.github/ISSUE_TEMPLATE`](../.github/ISSUE_TEMPLATE) are the source of truth for field names, prompts and required fields. GitHub's web form asks for these fields; CLI/API submissions can bypass the form. When using those routes, read the appropriate YAML file and write a Markdown body with `### <label>` for each field, in form order. Fill every required field; use `Unknown / 未知` or `Not applicable / 不适用` with a brief reason when appropriate. Optional fields may be omitted. The introductory `markdown` block is guidance, not a response field.

[`.github/ISSUE_TEMPLATE`](../.github/ISSUE_TEMPLATE) 中的 YAML 表单是字段名称、提示和必填要求的唯一来源。网页表单会引导填写，CLI/API 则可能绕过表单。使用这些途径时，先读取对应 YAML，按字段顺序以 `### <label>` 写 Markdown 正文。填写所有必填项；未知或不适用时请注明并简述原因。选填项可省略，开头的 `markdown` 块是说明，无需当作回答字段。

Use the form's title prefix and add a concrete summary. Do not claim to have run a command, reproduced a bug or searched existing issues unless you actually did. Submit only within the user's authorization; otherwise prepare the issue body for review.

使用表单的标题前缀并补充具体摘要。没有实际执行过命令、复现问题或搜索已有 Issue，就不要声称已经做过。仅在用户授权范围内提交，否则先准备正文供用户审阅。

```bash
# After preparing and reviewing issue.md / 准备并检查 issue.md 后
# Requires authorization to publish / 需要获得发布授权
gh issue create --repo LemonCANDY42/codex-balanced-agents \
  --title "[Bug] <specific summary>" --body-file issue.md
```

These templates guide reporting; they do not enforce a server-side schema on API submissions. No automated issue-closing workflow is installed.

模板用于引导反馈，不会对 API 提交执行服务端格式校验，也没有自动关闭 Issue 的工作流。
