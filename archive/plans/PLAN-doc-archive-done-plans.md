---
implementation_status: done
created_at: 2026-11-20 05:33:00
updated_at: 2026-11-20 05:36:00
---

# PLAN：归档已完成计划

## 目标

把 `doc/plans/` 中已 `done` 的计划移入 `doc/archive/plans/`，消除活跃计划目录与文档规范的偏差。

## 范围

包含：`doc/plans/` 下 3 份 `implementation_status: done` 的计划。

| 文件 | 行数 |
|---|---|
| `PLAN-doc-check-limits.md` | 81 |
| `PLAN-dsh-default-full-access.md` | 40 |
| `PLAN-experience-ai-taxonomy.md` | 93 |

不包含：任何计划正文改写；`not_started` / `in_progress` 计划；其他仓库文档。

## 实施步骤

1. `git mv` 三份文件到 `doc/archive/plans/`。
2. 全工作区检索引用，保留者改指归档路径；示例性路径（如 `task/example/...`）不改。
3. 运行 `./scripts/check.sh --repo doc --strict` 与 `./scripts/check.sh --all --strict`。
4. 在 `doc` 仓单独提交并推送 `main`。

## 验收

- `doc/plans/` 只剩 `not_started` / `in_progress` 计划。
- 两份检查命令均退出 0，无 FAIL、无 WARN。
- 无指向旧路径的断链。

## 回滚

`git mv` 反向移回 `doc/plans/` 后重新检查；或 `git revert <提交>`。

## 改动记录

| 时间 | 改动点 |
|---|---|
| 2026-11-20 05:33 | 建档，等待执行确认 |
| 2026-11-20 05:36 | 三份 done 计划移入 `doc/archive/plans/`；无旧路径引用需修 |
| 2026-11-20 05:36 | `check.sh --all --strict` 通过；计划自身标记 done 并归档 |
