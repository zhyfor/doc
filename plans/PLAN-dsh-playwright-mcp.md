---
implementation_status: not_started
created_at: 2026-11-19 10:52:00
updated_at: 2026-11-19 10:52:00
---

# PLAN：DSH 接入 Playwright MCP

## 目标

1. 在 DSH（`dsh-web`）注册 Playwright MCP，模型可用 `mcp__playwright__*` 工具驱动浏览器。
2. 调查并说明 superCreater 发抖音的实现方式（只读，不改该仓代码）。

## 范围

| 类型 | 对象 |
|---|---|
| 可写 | 全局 npm 包、`~/.dsh/cordis.patch.yml`、本计划文件 |
| 只读 | `personalCloud/task/superCreater`（仅读代码/配置，不改动） |
| 不做 | 不重启其他服务；不动 superCreater 的 Edge profile 与 CDP 9223 |

## 改动位置

| 位置 | 改动 |
|---|---|
| `/home/zh/.npm-global/lib/node_modules/@playwright/mcp` | 全局安装 `@playwright/mcp@0.0.86` |
| `~/.dsh/cordis.patch.yml` | `insert:` 段新增 `playwright-mcp` 条目 |
| `/home/zh/.dsh/mcp-artifacts/playwright/` | MCP 快照输出目录（运行时自建） |

新增配置（插在 `workdir-rag-mcp` 之后）：

```yaml
    - id: playwright-mcp
      name: "@deepseek-ai/dsh-mcp-client"
      config:
        serverName: playwright
        transport: stdio
        command: /home/zh/opt/node24/bin/node
        args:
          - /home/zh/.npm-global/lib/node_modules/@playwright/mcp/cli.js
          - --headless
          - --no-sandbox
          - --browser
          - chromium
          - --isolated
          - --viewport-size=1280,800
          - --output-dir=/home/zh/.dsh/mcp-artifacts/playwright
        cwd: /home/zh/www
        env:
          HOME: /home/zh
          PLAYWRIGHT_BROWSERS_PATH: /home/zh/.cache/ms-playwright
        toolCallTimeoutMs: 180000
```

参数依据（已本机验证）：

- `--browser chromium` 直接用已装 `chromium-1255`，不需要 `--executable-path`；默认 channel 是 `chrome`，本机没装会报 `Chromium distribution 'chrome' is not found`。
- 无 `DISPLAY`，必须 `--headless`；不加 `--no-sandbox` 时 chromium 启动后 SIGABRT。
- `--isolated` 用内存 profile：多会话不抢锁；代价是 DSH 重启后网站登录态丢失。
- `--output-dir` 避免快照写进当前目录（此前默认写到 `~/.playwright-mcp/`）。

## 实施步骤

1. `npm i -g @playwright/mcp@0.0.86`，确认 `/home/zh/.npm-global/lib/node_modules/@playwright/mcp/cli.js` 存在。
2. 备份 `~/.dsh/cordis.patch.yml`，在 `insert:` 段追加上述条目；不改动其它插件。
3. 裸跑冒烟（不经过 DSH）：stdio 发送 `initialize` + `tools/call browser_navigate`，期望返回 `Page Title: Example Domain`。
4. 报告并等待确认后重启：`systemctl --user restart dsh-web`（会中断当前会话与所有进行中的 DSH 会话）。
5. 重启后新建会话，确认工具列表出现 `mcp__playwright__browser_navigate` / `browser_snapshot`。

## 验收

- `node ~/.npm-global/lib/node_modules/@playwright/mcp/cli.js --version` 返回 `0.0.86`。
- 冒烟脚本返回 `Example Domain`，退出后无残留 `chrome-linux64/chrome` 进程。
- 重启后新会话可调用 `mcp__playwright__browser_navigate`，快照落在 `/home/zh/.dsh/mcp-artifacts/playwright/`。

## 回滚

1. 从 `~/.dsh/cordis.patch.yml` 删除 `playwright-mcp` 条目，`systemctl --user restart dsh-web`。
2. 需要彻底移除时 `npm rm -g @playwright/mcp`；`~/.dsh/mcp-artifacts/playwright/` 可直接删除。
3. 备份文件保留在 `~/.dsh/cordis.patch.yml.bak-playwright-mcp-<时间戳>`。

## 遗留

- 调查期冒烟在 `/home/zh/.playwright-mcp/` 留下一个 `page-*.yml` 快照；删除动作被用户拒绝，待确认后清理。

## 改动记录

- 2026-11-19 10:52 创建计划。
