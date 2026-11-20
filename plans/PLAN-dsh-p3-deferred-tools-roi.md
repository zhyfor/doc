---
implementation_status: not_started
created_at: 2026-11-19 20:36:08
updated_at: 2026-11-19 20:40:00
---

# DSH 待装能力项方案与 ROI 评估

> 承接 [PLAN-dsh-toolchain-upgrade.md](PLAN-dsh-toolchain-upgrade.md) 的 P3「暂缓」清单，逐项算成本与收益，给出装 / 换 / 不装结论。
> 本机事实：AMD Ryzen 7 8845HS（16 线程，AVX-512）、46 GB 内存、Radeon 780M 核显（无 CUDA）、`/` 可用 734 GB、出口走 `127.0.0.1:7897` 代理。

## 1. 结论先行

| 项 | 结论 | 一次性成本 | 收益 | ROI |
|---|---|---|---|---|
| **ollama**（+ qwen2.5vl:3b） | **装**，用户级、不需要 root | 约 4.5 GB 磁盘（1.3 GB 程序 + 3.2 GB 模型）、15 分钟 | 解锁已存在但**当前直接报错**的 `dsh-vision describe`；本机 OCR/看图/隐私路径闭环 | ★★★★☆ |
| **radare2** | **装**（替代 Ghidra 当日常） | 3.9 MB、1 条 apt、1 分钟 | 反汇编/字符串/函数图，覆盖逆向 60–70% 日常需求 | ★★★☆ |
| **Ghidra** | **暂不装**，等有具体目标 | 约 600 MB（+ JDK 21 约 94 MB）、10 分钟、需 JDK 常驻维护 | 反编译质量最高，但历史需求只有 2 次、无明确目标 | ★★ |
| **aria2** | 可选，随手装 | 2 MB、1 分钟 | 多线程/断点/磁力下载，5 GB 模型下载可见提速 | ★★ |
| **auditd** | **不装** | 0.7 MB + 常驻约 10 MB，规则调优是主要成本 | 单用户开发机，`journald` + 现有日志已覆盖；噪声大于价值 | ★ |
| **git-lfs** | **不装**，遇到再装 | 13 MB、1 分钟 | 仅在克隆 LFS 仓库时需要，目前无此需求 | ★ |

排序逻辑：**能解锁"已经装了但用不了"的能力 > 便宜且通用 > 体积大且无明确目标 > 纯预防性**。

## 2. 评分口径

- **成本**：磁盘占用 + 安装/维护时间 + 常驻内存/token + 是否需要 root。
- **收益**：解卡次数（历史会话证据）× 不可替代性（现有工具能不能顶）+ 是否补上隐私/离线的空白。
- **ROI**：`(每次解卡节省时间 × 预期频次) / 一次性成本`，以星级表示，不折算成钱。
- 只算"证据支持的需求"，不算"听起来很酷"的需求。

## 3. 逐项分析

### 3.1 ollama —— 唯一的"解锁既有能力"项

**现状（已实测）**

```bash
$ dsh-vision describe /tmp/t.png
dsh-vision：连接本机 Ollama 失败（http://127.0.0.1:11434）：[Errno 111] Connection refused。
请先启动 `ollama serve`，并执行 `ollama pull qwen2.5vl:3b`。
```

`dsh-vision` 的 `ocr` / `info` / `enhance` 子命令可用（PIL + 系统 tesseract），**只有 `describe` 是硬依赖 Ollama**。也就是说这项不是"新增能力"，是"把已有工具的另一半接上"。

**成本**

| 项 | 数值 |
|---|---|
| 程序 | `ollama-linux-amd64.tar.zst`（v0.40.16，含 ROCm/CUDA 库，约 1.3 GB） |
| 模型 | `qwen2.5vl:3b` 约 3.2 GB；后续可选 `qwen3:4b` 约 2.6 GB |
| 常驻内存 | 空闲约 0；加载 3B 模型约 3.5 GB（46 GB 内存充裕） |
| 时间 | 下载走代理约 10 分钟，解压 1 分钟，勿需编译 |
| root | **不需要**：解压到 `~/opt/ollama`，写用户级 systemd unit，只绑 `127.0.0.1:11434` |

**收益与预期性能（估算，装后实测校准）**

- 3B q4 在 8845HS 上纯 CPU 约 18–22 tok/s；780M 核显走 Vulkan 可能更快，但 ROCm 对 `gfx1103`（780M）非官方支持，需实测。
- 8B 模型约 7–9 tok/s，**不适合当编码 agent 主力**，本项价值在视觉理解与离线兜底，不在替代 API 模型。
- 隐私：截图、UI 截图分析不再需要出本机。
- 与 `free-ai-router` 技能的"本机分支"打通（该技能把 Ollama 列为本地选项之一）。

**结论**：装。这是唯一一项"装完立刻消除一个已存在的报错"的能力项。

**已落地实测（2026-11-19 21:45）**：`~/opt/ollama` v0.40.16 + 用户级 `dsh-ollama.service`（只绑 `127.0.0.1:11434`）+ `qwen2.5vl:3b`。`dsh-vision describe` 冷启 72.7 s、热启 9.8 s（218 eval tokens），加载占用 2.8 GB、100% CPU。模型下载走官方 registry 峰值 78 MB/s，不需要国内源。

### 3.2 Ghidra vs radare2 —— 拆成"日常"和"专项"

