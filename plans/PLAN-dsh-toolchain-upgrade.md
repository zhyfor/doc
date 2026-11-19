---
implementation_status: in_progress
created_at: 2026-11-19 20:15:00
updated_at: 2026-11-20 05:50:00
---

# PLAN：DSH 能力升级总计划（交接版）

> 本轮能力升级的唯一主文档：做了哪些、现状、待办、交接规程与坑。决策明细见 [PLAN-dsh-p3-deferred-tools-roi.md](PLAN-dsh-p3-deferred-tools-roi.md)。

## 0. 新会话从这里开始

**一句话**：P0–P2 与 P3 Tier A 已全部落地并验证；剩余为可选项与一个 RAG 向量链路缺陷。

**必读 3 个文件**

| 文件 | 看什么 |
|---|---|
| 本文 | 历史、现状、待办、坑 |
| [PLAN-dsh-p3-deferred-tools-roi.md](PLAN-dsh-p3-deferred-tools-roi.md) | P3 五项成本/收益与执行序列 |
| [dsh-config-check.py](/home/zh/www/personalCloud/workspace/scripts/dsh-config-check.py) | 改 DSH 配置后的必跑自检 |

**开工前三条自检**（确认现状与本文一致）

```bash
for c in rg fd fzf bat delta sqlite3 shellcheck pandoc tesseract ocrmypdf \
         convert exiftool qpdf mediainfo mkvinfo csvlook mlr zoxide hyperfine \
         xdotool yq ruff duckdb dsh-rag; do printf "%-11s %s\n" "$c" "$(command -v $c || echo MISSING)"; done
cd /home/zh/www/personalCloud/workspace && python3 scripts/dsh-config-check.py --deep | tail -5
systemctl --user show dsh-web -p ActiveState -p Environment
```

## 1. 缺口（为什么做）

| 类型 | 表现 | 处理 |
|---|---|---|
| 真没装 | `sqlite3`/`shellcheck`/`xdotool`/`ruff`/`aria2` 等被反复用脚本顶替 | apt 或 GitHub 安装 |
| 假缺失 | `gh`/`uv`/`dsh-rag` 已装但不在非交互 PATH | 修 systemd `Environment=PATH` |

## 2. 已完成（P0–P2）

### 2.1 系统工具

| 类别 | 工具（版本） |
|---|---|
| 搜索/浏览 | `rg` 15.1.0、`fd` 10.3.0、`fzf` 0.67.0、`bat` 0.25.0、`delta` 0.18.2 |
| 数据 | `sqlite3` 3.46.1、`duckdb` v1.5.6、`csvlook` 2.2.0、`mlr` 6.16.0、`yq` v4.54.3 |
| 文档/OCR | `pandoc` 3.7.0.2、`tesseract` 5.5.0（chi_sim+eng+osd）、`ocrmypdf` 16.13.0 |
| 媒体 | `convert` 7.1.2、`exiftool`、`qpdf` 12.3.2、`mediainfo`、`mkvinfo` v97.0 |
| 质量/效率 | `shellcheck` 0.11.0、`ruff` 0.17.5、`zoxide` 0.9.8、`hyperfine` 1.19.0、`xdotool` 3.20160805.1 |

安装细节：

- apt 包由用户在宿主终端执行（AI 无 root）；`fdfind`/`batcat` 已软链为 `fd`/`bat`。
- `uv tool install duckdb` 无效（无 CLI 入口），须下载 GitHub release 的 `duckdb_cli-linux-amd64.zip` **且指定版本**（`latest` 无该资产）。
- `yq` 用 GitHub 二进制装到 `~/.local/bin`，不要 apt 的 Python 版。

### 2.2 PATH 修复

`~/.config/systemd/user/dsh-web.service` 的 `Environment=PATH` 前插 `%h/.local/bin`，重启后非交互 PATH：

```
/home/zh/.local/bin:/home/zh/opt/node24/bin:/home/zh/.npm-global/bin:/usr/local/bin:/usr/bin:/bin
```

### 2.3 DSH 侧

| 项 | 状态 | 说明 |
|---|---|---|
| `context7` MCP | 开 | `cordis.patch.yml` 新增，2 个工具，schema 小 |
| `session-search` | 开 | `@deepseek-ai/dsh-experimental-session-search@0.2.2-rc.1`，已登记 web profile |
| `rea-mcp` / `headroom-mcp` | 关 | 原本 `disabled: true` |
| `workdir-rag` / `playwright` | 开 | 握手 + 导航实测通过 |

