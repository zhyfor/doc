---
implementation_status: done
created_at: 2026-11-20 05:42:00
updated_at: 2026-11-20 06:05:00
---

# PLAN：文档精简与 check.sh 精简入口

## 目标

1. 用 `doc-slim` 规范压缩超 200 行的活跃计划 `PLAN-dsh-toolchain-upgrade.md` 到 ≤200 行。
2. 给 `check.sh` 增加 `--slim` 入口：只列出超限文档并给出 doc-slim 操作指引，不自动改写文件。

项目仓超长 README/STATUS（linuxops、dsh-workbench、project-experience、dsh-context-guard）本轮按用户决定**不做**，留待单独授权。

## 范围

包含仓库：`doc`、`personalCloud`（脚本）。

| 对象 | 改动前 | 改动后 |
|---|---|---|
| `doc/plans/PLAN-dsh-toolchain-upgrade.md` | 289 行 | 200 行，保留结论、待办、规程、坑、验证 |
| `scripts/check.sh` + `check_docs.py` | 无精简入口 | 新增 `--slim`（只读清单，超限退出 1） |
| `doc/README.md`、`doc/specs/documentation-rules.md` | 未提 `--slim` | 补一行用法 |

不包含：项目仓 README/STATUS；任何运行时行为改动；`doc/archive/**` 既有内容。

## 实施步骤

1. 逐份按 doc-slim 分类：结论/硬约束/命令保留，背景、过程日志、重复示例删除；重复内容合并到唯一主文档并留链接。
2. `scripts/check.sh` + `check_docs.py` 增加 `--slim`：运行检查后输出去重后的超限文件清单与 doc-slim 步骤；退出码 0，不写文件。
3. 同步 `doc/README.md`、`doc/specs/documentation-rules.md` 与 `check.sh --help`。
4. 每仓跑 `./scripts/check.sh --repo <id> --strict`，最后 `--all --strict`；单独提交推送。
5. 本计划完成后移入 `doc/archive/plans/`。

## 验收

- `PLAN-dsh-toolchain-upgrade.md` 200 行，`--all --strict` 退出 0、0 WARN。
- `./scripts/check.sh --all --slim` 退出 0、无 `[SLIM]` 行；临时调低上限时能列出清单并退出 1，且不改文件（已实测）。
- `bash -n scripts/check.sh` 通过；帮助文本含 `--slim`。

## 回滚

各仓 `git revert <提交>`；文档恢复用 `git checkout <提交前> -- <文件>`。

## 改动记录

| 时间 | 改动点 |
|---|---|
| 2026-11-20 05:42 | 建档：确认三项范围与涉及仓库 |
| 2026-11-20 05:55 | 交接计划 289→200 行，`--repo doc` 0 警告 |
| 2026-11-20 06:00 | `check.sh`/`check_docs.py` 增加 `--slim`；降上限实测可列出清单并退出 1 |
| 2026-11-20 06:05 | 用户决定跳过项目仓 README/STATUS；同步 doc/README 与文档规范；计划完成归档 |
