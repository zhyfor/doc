---
implementation_status: done
created_at: 2026-11-18 23:03:13
updated_at: 2026-11-18 23:15:30
---
# PLAN：文档减法与检查工具收敛

## 改动记录

- 2026-11-18 23:03:13 初稿：确定文档收敛、归档、脚本调整。
- 2026-11-18 23:03:26 调整：补充计划时间/改动记录、删除与压缩判定、检查字段。
- 2026-11-18 23:04:42 开始实施：新增 `doc/specs/documentation-rules.md`。
- 2026-11-18 23:15:30 完成：删除重复文档与各仓策略，迁移压缩文档，重写检查/巡检/仓库状态工具，修复全仓旧引用；`check.sh --all`、`--strict`、`--changed` 与 `docs-watch.sh --once` 均通过。

## 目标

把跨仓规范收敛到少数几个入口，删除重复与过期文档，合并冲突规则，迁移项目专属知识；同时把 `scripts/` 下三个工具改成与这套规范一致，让 AI 能按检查报告持续维护文档，用户不需要手工改。

硬约束：

- 跨项目通用规则保留在 `/home/zh/www` 的共享规范里，项目专属事实迁回对应仓库。
- 普通文档不再要求 `audience` / `status` frontmatter；只有 `PLAN-*.md` 保留 `implementation_status`、`created_at`、`updated_at`。
- 删除各仓 `docs-policy.json`，检查策略只保留 `scripts/docs-policy.json` 一份。
- 行数超限默认 `WARN`，断链、非法计划状态为 `FAIL`。
- 已完成计划移入 `doc/archive/plans/`，不删除用户需要的历史资料。

## 删除与压缩判定

处理顺序：先合并，再迁走，最后删除；拿不准就只归档。

- **删除**：内容已过期或与现行规则冲突；同一事实已有唯一权威源且无独有细节；项目专属事实应迁回项目仓；一次性计划已完成并归档。
- **合并**：同一主题散落多份；通用规则写在项目文档里；同一规则在入口、流程、规范中重复出现。合并后只留一处主文档，其他位置用链接。
- **压缩**：只留结论、硬约束、适用边界、例外、入口和最小验收；删背景、推导、过程日志、重复示例、可现查的细节。
- **保留**：安全红线、授权边界、非显然事实、失效条件、必要命令和跨项目通用规则。
- **不求全**：入口文档只写“必须知道、必须禁止、去哪看”；项目文档不要求全部符合，只检查治理范围；行数超限先 `WARN`。

## 范围

包含：

- 根入口：`AGENTS.md`、`PROJECT_INDEX.md`、`personalCloud/AGENTS.md`。
- 跨仓规则：`personalCloud/workspace/_meta/doc/`、`doc/specs/`、`doc/README.md`。
- 文档整理：合并、迁移、归档上述目录中的旧文档，更新全工作区引用。
- 工具：`scripts/check.sh`、`scripts/check_docs.py`、`scripts/docs-watch.sh`、`scripts/repo-status.sh`。

不包含：

- 各项目业务代码、服务配置与运行状态。
- 对所有历史 Markdown 做全量重写；只修被新检查覆盖的入口/规范文档和断链。

## 改动位置

