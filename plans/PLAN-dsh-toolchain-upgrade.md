---
title: DSH 能力升级总计划（历史 / 现状 / 后续 · 交接版）
implementation_status: in_progress
created_at: 2026-11-19 20:15:00
updated_at: 2026-11-19 21:30:00
---

# PLAN：DSH 能力升级总计划（交接版）

> 本文是「这次能力升级」的**唯一主文档**：以前为什么做、现在做到哪、以后还要做什么、新会话怎么接手，全部在这里。
> 决策明细（成本/收益打分）在子文档 [PLAN-dsh-p3-deferred-tools-roi.md](PLAN-dsh-p3-deferred-tools-roi.md)。

## 0. 新会话从这里开始

**一句话**：2026-11-19 给这台机器补了一轮工具链和 DSH 配置：P0–P2 已完成并验证；P3 的 Tier A **已全部落地**（ollama v0.40.16 + `qwen2.5vl:3b`、radare2 6.0.7、aria2 1.37.0），`dsh-vision describe` 已打通。

**必读 3 个文件**

| 文件 | 看什么 |
|---|---|
| 本文 | 历史、现状、待办、坑 |
| [PLAN-dsh-p3-deferred-tools-roi.md](PLAN-dsh-p3-deferred-tools-roi.md) | P3 五项的成本/收益与执行序列 |
| [personalCloud/workspace/scripts/dsh-config-check.py](/home/zh/www/personalCloud/workspace/scripts/dsh-config-check.py) | 改 DSH 配置后的必跑自检 |

**三条自检命令**（新会话开工先跑，确认现状与本文一致）

```bash
# 1) 工具链是否还在
for c in rg fd fzf bat delta sqlite3 shellcheck pandoc tesseract ocrmypdf \
         convert exiftool qpdf mediainfo mkvinfo csvlook mlr zoxide hyperfine \
         xdotool yq ruff duckdb dsh-rag; do printf "%-11s %s\n" "$c" "$(command -v $c || echo MISSING)"; done

# 2) DSH 配置是否可以加载（改过 patch 必须跑）
cd /home/zh/www/personalCloud/workspace && python3 scripts/dsh-config-check.py --deep | tail -5

# 3) 服务与 MCP 现状
systemctl --user show dsh-web -p ActiveState -p Environment
```

**新会话可以直接这么说**：「按 [doc/plans/PLAN-dsh-toolchain-upgrade.md](/home/zh/www/doc/plans/PLAN-dsh-toolchain-upgrade.md) 的 Tier A 继续，ollama 你装、radare2 我跑 apt」。

## 1. 背景：以前为什么反复卡

历史 480 个会话日志（283 MB）单次扫描出来的真实缺口：

| 缺口 | 证据 | 当时的绕法 |
|---|---|---|
| `sqlite3` CLI | 4 次直接报缺 + 30 次 `import sqlite3` 顶替 | 写 Python 脚本 |
| `shellcheck` | ≥5 次 | 降级 `bash -n` |
| `xdotool` | 3 次 | `dpkg -x libxdo3_*.deb` 解包到 `/tmp` + `LD_LIBRARY_PATH` |
| Playwright/chromium | 9 次缺失 + 11 个手写 `/tmp/cdp*.mjs` | 自己写 CDP 脚本 |
| `ollama` | 9 次 | 回退 `dsh-vision`（`describe` 仍不可用） |
| `ruff` | 3 次 | 手工看 |
| Ghidra / Hopper / IDA | 2 次 | 放弃 |
| `aria2` / `uget` | 1 次 | 单连接 `curl` |
| `git-lfs` | 2 次 | 放弃 |
| **`gh`/`uv`/`dsh-rag` 判为"未装"** | 多次 | 实为 `~/.local/bin` 不在非交互 PATH，**假缺失** |

结论：缺口分两类——**真没装**（用 apt/GitHub 补）和**装了但 PATH 看不见**（改 systemd 环境变量）。这次两类都处理了。

## 2. 已完成（P0–P2）

### 2.1 系统工具（22 个 apt 包 + 3 个用户级）

