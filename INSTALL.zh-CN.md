# 安装 Codex Balanced Agents

[English](INSTALL.md) · [README](README.zh-CN.md)

本文件也供 agent 代用户安装时使用。只安装本项目文件，不替换主模型、全局指导、认证、MCP 或其他角色。

## Agent 安装流程：最多两次提问

1. 阅读 README 与 `install.py`，把仓库克隆到新目录，不覆盖已有目录。用户指定版本时使用指定版本，否则克隆默认分支，并报告检查过的 commit。
2. **第一次提问**：用户尚未选择时，询问 Quality 或 Balanced。日常使用推荐 Balanced；两套均有 14 个角色，区别是 Luna/Terra 的 `xhigh` 与 `medium`，其余档位相同。
3. 检查 Python 3.11+、实际使用的 Codex 路径和版本。运行 `python3 install.py models`，再运行 `python3 install.py install --preset <方案> --dry-run`。模型目录不等于账号权限验证。失败或发现冲突时说明原因，不自动安装／升级 Codex，也不修改无关配置。
4. **第二次提问**：集中展示目标目录与变更。如果缺少模型／档位或无法验证，列出受影响角色，提供**取消（默认）**或**明确接受部分角色可能无法运行，原样安装**。全部可见时确认安装即可。不要逐个模型追问；用户已明确授权同样的安装变更时，不重复确认。
5. 执行 `python3 install.py install --preset <方案> --yes`。仅当用户明确选择接受未验证状态时，才加 `--allow-unverified-models`。不能因命令报错就自动补这个参数，也不能静默替换模型。
6. 运行 `python3 install.py status`。告知用户重启 Codex、确认角色可发现，再用一个小任务试用。区分文件安装成功、模型目录可见、角色实际运行三种证据；安装本身不额外发起推理任务。

第二次提问后若出现新问题，清楚报告并停止，不继续连续追问。后续由用户发起的修复属于另一次操作。已有选择和授权持续有效。

## 终端安装

```bash
git clone https://github.com/LemonCANDY42/codex-balanced-agents.git
cd codex-balanced-agents
python3 install.py install
```

Windows 可以用 `py -3.11` 替代 `python3`。终端交互同样最多两次提问；命令行指定方案后跳过第一次。

```bash
python3 install.py install --preset balanced --dry-run
python3 install.py install --preset balanced
python3 install.py status
```

仅在明确接受模型缺失或无法验证时：

```bash
python3 install.py install --preset quality --yes --allow-unverified-models
```

该命令只原样安装文件，不会开通模型权限。

## 安装内容

默认目标为 `$CODEX_HOME`，未设置时为 `~/.codex`。可在子命令后使用 `--codex-home /path/to/codex-home` 指定目录。

```text
<codex-home>/
  agents/                              所选方案的 14 个角色
  skills/codex-balanced-agents/SKILL.md 使用与选择指导
  codex-balanced-agents/manifest.json 所有权与文件哈希
  codex-balanced-agents/backups/      更新前的已管理版本
```

技能提供选择指导，不会自动启动代理团队。现代 Codex 自动发现独立 TOML 角色，无需向 `config.toml` 追加角色注册。

安装器写入前检查所有目标，拒绝接管不归它管理的同名文件、覆盖修改过的已管理文件或写入符号链接目标。`config.toml`、`AGENTS.md`、认证和 MCP 不属于它管理的内容。dry run 不写入本项目文件或状态；被调用的 Codex 进程可能维护自己的常规缓存／日志。

切换前结束正在运行的任务。不要并发运行安装器，也不要在安装时修改目标文件。更新保留旧文件备份，捕获写入错误时尝试回滚；这不是断电／进程被强制终止下的文件系统事务。备份只保存在本机，不上传。

## 模型与版本

`models` 通过 PATH 中的 `codex`，使用它已有的账号与配置调用 stdio `app-server` 的 `model/list`。安装器本身不登录、不发送推理请求、不购买额度，也不直接读取凭据。`--codex-home` 只指定安装目标，不改变查询所用账号；需要指定查询所用的 Codex home 时，设置环境变量 `CODEX_HOME`。

桌面捆绑版本与另装 CLI 可能不同，模型目录也可能不同。可通过 PATH 选择实际使用的可执行文件。缺少模型时，先决定换用合适客户端、取消，或接受暂时无法使用而原样安装；安装器不会自动升级软件。

离线检查／测试可通过 `--models-file capture.json` 提供 `model/list` 的 JSON response/result 或 `data` 数组。该方式信任输入目录，不证明当前模型权限。不要提供凭据或完整账号导出。

## 切换、更新与卸载

在干净的仓库目录中拉取并检查更新，再执行安装器。只有哈希仍匹配所有权记录的文件才会更新。

```bash
python3 install.py install --preset quality
python3 install.py status
python3 install.py uninstall
```

卸载只删除未被修改的已管理角色／技能文件，保留本机备份与停用状态记录。若你修改了已管理文件，先另外保存定制版本，再明确处理冲突；安装器不会擅自覆盖或删除它。不要通过删除 manifest 来强行更新。

一键卸载、agent 执行步骤、预览与确切保留边界见[卸载指南](UNINSTALL.zh-CN.md)。

若只想在单个项目使用，可手工把一套 TOML 放到 `.codex/agents/`，把使用技能放到 `.agents/skills/`。这条手工路径不归全局安装器管理，需要检查项目信任设置，并使用项目原有版本控制流程。
