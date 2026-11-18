---
audience: human
status: current
implementation_status: done
---

# PLAN：权限阻断规则与跨项目文档归并

## 目标

1. 在根 AI 规则中补全 sudo/只读阻断后的行为边界，禁止用 `/tmp`、`.tmp` 或仓外临时目录绕过。
2. 把 `personalCloud/doc` 中跨项目文档按 `spec / guide / reference / host fact` 分层迁入 `www/doc`，原位置只留链接。
3. 统一两份分叉的 task-workflow，`_meta/doc/task-workflow.md` 为唯一现行版。
4. 按 Specification-Driven Development 建立规则：长期约束进 spec，一次性变更留在 PLAN，PLAN 确认后回写 spec。

## 范围

纳入：

- `personalCloud/workspace/AGENTS.md`、`personalCloud/AGENTS.md`
- `personalCloud/workspace/_meta/doc/task-workflow.md`
- `personalCloud/doc/` 中下表的 8 份通用文档及 2 份重复文档
- `www/doc/specs/`、`www/doc/guides/`、`www/doc/reference/`、`www/doc/README.md`
- `www/doc/docs-policy.json` 的目录分类规则
- 受影响的阅读路由和链接：`personalCloud/README.md`、`personalCloud/workspace/PROJECT_INDEX.md`

不纳入：

- 宿主机专属文档内容重写
- `superCreater`、`xctl` 项目内 `audience: shared` 文档
- 任何代码、服务、git 仓库拆分

## 改动位置

### 规则

- `personalCloud/workspace/AGENTS.md`：「权限/只读阻断」补一句：
  `不在 /tmp、.tmp 或仓外临时目录做替代实验；确需临时验证时，先说明原因、位置和清理方式。`
- `personalCloud/AGENTS.md`：同步同一句，避免单仓入口与根入口不一致。
- `_meta/doc/task-workflow.md`：不重复规则，只在相关段落引用根 AGENTS。

### 文档分层

| 原位置 `personalCloud/doc/` | 新位置 | 类型 |
|---|---|---|
| `engineering-rules.md` | `doc/specs/engineering-rules.md` | spec |
| `operations-safety.md` | `doc/specs/operations-safety.md` | spec |
| `multi-repo-workspace.md` | `doc/specs/workspace-layout.md` | spec |
| `host-permission-pitfalls.md` | `doc/specs/host-permissions.md` | spec |
| `go-scaffold-guide.md` | `doc/guides/go-scaffold-guide.md` | guide |
| `troubleshooting-playbook.md` | `doc/guides/troubleshooting-playbook.md` | guide |
| `dsh-context-compaction.md` | `doc/reference/dsh-context-compaction.md` | reference |
| `dsh-plugins.md` | `doc/reference/dsh-plugins.md` | reference |

原位置改为 3 行以内的链接页，保留 `audience`/`status` frontmatter，并写明 canonical 路径。

### 规范元数据

每份 `doc/specs/*.md` 增加：

```yaml
owner: workspace
scope: /home/zh/www
```

`docs-policy.json` 增加 `specs/**` 分类规则；spec 正文只写适用范围、硬约束、验收方式和失效条件，不写一次性背景。

### 去重与索引

- `personalCloud/doc/task-workflow.md`：保留旧版中仍有效的任务边界、探索门禁、自动创建实施会话、常见坑，并入 `_meta/doc/task-workflow.md`；旧文件只留链接。
- `personalCloud/doc/project-registry.md`：以 `_meta/doc/project-registry.md` 为准，旧文件只留链接。
- `personalCloud/AGENTS.md`、`personalCloud/README.md` 的任务流程链接改指 `workspace/_meta/doc/task-workflow.md`。
- `doc/README.md` 增加 `specs/` 目录和权威来源说明。

## 实施步骤

1. 修改两份 AGENTS 规则；同步 `_meta/doc/task-workflow.md` 的阻断说明。
2. 对照旧版 task-workflow，把现行版缺失且仍有效的内容并入 canonical；不整篇复制旧文。
3. 用 `mv` 把 8 份文档移到 `doc/` 对应目录，在两个仓分别 `git add`；原位置生成链接页。
4. 给 4 份 spec 补 `owner`/`scope`，检查内容只保留长期有效约束；一次性背景移入 `decisions/` 或删除。
5. 全局搜索旧路径和文件名，更新 `AGENTS.md`、`README.md`、`PROJECT_INDEX.md`、`docs-policy.json` 中的引用。
6. 更新 `doc/README.md` 和 `doc/docs-policy.json`；补齐迁移文档的 `audience`/`status`。
7. 运行 `./scripts/check.sh --repo doc`、`./scripts/check.sh --repo personalCloud`，再检查仓内 Markdown 相对链接。
8. 两仓分别提交、推送，汇报 commit 和校验结果。

## 验收

- 根 AGENTS 和 personalCloud AGENTS 的权限阻断表述一致，且包含禁止临时目录绕过的内容。
- 旧 task-workflow/project-registry 不再有第二份正文，所有入口指向 `_meta/doc/`。
- 8 份文档只在 `www/doc` 保留正文，`personalCloud/doc` 原位置链接可打开。
- `doc/specs/` 下每份文件都有 `owner`、`scope`、适用范围和可执行验收方式。
- 全仓搜索不再有指向旧正文路径的失效链接。
- `doc` 与 `personalCloud` 的文档检查通过。

## 回滚

- 按仓 revert 对应 commit，恢复迁移前文件。
- 若只回滚文档、不回滚规则：单独 revert `doc` 仓迁移提交，再把 `personalCloud/doc` 链接页恢复为原正文。
