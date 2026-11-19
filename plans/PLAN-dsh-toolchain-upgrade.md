---
implementation_status: not_started
created_at: 2026-11-19 20:15:00
updated_at: 2026-11-19 20:15:00
---

# PLAN：补齐本机工具链与 DSH 能力（一天升级）

## 目标

1. 消掉历史会话里反复出现的「本机没装 → 只能在 /tmp 里绕」的能力缺口。
2. 补上成熟、用的人多的命令行工具，减少临时脚本。
3. 把 DSH 侧按需能力（MCP、实验 bundle）配好开关，不默认吃 token。

## 依据

- 480 个会话日志（283MB）单次解压扫描：`sqlite3` CLI 4 次直接报缺 + 30 次用 `import sqlite3` 顶替；`shellcheck` ≥5 次降级为 `bash -n`；`xdotool` 3 次用 `dpkg -x` 解包到 `/tmp/xdotool` 绕；`ollama` 9 次回退到 `dsh-vision`；`gh`/`uv`/`dsh-rag` 误判未装，实因 `~/.local/bin` 不在非交互 PATH。
- 本机实测：Ubuntu 26.04 LTS（resolute），apt 只索引 `resolute-security`，装 universe 包前需 `sudo apt update`。

## 范围

| 类型 | 对象 |
|---|---|
| 可写 | `~/.config/systemd/user/dsh-web.service`、`~/.local/bin`、`~/.dsh/cordis.patch.yml`、`~/.dsh/profiles/web/package.json`、本计划文件 |
| 需 root（用户执行） | `apt install` 系统包、`/usr/local/bin/yq` |
| 不做 | DSH 核心升级（0.2.2-rc.1 → rc.5）；libreoffice、rclone、git-lfs；filesystem/fetch/sequential-thinking MCP |

## 分档

### P0 已定位的小改动（无 root）

| 项 | 改动 | 状态 |
|---|---|---|
| `~/.local/bin` 进 PATH | `dsh-web.service` 的 `Environment=PATH` 前插 `%h/.local/bin`，`daemon-reload` | 已改，待重启生效 |

### P1 系统工具（用户执行 apt，一次装完）

```bash
sudo apt update
sudo apt install -y ripgrep fd-find fzf bat git-delta shellcheck sqlite3 \
  pandoc tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng ocrmypdf \
  imagemagick libimage-exiftool-perl qpdf mediainfo mkvtoolnix csvkit miller zoxide hyperfine xdotool
ln -sf "$(command -v fdfind)" ~/.local/bin/fd
ln -sf "$(command -v batcat)" ~/.local/bin/bat
```

用户级补充（AI 执行）：`uv tool install duckdb`、`~/.local/bin/yq`（GitHub 二进制，不用 apt 的 Python 版）、`uv tool install ruff`。

### P2 按需 DSH 能力（需重启 dsh-web）

| 项 | 动作 | 默认状态 |
|---|---|---|
| session-search bundle | `dsh plugin --profile web add @deepseek-ai/dsh-experimental-session-search` | 开 |
| context7 MCP | `cordis.patch.yml` 插入，2 个工具 | 开（schema 小） |
| chrome-devtools MCP / markitdown MCP / serena | 插入并 `disabled: true` | 关，按需开 |
| cot-translation / agent-team / ralph / cua / plugin-market | — | 不装 |

### P3 待定（成本或风险高，需单独决定）

ollama（模型 GB 级）、Ghidra（REA provider）、auditd、aria2、git-lfs。

## 验证

- `command -v` 逐个核对（用显式 `PATH=$HOME/.local/bin:$PATH`，避免再次误判）。
- `sqlite3 --version`、`shellcheck -V`、`rg --version`、`yq --version`、`duckdb --version`。
- DSH 侧：`workspace/scripts/dsh-config-check.py --deep` 通过后再重启；重启后确认 `mcp__context7__*` 与 session-search 工具出现。

## 回滚

- 服务文件：`cp ~/.config/systemd/user/dsh-web.service.bak.<时间戳> ~/.config/systemd/user/dsh-web.service && systemctl --user daemon-reload`。
- MCP/bundle：patch 条目改回 `disabled: true`；bundle 用 `dsh plugin --profile web remove <包名>`。
- apt 包：`sudo apt remove <包名>`（不影响既有配置）。

## 执行进展

| 项 | 状态 |
|---|---|
| `dsh-web.service` PATH 前置 `%h/.local/bin` | 已改 + `daemon-reload`，待重启生效 |
| `yq v4.54.3` | 已装到 `~/.local/bin/yq` |
| `ruff 0.17.5` | 已装（`uv tool`） |
| `duckdb` | 未装：`uv tool install duckdb` 无 CLI 入口被回滚；GitHub release 资产名 404，待查 |
| `@upstash/context7-mcp` | 已全局安装；`cordis.patch.yml` 新增 `context7-mcp`（2 工具） |
| `dsh-experimental-session-search@0.2.2-rc.1` | 已装入 web profile，bundle 已登记 |
| `dsh-config-check.py --deep` | 通过（结论：配置可加载） |
| apt 系统包 | 待用户执行 |
| 重启 dsh-web | 待执行 |

## 顺带修的一个脚本缺陷

`scripts/dsh-config-check.py` 的 `--deep` 原来对**所有** MCP 都调用 `browser_navigate` 探测，只有 `playwright` 有这个工具，导致 `workdir-rag`、`context7` 必然 FAIL，并误报"配置不可加载，不要重启 dsh"。已把探测条件收敛为 `if deep and server == "playwright"`。

## 改动记录

| 日期 | 内容 |
|---|---|
| 2026-11-19 | 建档；PATH 已改待重启；yq/ruff/context7/session-search 已落地；修正自检脚本浏览器探测 |
