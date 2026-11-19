---
implementation_status: in_progress
created_at: 2026-11-19 22:40:00
updated_at: 2026-11-19 22:52:00
---

# PLAN：文档检查与篇幅限制优化

## 目标

1. 重要计划需要保留必要行数时，有明确、可审计的放行方式。
2. 把 `personalCloud/workspace/_meta/doc/` 三份跨仓规则迁到 `doc/specs/`，消除路径过深和仓边界错位。
3. 压缩 `task-workflow.md`，并新增 `doc-slim` 技能，让超限文档可按规范自动精简。

## 范围

包含：`scripts/docs-policy.json`、`scripts/check_docs.py`、`scripts/check.sh`、`doc/specs/`、根入口文档、`personalCloud` 文档与根链接脚本、3 个引用仓的路径更新、`/home/zh/www/.dsh/skills/doc-slim/`。

不包含：文档内容的大规模重写；各项目业务代码；`dsh-workflow-shortcuts` 功能逻辑。

## 改动位置

| 动作 | 文件 | 说明 |
|---|---|---|
| 新增 | `doc/specs/task-workflow.md` | 由 `_meta/doc/task-workflow.md` 迁入并压缩到 117 行 |
| 新增 | `doc/specs/project-registry.md` | 迁入，只修链接 |
| 新增 | `doc/specs/github-collaboration.md` | 迁入，只修链接 |
| 修改 | `scripts/docs-policy.json` | `plan_status.long_plan`：标题 `## 篇幅说明`、`max_lines: 400` |
| 修改 | `scripts/check_docs.py` | 计划声明篇幅说明后放宽上限；行数 WARN 附 `doc-slim` 提示 |
| 修改 | `scripts/check.sh` | 帮助文本说明长计划规则 |
| 修改 | `doc/specs/documentation-rules.md` | 文档层级、计划篇幅、检查规则 |
| 修改 | `doc/README.md` | 目录说明与入口 |
| 修改 | `AGENTS.md`（真实文件 `personalCloud/workspace/AGENTS.md`） | 路由改指 `doc/specs/`，移除 `_meta` |
| 修改 | `PROJECT_INDEX.md`（真实文件同上目录） | 入口与工作区地图移除 `_meta` |
| 修改 | `personalCloud/PROJECT_INDEX.md`、`personalCloud/README.md`、`personalCloud/AGENTS.md` | 引用改到 `../doc/specs/` |
| 修改 | `personalCloud/task/project-experience-reuse/README.md` | 引用改到 `doc/specs/` |
| 修改 | `personalCloud/workspace/install-root-links.sh` | `ITEMS` 去掉 `_meta` |
| 删除 | `personalCloud/workspace/_meta/`、根符号链接 `/home/zh/www/_meta` | 文件迁出后删除 |
| 修改 | `dsh-workflow-shortcuts/README.md`、`README.en.md`、`STATUS.md`、`PLAN-configurable-spec-paths.md` | 路径更新；`planTemplate` 示例留空（无真实模板，不再指向不存在路径） |
| 修改 | `dsh-context-guard/docs/context-compaction.md` | 路径更新 |
| 修改 | `project-experience/entries/conventions/exp-doc-0001.md` | 规则文本路径更新 |
| 修改 | `doc/plans/PLAN-dsh-toolchain-upgrade.md` | 补 `## 篇幅说明`，作为首个适用样本 |
| 新增 | `/home/zh/www/.dsh/skills/doc-slim/SKILL.md` | 超限文档精简技能；`~/.dsh/skills/doc-slim` 软链暴露 |

## 实施步骤

1. 修改 `docs-policy.json` 与 `check_docs.py`：
   - 计划文件超过基础上限时，若正文存在 `## 篇幅说明` 且总行数 ≤ 400，输出 `[INFO]` 不计数 WARN；
   - 无 `## 篇幅说明` 或超过 400 行，仍按原规则 WARN；
   - 行数 WARN 文案追加“可用 doc-slim 技能精简”。
2. 迁移三份规则：复制到 `doc/specs/`，修相对链接，`git rm` 原文件；压缩 `task-workflow.md`，删除与根 `AGENTS.md` 重复的约束、`_meta/scripts` 失效引用和重复排查条目。
3. 更新 `doc/` 内全部引用、文档层级表与检查规则；给 `PLAN-dsh-toolchain-upgrade.md` 补篇幅说明。
4. 更新 `personalCloud` 文档与 `install-root-links.sh`；删除空目录和根 `_meta` 符号链接。
5. 更新 `dsh-workflow-shortcuts`、`dsh-context-guard`、`project-experience` 的路径引用；把不存在的 `planTemplate` 示例路径改为空值。
6. 新建 `doc-slim` 技能：定位超限 → `rg`/`workdir-rag` 找权威源 → 压缩 → `check.sh --strict` 验收 → 报告；不自动提交。
7. 逐仓运行 `./scripts/check.sh --repo <id>`，再跑 `--all --strict`；按仓分别提交推送。

## 验收

- `./scripts/check.sh --all --strict` 返回 0，0 FAIL、0 WARN。
- `PLAN-dsh-toolchain-upgrade.md` 因 `## 篇幅说明` 不再报 WARN；无该节的超限计划仍报 WARN。
- `_meta` 不再存在；全工作区 `rg "_meta/doc"` 只剩归档或历史记录。
- `task-workflow.md` ≤ 120 行（实际 117），三份规则均位于 `doc/specs/`。
- `doc-slim` 技能文件存在，`~/.dsh/skills/doc-slim` 指向 `/home/zh/www/.dsh/skills/doc-slim`。
- 每仓独立提交，提交信息说明搬迁与规则变化。

## 回滚

- 按仓 `git revert <提交>`；`personalCloud` 中被删的三份文件可从本任务提交前历史恢复。
- 恢复 `_meta`：从 `doc/specs/` 复制回 `personalCloud/workspace/_meta/doc/`，运行 `install-root-links.sh` 重建符号链接。
- 检查器回退：`git revert` `doc`/`personalCloud` 中策略与脚本提交；文档内容不受影响。

## 改动记录

| 时间 | 改动点 |
|---|---|
| 2026-11-19 22:40 | 建档：确认三项方案与跨仓授权 |
| 2026-11-19 22:48 | 策略与检查器完成：`long_plan`、`## 篇幅说明` 放宽、INFO/WARN 文案 |
| 2026-11-19 22:50 | 三份规则迁入 `doc/specs/`；`task-workflow.md` 压缩到 117 行；删除 `_meta` 目录与根链接 |
| 2026-11-19 22:52 | 更新 `doc`、`personalCloud`、三个引用仓；新建 `doc-slim` 技能；`check.sh --all --strict` 13 仓通过 |
