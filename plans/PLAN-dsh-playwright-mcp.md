---
implementation_status: in_progress
created_at: 2026-11-19 12:46:55
updated_at: 2026-11-19 15:35:00
---

# PLAN：DSH 接入 Playwright MCP

## 目标

1. 在 DSH（`dsh-web`）注册 Playwright MCP，模型可用 `mcp__playwright__*` 工具驱动浏览器。
2. 提供重启前的配置自检入口（类似 `nginx -t`），提前暴露补丁合成、路径、握手、浏览器启动问题。
3. 说明 superCreater 发抖音的实现方式（只读调查，未改该仓代码）。

## 范围

| 类型 | 对象 |
|---|---|
| 可写 | 全局 npm 包、`~/.dsh/cordis.patch.yml`、`workspace/scripts/dsh-config-check.py`、本计划文件 |
| 只读 | `personalCloud/task/superCreater`（仅读代码/配置） |
| 不做 | 不重启其他服务；不动 superCreater 的 Edge profile 与 CDP 9223 |

## 改动位置

| 位置 | 改动 |
|---|---|
| `/home/zh/.npm-global/lib/node_modules/@playwright/mcp` | 全局安装 `@playwright/mcp@0.0.86`（用户已执行） |
| `~/.dsh/cordis.patch.yml` | `insert:` 段新增 `playwright-mcp` 条目（用户已执行） |
| `workspace/scripts/dsh-config-check.py` | 新增重启前自检脚本 |
| `/home/zh/.dsh/mcp-artifacts/playwright/` | MCP 快照输出目录（运行时自建） |

配置条目（已写入）：

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

参数依据（本机验证）：

- `--browser chromium` 直接使用已装 `chromium-1255`，无需 `--executable-path`；默认 channel 是 `chrome`，本机没有会报 `Chromium distribution 'chrome' is not found`。
- 无 `DISPLAY`，必须 `--headless`；不加 `--no-sandbox` 时 chromium 启动即 SIGABRT。
- `--isolated` 用内存 profile：多会话不抢锁；代价是 DSH 重启后网站登录态丢失。
- `--output-dir` 防止快照写进当前目录。

## 自检脚本

`./scripts/dsh-config-check.py`（`--profile` 默认 `web`，`--mcp` 只查单个，`--deep` 额外启动浏览器导航）：

1. 跑 `dsh --profile web --dump-config`，校验补丁能合成、插件能解析（非 0 直接失败，stderr 归为 WARN）。
2. 解析合成结果，逐个 MCP 校验 `serverName`、`transport`、`command` 可执行、参数里的绝对路径、`cwd`、`env.HOME/NODE_PATH`、`--output-dir` 可写。
3. 按配置真实启动 MCP 子进程（冻结 env、cwd），发 `initialize` + `tools/list`，30s 内拿不到结果即失败；结束后按进程组回收，不留浏览器。
4. `--deep` 再调一次 `browser_navigate https://example.com`，验证浏览器真能启动并导航。

## 实施步骤

1. ~~`npm i -g @playwright/mcp@0.0.86`~~（用户已执行，`npm ls -g` 确认 0.0.86）。
2. ~~`~/.dsh/cordis.patch.yml` 追加 `playwright-mcp`~~（用户已执行，`dsh --dump-config` 已能读出该条目）。
3. ~~新增自检脚本~~并跑通浅检 + 深检。
4. 用户确认后重启：`systemctl --user restart dsh-web`（中断当前及所有进行中的会话）。
5. 重启后新建会话，确认工具列表出现 `mcp__playwright__browser_navigate` / `browser_snapshot`。

## 验收

- `./scripts/dsh-config-check.py --deep` 返回 exit 0，playwright 条目「握手成功 … 25 个工具」+「浏览器启动并导航成功」。
- 重启后新会话可调用 `mcp__playwright__browser_navigate`，快照落在 `/home/zh/.dsh/mcp-artifacts/playwright/`。
- 自检与冒烟结束后无残留 `chrome-linux64/chrome` 进程（已确认）。

## 回滚

1. 从 `~/.dsh/cordis.patch.yml` 删除 `playwright-mcp` 条目，`systemctl --user restart dsh-web`。
2. 彻底移除：`npm rm -g @playwright/mcp`；`~/.dsh/mcp-artifacts/playwright/` 可删。
3. 自检脚本删除 `workspace/scripts/dsh-config-check.py` 即可，无运行时依赖。

## 遗留

- 调查期快照 `/home/zh/.playwright-mcp/` 与自检产生的 `~/.dsh/mcp-artifacts/playwright/page-*.yml` 需要清理；本会话删除操作被审批策略自动拒绝，命令交用户执行（见收尾报告）。
- 自检的 6 条 `patch: entry ... not found` 属既有 profile 补丁告警（`auto-continue`、`vision-router`、`dsh-superagent`），与本次改动无关，未处理。

## 改动记录

- 2026-11-19 10:52 创建计划。
- 2026-11-19 15:35 用户完成全局安装与配置写入；新增 `scripts/dsh-config-check.py`，浅检/深检通过；补记录与遗留清理说明。
