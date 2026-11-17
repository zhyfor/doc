---
audience: human
status: current
implementation_status: done
---

# PLAN: 文档治理与实施状态规范

- 日期：2026-11-18
- 适用范围：`/home/zh/www/doc`、根计划、`personalCloud/doc`、`dshSuperagentRepo/doc`、公共检查脚本

## 目标

1. 所有 `PLAN-*.md` 的 frontmatter 增加 `implementation_status`，正文不再写状态行。
2. 根计划迁入 `doc/plans/`，`doc/` 按类型分层并纳入统一校验。
3. AI/shared 文档执行简洁规范：新文档超 120/200 行直接失败，旧文档先告警；PLAN 不设行数上限，但只写可执行内容。
4. `www/doc` 纳入 `scripts/check.sh --all`，并更新 `repos.yaml` 的 `doc.verify`。

## 状态枚举

`not_started | in_progress | fixing | blocked | done | rolled_back`

- `fixing`：已实施，验收/测试有问题，正在修。
- `blocked`：等待用户确认、外部依赖或权限。
- 实施完成但待用户确认的，统一记为 `done`。

## 范围

纳入：

- `personalCloud/workspace/scripts/check_docs.py`：`include`、`plan_status`、行数限制、旧文档豁免。
- `personalCloud/workspace/_meta/doc/task-workflow.md`、`dshSuperagentRepo/doc/task-workflow.md`：计划模板、状态更新时机、简洁规范。
- `personalCloud/workspace/AGENTS.md`、`PROJECT_INDEX.md`：`_meta/doc` 与 `doc/` 的职责边界和路由。
- `personalCloud/workspace/repos.yaml`：`doc.verify`。
- `doc/`：新目录结构、`docs-policy.json`、根计划迁入、`README.md`。
- `personalCloud/doc/`：补 frontmatter，新增 `personalCloud/docs-policy.json`，仅校验 `doc/**`。
- `dshSuperagentRepo/doc/`：补 `implementation_status`，扩展现有 `docs-policy.json`。

不纳入：

- `personalCloud` 除 `doc/**` 外的 296 篇 Markdown 批量改造。
- 各仓目录大搬迁、正文重写、历史内容审校。
- `doc/subscribeWatch/` 现有隐私页迁移和 URL 变更。

## 改动位置

- `check_docs.py`：policy 支持 `include`、`plan_status`、`line_limits`、`legacy_over_limit`；`--tag` 只补 `audience`/`status`，不写 `implementation_status`。
- `/home/zh/www/doc/`：
  - `README.md`、`docs-policy.json`
  - `plans/`、`guides/`、`reference/`、`decisions/`、`archive/`
  - 4 个根计划移入 `plans/`（含本文件）
  - `subscribeWatch/` 原位保留
- 根计划状态：`PLAN-cross-repo-workspace.md`=`done`；`PLAN-doc-audience-split.md`、`PLAN-repo-governance.md`、本计划=`not_started`。
- `personalCloud/doc/PLAN-session-task-isolation.md`=`done`；其余 `personalCloud/doc/*.md` 由 `--tag` 补 `audience`/`status`。
- `dshSuperagentRepo/doc/PLAN-*.md`：`PLAN-dsh-immersive-glass.md`、`PLAN-dsh-immersive-glass-scope-fix.md`、`PLAN-sa-thread-sessions-closeout.md`、`PLAN-sa-thread-sessions.md` 均=`done`。
- 所有旧计划删除正文 `- 状态：...` 行，frontmatter 唯一来源。

## 实施步骤

1. 扩 `check_docs.py`：policy 解析新增 `include`；按 `plan_status.glob` 强制校验 `implementation_status` 枚举；按 `audience` 检查行数。
2. 行数规则：`ai` ≤120 行、`shared` ≤200 行；实现时把当前超限文件写入 `legacy_over_limit`，命中仅告警，新文件超限失败。
3. 新建 `doc/` 分层与 `docs-policy.json`；创建 `doc/README.md` 说明每层用途和“一个主题一个主文档”。
4. 迁移 4 个根计划到 `doc/plans/`，按上述映射补 frontmatter，删除正文状态行；更新 `AGENTS.md`、`PROJECT_INDEX.md`、`_meta/doc/task-workflow.md` 中的路径与职责说明。
5. 更新工作流：计划模板加 `implementation_status`；明确计划创建=`not_started`、开始实施=`in_progress`、验收问题=`fixing`、等待外部=`blocked`、完成=`done`、回滚=`rolled_back`；PLAN 只写目标/范围/改动位置/步骤/验收/回滚。
6. 同步简洁规范：AI/shared 只写事实、约束、路由、可执行步骤；背景、复盘、重复论证放 `archive/`，决策理由放 `decisions/`，禁止多文档复制同一内容。
7. 新建 `personalCloud/docs-policy.json`（`include: ["doc/**"]`），扩展 `dshSuperagentRepo/docs-policy.json`；跑 `--tag` 补 `audience`/`status`，再手工补旧计划 `implementation_status`。
8. 更新 `repos.yaml` 的 `doc.verify` 为 `../scripts/check.sh --repo doc`；跑 `./scripts/check.sh --all`，清理失败项。
9. 分别在 `doc`、`personalCloud`、`dshSuperagentRepo` 独立提交并推送；提交前确认不混入各仓既有无关改动。

## 验收

- `/home/zh/www` 根目录不再有 `PLAN-*.md`；`doc/plans/` 下 4 个计划均有合法 `implementation_status`，正文无状态行。
- `./scripts/check.sh --repo doc`、`--repo personalCloud`、`--repo dshSuperagentRepo` 全部通过。
- `./scripts/check.sh --all` 自动包含 `doc` 且通过；`repos.yaml` 的 `doc.verify` 可直接执行。
- 缺少或非法 `implementation_status` 的 PLAN 校验失败；`--tag` 不修改该字段。
- 新增超 120 行的 `ai` 文档或超 200 行的 `shared` 文档校验失败；`legacy_over_limit` 中旧文档仅告警。
- `AGENTS.md`、`PROJECT_INDEX.md` 已改为 `_meta/doc/` 放操作规则、`doc/` 放跨仓文档与计划。

## 回滚

- 各仓用 `git revert` 回退对应提交，不用 `reset` 或强推。
- 根计划从 `doc/plans/` 移回 `/home/zh/www/`；`doc/` 新目录和 policy 一并回退。
- 恢复 `check_docs.py`、各 `docs-policy.json`、`repos.yaml`、`AGENTS.md`、`PROJECT_INDEX.md` 到改动前版本。
