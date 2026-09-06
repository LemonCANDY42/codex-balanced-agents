# Codex Balanced Agents

[English](README.md) · [安装](INSTALL.zh-CN.md) · [角色说明](docs/roles.md) · [验证记录](docs/verification.md)

**一套个人使用的 Codex 配置：按任务选择子代理，让分工更清楚。**

明确的小任务交给轻量模型；逻辑密集的实现交给有明确边界的 Worker；复杂、模糊的问题交给更深入的调查角色。独立审查有明确收益时，再让 Reviewer 对照原需求检查。

这个仓库把这种方式整理为 **14 个原生 Codex 角色、两套配置和一个安装器**，面向希望兼顾能力、效率与成本的个人开发者。配置可以直接阅读，也方便按自己的任务调整。

![架构：主代理负责范围、委派、整合与最终验收；Explore、Plan、Worker、Review 各自返回有界结果。Quality 和 Balanced 保留同一套角色，调整日常任务的推理投入。](assets/architecture.png)

## 从任务出发

没有明确偏好时，建议从 **Balanced** 开始：四个日常 Luna/Terra 调查与实现角色的默认推理档位为 `medium`；**Quality** 保留它们的 `xhigh` 默认档位。其余角色名称、指令、选择指南与工作边界完全相同。名称用于区分预设，不代表已测得的质量、费用或速度优势。

每次委派都应按当前要交付的结果重新选择角色。安装后的角色文件固定了模型和默认推理档位；本项目没有自适应推理机制或后台路由器。调查角色与实现角色恰好有相同默认值，并不要求不同阶段选择相同模型或推理档位；安装任一预设也不会改变主代理模型。[查看角色选择与完整默认值 →](docs/roles.md)

## 让 agent 帮你安装

把下面这段发给 Codex：

```text
读取 https://raw.githubusercontent.com/LemonCANDY42/codex-balanced-agents/main/INSTALL.zh-CN.md
并安装 Codex Balanced Agents，让我选择 Quality 或 Balanced。
整个流程最多问我两次。保留现有配置；如果缺少模型，先说明并让我选择处理方式，不要静默替换。
```

也可以在终端安装，需要 Python 3.11+ 和已安装的 Codex CLI：

```bash
git clone https://github.com/LemonCANDY42/codex-balanced-agents.git
cd codex-balanced-agents
python3 install.py install
```

第一次选方案，第二次集中确认安装。如果缺少模型或无法检查，第二次可以选择取消，或明确接受“原样安装，但部分角色可能暂时不能运行”。不会逐个模型追问。

安装器仅安装 14 个原生角色及本机归属记录，不安装技能或常驻工作流指令；不会覆盖主模型、`config.toml`、全局 `AGENTS.md`、认证或 MCP。遇到不归它管理的同名文件会停止，即使内容相同也不会擅自接管。[安装、切换与卸载 →](INSTALL.zh-CN.md)

## 让 agent 一键卸载

把下面这段发给 Codex：

```text
读取 https://raw.githubusercontent.com/LemonCANDY42/codex-balanced-agents/main/UNINSTALL.zh-CN.md
并从安装时使用的 Codex 目录卸载 Codex Balanced Agents。
先预览确切删除清单，再仅删除通过归属与完整性检查的本项目文件。
保留无关配置和用户修改；遇到冲突就停止。
```

也可在本仓库执行：`python3 install.py uninstall --yes`。
使用 `--dry-run` 可只预览、不改动。[删除边界与恢复说明 →](UNINSTALL.zh-CN.md)

## 安装之后

重新启动 Codex，让客户端发现原生角色。直接描述要完成的工作，并在适当时授权委派：

```text
修复这个 bug。仅在有帮助时使用已安装的子代理，按任务选择角色和所需上下文。
保留无关改动，并验证结果。
```

是否委派、如何使用角色由主代理判断，无需调用额外技能，也没有必经阶段或后台路由。[角色参考 →](docs/roles.md)

## 这套配置关注什么

- **先处理不确定性，再执行。** 归属、生命周期等事实还不清楚时，先调查。
- **按任务选角色。** 角色定位只作选择参考，不要求固定顺序、UI 专用模型或先失败再使用更深入的角色。
- **实现有范围。** Worker 有负责的边界与验收条件，发现附近的问题不等于获准顺手修改。
- **审查有证据。** Reviewer 给出位置、触发条件和影响，不把个人风格偏好变成新需求。
- **主代理负责收尾。** 子代理返回结果，主代理整合、处理发现并验收。

[使用示例 →](docs/example.md) · [设计依据与参考 →](docs/design.md)

## 使用边界

这是**个人实践配置**，不是 OpenAI 官方预设，也不是已经证明有效的成本优化器。更多推理和更多代理可能增加耗时与 token 消耗，目前没有代表性基准证明两套配置之间的质量、速度或费用差异。

角色提示词不会建立安全隔离。在本仓库核对的 Codex 版本中，子代理继承父会话权限与 MCP；角色内的 sandbox 和委派开关不生效，因此公开配置没有保留这些无效项。“只读”和“不再委派”属于行为要求。[版本依据与验证记录 →](docs/verification.md)

模型可用性取决于账号、服务提供方与客户端。安装器查询 CLI 公布的模型及推理档位目录，这不等于验证了账号权限或实际推理成功。桌面应用与单独安装的 CLI 可能返回不同目录。

后续会根据模型能力与实际使用体验，持续优化角色分级、模型选择和推理档位，并结合调用分布、任务完成情况、返工与耗时调整。[后续优化思路 →](docs/design.md#how-the-tiers-will-evolve--后续优化与分级)

## 问题与反馈

遇到安装问题、角色行为不清楚，或有尚未覆盖的使用场景，欢迎[选择 Issue 模板](https://github.com/LemonCANDY42/codex-balanced-agents/issues/new/choose)：问题报告、改进建议或使用疑问。模板字段与提示统一使用英文，内容仍可用中文或英文填写。通过 agent、CLI 或 API 提交时，请按[提交指南](docs/issues.md)填写相同字段。发布前请移除凭据与隐私信息。

目前优先通过 Issue 收集反馈。采用 [MIT 许可](LICENSE)。

社区交流：[LINUX DO](https://linux.do/)，交流开发思路与使用经验。
