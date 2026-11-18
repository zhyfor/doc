---
audience: shared
status: current
---

# DSH 上下文压缩：依据、成本与调参

> 记录日期：2026-11-10
> 用途：会话与压缩规则见 [`task-workflow.md`](../../personalCloud/workspace/_meta/doc/task-workflow.md) 第 9 节；本文件放**源码依据、成本换算和调参方式**。
> 结论一句话：**自动压缩默认就开着，不用手动 `/compact`，也不要自造绝对 token 阈值。**

## 1. 问题

原始诉求是「上下文 > 10M，或请求 N 次后自动压缩」这类定时压缩规则，写进 `AGENTS.md` 让模型执行。
核查后这个形式**不可行**，原因见第 3 节；替代方案见第 4、5 节。

## 2. 已核对的事实（源码为准）

### 2.1 谁在做压缩，什么时候触发

| 事实 | 出处 |
|---|---|
| 压缩器是 `@deepseek-ai/dsh-compaction-basic`，`auto: true` **默认开启** | `dsh-compaction-basic/lib/types/types.d.ts`（`BasicCompactionConfig.auto`）|
| 触发点是**步边界**的 token 压力，不是定时器、不是请求次数 | 同上，`compact()` 注释：“replayed step-boundary pressure or provider-confirmed context overflow” |
| 阈值基线 `thresholdRatio = 0.8` | 同上，默认注释 |
| 压力线被硬性封顶为 `窗口 − 本次输出预留 − headroomTokens(65536)` | `dsh-compaction-basic/lib/types/config.d.ts` 的 `resolveCompactSpec` 注释 |
| 压缩后保留最近 `retainRatio = 0.16` 窗口的原文 | 同上 |
| 压一次仍超阈值会再压一次：`compactionRetries = 1` | 同上 |
| 真超窗时先救一次再重试：`maxOverflowRetries = 1` | 同上 |
| 另有 `tool-result-pruner`：单条工具结果超 `8192` 字符就先裁（留头 4096 / 尾 1024） | `dsh-base/cordis.patch.yml` 的 `tool-result-pruner` 行 |

### 2.2 Web 模式下的挂载位置

- `dsh-web-app/cordis.patch.yml` 在宿主层 `disabled: true` 掉 `compaction-basic` / `command-compact` / `tool-result-pruner`，
  改由 **agent preset** 承载（注释理由是 token-meter 的投影表是进程级的）。
- `dsh-web-app/presets/standard.patch.yml` 在 `standard` preset 里**不写 config** 地挂载 `compaction-basic`，
  因此生效值就是 2.1 的 schema 默认值。
- 结论：当前 web profile（`semantic: standard`）走的就是默认 0.8 / 0.16 / 65536。

### 2.3 窗口多大

`dsh-llm-deepseek/lib/index.js`：

```js
const DEFAULT_CONTEXT_WINDOW = 1e6;   // 1,000,000 token
// deepseek-flash 与 deepseek-v4-pro 的 catalog 条目都用它
```

所以压力线 ≈ `min(1e6 × 0.8, 1e6 − 输出预留 − 65536)`。
`0.8 × 1e6 = 800K` 明显小于封顶值（除非输出预留超过约 135K），**实际压缩点约 80 万 token**；
压缩后保留 `0.16 × (1e6 − 输出预留) ≈ 15 万` token 的近期原文 + 摘要。

> 未验证项：输出预留（`reservedCompletionTokens`）对当前路由的具体取值我没从适配器里逐项确认，
> 只能确定它不影响「800K 先到」这个结论，除非它异常地大于 135K。

### 2.4 怎么看真实用量

`dsh-client-ui-conversation` 的 `ContextMeter`：输入框下方一个环 + 「上下文已用 X%」，
数据来自 token-meter 的 `contextPressure` 投影，点开是 `contextBreakdown` 的构成占比
（system prompt / tools / conversation）。**这是唯一可信来源**，模型自己报不出 token 数。

## 3. 为什么「10M / 每 N 次请求」这套写不进去

1. **10M 永远到不了**：窗口 1M，10M 是 10 倍。阈值写成 10M 等于永不触发。
2. **请求次数不是上下文增长的自变量**：同一轮里 `grep` 命中 20 行和整读一个 3000 行文件，
   增量差两个数量级；「第 30 次请求」既可能才 2 万 token，也可能已 50 万。
3. **模型执行不了**：模型没有读取自身 token 计数的工具，也没有触发压缩的工具
   （`/compact` 是用户侧 slash command）。写进 `AGENTS.md` 的绝对阈值只会变成
   「看起来有、永远不生效、也没法自查」的规则，属于自欺条款（对应 [`engineering-rules.md`](../specs/engineering-rules.md) 第 1 节“不编造”）。