| 维度 | Ghidra 12.2 | radare2 6.0.7 |
|---|---|---|
| 体积 | 约 500 MB + JDK 21 headless 94 MB | 3.9 MB（apt `radare2`） |
| 反编译 | 有（质量最高，接近 IDA） | 无原生反编译；`r2dec`/`r2ghidra` 插件可补，弱于 Ghidra |
| 反汇编 / strings / xref / 函数图 | 有 | 有，CLI 更快 |
| 脚本化 | Java/Python（Jython） | r2pipe（Python/JS/Go 均可） |
| 启动成本 | 冷启动数十秒（JVM） | 毫秒级 |
| 维护 | 需跟 JDK 版本 | apt 跟随系统 |

**历史证据**：会话里 Ghidra/Hopper/IDA 相关需求 2 次，均无具体目标落地；同时 `objdump`/`strings`/`nm` 已在用。

**结论**：先 `apt install radare2`（3.9 MB，一分钟），把"随手看一眼二进制"的路径铺平；Ghidra 留到有明确目标（例如要读某个闭源 native 库的算法）再装，届时再花 600 MB 与 JDK 维护成本。

**已落地（2026-11-19 21:30）**：radare2 **6.0.7**（`/usr/bin/r2`），`rabin2 -I /bin/ls`、`r2 -c 'pi 4'`、`rabin2 -z` 抽样正常；Ghidra 仍未装。

### 3.3 auditd —— 不装

- 成本：包 0.7 MB，但真正的成本是**规则调优与日志治理**（默认规则噪声大，`audit.log` 增长快，需要 rotation 与过滤）。
- 收益：内核级系统调用/文件访问审计。本机是单用户开发机，`journald`、`docker logs`、`sudo` 日志、`last` 已覆盖绝大多数排障需求。
- 只在"怀疑有越权访问、需要取证"时才有价值，而那种场景一次性 `apt install auditd` 也就一分钟。

**结论**：不装。需要时一分钟的事，不值得常驻。

### 3.4 aria2 —— 可选

- 成本：1.9 MB，无守护进程（纯 CLI），零常驻。
- 收益：`-x16` 多线程下载、断点续传、磁力/BT。今天下 duckdb、yq、ollama 这类 GitHub release 走的是单连接；GB 级模型下载有可见提速。
- 替代：`curl -C -` / `wget -c` 已够用，但速度不如多线程。

**结论**：可选，随手装（Tier B）。不装也不影响任何现有流程。

**已落地（2026-11-19 21:30）**：aria2 **1.37.0**，`aria2c -x4 -s4` 抽样下载正常；后续 GB 级文件优先 `aria2c -x16 -s16 -c`。

### 3.5 git-lfs —— 不装

- 成本：13 MB。
- 收益：只在克隆/推送使用 LFS 的仓库时需要。目前登记仓库（personalCloud、doc、superCreater、xctl 等）均未用 LFS。
- 触发条件明确：`git clone` 报 `smudge filter lfs failed` 时装，一分钟解决。

**结论**：不装。

## 4. 推荐执行序列

### Tier A（建议今天就做）

| 步骤 | 执行者 | 命令 |
|---|---|---|
| A1 radare2 | 你（root） | `sudo apt install -y radare2` |
| A2 ollama 程序 | AI（用户级） | 下载 `ollama-linux-amd64.tar.zst` → 解压 `~/opt/ollama` |
| A3 ollama unit | AI（用户级） | 写 `~/.config/systemd/user/dsh-ollama.service`（`OLLAMA_HOST=127.0.0.1:11434`、`OLLAMA_MODELS=~/.local/share/ollama/models`），`daemon-reload` + `enable --now` |
| A4 拉模型 | AI | `ollama pull qwen2.5vl:3b`（3.2 GB，后台跑） |
| A5 验收 | AI | `dsh-vision describe` 对一张截图跑通；`ollama ps` 看显存/内存占用 |

### Tier B（随手，不阻塞）

- `sudo apt install -y aria2`（2 MB）。

### Tier C（等触发条件，不做）

- Ghidra：出现需要反编译闭源二进制的具体任务时再装（约 600 MB + JDK 21）。
- git-lfs：克隆 LFS 仓库报错时再装。
- auditd：需要取证/合规审计时再装。

## 5. 验证与回滚

**验证**

```bash
r2 -v                                   # radare2
systemctl --user status dsh-ollama      # active
curl -s 127.0.0.1:11434/api/tags | jq -r '.models[].name'
dsh-vision describe <某张截图>          # 能返回中文描述
```

**回滚**

| 项 | 回滚 |
|---|---|
| radare2 | `sudo apt remove radare2` |
| ollama | `systemctl --user disable --now dsh-ollama`，删 `~/opt/ollama`、`~/.local/share/ollama`（约 4.5 GB） |
| aria2 | `sudo apt remove aria2` |

ollama 只绑 `127.0.0.1`，不对外开放；模型目录独立，删除即还原。

## 6. 附：比这五项更值钱的两件事（本次不实施，仅登记）

1. **修通 RAG 向量链路**。`dsh-rag status` 显示 `向量 0/53967`、向量服务"未就绪（降级 bge-small-zh-v1.5）"，但 `dsh-ml`（`127.0.0.1:8765`）自报 `backend: ready`、`bge-m3` 与 `bge-small-zh-v1.5` 均已加载。两者口径矛盾，说明问题是**索引侧没写向量**或探测路径不一致，不是模型缺失。修好后 4226 个文件、5.4 万块的语义检索才真正可用——对日常检索收益远大于本页五项。
2. **chrome-devtools MCP**：工具约 26 个、每请求多约 6k token，与现有 Playwright MCP 重叠，维持"已装但禁用"。

## 改动记录

| 日期 | 内容 |
|---|---|
| 2026-11-19 | 建档：五项 ROI 评估 + Tier A/B/C 执行序列 |
