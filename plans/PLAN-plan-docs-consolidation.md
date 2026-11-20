---
implementation_status: done
created_at: 2026-11-20 21:31:44
updated_at: 2026-11-20 22:20:00
---

# PLAN：计划文档集中到各仓 plans/ 并归档

## 目标

- 仓库根不再平铺 `PLAN*.md`；每仓只有一个活跃计划目录 `plans/`，完成的移入 `plans/archive/`。
- 所有活跃计划受统一检查：frontmatter、状态枚举、`## 改动记录`、行数上限。
- 跨仓计划仍放 `doc/plans/`，完成移入 `doc/archive/plans/`；历史归档不改写。

## 范围

涉及 8 个独立仓：`doc`、`personalCloud`、`dshSuperagentRepo`、`dsh-workbench`、`dsh-context-guard`、`dsh-workflow-shortcuts`、`superCreater`、`xctl`，共 43 份计划（仓库级 39 份 + doc/plans 4 份保持原位）。
不含：`doc/archive/plans/`、`plans/archive/` 历史文件正文、`.work/` 副本、`project-experience/entries/` 历史条目、任务级项目内其他文档。

## 目标结构

| 类型 | 活跃 | 完成 |
|---|---|---|
| 单仓计划 | `<repo>/plans/PLAN-<主题>.md` | `<repo>/plans/archive/PLAN-<主题>.md` |
| 跨仓计划 | `doc/plans/PLAN-<主题>.md` | `doc/archive/plans/PLAN-<主题>.md` |

- 文件名同仓唯一；多任务仓加任务前缀（如 `PLAN-token-control-...`），不用泛名 `PLAN.md`。
- 活跃计划必须补 frontmatter（`implementation_status`、`created_at`、`updated_at`）与 `## 改动记录`；归档文件受检豁免，正文不动。
- 完成后才移入 archive；仍在验证或阻塞的留在 `plans/`。

## 迁移映射

完成 → `plans/archive/`：

| 现路径 | 新路径 |
|---|---|
| `personalCloud/PLAN-experience-review-supervise.md` | `personalCloud/plans/archive/PLAN-experience-review-supervise.md` |
| `personalCloud/PLAN-file-transfer.md` | `personalCloud/plans/archive/PLAN-file-transfer.md` |
| `personalCloud/doc/PLAN-personal-sync-refresh.md` | `personalCloud/plans/archive/PLAN-personal-sync-refresh.md` |
| `personalCloud/task/dsh-token-control/PLAN-20261118-ops-token-value.md` | `personalCloud/plans/archive/PLAN-token-control-ops-token-value.md` |
| `personalCloud/task/dsh-workflow-shortcuts/PLAN-ok-no-auto-archive-prompts.md` | `personalCloud/plans/archive/PLAN-dsh-workflow-shortcuts-no-auto-archive.md` |
| `personalCloud/task/health-watch/PLAN-2026-11-16-noise-reduction.md` | `personalCloud/plans/archive/PLAN-health-watch-noise-reduction.md` |
| `dshSuperagentRepo/doc/PLAN-dsh-immersive-glass.md` | `dshSuperagentRepo/plans/archive/PLAN-dsh-immersive-glass.md` |
| `dshSuperagentRepo/doc/PLAN-dsh-immersive-glass-scope-fix.md` | `dshSuperagentRepo/plans/archive/PLAN-dsh-immersive-glass-scope-fix.md` |
| `dshSuperagentRepo/doc/PLAN-sa-thread-sessions.md` | `dshSuperagentRepo/plans/archive/PLAN-sa-thread-sessions.md` |
| `dshSuperagentRepo/doc/PLAN-sa-thread-sessions-closeout.md` | `dshSuperagentRepo/plans/archive/PLAN-sa-thread-sessions-closeout.md` |
| `dshSuperagentRepo/workdir-rag/docs/PLAN.md` | `dshSuperagentRepo/plans/archive/PLAN-workdir-rag.md` |
| `dsh-workbench/PLAN-archived-session-display.md` | `dsh-workbench/plans/archive/PLAN-archived-session-display.md` |
| `dsh-workbench/PLAN-todo-marker-fallback.md` | `dsh-workbench/plans/archive/PLAN-todo-marker-fallback.md` |
| `dsh-workbench/PLAN-todo-user-action.md` | `dsh-workbench/plans/archive/PLAN-todo-user-action.md` |
| `dsh-context-guard/PLAN-call-limits.md` | `dsh-context-guard/plans/archive/PLAN-call-limits.md` |
| `dsh-context-guard/PLAN-continue-draft-on-hard-limit.md` | `dsh-context-guard/plans/archive/PLAN-continue-draft-on-hard-limit.md` |
| `dsh-context-guard/PLAN-risk-always-allow-fix.md` | `dsh-context-guard/plans/archive/PLAN-risk-always-allow-fix.md` |
| `dsh-context-guard/PLAN-rm-opt-whitelist.md` | `dsh-context-guard/plans/archive/PLAN-rm-opt-whitelist.md` |
| `dsh-context-guard/PLAN-temp-rm-step-wording.md` | `dsh-context-guard/plans/archive/PLAN-temp-rm-step-wording.md` |
| `dsh-workflow-shortcuts/PLAN-configurable-spec-paths.md` | `dsh-workflow-shortcuts/plans/archive/` 同名 |
| `dsh-workflow-shortcuts/PLAN-dg-plan-title.md` | `dsh-workflow-shortcuts/plans/archive/` 同名 |
| `dsh-workflow-shortcuts/PLAN-g-empty-recent-plan.md` | `dsh-workflow-shortcuts/plans/archive/` 同名 |
| `dsh-workflow-shortcuts/PLAN-g-event-entry-shape.md` | `dsh-workflow-shortcuts/plans/archive/` 同名 |
| `dsh-workflow-shortcuts/PLAN-g-session-title-from-plan.md` | `dsh-workflow-shortcuts/plans/archive/` 同名 |
| `doc/plans/PLAN-republish-plugin-market.md` | `doc/archive/plans/PLAN-republish-plugin-market.md` |