4. **真正的触发权在 harness**：token-meter 提供计量，compaction-basic 在步边界读计量做决策。
   要在文档层「配置」它，唯一的入口是 `compaction-basic` 的 config，不是 prompt。

## 4. 压缩到底有什么用、代价是什么

| 维度 | 判断 | 说明 |
|---|---|---|
| 省 token 计数 | 有 | 从 ~80 万回落到 ~15 万，后续每轮 prompt 显著变小 |
| 省账单 | 有，但被高估 | DeepSeek 有上下文缓存，命中前缀单价本来就低；压缩还会作废缓存前缀 |
| 提速 | 有明显收益 | prefill 时间随 prompt 长度近似线性增长 |
| 质量 | 正收益 | 超长上下文存在注意力稀释（context rot），砍掉陈旧内容反而更稳 |
| 代价 | 一次摘要请求 | 输入约等于压缩时的上下文（这里约 80 万），输出受 `headroomTokens` 约束 |

**额外开销的粗略估算**（按默认策略推的算术，不是实测）：

设触发点 `T`、压缩后保留 `R`。一个压缩周期里新增 `T − R` 的有效内容，却要额外付一次 `T` 的摘要输入，
所以稳态 token 开销倍率约

```
T / (T − R) = 0.8 / (0.8 − 0.16) ≈ 1.25
```

即约 **+25%**，换来的是每轮延迟更平、质量更稳、以及不会撞窗口。
这类估算只用于判断量级，**不要当成账单预测**。

结论：压缩主要买「延迟平稳 + 质量稳定」，不是买「省钱」。
省钱的主要杠杆在源头——少往上下文里搬无关内容（见 [`task-workflow.md`](../../personalCloud/workspace/_meta/doc/task-workflow.md) 第 9.2 节）。

### 4.5 2026-11-10 实测：为什么「卡」不能反推「上下文大」

当晚 dsh 反复卡顿，第一轮排查误判为 MCP（19:13 把 `rea-mcp`、`headroom-mcp` 设为 `disabled: true` 后重启），
22:50、23:13 仍然复现。翻 headroom 日志得到的证据：

| 证据 | 数值 | 含义 |
|---|---|---|
| 9246 token 的单消息请求 ttfb | 67 s | 上下文很小也一样卡，与大小无关 |
| 11 万 token / 123 条消息请求 ttfb | 151 s（总 162 s） | 大请求同样卡，且卡在首字节 |
| `total_ms` 与 `ttfb_ms` 的关系 | ttfb 占绝对多数 | 不是输出慢，也不是本地转换慢 |
| headroom `read_request_json` | 5.2 s / 686 KB | 本地确有开销，但远小于 ttfb |
| 本机 → `api.deepseek.com` | DNS 1ms / TCP 2ms / TLS 29ms / 0% 丢包 | 网络链路排除 |
| 并发会话 | 同时 5–6 个 session 打同一代理 | 放大重试与排队，但不是根因 |

推论：**压缩的收益门槛是「当前上下文 vs 压缩后保留量」**。
默认 `retainRatio = 0.16` 对 1M 窗口保留约 15 万 token；当会话只有 11 万 token 时，
压一次会把保留量抬回 ~15 万，单轮请求体不降反升，还要多付一次摘要调用。
因此「因为卡了所以压缩」在 11 万这个量级上是错误操作；它只在上下文显著超过 15 万时才有正收益。

对应的排查脚本：`task/dsh-health-check/scripts/check.sh`（ttfb 判据、上游错误时间、进行中请求）。

> 依据：`~/.headroom/logs/proxy-8787.log` 的 `PERF`/`STAGE_TIMINGS`/`proxy_inbound_response` 行，2026-11-10 22:45–23:15。

## 5. 调参（真要改时）

参数都在 `compaction-basic` 的 config 里，语义见 2.1：

| 参数 | 默认 | 调大的效果 | 调小的效果 |
|---|---|---|---|
| `thresholdRatio` | `0.8` | 压得更晚，摘要次数少但单次更贵、延迟更高 | 压得更早，延迟更稳但摘要更频繁 |
| `retainRatio` / `retainTokens` | `0.16` | 压缩后留更多原文，细节好但更费 | 留更少，更省但更容易丢细节 |
| `headroomTokens` | `65536` | 给输出留更多余量，压得更早 | 压得更晚，更贴窗口上限 |
| `compactionRetries` | `1` | 一次不够会多压几轮，适合超大任务 | `0` 表示压一次就停 |
| `maxOverflowRetries` | `1` | 撞窗口后多救几次 | `0` 关闭超窗自救 |

改法：在补丁层按 id 覆盖（本机写在 `~/.dsh/cordis.patch.yml`，web 与 superagent profile 都读）。
**注意补丁是整行替换 `config`，不是字段合并**，省略的字段会回落 schema 默认值，需按需写全。
改前 `cp` 备份、改后重启 `dsh web` 验证。

