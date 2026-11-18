---
audience: human
status: current
implementation_status: done
---
# PLAN: SA/dsh 仓库治理与 dsh-superagent 迁移
- 日期：2026-11-17
- 已确认：zhyfor 是唯一提交人；super-YF 只作为 SA 执行身份，按仓库给 Write；dsh-superagent 新建 zhyfor fork 并迁移现有改动；Gitee 个人项目只由 zhyfor 提交，SA 改动必须标记“由SA更改”；飞书话题作为 SA 触发入口，转 Issue 必须由你选择。

## 目标

- SA（super-YF）和 dsh（借用 zhyfor）共同维护代码，但所有仓库的最终提交人都保持为 zhyfor。
- 任务统一在 `zhyfor/dshSuperagentRepo/issues` 跟踪，覆盖 GitHub 和 Gitee 项目。
- 新仓库/新 fork 都由 zhyfor 创建，再按需给 super-YF 分 Write 权限。
- 把 `dsh-superagent` 从 super-YF fork 迁移到 zhyfor fork，且不丢失现有提交。
- 每处 SA 产生的改动都能从提交信息识别；dsh 改动不额外标记。

## 范围

**纳入：**

- 任务台账：`zhyfor/dshSuperagentRepo/issues`
- 飞书聊天话题：SA 的触发入口，支持“转 Issue / 仅聊天 / 稍后”选择。
- GitHub Org `person-clouds`：`superagent-workbench`、`dsh-context-guard`、`dsh-workflow-shortcuts`
- 待迁移：`super-YF/dsh-superagent-prototype` → 新建 `zhyfor/dsh-superagent-prototype`
- 个人 GitHub：`zhyfor/doc`、`zhyfor/dshSuperagentRepo`
- Gitee 仓库：`personalCloud`、`superCreater`、`xctl`、`project-experience`、`subscribeWatch`、`linuxops`
- 工作区文件：`AGENTS.md`、`PROJECT_INDEX.md`、`repos.yaml`、`_meta/doc/`

**不纳入：**

- 不重写 git 历史，不强制推送，不删除仓库。
- 不做 GitHub/Gitee 双向同步；每个仓库只保留一个主平台。
- 不把 Gitee 仓库迁移到 GitHub。

## 统一规则

1. **身份**
   - zhyfor：Org Owner，所有仓库的最终提交人。
   - super-YF：Org member，基准 Read；只对需要维护的仓库给 Write，不给 Admin。
   - 本机所有 clone 默认用 zhyfor；只有 SA 自己的运行环境固定用 super-YF。
   - 新仓库、新 fork 一律 zhyfor 先创建，再邀请 super-YF。

2. **分支与 PR**
   - 活跃 GitHub 仓库的 `main`：必须 PR、CI 通过、线性历史、禁止强推/删除；审批人数 0，用 CI + 自检清单。
   - dsh 分支：`dsh/<issue>-<slug>`；SA 分支：`sa/<issue>-<slug>`。
   - PR 标签：`agent:dsh` / `agent:sa`；PR 描述写任务 issue、验证方式、回滚方式。
   - Gitee 个人仓库不强制 PR，继续直接推送；但必须遵守下面的来源标记。

3. **改动来源标记**
   - dsh 改的：不额外标记。
   - SA 改的：提交信息正文必须加一行 `由SA更改`；PR 描述或 issue 收尾也写 `由SA更改`。
   - 只在提交说明/PR/issue 中标记，不在代码里到处插注释。
   - 历史提交不再改写；已由 SA 改动但未标记的提交，在对应 issue 中补一条说明。

4. **任务台账**
   - 每个任务在 `zhyfor/dshSuperagentRepo/issues` 建 issue。
   - issue 必须写：目标仓库、平台（GitHub/Gitee）、分支、提交号/PR、验证结果、是否 SA 改动。
   - 跨仓库任务拆成子任务，逐仓收尾。

5. **Gitee 管理**
   - Gitee 仓库继续由 zhyfor 直接提交，SA 不直接推。
   - SA 只产出补丁/分支/修改说明，由 dsh 或 zhyfor 落到 Gitee。
   - 由 SA 产出并提交的改动，提交信息加 `由SA更改`。

6. **飞书话题转 Issue**
   - 飞书话题是触发入口，不是自动任务库；默认不建 Issue，由你选择。
   - SA 只在出现具体任务、方案初稿完成或你输入 `/issue` 时询问一次，不每条消息都问。
   - 回复末尾给文本菜单：
     ```
     是否将此话题转为 GitHub Issue？
     1. 转 Issue
     2. 仅聊天，不转
     3. 稍后再说
     ```
   - 已有 Issue 时改为：`1. 追加到 #编号`、`2. 新建 Issue`、`3. 仅聊天`。
   - 选 1 后在 `zhyfor/dshSuperagentRepo` 建 Issue，正文写：飞书话题链接、原始需求、方案、目标仓库/平台、验收、是否 SA 改动；标签 `source:feishu`、`agent:sa`，assignee 为 zhyfor。
   - 建完在飞书回 Issue 链接，并记录 `话题 -> Issue` 映射；同一话题同一任务不重复建。
   - 选 2 后本话题不再自动询问，直到你输入 `/issue` 或出现新任务。
   - 转 Issue 前必须去掉 token、密码、隐私内容。

7. **dsh-superagent 迁移**
   - 新建 `zhyfor/dsh-superagent-prototype` fork，保留官方 `deepseek-ai/dsh-superagent-prototype` 为上游。
   - 迁移本地 `main` 的 `c4654c3`，以及 `feat/executor-budget-phase-end` 的 `93ca866`、`d2a3b60`、`db5f06d`、`31ec20c`。
   - 本地远程最终为：`upstream` = 官方，`origin` = zhyfor fork，`sa-fork` = 原 super-YF fork。
   - 在 zhyfor fork 内开 PR：`feat/executor-budget-phase-end` → `main`，确认 CI 后合并。

