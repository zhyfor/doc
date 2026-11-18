---
audience: shared
status: current
---

# 跨仓文档

> `/home/zh/www/doc` 存放跨仓文档、计划与隐私页。操作规则在 `_meta/doc/`，项目事实在各仓自己的 `README.md` / `STATUS.md`。

## 目录

| 目录 | 放什么 | audience |
|---|---|---|
| `specs/` | 跨仓硬约束（工程、运维、权限、布局） | shared |
| `plans/` | 跨仓任务计划 `PLAN-*.md` | human |
| `guides/` | 可执行的跨仓操作指南 | shared |
| `reference/` | 稳定事实、索引、对照表 | shared |
| `decisions/` | 跨仓决策记录 | shared |
| `archive/` | 已结束任务的过程记录与复盘 | human |
| `subscribeWatch/` | 订阅监控隐私页 | human |

`specs/` 是跨仓硬约束的唯一权威源；`personalCloud/doc/` 下的同名文件只留一行链接，不再保留正文。

## 规则

- 一个主题只放一份主文档，其他位置只留一行链接。每个 `specs/*.md` 必须写 `owner`、`scope`、适用范围、可执行的验收方式与失效条件。
- 新计划 frontmatter 必须写 `implementation_status`，正文不再写状态行。
- 状态枚举：`not_started | in_progress | fixing | blocked | done | rolled_back`。
- AI/shared 文档只写事实、约束、路由、可执行步骤；新文档上限分别为 120/200 行。
- 背景与复盘放 `archive/`，决策理由放 `decisions/`，禁止多文档复制同一内容。

## 校验

```bash
cd /home/zh/www
./scripts/check.sh --repo doc
```
