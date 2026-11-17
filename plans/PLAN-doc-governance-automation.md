---
audience: human
status: current
implementation_status: done
---

# 计划：文档规范自动化巡检与 DSH/SA 同步

## 目标

- DSH 助手与 SA 同时遵守现有文档规范。
- 每天自动巡检，结果写本机报告；仅异常时发飞书，减少人工注意力。
- 机械问题自动处理，规范类特殊情况才需要人判断。

## 范围

- 跨仓检查入口：`personalCloud/workspace/scripts/check.sh`
- 每日巡检与飞书通知：新增 `personalCloud/workspace/scripts/docs-watch.sh`
- 定时器安装：新增 `personalCloud/workspace/scripts/install-doc-watch.sh` 与 `personalCloud/workspace/systemd/dsh-docs-watch.{service,timer}`
- 提交前门禁：`personalCloud/task/dsh-context-guard/lib/doc-guard.js`、`index.js`、`test.mjs`
- 规则同步：根 `AGENTS.md`、`personalCloud/workspace/_meta/doc/task-workflow.md`、`dshSuperagentRepo/AGENTS.md`、`dshSuperagentRepo/doc/task-workflow.md`
- SA 提示词：`dsh-superagent/prompts/shared.md`、`dsh-superagent/prompts/work.md`
- 不改文档检查算法，不改 `legacy_over_limit` 名单。

## 改动位置与要点

1. `docs-watch.sh`
   - 以 `check.sh --all --tag` 自动补 `audience/status`，再以 `check.sh --all` 判定最终结果。
   - 报告固定写 `/home/zh/www/personalCloud/.run/docs-watch/latest.md`（已被 gitignore）。
   - 飞书通过现有 lark-cli 发送；仅 `FAIL` 或出现新增违规时发送，全部通过不打扰。
   - 配置从 `/home/zh/.config/dsh/docs-watch.env` 读取，不提交凭据。
   - 支持 `--once`、`--test-notify`。

2. systemd 用户级定时器
   - 每天运行一次；`install-doc-watch.sh` 负责 link/enable/start，支持 `--uninstall`。
   - 不使用 root，不改系统级 unit。

3. `dsh-context-guard` 提交门禁
   - `tools/pre-execute` 识别 `git commit`，解析目标仓；有 `docs-policy.json` 时运行 `check.sh --repo <repo>`。
   - 检查失败直接 `deny` 并返回失败项；只检查，不在插件内自动 `--tag`。
   - 新增配置 `docGuardEnabled`、`docGuardWorkspaceRoot`、`docGuardTimeoutMs`。
   - `web` 与 `superagent` 两个 profile 共用本地插件；改后重启对应 DSH 服务生效。

4. DSH 与 SA 规则
   - 文档/计划修改后，提交前必须运行目标仓 `scripts/check.sh --repo <repo>`；跨仓收尾运行 `--all`。
   - “开工时”定义为：接到文档维护任务后、第一次编辑前，运行一次目标仓检查。
   - 新文档缺 frontmatter、`implementation_status` 或超行数上限 = 失败，修完才能提交。
   - 旧文档已在 `legacy_over_limit` 的仅告警；本轮编辑该文件时至少补齐 frontmatter/状态。
   - 允许自动 `--tag` 补 `audience/status`；`implementation_status` 必须按实际状态填写，不自动猜。
   - 自动化优先：机械问题自动修，只上报必须人工判断或无法自动修复的阻塞。
   - 若 DSH/SA 任一方无法同时遵守，必须报告原因、影响和可选处理，不得静默跳过。

## 实施步骤

1. 新增 `docs-watch.sh` 与测试用临时 fixture，验证超限、缺状态、legacy 告警和 `--tag` 行为。
2. 新增 systemd unit 与安装脚本，安装后验证 timer 已启用。
3. 配置飞书目标并运行 `--test-notify`，确认实际收到消息。
4. 同步根 AGENTS、two task-workflow 与 SA prompts。
5. 验证插件门禁：坏文档时 `git commit` 被 deny；修好后放行。
6. 各仓分别提交；`dsh-superagent` 当前在 `feat/executor-budget-phase-end` 分支，只在该分支追加提交，不自动合并。

## 验收

- `./scripts/docs-watch.sh --once` 退出码正确，报告文件生成；全部通过时飞书静默。
- 人为制造未列入 legacy 的超限新文档时，巡检失败并发送飞书；恢复后通过。
- `systemctl --user list-timers | grep dsh-docs-watch` 显示每日任务。
- `grep` 可确认 AGENTS、task-workflow、SA prompts 均含上述硬约束。
- 构造坏文档后执行 `git commit` 被插件拒绝；修复后同一提交放行。
- `./scripts/check.sh --all` 通过；`--tag` 不改 `implementation_status`。

## 回滚

- 先执行 `./scripts/install-doc-watch.sh --uninstall` 停用并移除 timer。
- 各仓用 `git revert <commit>` 回滚；删除 `/home/zh/.config/dsh/docs-watch.env` 和本机报告目录。