| 动作 | 文件 | 说明 |
|---|---|---|
| 新增 | `doc/specs/documentation-rules.md` | 总体文档规范：层级、唯一源、删除/合并/压缩判定、计划元数据、生命周期、AI 维护责任、检查约定 |
| 新增 | `scripts/docs-policy.json` | 中央检查策略：治理范围、行数建议、PLAN 状态、断链检查 |
| 修改 | `AGENTS.md` | 只留阅读顺序和不可违反的硬约束，目标 ≤60 行 |
| 修改 | `personalCloud/AGENTS.md` | 只写 personalCloud 局部差异，目标 ≤20 行，不重复根规则 |
| 修改 | `PROJECT_INDEX.md` | 只做导航，删除与 AGENTS 重复的 AI 路线，目标 ≤100 行 |
| 修改 | `personalCloud/workspace/_meta/doc/task-workflow.md` | 合并授权、分支、脏工作区、排查顺序，目标 ≤120 行 |
| 修改 | `personalCloud/workspace/_meta/doc/project-registry.md` | 合并工作区布局与仓库登记规则，目标 ≤120 行 |
| 修改 | `personalCloud/workspace/_meta/doc/github-collaboration.md` | 只留身份、PR、改动标记、任务台账，目标 ≤120 行 |
| 修改 | `doc/specs/operations-safety.md` | 吸收 `host-permissions.md` 的“读不到≠不存在”和工具视图复核 |
| 修改 | `doc/specs/engineering-rules.md` | 吸收 Go 脚手架、接口/列表、DSH 插件发布的最低规则 |
| 修改 | `doc/README.md` | 更新目录说明、元数据规则和检查命令 |
| 修改 | `scripts/check.sh`、`scripts/check_docs.py` | 使用中央策略；去掉 `--tag`；新增 `--changed`；默认 WARN 可通过，`--strict` 才失败 |
| 修改 | `scripts/docs-watch.sh` | 去掉 `--tag` 自动改文件；修正飞书 CLI 默认路径；只跑一次检查，失败才通知 |
| 修改 | `scripts/repo-status.sh` | 用 `git rev-parse --git-dir` 识别仓库/worktree，保持现有分支与 dirty 判定 |
| 移动 | `doc/reference/dsh-context-compaction.md` | 迁至 `dsh-context-guard/docs/context-compaction.md`，归项目仓维护 |
| 删除 | `personalCloud/workspace/_meta/doc/workspace-authorization.md` | 内容并入 `task-workflow.md` |
| 删除 | `doc/specs/host-permissions.md` | 内容并入 `operations-safety.md` |
| 删除 | `doc/specs/workspace-layout.md` | 核心约束并入 `project-registry.md` |
| 删除 | `doc/guides/go-scaffold-guide.md` | 只保留“新 Go 项目优先用 gf-scaffold”并入 `engineering-rules.md` |
| 删除 | `doc/guides/troubleshooting-playbook.md` | 通用排查步骤并入任务流程，接口/列表规则并入 `engineering-rules.md` |
| 删除 | `doc/reference/dsh-plugins.md` | 插件清单归 `PROJECT_INDEX.md` 和 `repos.yaml`，发布规则并入 `engineering-rules.md` |
| 删除 | `personalCloud/doc/*.md` 中 10 个 8 行链接页 | 包括 task-workflow、project-registry、engineering-rules、operations-safety、host-permission-pitfalls、multi-repo-workspace、go-scaffold-guide、troubleshooting-playbook、dsh-plugins、dsh-context-compaction；引用改为直接链接 |
| 删除 | 10 份各仓 `docs-policy.json` | 由 `scripts/docs-policy.json` 统一代替 |
| 归档 | `doc/plans/` 中 9 份旧计划 | 全部移入 `doc/archive/plans/`，git 历史与新归档同时保留 |

## 实施步骤

1. 写 `doc/specs/documentation-rules.md`，明确以下规则：
   - 文档层级：`AGENTS.md` 硬约束与路由、`PROJECT_INDEX.md` 导航、`_meta/doc/` 工作流、`doc/specs/` 跨仓硬约束、`doc/reference/` 非必读操作事实、`doc/plans/` 活跃计划、`doc/archive/` 人类历史资料。
   - 一个主题只有一份主文档，其他地方只链接；冲突时以磁盘现状和安全硬规则为准。
   - 普通文档不写 frontmatter；`PLAN-*.md` 只写 `implementation_status`、`created_at`、`updated_at`，正文必须有 `## 改动记录`，每条只记“时间 + 改动点”，完成即移入 `archive/`。
   - 删除、合并、压缩按“删除与压缩判定”执行：先合并、再迁走、最后删除，拿不准只归档。
   - 只写事实、硬约束、路由、可执行步骤；不写复盘、论证、过程日志和重复规则。
   - 修改入口或规则后，必须同步 `README.md` / `STATUS.md` / `PROJECT_INDEX.md`。
   - AI 负责按检查报告修文档，用户不手工整改。
