---
audience: human
status: current
implementation_status: blocked
---

# 文档受众分层：扩展到其余项目

## 目标

为其余独立项目接入 `docs-policy.json`，给活跃 Markdown 补 `audience` / `status` frontmatter，使 `./scripts/check.sh --all --strict` 全部通过。

## 范围

首批 6 个仓库：

| 仓库 | 分支 | 分层要点 |
|---|---|---|
| `superCreater` | `master` | `AGENTS.md`、`.trae/rules/**` 为 `ai`；计划/历史文档为 `human`；其余 `shared` |
| `xctl` | `main` | `AGENTS.md` 为 `ai`；`docs/PLAN.md` 为 `human`；README/插件说明为 `shared` |
| `superagent-workbench` | `main` | README/PUBLISHING/STATUS 均为 `shared` |
| `project-experience` | `master` | 排除 `entries/**`；`AGENTS.md` 为 `ai`；docs/feedback 为 `shared` |
| `subscribeWatch` | `master` | README/发布说明分层；历史发布记录为 `human` |
| `linuxops` | `master` | README 为 `shared` |

- `personalCloud`：保持现有 `doc/**` 范围，本次不扩到 `task/**`。
- 待做项：`personalCloud/task/**` 文档量过大，后续单独分批迁移。
- `dsh-superagent`：当前在 `feat/executor-budget-phase-end` 且有未提交改动，暂缓；合入 `main` 后按同样规则处理，`prompts/**`、`skills/**` 已确认属于 AI 规范，标为 `ai`。

## 改动位置

每个仓库新增/修改：

- `docs-policy.json`：`version`、`include`/`exclude`、`defaults`、按路径的 `audience`/`status` 规则、`required_reading`。
- 活跃 Markdown 的 frontmatter 头部；保留已有键（如 `.trae/rules` 的 `alwaysApply`、`entries` 除外）。
- 有 `AGENTS.md` 的仓库补充默认阅读范围与校验命令；有 `PROJECT_INDEX.md` 的同步入口表。

## 实施步骤

1. 逐仓检查现有 frontmatter 与目录，确定 `include`/`exclude`，避免改动 `project-experience/entries/**`、测试语料和生成文件。
2. 写入各仓 `docs-policy.json`，运行 `./scripts/check.sh --repo <id> --tag`。
3. 人工检查 diff：只允许头部、policy、阅读路由变化，不改正文。
4. 更新有 `AGENTS.md` 仓库的阅读路由；`project-experience/AGENTS.md` 加入必读约束。
5. 逐仓运行 `./scripts/check.sh --repo <id>`，再运行 `./scripts/check.sh --all --strict`。
6. 每仓独立 `git add <本任务文件>`、commit、push；不触碰未提交的无关文件。

## 验收

```bash
cd /home/zh/www
./scripts/check.sh --all --strict          # 退出码 0
./scripts/check.sh --repo <id> --tag       # 二次执行修改 0 篇
./scripts/check.sh --repo <id>             # 单仓通过
```

- `project-experience/entries/**` 与各仓测试语料无 diff。
- `git diff --check` 通过。
- 每仓提交范围仅包含本任务文件。

## 回滚

逐仓执行 `git revert <提交号>`；`personalCloud` 本次不改，无需回滚。