| 类别 | 工具（版本） |
|---|---|
| 搜索/浏览 | `rg` 15.1.0、`fd` 10.3.0、`fzf` 0.67.0、`bat` 0.25.0、`delta` 0.18.2 |
| 数据 | `sqlite3` 3.46.1、`duckdb` v1.5.6、`csvlook` 2.2.0、`mlr` 6.16.0、`yq` v4.54.3 |
| 文档/OCR | `pandoc` 3.7.0.2、`tesseract` 5.5.0（chi_sim+eng+osd）、`ocrmypdf` 16.13.0 |
| 媒体 | `convert` ImageMagick 7.1.2、`exiftool`、`qpdf` 12.3.2、`mediainfo`、`mkvinfo` v97.0 |
| 质量/脚本 | `shellcheck` 0.11.0、`ruff` 0.17.5 |
| 效率 | `zoxide` 0.9.8、`hyperfine` 1.19.0、`xdotool` 3.20160805.1 |

安装细节：
- apt 包由用户在宿主终端执行（AI 无 root）。
- `uv tool install duckdb` **无效**——该 PyPI 包没有 CLI 入口，uv 会自动回滚。正解是 GitHub release `duckdb_cli-linux-amd64.zip`，**且必须指定版本**（`latest` 标签没有这个资产）。
- `yq` 用 GitHub 二进制装到 `~/.local/bin/yq`，**不要** apt 的 Python 版（语义不同）。
- Ubuntu 的 `fdfind`/`batcat` 已软链成 `fd`/`bat` 到 `~/.local/bin`。

### 2.2 PATH 修复（治"假缺失"）

`~/.config/systemd/user/dsh-web.service` 的 `Environment=PATH` 前插 `%h/.local/bin`，`daemon-reload` 后于 20:18:56 重启生效。现在非交互 shell 的 PATH 是：

```
/home/zh/.local/bin:/home/zh/opt/node24/bin:/home/zh/.npm-global/bin:/usr/local/bin:/usr/bin:/bin
```

### 2.3 DSH 侧

| 项 | 状态 | 说明 |
|---|---|---|
| `context7` MCP | **开** | `cordis.patch.yml` 新增 `context7-mcp`，2 个工具，schema 小；实测 `resolve-library-id` 返回 DuckDB 5 条库 |
| `session-search` | **开** | `@deepseek-ai/dsh-experimental-session-search@0.2.2-rc.1`（对齐当前 DSH 版本），已登记进 web profile bundles |
| `rea-mcp` / `headroom-mcp` | 关 | 原本就是 `disabled: true` |
| `workdir-rag` / `playwright` | 开 | 握手 + 浏览器导航实测通过 |

**刻意没装**：filesystem / fetch / sequential-thinking（与内置工具重复）、cot-translation（延迟翻倍）、agent-team（上下文爆炸）、ralph、cua、plugin-market（与 dshmarket 重复）、chrome-devtools-mcp（26 工具、约 +6k token/请求，与 Playwright 重叠）、markitdown-mcp、serena（20+ 工具）。

**刻意没升级**：DSH 0.2.2-rc.1 → rc.5。18 个插件的 peer 约束都对着 rc.1，升级要整体重对齐，收益不抵风险。

### 2.4 顺带修的两个缺陷

1. `scripts/dsh-config-check.py` 的 `--deep` 对**所有** MCP 调 `browser_navigate`，只有 playwright 有这个工具 → `workdir-rag`/`context7` 必然 FAIL 并误报"配置不可加载"。已收敛为 `if deep and server == "playwright"`。
2. `doc/specs/operations-safety.md` 里 `browser-debug` 技能链接指向不存在的 `personalCloud/.dsh/...`，导致 doc 门禁失败。已改为 `../../.dsh/skills/browser-debug/SKILL.md`。

### 2.5 提交与备份

