# 跨仓文档

> `/home/zh/www/doc` 存放跨仓规范、流程、计划与人类历史资料。项目事实在各仓自己的 `README.md` / `STATUS.md` / `docs/`。

## 目录

| 目录 | 放什么 |
|---|---|
| `specs/` | 跨仓硬约束与流程：工程、运行安全、文档规范、任务工作流、仓库登记、Git 协作 |
| `plans/` | 当前活跃的跨仓计划 `PLAN-*.md` |
| `reference/` | 稳定事实、索引、对照表等非必读参考 |
| `archive/` | 已结束计划、过程记录与复盘 |
| `subscribeWatch/` | 订阅监控隐私页 |

`specs/` 是跨仓规则与流程的唯一权威源；其他位置只链接，不复制正文。

## 规则

- 一个主题只放一份主文档，其他位置只留链接。
- 普通文档不写 frontmatter；`PLAN-*.md` 只写 `implementation_status`、`created_at`、`updated_at`，正文必须有 `## 改动记录`，每条只记「时间 + 改动点」。
- 状态枚举：`not_started | in_progress | fixing | blocked | done | rolled_back`。
- 只写事实、硬约束、路由、可执行步骤和最小验收；背景、推导、过程日志放 `archive/`。
- 行数超限默认 `WARN`；计划含 `## 篇幅说明` 且 ≤400 行时放行；断链、非法计划状态、缺计划元数据为 `FAIL`。完整规则见 [`specs/documentation-rules.md`](specs/documentation-rules.md)。
- README / npm / 插件市场文案的硬规则见 [`specs/documentation-rules.md`](specs/documentation-rules.md) §6。

## 校验

```bash
cd /home/zh/www
./scripts/check.sh --repo doc
./scripts/check.sh --all --strict
./scripts/check.sh --all --slim    # 只列超限文档与 doc-slim 步骤
./scripts/docs-watch.sh --once
```