- 刻意没装：filesystem/fetch/sequential-thinking（与内置重复）、cot-translation、agent-team、ralph、cua、plugin-market、chrome-devtools-mcp（26 工具、+6k token）、markitdown-mcp、serena。
- 刻意没升级：DSH 0.2.2-rc.1 → rc.5（18 个插件 peer 约束都对着 rc.1，收益不抵风险）。

### 2.4 顺带修的两个缺陷

1. `dsh-config-check.py --deep` 对所有 MCP 调 `browser_navigate`，只有 playwright 有该工具导致误报 FAIL；已收敛为仅对 playwright 深检（`c753332`）。
2. `doc/specs/operations-safety.md` 的 `browser-debug` 链接指向不存在路径；已改指 `../../.dsh/skills/browser-debug/SKILL.md`。

### 2.5 回滚备份

unit `~/.config/systemd/user/dsh-web.service.bak.20261119-200000`；patch `~/.dsh/cordis.patch.yml.bak.20261119-201330`；web profile `~/.dsh/profiles/web/package.json.bak.20261119-*`。

## 3. 现状快照（2026-11-19 21:30）

硬件：Ryzen 7 8845HS（16 线程、AVX-512）、46 GB 内存、Radeon 780M 核显（无 CUDA）、`/` 可用 734 GB、代理 `127.0.0.1:7897`。

| 服务 | 地址/入口 | 状态 |
|---|---|---|
| `dsh-web` | `https://zh-gem-r7.tailb6e152.ts.net:8443/`（本机 3080） | active |
| `dsh-ml` | `127.0.0.1:8765` | ready，`bge-m3`/`bge-small-zh-v1.5`/`bge-reranker-v2-m3` 已加载 |
| `dsh-rag` | MCP `workdirrag` | 4226 文件 / 53967 块，**向量 0/53967**（见 §4.4） |
| `dsh-vision` | `~/.local/bin/dsh-vision` | `ocr`/`info`/`enhance`/`describe` 全部可用 |
| `dsh-ollama` | `127.0.0.1:11434`，程序 `~/opt/ollama` | active；`qwen2.5vl:3b`（3.2 GB），空载自动卸载 |

DSH 运行时：0.2.2-rc.1，profile `web`，preset `preset-standard`（无持久 bash）。

## 4. 待办

### 4.1 Tier A（已完成，留作验收依据）

| 步骤 | 结果 |
|---|---|
| A1 | `radare2` 6.0.7、`aria2` 1.37.0（apt，用户执行） |
| A2–A4 | ollama v0.40.16 → `~/opt/ollama`；用户级 unit 只绑 `127.0.0.1:11434`；`ollama pull qwen2.5vl:3b` 完成 |
| A5 | `dsh-vision describe` 返回中文描述；冷启 72.7 s、热启 9.8 s；`ollama ps` 2.8 GB，`KEEP_ALIVE=5m` 自动卸载 |

### 4.2 Tier B / C

Tier B（随时可做）：`aria2` 已随 A1 安装；可选 `qwen3:4b`（2.6 GB）离线兜底，本机 8B 级约 8 tok/s，不能替代 API 模型。

Tier C（等触发条件）：

| 项 | 触发条件 | 成本 |
|---|---|---|
| Ghidra 12.2 | 需要反编译闭源二进制的具体任务 | 约 500 MB + `openjdk-21-jdk-headless` 94 MB |
| `git-lfs` | `git clone` 报 `smudge filter lfs failed` | 13 MB，一分钟 |
| `auditd` | 需要取证/合规审计 | 0.7 MB，规则调优是真成本 |

### 4.4 RAG 向量链路（优先级最高）

`dsh-rag status` 报向量 0/53967、向量服务未就绪，但 `dsh-ml` 自报 ready 且两个 bge 模型已加载——**两边口径矛盾**。问题在索引侧未写向量或探测端口不一致，不是模型缺失。

排查：`dsh-rag index --help` 是否有向量开关；`dsh-rag status` 探测端口是否等于 8765；索引是否提前退出。修好后 5.4 万块语义检索才可用，收益大于 P3 五项之和。

### 4.5 明确不做