活跃 → `plans/`（无状态证据的保留并标 `in_progress`，改动记录注明待确认）：

| 现路径 | 新路径 | 状态 |
|---|---|---|
| `personalCloud/doc/PLAN-session-task-isolation.md` | `personalCloud/plans/PLAN-session-task-isolation.md` | in_progress |
| `personalCloud/task/dsh-token-control/PLAN-20261118-ops-3day-trial-and-ptc.md` | `personalCloud/plans/PLAN-token-control-ops-3day-trial-and-ptc.md` | not_started |
| `personalCloud/task/dsh-workspace-symlink/PLAN-workspace-file-symlink.md` | `personalCloud/plans/PLAN-workspace-file-symlink.md` | blocked |
| `personalCloud/task/nextcloud-storage-1t/PLAN-nextcloud-storage-1t.md` | `personalCloud/plans/PLAN-nextcloud-storage-1t.md` | in_progress |
| `personalCloud/task/notes/PLAN-obsidian-trial-20261120.md` | `personalCloud/plans/PLAN-obsidian-trial-20261120.md` | in_progress |
| `personalCloud/task/project-experience-watch/PLAN-personalcloud-watch.md` | `personalCloud/plans/PLAN-personalcloud-watch.md` | in_progress |
| `dshSuperagentRepo/task/project-experience/PLAN.md` | `dshSuperagentRepo/plans/PLAN-project-experience-compiler.md` | in_progress |
| `dshSuperagentRepo/task/project-experience-watch/PLAN.md` | `dshSuperagentRepo/plans/PLAN-project-experience-watch.md` | not_started |
| `dsh-workbench/PLAN-dsh-workbench.md` | `dsh-workbench/plans/PLAN-dsh-workbench.md` | in_progress |
| `dsh-workbench/PLAN-sa-ui-migration.md` | `dsh-workbench/plans/PLAN-sa-ui-migration.md` | in_progress |
| `dsh-workbench/PLAN-todo-title-listener-fix.md` | `dsh-workbench/plans/PLAN-todo-title-listener-fix.md` | in_progress |
| `dsh-context-guard/PLAN.md` | `dsh-context-guard/plans/PLAN-context-guard.md` | in_progress |
| `superCreater/PLAN-creator-tg-targeting.md` | `superCreater/plans/PLAN-creator-tg-targeting.md` | in_progress |
| `xctl/docs/PLAN.md` | `xctl/plans/PLAN-xctl-roadmap.md` | in_progress |