### 5.1 2026-11-14 实测：组内条目只能整段重写 preset

- **顶层按 id 补丁打不到组内条目**：`compaction-basic` 在 `preset-standard` 的 `config.plugins[].config[]` 里，
  顶层写 `- id: compaction-basic` 会被跳过（`--dump-config` 里仍是默认值）。
- **agent preset 的 `plugins` 按 id 取第一个匹配项**：所以覆盖必须整段重写 `preset-standard`，
  把 default 的 plugins（含 plan-mode 长提示词）原样抄一遍，只给 `compaction-basic` 加 `config`。
  升级 dsh 后 preset 内容若变，需同步这份拷贝；官方 preset 摘要补丁在本层之后应用，出现「摘要补丁覆写」告警时要处理。
- **当前生效值**（`dsh --profile web --dump-config` 核对）：`thresholdRatio: 0.08 / retainRatio: 0.02 / headroomTokens: 65536`。
  按源码 `resolveCompactSpec`：阈值 = `min(1e6×0.08, 1e6−256000−65536)` = **80000**，保留 = `(1e6−256000)×0.02` = **14880**。
  即每接近 8 万 token 在步边界压缩一次，压后约剩 1.5 万原文 + 摘要。
- 代价：压缩频率是默认值的 10 倍，摘要请求次数与总额外 token 显著上升，属用户明确要求的取舍。

### 5.2 推理档位：别用 `thinking: disabled` 去"省 token"

2026-11-14 曾为省 token 在 `~/.dsh/cordis.patch.yml` 给 `llm-deepseek` 写
`thinking: disabled` + `reasoningEffort: "off"`，结果界面推理档位**锁死在 off、无法改**。

- `thinking` 是**部署级策略**，不是默认值：`disabled` 表示适配器拒绝任何非 off 档位，
  界面上选 low/high/max 会直接 `UNSUPPORTED_REASONING_EFFORT`（`dsh-llm-deepseek` 源码
  `resolveAdapterOptions` 与每请求校验两处都会拦）。
- 想"默认不思考、但允许切回"：`thinking: enabled` + `reasoningEffort: "off"`。
  档位解析顺序是 `请求参数 → defaults.reasoningEffort → (thinking 为 disabled ? off : high)`，
  所以默认值设在 `reasoningEffort` 上即可，`thinking` 保持默认 `enabled`。
- 与压缩无关：压缩阈值调低省的是上下文，推理档位管的是每次请求要不要思考，两者别互相顶替。

### 5.3 2026-11-14 二次修正：实际会话用的是 minimal

5.1 只覆盖了 `preset-standard`，但实际会话的 `agentPreset` 是 **`minimal`**
（profile 里 `agent-preset-registry.selectedDefault: minimal`）。minimal 内的
`compaction-basic` 没有 config，仍在用默认 `0.8`，所以表现为「配置了 8 万却直到
30 万+、45M 累计 token 都没压」。

修复方式：`~/.dsh/cordis.patch.yml` 同时覆盖 `standard/minimal/ptc/cordis`
四个内置 preset；superagent 自己的 `dsh-superagent-worker` / `dsh-superagent-router`
也补同样 config。可重复执行脚本在 `task/dsh-token-control/`。

验证判据：`--dump-config` 中每个 `id: compaction-basic` 后都必须出现
`thresholdRatio: 0.08`；只看 `preset-standard` 不算通过。

### 5.4 2026-11-14 新增：压缩结果落盘为 STATUS

DSH 原生 `compaction-basic` 只在会话日志里写 `compaction/summary` checkpoint，
不会生成项目目录里的 `STATUS.md`。新增本机插件
[`task/dsh-context-guard/`](../../personalCloud/task/dsh-context-guard/README.md)：

- 监听 `compaction/start`：先写压缩前的标题、工作目录、最近用户意图、最近工具调用；
- 监听 `compaction/summary`：把 DSH 自己生成的结构化摘要追加进同一份 `STATUS.md`，
  并另存一份带时间戳的历史文件；
- 不额外调用模型，不增加压缩成本；
- 默认写到 `${DSH_HOME:-$HOME/.dsh}/compaction-archive/<session-id>/STATUS.md`。

插件已安装进 `web` 与 `superagent` profile；只有实际发生压缩的会话才有归档。

## 6. 一句话备忘

- 默认 0.8 对 1M 窗口是合理值；本机已按用户要求改为 0.08（约 8 万 token 触发，见 5.1、5.3）。
- 想立刻压缩一次：用户执行 `/compact`（它做一次「低于自动阈值的有用压缩」，可反复用）。
- 手动压缩的合适时机是**任务达到干净边界**时——此时摘要质量最好；中途压缩容易丢细节。
