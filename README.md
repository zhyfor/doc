# 跨仓文档

> `/home/zh/www/doc` 存放**可公开**的跨仓规范与流程。项目事实在各仓自己的 `README.md` / `STATUS.md` / `docs/`；个人计划、主机网络事实与运行细节不在此仓。

## 目录

| 目录 | 放什么 |
|---|---|
| `specs/` | 跨仓硬约束与流程：工程、运行安全、文档规范、任务工作流、仓库登记、Git 协作、npm 发布 |
| `subscribeWatch/` | 订阅监控隐私页（GitHub Pages 公开） |

`specs/` 是跨仓规则与流程的唯一权威源；其他位置只链接，不复制正文。个人计划与主机运行事实在私有 `personalCloud` 仓。

## 规则

- 一个主题只放一份主文档，其他位置只留链接。
- 普通文档不写 frontmatter；`PLAN-*.md` 只写 `implementation_status`、`created_at`、`updated_at`，正文必须有 `## 改动记录`，每条只记「时间 + 改动点」。
- 状态枚举：`not_started | in_progress | fixing | blocked | done | rolled_back`。
- 只写事实、硬约束、路由、可执行步骤和最小验收；背景、推导、过程日志放私有归档。
- 行数超限默认 `WARN`；计划含 `## 篇幅说明` 且 ≤400 行时放行；断链、非法计划状态、缺计划元数据为 `FAIL`。完整规则见 [`specs/documentation-rules.md`](specs/documentation-rules.md)。
- README / npm / 插件市场文案的硬规则见 [`specs/documentation-rules.md`](specs/documentation-rules.md) §6。
- 本仓不得写入内网地址、主机名、MAC、设备标识、账号口令与个人计划；新增内容先按此复核再提交。

## 校验

```bash
cd /home/zh/www
./scripts/check.sh --repo doc
./scripts/check.sh --all --strict
./scripts/check.sh --all --slim    # 只列超限文档与 doc-slim 步骤
./scripts/docs-watch.sh --once
```
