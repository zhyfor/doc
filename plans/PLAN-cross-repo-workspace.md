---
audience: human
status: current
implementation_status: done
---

> 推送策略已被 [`PLAN-repo-governance.md`](PLAN-repo-governance.md) 取代；本计划其余内容仍有效。

# PLAN: 跨仓工作区授权
- 日期：2026-11-17

## 目标
让一个 DSH 会话以 `/home/zh/www` 为唯一工作区根，在一次会话内跨多个独立 git 仓读代码、改代码；写权限按任务逐仓授权，越界先报告等确认；目标仓默认直接 commit + push 到 `master`（无 `master` 用 `main`）；SA 的非默认分支未合并时只提醒，不自动合并。

## 范围
新增：
- `/home/zh/www/AGENTS.md`：跨仓硬规则与越界确认流程
- `/home/zh/www/PROJECT_INDEX.md`：仓库导航（路径、远程、默认分支、角色、验证命令）
- `/home/zh/www/repos.yaml`：机器可读仓库清单与任务级写权限开关
- `/home/zh/www/scripts/repo-status.sh`：全仓状态扫描
- `/home/zh/www/_meta/doc/`：跨仓任务、授权、仓库登记专题
- DSH 工作区：`/home/zh/www`

不改：
- 各项目目录结构、git 历史、远程地址
- 不合并成 monorepo，不引入 submodule
- SA 的 `feat/executor-budget-phase-end` 分支不自动合并

## 关键规则
1. 任务开始先列本次可写仓库；未点名的仓默认只读。
2. 需要改其他仓时，先报告仓库、路径、原因、改动方案、验证方式，等用户明确确认。
3. 每个仓独立 commit；默认直接 push 到 `master`/`main`。
4. 禁止 `push --force`、自动 merge、自动 rebase、删除未提交改动。
5. 目标仓当前不在默认分支时先停下说明，等用户选择。
6. 涉及 SA 时检查 `feat/executor-budget-phase-end` 是否已合入 `main`，未合并必须提醒。
7. 收尾输出每仓 commit 号、push 结果、测试结果、未合并分支。

## 约束文档维护（已确认方案）

不新建仓库。真实文件放已有 `personalCloud` 仓库，根目录只放符号链接。

```text
/home/zh/www/personalCloud/workspace/     # 真实文件，进 personalCloud 仓库
├── AGENTS.md
├── PROJECT_INDEX.md
├── repos.yaml
├── _meta/doc/...
├── scripts/repo-status.sh
└── install-root-links.sh

/home/zh/www/                             # 根目录只放链接
├── AGENTS.md          -> personalCloud/workspace/AGENTS.md
├── PROJECT_INDEX.md   -> personalCloud/workspace/PROJECT_INDEX.md
├── repos.yaml         -> personalCloud/workspace/repos.yaml
├── _meta              -> personalCloud/workspace/_meta
└── scripts            -> personalCloud/workspace/scripts
```

日常维护：

```bash
git -C /home/zh/www/personalCloud add workspace
git -C /home/zh/www/personalCloud commit -m "docs(workspace): 更新跨仓约束"
git -C /home/zh/www/personalCloud push origin master
```

`install-root-links.sh` 只做幂等建链；新机器或 `personalCloud` 换位置后跑一次。若 DSH 不识别符号链接形式的 `AGENTS.md`，改为保留一个 5 行根 `AGENTS.md` 引导文件，详细规则仍在 `personalCloud/workspace/`。

## 实施步骤
1. 在 `personalCloud/workspace/` 建立与根目录一致的镜像结构，移入现有根文档、`_meta/` 和 `scripts/`。
2. 写 `install-root-links.sh`：校验源文件存在，幂等创建上述链接；已存在的真实文件/目录先报错，不自动覆盖。
3. 跑脚本建链，确认根路径内容可读；验证 DSH 能读取符号链接形式的 `AGENTS.md`，不生效则改用引导文件。
4. 写 `repos.yaml`，登记 `doc`、`dsh-superagent`、`dshSuperagentRepo`、`linuxops`、`personalCloud`、`project-experience`、`subscribeWatch`、`superagent-workbench`、`personalCloud/task/superCreater`、`personalCloud/task/xctl`。
5. `scripts/repo-status.sh` 逐仓输出当前分支、dirty、ahead/behind、未合并分支；不默认 `git fetch`。
6. 在 `personalCloud` 仓库提交并推送 `workspace/`。
7. 在 DSH 工作区界面新增 `/home/zh/www`；保留现有 `personalCloud` 等工作区不删。
8. 新建一个 `/home/zh/www` 会话验收：运行状态脚本、按索引定位 2 个仓、确认跨仓只读访问正常。

## 验收
- 新会话能直接读取 `/home/zh/www` 下所有登记仓库。
- 任务开始时能输出本次可写仓清单；未授权仓不产生写操作。
- 越界修改会先报告并等待确认。
- 根目录 `AGENTS.md`、`PROJECT_INDEX.md`、`repos.yaml`、`_meta/`、`scripts/` 均可读，且真实文件位于 `personalCloud/workspace/`。
- 修改根文件后，`git -C personalCloud status` 能看到对应改动；提交推送后远端有记录。
- `repo-status.sh` 能发现 dirty、ahead/behind 和 SA 未合并分支。
- 现有仓库目录结构和 git 历史不变。

## 回滚
- 删除根目录符号链接，从 `personalCloud/workspace/` 把文件复制回 `/home/zh/www/`。
- 从 `personalCloud` 仓库移除 `workspace/` 并提交回滚，或保留但不再建链。
- 在 DSH 中移除 `/home/zh/www` 工作区，继续使用原来的单仓工作区。
- 各项目仓库不受影响，无需回滚。

## 实施记录

- 2026-11-17：根文档、索引、仓库清单、`_meta/`、`scripts/` 的真实文件已迁入 `personalCloud/workspace/`；根目录对应 5 个入口均为符号链接。
- `install-root-links.sh` 已执行并重复执行验证幂等；`repo-status.sh` 能识别全部 10 个登记仓库。
- `personalCloud` commit `180a8ce` 已推送到 `origin/master`；SA 仍在 `feat/executor-budget-phase-end`，领先 `main` 3 个提交，未合并。