| 仓库 | 提交 | 内容 |
|---|---|---|
| `doc` | `95354f2` | 新增本计划 + 修 browser-debug 链接 |
| `personalCloud` | `c753332` | 修自检脚本浏览器探测 |
| `doc` | `526c7b0` | 记录 apt 安装完成 |
| `doc` | `000aa43` | 补 duckdb、重启后验证结果 |
| `doc` | `224a2f2` | P3 ROI 评估 |

备份（回滚用）：

| 对象 | 备份路径 |
|---|---|
| systemd unit | `~/.config/systemd/user/dsh-web.service.bak.20261119-200000` |
| DSH patch | `~/.dsh/cordis.patch.yml.bak.20261119-201330` |
| web profile | `~/.dsh/profiles/web/package.json.bak.20261119-*` |

## 3. 现状快照（2026-11-19 21:30）

**硬件**：AMD Ryzen 7 8845HS（16 线程，AVX-512）、46 GB 内存、Radeon 780M 核显（**无 CUDA**）、`/` 可用 734 GB、出口代理 `127.0.0.1:7897`。

**本机既有能力（这次没动，但要知道有）**

| 服务 | 地址/入口 | 状态 |
|---|---|---|
| `dsh-web` | `https://zh-gem-r7.tailb6e152.ts.net:8443/`（本机 127.0.0.1:3080） | active |
| `dsh-ml`（embedding/PDF/OCR） | `127.0.0.1:8765` | ready，模型 `bge-m3`、`bge-small-zh-v1.5`、`bge-reranker-v2-m3` 已加载 |
| `dsh-rag` | `~/.local/bin/dsh-rag`，MCP `workdirrag` | 索引 4226 文件 / 53967 块，**向量 0/53967**（见 §4.4） |
| `dsh-vision` | `~/.local/bin/dsh-vision` | `ocr`/`info`/`enhance`/`describe` **全部可用**（describe 走本机 ollama） |
| `dsh-ollama` | `127.0.0.1:11434`，程序 `~/opt/ollama` | active；模型 `qwen2.5vl:3b`（3.2 GB），空载自动卸载 |

**DSH 运行时**：0.2.2-rc.1，profile `web`，preset `preset-standard`（**不是** `preset-minimal`，所以没有持久 bash）。

## 4. 未来（待办）

### 4.1 Tier A —— 建议下一步就做（rollout 详见 ROI 文档）

| 步骤 | 执行者 | 状态 | 动作 / 结果 |
|---|---|---|---|
| A1 | 你（root） | **完成** | `sudo apt install -y radare2 aria2` → radare2 **6.0.7**、aria2 **1.37.0**（`/usr/bin/r2`、`/usr/bin/aria2c`） |
| A2 | AI（用户级） | **完成** | `ollama-linux-amd64.tar.zst` v0.40.16 → `~/opt/ollama`（解压后 2.5 GB） |
| A3 | AI（用户级） | **完成** | `~/.config/systemd/user/dsh-ollama.service`：`OLLAMA_HOST=127.0.0.1:11434`、`OLLAMA_MODELS=~/.local/share/ollama/models`，已 `enable --now` |
| A4 | AI（后台） | **完成** | `ollama pull qwen2.5vl:3b`（3.2 GB），`ollama list` 显示 `qwen2.5vl:3b fb90415cde1e 3.2 GB` |
| A5 | AI | **完成** | `dsh-vision describe <截图>` 返回中文描述；`ollama ps`：2.8 GB、100% CPU、ctx 4096 |

**实测数据（2026-11-19 21:40）**

| 项 | 结果 |
|---|---|
| 绑定 | `ss -ltn` 只有 `127.0.0.1:11434`，未对外监听 |
| 冷启动 describe | 72.7 s（含加载模型） |
| 热启动 describe | 9.8 s / 218 eval tokens（抖音创作者中心截图，返回中文界面描述正确） |
| 内存占用 | `ollama ps` 2.8 GB，`OLLAMA_KEEP_ALIVE=5m` 后自动卸载 |
| 程序下载 | GitHub release 单连接约 210 KB/s；改 16 段并发后约 3–5 MB/s，1.43 GB 约 8 分钟 |
| 模型下载 | `registry.ollama.ai` 走代理峰值 78 MB/s，末尾第 7 段卡死，重启 pull 后续传完成 |