2. 合并跨仓规则：先改 `operations-safety.md`、`engineering-rules.md`，再改 `_meta/doc/task-workflow.md`、`project-registry.md`、`github-collaboration.md`，最后删除被合并文件。
3. 精简入口：压缩 `AGENTS.md`、`personalCloud/AGENTS.md`、`PROJECT_INDEX.md`，只保留硬约束、路由和不显然的事实。
4. 清理旧入口：删除 `personalCloud/doc/` 的 10 个链接页；迁移 `dsh-context-compaction.md`；全仓搜索并更新旧路径引用，确保链接直达新位置。
5. 新建 `scripts/docs-policy.json`：治理 `AGENTS.md`、`PROJECT_INDEX.md`、`README.md`、`STATUS.md`、`SPEC.md`、`PLAN-*.md`、`_meta/doc/*.md`、`doc/specs/*.md`、`doc/reference/*.md`、`doc/README.md`；其他历史文档不纳入行数检查。
6. 调整三个脚本：
   - `check.sh` / `check_docs.py`：删除受众与 `--tag` 逻辑，保留断链、计划状态、`created_at`/`updated_at` 格式与 `## 改动记录` 检查；`--changed` 只查改动文件；`WARN` 默认返回 0，`--strict` 才返回非 0。
   - `docs-watch.sh`：只执行 `check.sh --all`，报告写 `../.run/docs-watch/latest.md`，失败才发飞书；默认 CLI 路径改为 `personalCloud/task/superagent-feishu/bin/lark-bot`。
   - `repo-status.sh`：兼容 worktree；`--strict` 对缺失、dirty、非默认分支返回 1，`ahead/behind` 只展示。
7. 移走 9 份旧计划到 `doc/archive/plans/`；`doc/decisions/` 空目录删除。
8. 运行验收命令，修复被治理文档的 FAIL 与新引入 WARN；按仓分别提交：`doc`、`personalCloud`、`dsh-context-guard`，其他仓只做链接修复提交。

## 验收

- `./scripts/check.sh --all` 返回 0，0 FAIL；被治理文档 0 WARN，非治理历史文档允许 WARN。
- `./scripts/check.sh --all --strict` 在治理文档无 WARN 时返回 0。
- 所有被治理文档的本地链接可解析，无断链。
- 根 `AGENTS.md` ≤60 行，`personalCloud/AGENTS.md` ≤20 行，`PROJECT_INDEX.md` ≤100 行，`doc/specs/documentation-rules.md` ≤70 行。
- 文档规范中包含删除、合并、压缩、保留四类判定，并明确“抓大放小、不求全”。
- 当前计划含 `created_at` / `updated_at` 和一条以上“时间 + 改动点”的改动记录。
- `doc/specs/` 只剩 `operations-safety.md`、`engineering-rules.md`、`documentation-rules.md`；`doc/guides/` 不存在；`doc/reference/` 只保留确实非必读的参考文档。
- `doc/plans/` 只剩当前活跃计划；9 份旧计划在 `doc/archive/plans/`。
- 全工作区只剩 `scripts/docs-policy.json` 一份检查策略。
- `./scripts/docs-watch.sh --once` 能生成报告；成功时不发飞书；脚本不改任何文档。
- `./scripts/repo-status.sh` 能列出 `repos.yaml` 中的 13 个仓；`--strict` 语义与文档一致。
- 每个有改动的仓单独提交，`README.md` / `STATUS.md` / `PROJECT_INDEX.md` 已同步。

## 回滚

- 按仓执行 `git revert <本次提交>`；被删文档都在 git 历史中，可单独恢复。
- 计划归档可整体移回 `doc/plans/`；`dsh-context-compaction.md` 可从 `dsh-context-guard` 迁回。
- 工具若出现误报，先回退 `scripts/` 与 `scripts/docs-policy.json`，文档整理成果不受影响。
