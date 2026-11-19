---
implementation_status: done
created_at: 2026-11-19 00:00:00
updated_at: 2026-11-19 00:00:00
---

# PLAN：DSH 默认权限改为 danger-full-access

## 目标

去掉新会话默认 `workspace-write` 造成的伪“挂载只读”，让 AI 可以直接写仓库 `.git` 并提交。

## 范围

- 改：`~/.dsh/profiles/web` 的 `permission.defaultPreset`。
- 不改：AGENTS、operations-safety、仓库代码、危险命令检查。
- 已存在会话不受影响，需要时用 `/permission danger-full-access` 切换。

## 改动位置

- `~/.dsh/profiles/web/cordis.patch.yml`：`permission.defaultPreset: danger-full-access`。

## 实施步骤

1. 通过 DSH `settings/update` 写入 `permission.defaultPreset=danger-full-access`。
2. 新建会话，确认事件为 `danger-full-access` / `never`。
3. 归档验证会话。

## 验收

- 新建会话首事件为 `permission/preset: danger-full-access`、`sandbox/mode: danger-full-access`、`approval/policy: never`。
- 后续任务会话可直接写入仓库父级 `.git`，不再出现沙箱伪只读。

## 回滚

- 将 `permission.defaultPreset` 改回 `workspace-write`，或删除该项并重启 dsh-web。

## 改动记录

- 2026-11-19：通过 DSH settings API 写入 `permission.defaultPreset=danger-full-access`；新建验证会话 `session-60b0995d-9f71-47e3-a355-a1847066f604` 的事件确认三项均为 full access，验证后已归档。