**验收标准**：`dsh-vision describe` 不再报 `Connection refused`；ollama 只绑 `127.0.0.1`。——**已全部达成**。

**A1 验收（2026-11-19 21:30）**

```bash
rabin2 -I /bin/ls          # elf / x86-64 / binsz 等字段正常
r2 -q -c 'pi 4 @ 0x1000' /bin/ls
rabin2 -z /bin/ls | head   # .rodata 字符串正常
aria2c -x4 -s4 -d ~/opt/aria2-test -o test.html https://example.com   # 577 B 落盘
```

结论：radare2 反汇编/字符串可用；aria2 多连接下载可用（后续 GB 级文件优先 `aria2c -x16 -s16 -c`）。
测试残留 `~/opt/aria2-test/` 可删。

### 4.2 Tier B —— 随时可做

- `aria2` 已在 A1 里带上；独立装也行。
- 可选：`qwen3:4b`（2.6 GB）当离线兜底，但 8B 级在本机只有约 8 tok/s，不要指望替代 API 模型。

### 4.3 Tier C —— 等触发条件

| 项 | 触发条件 | 成本 |
|---|---|---|
| Ghidra 12.2 | 出现需要反编译闭源二进制的具体任务 | 约 500 MB + `openjdk-21-jdk-headless` 94 MB |
| `git-lfs` | `git clone` 报 `smudge filter lfs failed` | 13 MB，一分钟 |
| `auditd` | 需要取证/合规审计 | 0.7 MB，但规则调优是真成本 |

### 4.4 更值钱的一件事：RAG 向量链路

`dsh-rag status` 报 `向量 0/53967`、向量服务"未就绪（降级 bge-small-zh-v1.5）"，但 `dsh-ml` 在 `127.0.0.1:8765` 自报 `backend: ready`、两个 bge 模型都已加载。**两边口径矛盾**，说明问题在索引侧没有写向量，或探测路径/端口不一致，不是模型缺失。

下一步排查方向：`dsh-rag index --help` 是否有向量开关、`dsh-rag status` 探测的端口与 `dsh-ml` 实际端口是否一致、索引时是否因"索引被截断"提前退出。修好后 5.4 万块的语义检索才真正可用，对日常检索收益大于 P3 五项之和。

### 4.5 明确不做

- DSH 核心升级（rc.1 → rc.5）。
- 装 libreoffice（DSH 自带 office 技能）、rclone、filesystem/fetch/sequential-thinking MCP。
- 再推荐 `personalCloud/task/selfhost-recommendations/README.md` 里已有的服务。

## 5. 交接规程（新会话照着做）

### 5.1 改 DSH 配置的正确姿势

```
改 ~/.dsh/cordis.patch.yml（或 dsh plugin add）
  → cd personalCloud/workspace && python3 scripts/dsh-config-check.py --deep
  → 结论必须是「配置可加载」
  → 重启 dsh-web（会断开当前页面、会杀掉正在跑的子代理）
  → 刷新页面后验证工具真的挂上
```

**重启前必须确认没有正在跑的子代理**，否则会一起被杀。

### 5.2 提交规矩（跨仓硬约束）

- 每仓独立 `git add`/`commit`/`push`，禁止 `git add -A`。
- 提交前跑 `./scripts/check.sh --repo <id>`，失败不提交。
- 默认直接 commit + push 到 `master`；非快进时 `git pull --rebase origin master` 后重推，只有冲突才停。
- 提交人 zhyfor；SA 改动才加「由SA更改」。

### 5.3 root 操作

AI 不执行，生成可复制命令交用户在宿主终端跑。本次 apt 就是这样完成的。

## 6. 已知坑（踩过的，别再踩）