- DSH 核心升级（rc.1 → rc.5）。
- 装 libreoffice（DSH 自带 office 技能）、rclone、filesystem/fetch/sequential-thinking MCP。
- 重复推荐 `personalCloud/task/selfhost-recommendations/README.md` 已有服务。

## 5. 交接规程

### 5.1 改 DSH 配置

```
改 ~/.dsh/cordis.patch.yml（或 dsh plugin add）
  → cd personalCloud/workspace && python3 scripts/dsh-config-check.py --deep
  → 结论必须是「配置可加载」
  → 重启 dsh-web（会断开页面、杀掉子代理）
  → 刷新页面验证工具挂上
```

**重启前必须确认没有正在跑的子代理。**

### 5.2 提交规矩

- 每仓独立 `git add`/`commit`/`push`，禁止 `git add -A`；提交前跑 `./scripts/check.sh --repo <id>`。
- 默认直接 commit + push 默认分支；非快进时 `git pull --rebase origin <分支>` 后重推，仅冲突才停。
- 提交人 zhyfor；SA 改动才加「由SA更改」。

### 5.3 root 操作

AI 不执行，生成可复制命令交用户在宿主终端跑。

## 6. 已知坑

| 坑 | 现象 | 正解 |
|---|---|---|
| 中文 locale 干扰 `apt-cache` | `awk '/Candidate/'` 得空，误判包不存在 | 先 `export LC_ALL=C` |
| GitHub `latest` 资产缺失 | duckdb `releases/latest/...` 404 | 用具体 tag |
| `uv tool install duckdb` | 无 executable，自动回滚 | 直接下 CLI 压缩包 |
| `--deep` 假 FAIL | 非 playwright MCP 报 `Unknown tool` | 已修（`c753332`），回归时查这行 |
| 非交互 PATH | `dsh-vision: 未找到命令` | 修 unit；先 `echo $PATH` |
| 符号链接路径 | `ops_*` 报 `PATH_RESTRICTED` | 用 `personalCloud/workspace/...` 真实路径 |
| `rm` 被策略拦 | 删 `/tmp` 文件被拒 | 交用户执行 |
| `preset-standard` 无持久 bash | `cd` 不保留 | 用 `workdir` 或绝对路径 |
| GitHub 单连接限速 | 1.4 GB 要 2 小时 | `~/opt/ollama-dl.sh` 16 段并发 + `zstd -t` 校验 |
| `ollama pull` 单段卡死 | 15/16 段完成、最后一段不动 | `kill` → `systemctl --user restart dsh-ollama` → 续传 |
| Registry 比 GitHub 快 | GitHub 1–3 MB/s，registry 峰值 78 MB/s | 先直连实测再决定 |

## 7. 验证清单

```bash
export LC_ALL=C
for c in rg fd fzf bat delta sqlite3 shellcheck pandoc tesseract ocrmypdf \
         convert exiftool qpdf mediainfo mkvinfo csvlook mlr zoxide hyperfine \
         xdotool yq ruff duckdb dsh-rag; do command -v $c >/dev/null || echo "缺 $c"; done
rg --version | head -1; sqlite3 :memory: "select 1+1;"; duckdb -c "select 42;"; yq --version
r2 -v | head -1; aria2c --version | head -1
systemctl --user show dsh-ollama -p ActiveState
ss -ltn | grep 11434           # 只应出现 127.0.0.1
~/opt/ollama/bin/ollama list   # qwen2.5vl:3b
dsh-vision describe <某张截图>  # 返回中文描述，热启约 10 s
cd /home/zh/www/personalCloud/workspace && python3 scripts/dsh-config-check.py --deep | tail -3
cd /home/zh/www && ./scripts/check.sh --repo doc
```

## 改动记录

| 日期 | 内容 |
|---|---|
| 2026-11-19 20:15–20:50 | 建档、PATH 生效、apt 22 包与 duckdb、P3 ROI 子文档、改写成交接版 |
| 2026-11-19 21:28–21:30 | ollama 0.40.16 + qwen2.5vl:3b 与 radare2/aria2 落地，Tier A 完成 |
| 2026-11-19 21:40 | 清理下载残留约 2.9 GB，`~/opt/ollama` 保留 |
| 2026-11-19 22:50 | 补 `## 篇幅说明`（≤400 行） |
| 2026-11-20 05:50 | 按 doc-slim 压缩 289→约 190 行，删背景推导与提交流水，保留现状、待办、规程、坑、验证 |