## 改动位置

- 规范：`doc/specs/documentation-rules.md` §4、`doc/specs/task-workflow.md` §1/§2；`dshSuperagentRepo/doc/task-workflow.md` §2 改为指向中央规范。
- 检查器：`personalCloud/workspace/scripts/docs-policy.json` 增加 `plans/PLAN-*.md` 到 `include`、`plan_status.glob`、`line_limits`；`plans/archive/**` 与 `*/plans/archive/**` 加入 `exclude`。
- 入口：根 `AGENTS.md`、`personalCloud/AGENTS.md`、`personalCloud/workspace/AGENTS.md`、`dshSuperagentRepo/AGENTS.md`、`dsh-workbench/AGENTS.md`、`dsh-context-guard/AGENTS.md`、`dsh-workflow-shortcuts/AGENTS.md` 中的 `PLAN*.md` 路径。
- 链接：`dsh-workbench/README.md`（3 处 + 目录树）、`dsh-workbench/STATUS.md`、`dshSuperagentRepo/PROJECT_INDEX.md`、`personalCloud/PROJECT_INDEX.md`、`dsh-context-guard/README.md`/`STATUS.md` 中指向旧计划路径的链接。
- 长计划：`PLAN-dsh-workbench.md` 428 行需压到 ≤400 并加 `## 篇幅说明`；`PLAN-todo-title-listener-fix.md` 228 行加 `## 篇幅说明`。

## 实施步骤

1. 先改 `docs-policy.json` 并试跑 `./scripts/check.sh --all`，确认新 glob 生效、无仓库被漏检。
2. `doc` 仓：归档 `PLAN-republish-plugin-market.md`；改两份 spec；跑 `./scripts/check.sh --repo doc --strict`。
3. 逐仓执行迁移：`mkdir -p plans[/archive]`、`git mv`、改名；为活跃计划补 frontmatter 与 `## 改动记录`（14 份中 13 份缺项，含本次迁移行）；完成态计划只移动不改正文。
4. 处理两份超长计划（压缩或补 `## 篇幅说明`）。
5. 全工作区更新旧路径链接：`rg -n "PLAN-" <repo>/README.md <repo>/STATUS.md <repo>/AGENTS.md <repo>/PROJECT_INDEX.md`，逐条改；历史归档与 `entries/` 不改。
6. 验证：逐仓 `./scripts/check.sh --repo <id> --strict`；最后 `./scripts/check.sh --all --strict`、`./scripts/repo-status.sh`、`rg` 确认旧路径引用清零。
7. 8 个仓分别 `git add <明确文件>`、提交、推送；提交信息 `docs(plans): 统一计划目录并归档已完成计划`。

## 验收

- 除 `doc/` 与 `plans/` 外，仓库根无 `PLAN*.md`；`doc/plans/` 只剩活跃计划。
- `./scripts/check.sh --all --strict` 退出 0，无 FAIL/WARN。
- `rg "PLAN-" --glob '*.md' -g '!**/archive/**' -g '!**/entries/**'` 无指向旧路径的链接。
- 每仓独立提交号与推送结果在收尾报告列出。

## 回滚

逐仓 `git revert <commit>`；已移动文件可 `git mv` 反向恢复。归档文件内容未改写，回滚只涉及路径。

## 改动记录

| 时间 | 改动点 |
|---|---|
| 2026-11-20 21:30 | 建档：完成现状盘点与结构选型，等待确认 |
| 2026-11-20 21:32 | 校正计划总数与缺元数据数量 |
| 2026-11-20 22:00 | 8 个仓共 39 个计划 `git mv` 到 `plans/` 或 `plans/archive/`；14 个活跃计划补 frontmatter 与 `## 改动记录`，created_at 按 git 历史校正 |
| 2026-11-20 22:10 | 更新 `docs-policy.json`（include/plan_status/line_limits/exclude）与 `documentation-rules.md`、`task-workflow.md` |
| 2026-11-20 22:20 | 全仓链接与引用改写到新路径，`check.sh --all --strict` 全部通过；xctl 设计章节拆到 `docs/DESIGN.md` |