| 坑 | 现象 | 正解 |
|---|---|---|
| 中文 locale 干扰 `apt-cache` | `apt-cache policy` 输出「候选：」，`awk '/Candidate/'` 得到空，误判包不存在 | 先 `export LC_ALL=C` |
| GitHub `latest` 资产缺失 | duckdb `releases/latest/download/duckdb_cli-linux-amd64.zip` → 404 | 用具体 tag：`.../download/v1.5.6/...` |
| `uv tool install duckdb` | "No executables are provided"，自动回滚 | 直接下 CLI 压缩包 |
| `dsh-config-check --deep` 假 FAIL | 非 playwright 的 MCP 报 `Unknown tool: browser_navigate` | 已修（`c753332`）；若回归检查这一行 |
| 非交互 PATH | `dsh-vision: 未找到命令`，误判未安装 | 已修 unit；排查时先 `echo $PATH` |
| 符号链接路径 | `ops_*` 工具报 `PATH_RESTRICTED` | 用 `personalCloud/workspace/...` 真实路径 |
| `rm` 被策略拦 | 删除 `/tmp` 文件被拒 | 用户将开 `/tmp` 删除白名单；或交用户执行 |
| `preset-standard` 无持久 bash | 每条命令是独立 `bash -c`，`cd` 不保留 | 用 `workdir` 参数或绝对路径 |
| 重启杀子代理 | 重启 dsh-web 时子代理一起死 | 重启前先收尾或等其结束 |
| GitHub release 单连接限速 | `curl` 直下 ollama 只有 200 KB/s，1.4 GB 要 2 小时 | 用 `~/opt/ollama-dl.sh`：16 段并发各写 `part.NN`，最后 `cat` 合并 + `zstd -t` 校验 |
| `ollama pull` 单段卡死 | 15/16 段完成、最后一段 0% 不动，进度条停在 100% | `kill` pull 客户端 → `systemctl --user restart dsh-ollama` → 重新 pull，已下部分自动续传 |
| Registry 反而比 GitHub 快 | GitHub 1–3 MB/s，`registry.ollama.ai` 峰值 78 MB/s | 模型不必找国内源；先直连实测再决定 |

## 7. 验证清单（收尾时跑）

```bash
export LC_ALL=C
# 工具
for c in rg fd fzf bat delta sqlite3 shellcheck pandoc tesseract ocrmypdf \
         convert exiftool qpdf mediainfo mkvinfo csvlook mlr zoxide hyperfine \
         xdotool yq ruff duckdb dsh-rag; do command -v $c >/dev/null || echo "缺 $c"; done
# 功能抽样
rg --version | head -1; sqlite3 :memory: "select 1+1;"; duckdb -c "select 42;"; yq --version
r2 -v | head -1; aria2c --version | head -1
# ollama
systemctl --user show dsh-ollama -p ActiveState
ss -ltn | grep 11434           # 只应出现 127.0.0.1
~/opt/ollama/bin/ollama list   # qwen2.5vl:3b
dsh-vision describe <某张截图>  # 返回中文描述，热启约 10 s
# DSH
cd /home/zh/www/personalCloud/workspace && python3 scripts/dsh-config-check.py --deep | tail -3
# 文档门禁
cd /home/zh/www && ./scripts/check.sh --repo doc
```

## 改动记录

| 日期 | 内容 |
|---|---|
| 2026-11-19 20:15 | 建档（P0–P3 分档） |
| 2026-11-19 20:25 | PATH 生效、apt 22 包、yq/ruff/context7/session-search 落地、自检脚本修复 |
| 2026-11-19 20:34 | 补 duckdb v1.5.6，重启后三项验证通过 |
| 2026-11-19 20:40 | 新增 P3 ROI 子文档（ollama/radare2/Ghidra/aria2/auditd/git-lfs） |
| 2026-11-19 20:50 | 改写成交接版总计划：历史、现状、待办、规程、坑、验证清单 |
| 2026-11-19 21:28 | Tier A 的 ollama 落地（v0.40.16 + qwen2.5vl:3b，用户级 unit 只绑 127.0.0.1）；`dsh-vision describe` 验收通过；radare2/aria2 待用户 apt |
| 2026-11-19 21:30 | 用户 apt 装好 radare2 6.0.7 + aria2 1.37.0；rabin2/r2/aria2c 抽样通过，Tier A 全部完成 |
