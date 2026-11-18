---
audience: human
status: current
implementation_status: not_started
---

# PLAN：task 项目拆分为独立仓库

## 目标

按 Specification-Driven Development 把已成熟、可独立运行或复用的项目从 `personalCloud/task/` 提升为 `/home/zh/www/<name>` 独立 git 仓库：

- 先有可验收的 `SPEC.md`，再拆仓；
- 保留原路径 git 历史；
- 新仓自己拥有 spec、测试和运行说明；
- `personalCloud` 只保留宿主机运维、一次性任务和孵化中项目。

## 范围

第一批拆分：

| 项目 | 新路径 | 说明 |
|---|---|---|
| `dsh-workbench` | `/home/zh/www/dsh-workbench` | 独立 DSH 工作台/插件 |
| `dsh-context-guard` | `/home/zh/www/dsh-context-guard` | 可复用 DSH 插件 |
| `dsh-workflow-shortcuts` | `/home/zh/www/dsh-workflow-shortcuts` | 可复用 DSH 插件 |

第二批评估，不在本计划直接执行：

- `health-watch`：有 systemd 和运行状态数据，先单独做数据迁移方案。
- `rea-tool`：独立工具，确认仍维护后再拆。
- `dsh-health-check`：文件少，优先观察是否会并入 `dsh-context-guard`。

不拆分：

- `superagent-*` 已退役项目：迁入 `task/archive/`，不新建仓库。
- `clash-*`、`host-*`、`disk-*`、`upValue`、`media-automation`、`notes` 等宿主强相关或一次性任务。

## 改动位置

- 源仓：`personalCloud/task/<name>/SPEC.md`；删除前保留在 `split/<name>` 分支历史中。
- 新仓：`/home/zh/www/<name>/`，根 `SPEC.md`、`README.md`、`AGENTS.md`、`docs-policy.json`。
- 索引：`personalCloud/workspace/repos.yaml` 增加 `spec: SPEC.md`，同步 `PROJECT_INDEX.md`、`personalCloud/README.md`。
- 规则：`personalCloud/workspace/_meta/doc/project-registry.md` 增加“task 项目提升为独立仓”的 spec 门禁和路径约定。
- 引用：全局更新 `personalCloud/task/<name>`、`dsh plugin ... link:` 等安装/文档链接。

## 实施步骤

1. 先清理待拆目录的未提交改动；当前 `dsh-context-guard`、`dsh-workflow-shortcuts` 有 dirty 文件，必须由对应任务提交或明确纳入本次迁移后才能开始。
2. 写提升门禁：每个项目在 `personalCloud/task/<name>/SPEC.md` 明确目标、用户、接口、非目标、运行方式、验收命令；不满足则先留在孵化区。
3. 对每个项目执行预检：`git -C personalCloud ls-files task/<name>`、`git status --short`、确认 README/启动方式/依赖/忽略文件清单。
4. 保留历史拆出：
   ```bash
   git -C personalCloud subtree split --prefix=task/<name> -b split/<name>
   git init -b main /home/zh/www/<name>
   git -C /home/zh/www/<name> pull /home/zh/www/personalCloud split/<name>
   ```
5. 补齐新仓根 `SPEC.md`、入口文档和 `docs-policy.json`；把原目录中必要的非跟踪运行文件按清单复制，不整体搬运 `node_modules`、日志和缓存。
6. 在新仓验证启动、测试、插件安装路径；确认 `git log --follow` 能看到原 `task/<name>` 提交。
7. 创建远端并推送；远端默认 `zhyfor/<name>`，若已有同名远端则复用，平台和可见性实施时确认。
8. 从 `personalCloud` 删除旧目录并提交；更新 `repos.yaml`、`PROJECT_INDEX.md`、README、AGENTS 和所有旧路径引用。
9. 全量运行 `./scripts/repo-status.sh`、`./scripts/check.sh --all`，确认新仓已登记、spec 可解析且无失效链接。
10. 验收通过后删除临时 `split/<name>` 分支；失败则从该分支恢复原目录。

## 验收

- 三个新仓均在 `/home/zh/www` 下独立 `git status`、独立提交、独立推送。
- 每个新仓根 `SPEC.md` 存在，包含目标、边界、接口、非目标、运行方式和验收命令。
- `repos.yaml` 的每个新仓都有 `spec: SPEC.md`，`PROJECT_INDEX.md` 有对应条目。
- `git log` 保留原项目历史，文件内容与迁移前一致，差异仅限入口文档、索引和安装路径。
- `personalCloud/task/` 不再保留已拆项目；`dsh-workbench` 等插件从新路径可正常安装/加载，旧路径引用清零。
- `scripts/check.sh --all` 通过；新仓文档有 `audience`/`status`。

## 回滚

- 从 `split/<name>` 分支恢复目录到 `personalCloud/task/<name>`，revert 删除提交。
- 删除新仓远端前先保留本地仓库；索引和引用按旧 commit revert。
- 运行中的数据/日志不进入 git；回滚只需恢复代码、SPEC 与文档，不动运行状态。