## 改动位置

**GitHub：**

- 新建 fork `zhyfor/dsh-superagent-prototype`。
- `person-clouds` 成员权限：zhyfor Owner，super-YF member + 指定仓库 Write。
- 3 个 org 仓库和 zhyfor fork 的 Rulesets。
- 新建 `person-clouds/.github`：PR/Issue 模板、贡献说明、安全策略。
- 各仓库标签：`agent:dsh`、`agent:sa`、`needs-human`。

**本地：**

- `/home/zh/www/dsh-superagent/.git/config`：远程和身份。
- `/home/zh/www/dsh-superagent/src/sources/feishu-channel.ts`、`feishu.ts`：飞书回复末尾菜单。
- `/home/zh/www/dsh-superagent/src/sources/github-channel.ts`：创建 Issue、回链。
- `/home/zh/www/dsh-superagent/src/sources/feishu-trigger.ts`、`github-trigger.ts`：话题与 Issue 映射、命令识别。
- `/home/zh/www/dsh-superagent/tests/`：菜单选择、重复创建、权限失败用例。
- `/home/zh/www/personalCloud/workspace/AGENTS.md`：默认 zhyfor；SA 改动标记规则；活跃 GitHub 仓库走分支 + PR。
- `/home/zh/www/personalCloud/workspace/PROJECT_INDEX.md`：补任务台账、平台、账号、远程。
- `/home/zh/www/personalCloud/workspace/repos.yaml`：增加 `owner`、`platform`、`task_ledger`、`protection`、`agent`。
- `/home/zh/www/personalCloud/workspace/_meta/doc/github-collaboration.md`：唯一规则文档。
- `/home/zh/www/PLAN-cross-repo-workspace.md` 顶部注明推送策略已被本计划取代。

## 实施步骤

1. **备份**：在 `dsh-superagent` 执行 `git bundle create /tmp/dsh-superagent-before-migration.bundle --all`；记录各仓库 remote 和 config。
2. **建新 fork**：zhyfor 在 GitHub 新建 `dsh-superagent-prototype` fork。
3. **迁移提交**：
   - `git remote add zhyfor https://zhyfor@github.com/zhyfor/dsh-superagent-prototype.git`
   - `git push zhyfor main:main`
   - `git push zhyfor feat/executor-budget-phase-end:feat/executor-budget-phase-end`
4. **改远程名**：
   - `git remote rename origin upstream`
   - `git remote rename fork sa-fork`
   - `git remote rename zhyfor origin`
   - `git fetch --all`
5. **合并到新 fork**：在 zhyfor fork 开 PR `feat/executor-budget-phase-end` → `main`；通过检查后合并，确认 `c4654c3` 和四个 feature 提交都在。
6. **归档旧 fork**：确认 `sa-fork` 没有独有提交后，归档 `super-YF/dsh-superagent-prototype`；有独有提交则先迁再归档。
7. **配权限与保护**：设置 org 成员角色；对 3 个 org 仓库、zhyfor fork、`zhyfor/dshSuperagentRepo` 加 ruleset；`zhyfor/doc` 只禁强推/删除。
8. **建 org 模板**：创建 `person-clouds/.github`，加入 PR/Issue 模板、`CONTRIBUTING.md`、`SECURITY.md`。
9. **更新工作区文档**：改 `AGENTS.md`、`PROJECT_INDEX.md`、`repos.yaml`，新增 `github-collaboration.md`；单独提交到 `personalCloud`。
10. **补任务记录**：在 `dshSuperagentRepo/issues` 为本次迁移建 issue，记录旧 fork、迁移提交、新 fork、验证结果；superCreater 已有 SA 改动补一条“由SA更改”说明。
11. **接入飞书转 Issue**：在 SA 回复末尾加菜单；实现 `/issue` 命令；创建后回链并记录话题映射；已有 Issue 时只提供追加或新建。
12. **验收收尾**：输出每个仓库的 commit、push、迁移和验证结果。

## 验收

- `zhyfor/dsh-superagent-prototype` 包含 `c4654c3` 和四个 feature 提交，无提交丢失。
- 本地 `upstream`/`origin`/`sa-fork` 指向正确；旧 super-YF fork 无独有提交。
- zhyfor 仍是所有仓库的最终提交人；SA 改动提交信息含 `由SA更改`，dsh 改动无额外标记。
- 活跃 GitHub 仓库 main 直接 push 被拒绝；PR 必须通过 CI。
- `super-YF` 不是 org Owner，仅对约定仓库有 Write。
- Gitee 仓库仍可直接推送，任务 issue 中能追溯 SA/dsh 来源。
- 飞书话题默认不建 Issue；选择“转 Issue”后能生成带来源链接的 Issue，并有回链。
- 同一飞书话题同一任务不会重复建 Issue；已有 Issue 时可追加评论。
- `repos.yaml`、`PROJECT_INDEX.md`、`AGENTS.md` 与新规则一致。
- 仓库和脚本中不存在明文 token。

## 回滚

- 迁移前已有 `git bundle`；回滚时从 bundle 恢复分支和远程。
- 新 fork 可删除；旧 `super-YF` fork 在验收前不归档、不删除。
- GitHub 设置：执行前保存 org 角色和 ruleset JSON；回滚时恢复。
- 本地：备份 `~/.gitconfig` 和各仓库 `.git/config`；逐项还原。
- 文档：用 `git revert` 回退提交，不用 `reset` 或强推。
