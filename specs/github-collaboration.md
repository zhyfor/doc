# GitHub/Gitee 协作与仓库治理

- 适用范围：`/home/zh/www` 下所有已登记仓库。
- 相关：[`task-workflow.md`](task-workflow.md)、[`project-registry.md`](project-registry.md)

## 1. GitHub 角色与身份

GitHub 的权限是“组织角色 + 仓库角色”两层叠加：

| 角色 | 定义与能做的事 | 本项目对应身份 |
|---|---|---|
| Org Owner | 组织最高权限：组织设置、成员、邀请、仓库创建/删除、计费、规则集 | `zhyfor` |
| Org Member | 组织成员；默认只有组织基础权限，具体仓库权限单独授予 | `super-YF` |
| Repository Admin | 单个仓库最高权限：设置、分支、协作者、删除仓库 | `zhyfor`（所有仓库） |
| Repository Maintain | 可管理仓库日常事务，但一般不能改危险设置或删仓 | 暂不单独授予 |
| Repository Write | 可推送分支、开 PR/Issue、合并（若允许）；不能改仓库设置 | `super-YF`（仅约定仓库） |
| Repository Read | 只读、克隆、评论；不能推送 | `super-YF` 的组织基准权限 |
| Outside Collaborator | 非组织成员，只按仓库授权 | 暂不使用 |
| Ruleset bypass actor | 规则集的例外身份，可绕过保护规则 | 当前不启用规则集 |

身份对应关系：

- `zhyfor`：GitHub 用户，`person-clouds` Org Owner，所有仓库的最终提交人和 Admin。
- `super-YF`：GitHub 用户，SA 运行身份，Org Member，基准 Read，仅在约定仓库有 Write。
- `person-clouds`：GitHub 组织，不是自然人身份。
- `fenghoer`：Gitee 账号，Gitee 个人仓库的最终提交人。
- dsh：不是独立 GitHub 账号，但本机执行助手可切换使用两个 GitHub 身份。
- SA：不是独立 GitHub 账号，在 SA 运行环境只能使用 `super-YF` 身份；提交信息正文加 `由SA更改`。

### dsh 可用的两个 GitHub 身份

| 身份 | 使用规则 |
|---|---|
| `zhyfor`（默认） | 默认提交、合并、发布、改仓库设置；最终提交人始终是 zhyfor |
| `super-YF`（特殊） | 仅在需要以 SA 身份操作时使用，如接受 Org/仓库邀请、归档或配置 super-YF 自有仓库、复现 SA 权限问题 |

- 默认一律使用 zhyfor；使用 super-YF 前确认操作确实属于 super-YF 权限范围。
- super-YF 只通过 `~/.config/gh-agent/` 的 `gh-agent` 凭证使用，不写入仓库或文档。
- 不把 super-YF 配成本机默认提交身份，不混用两个身份的提交历史。
- **SA 只能使用 super-YF 身份，不得使用 zhyfor。**
- 新仓库、新 fork 由 zhyfor 创建，再按需邀请 super-YF。
- super-YF 不给 Admin/Owner。

## 2. 分支与 PR

- 默认分支：`master`；无 `master` 用 `main`。
- 分支命名：dsh `dsh/<issue>-<slug>`；SA `sa/<issue>-<slug>`。
- 活跃 GitHub 仓库的 `main` 必须走 PR；CI 通过后合并；审批人数 0，用 CI + 自检清单。
- 禁止强推、删除受保护分支；历史有误用 `revert`，不改写。
- PR 标签：`agent:dsh` / `agent:sa`；PR 描述写任务 issue、验证方式、回滚方式。
- Gitee 个人仓库不强制 PR，由 zhyfor 直接推送。

## 3. 改动来源标记

- dsh 改动：不额外标记。
- SA 改动：提交信息正文加一行 `由SA更改`；PR 描述和 issue 收尾也写。
- 只写在提交说明/PR/issue，不在业务代码里散布标记。
- 历史提交不改写；已有 SA 改动未标记的，在对应 issue 补说明。

## 4. 规则集与权限（当前不启用）

Ruleset 是可选的限制工具，用来规定谁能推、谁必须走 PR、必须过哪些 CI、能否强推或删除分支；**不设置 ruleset 仓库也能正常使用**。

- 当前决定：先不启用 ruleset，靠约定、PR 模板、CI 和事后审查执行。
- 已做过的实验性 ruleset 已删除；`zhyfor/dshSuperagentRepo` 为私有免费仓库，本身也不支持 ruleset。
- 如未来要启用，再为仓库建 `main-protection`：要求 PR、禁止强推、禁止删除；需要时再加 required status checks。
- 启用前保存现有 ruleset JSON，便于回滚。
- GitHub Org：zhyfor Owner；super-YF 已接受邀请为 member，按仓库 Write。
- 标签：`agent:dsh`、`agent:sa`、`needs-human`、`source:feishu`。

## 5. 任务台账

- 所有任务统一登记在 `zhyfor/dshSuperagentRepo/issues`。
- 每个 issue 必填：目标仓库、平台（GitHub/Gitee）、分支、提交号/PR、验证结果、是否 SA 改动。
- 跨仓库任务拆子任务，逐仓收尾。
- Gitee 仓库的 SA 来源通过 issue 和提交信息追溯。

## 6. 飞书话题转 Issue

- 飞书话题是触发入口，不是自动任务库；默认不建 Issue。
- 出现具体任务、方案初稿完成或用户输入 `/issue` 时，询问一次。
- 菜单：
  - 新话题：`1. 转 Issue`、`2. 仅聊天，不转`、`3. 稍后再说`
  - 已有 Issue：`1. 追加到 #编号`、`2. 新建 Issue`、`3. 仅聊天`
- 选择 1/2 后在 `zhyfor/dshSuperagentRepo` 建 Issue，正文写飞书话题链接、原始需求、方案、目标仓库/平台、验收、是否 SA 改动；标签 `source:feishu`、`agent:sa`，assignee 为 zhyfor。
- 建完在飞书回链并记录 `话题 -> Issue` 映射；同一话题同一任务不重复建。
- 选择“仅聊天”后本话题不再自动询问，直到 `/issue` 或出现新任务。
- 转 Issue 前去掉 token、密码和隐私内容。

## 7. 迁移与回滚

- 迁移前执行 `git bundle create ... --all`，保存远程与本地 config。
- `dsh-superagent` 远程：`upstream` 官方、`origin` zhyfor fork、`sa-fork` 旧 super-YF fork。
- 旧 fork 在验收前不删除、不归档；确认无独有提交后再处理。
- 回滚文档用 `git revert`；GitHub 设置用事先保存的 JSON 恢复。
