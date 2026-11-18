---
audience: human
status: current
implementation_status: done
---

# PLAN：文档巡检路径显示优化

## 目标

让 `scripts/check.sh` 与 `scripts/docs-watch.sh` 的 `[WARN]`、`[FAIL]`、`[TAG]` 文件路径统一以 `/home/zh/www` 为基准显示，消除多个仓库同名 `README.md` 无法区分的问题。不做违规去重。

## 范围

- 纳入：`personalCloud/workspace/scripts/check_docs.py`、`personalCloud/workspace/scripts/check.sh`、`personalCloud/workspace/_meta/doc/task-workflow.md` 的相关说明。
- 不纳入：`docs-watch.sh` 的 state/新增异常去重逻辑、各仓库文档正文整改、巡检通知格式重构。

## 改动位置

- `check_docs.py`：新增可选 `--display-root`；将 `[WARN]/[FAIL]/[TAG]` 及必读文件检查中的仓库内相对路径转换为显示根目录下的半路径；不在显示根目录下时回退原相对路径。
- `check.sh`：从 `repos.yaml` 的 `workspace_root` 读取显示根目录并传给 `check_docs.py`；缺省回退当前仓库路径逻辑。
- `_meta/doc/task-workflow.md`：在文档门禁说明中补充“检查/巡检输出路径以 `/home/zh/www` 为基准”。

## 实施步骤

1. 修改 `check_docs.py`：增加 `--display-root`，统一生成显示用路径，覆盖检查与 `--tag` 输出。
2. 修改 `check.sh`：解析 `repos.yaml` 的 `workspace_root`，调用检查器时传入 `--display-root`。
3. 跑 `bash -n scripts/check.sh`、`python3 -m py_compile scripts/check_docs.py`。
4. 跑 `./scripts/check.sh --repo xctl`、`./scripts/check.sh --all`，核对输出示例：
   - `superCreater/AGENTS.md`
   - `superCreater/docs/api.md`
   - `xctl/README.md`
   - `project-experience/README.md`
   - `linuxops/README.md`
5. 跑 `./scripts/docs-watch.sh --once`，确认 `latest.md` 与飞书摘要使用相同路径。
6. 同步 `_meta/doc/task-workflow.md`，并将本计划 `implementation_status` 改为 `done`。

## 验收

- `check.sh --all` 的 WARN/FAIL 不再出现裸 `README.md`，同名文件可区分。
- `check.sh --repo <id>` 手工检查同样输出 www 相对路径。
- `docs-watch.sh --once` 报告与通知内容使用 www 相对路径。
- `check.sh --all` 退出码为 0（现有内容仅告警、不新增失败）。
- `bash -n scripts/check.sh`、`python3 -m py_compile scripts/check_docs.py` 通过。

## 回滚

- 用 `git revert` 回退本次提交，恢复 `check_docs.py`、`check.sh` 和 `_meta/doc/task-workflow.md` 到改动前版本；无数据迁移或配置变更。
