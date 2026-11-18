---
audience: shared
status: current
owner: workspace
scope: /home/zh/www
---

# 工作区仓库布局与多仓编辑（spec）

- 适用范围：`/home/zh/www` 下的仓库放置、嵌套仓库的编辑与提交方式。
- 相关：[`project-registry.md`](../../personalCloud/workspace/_meta/doc/project-registry.md)、[`go-scaffold-guide.md`](../guides/go-scaffold-guide.md)

## 1. 布局硬约束

- 一个仓库一个目录，各自带 `.git` 与远端；**不做 submodule、不做 gitlink**。
- 嵌套仓库必须被父仓库 `.gitignore` 显式排除（`personalCloud` 已排除 `task/xctl/`、`task/superCreater/`）。
- 父仓库不追踪子仓库文件，也不跨仓库做原子提交；每个仓库独立 `git add/commit/push`。
- 大仓库靠各自 `.gitignore` 控制体积（如 `superCreater` 约 8.8G，含 `.gomodcache`、`.go-build-cache`），缓存不入库。
- 跨项目文档统一放 `/home/zh/www/doc`（独立仓），不散落在各仓库 `doc/`。

## 2. 编辑器识别规则

Trae/VS Code 内置 Git 扩展扫描打开目录下**一层**子目录（`git.repositoryScanMaxDepth` 默认 `1`，`-1` 不限制）。因此：

- 打开 `personalCloud`：只显示 `personalCloud` 本身，二层仓库不出现；
- 打开 `personalCloud/task`：`xctl`、`superCreater` 同时出现在“源代码管理”；
- 打开某个子仓库目录：只显示该仓库。

需要在一个窗口管理多个仓库时，打开它们的共同父目录（当前即 `personalCloud/task`）；需要同时看不同层级目录时才用 `.code-workspace` 多根工作区，本工作区日常不使用。

## 3. 日常操作

1. 用编辑器打开 `/home/zh/www/personalCloud/task`，在“源代码管理”的 Repositories 区切换仓库。
2. 每个仓库各自执行检查与提交；xctl 按**当前目录**探测项目根：

```bash
cd /home/zh/www/personalCloud/task/xctl
./bin/xctl check && git add -A && ./bin/xctl commit --yes -m "..."

cd /home/zh/www/personalCloud/task/superCreater
../xctl/bin/xctl check && git add -A && ../xctl/bin/xctl commit --yes -m "..."
```

3. 推送按各自远端：`superCreater` 日常推 `origin`，其 `upstream`（`fenghoer/AICreater`）只作参考，不作为推送目标。

## 4. 新增仓库

1. 仓库放到 `task/<name>/`，自带 `.git`，不要复制成普通目录；
2. `personalCloud/.gitignore` 增加 `task/<name>/` 并写一行说明；
3. 同步 `repos.yaml` 与 `PROJECT_INDEX.md`；重载编辑器窗口。

## 5. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 只看到一个库 | 打开的是父仓库根目录 | 改开共同父目录（`task`） |
| 目标仓库没出现 | 不在打开目录的直接子目录 | 单独打开该目录，或用多根工作区 |
| 父仓库 `git status` 出现 `task/xxx/` | `.gitignore` 漏了 | 补忽略行并写注释 |
| 仓库显示为子模块 | 被登记成 gitlink | `git rm --cached` 后改回普通目录 |
| 推到错误远端 | 同时配了 `origin` 和 `upstream` | 明确 `git push origin <branch>` |

## 6. 验收方式

```bash
git -C /home/zh/www/personalCloud/task/xctl rev-parse --show-toplevel
git -C /home/zh/www/personalCloud/task/superCreater rev-parse --show-toplevel
git -C /home/zh/www/personalCloud status --short   # 不应出现 task/<name>/
```

- 每个子仓库 `remote -v` 有远端；父仓库 `git status` 不显示子仓库目录。
- 新增仓库后 `repos.yaml`、`PROJECT_INDEX.md` 与磁盘一致。

## 7. 失效条件

- 编辑器更换、`git.repositoryScanMaxDepth` 行为变化，或仓库不再嵌套放置时，第 2 节需重写。
- 回滚仅涉及“打开哪个目录”与忽略行，不改变任何仓库历史。
