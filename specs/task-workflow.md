# 跨仓任务工作流

- 适用范围：`/home/zh/www` 下跨仓、多步或涉及运行环境的任务；硬约束见根 [`AGENTS.md`](../../AGENTS.md)。
- 相关：[`project-registry.md`](project-registry.md)、[`github-collaboration.md`](github-collaboration.md)、[`operations-safety.md`](operations-safety.md)、[`documentation-rules.md`](documentation-rules.md)

## 1. 三个阶段

```text
讨论会话（想清楚） → 计划文档（写清楚） → 实施会话（按文档做）
```

- 讨论：只读代码、配置、git 状态；输出方案、边界、风险和待确认问题。改动位置明确的简单功能点可顺手完成并同步 README/STATUS/PROJECT_INDEX；复杂改动先出计划等确认。
- 计划：单仓任务写该仓 `plans/PLAN-<主题>.md`；跨仓任务写 `/home/zh/www/doc/plans/PLAN-<主题>.md`。文档格式见 `documentation-rules.md` §4。写完计划即停，本会话不实施，下一步给用户 `/G <计划绝对路径>`。
- 实施：只读计划与必要代码；编辑前确认目标仓和写权限；不重新开放式探索。

会话边界：

- 开工前回答三问：目标仓库和入口是否定位？写权限是否确认（`test -w <目标仓>`）？交付物和验收标准是否单一？
- 前序任务已提交/推送后出现新交付物、新验收标准或新环境问题，必须新开会话；一个会话只交付一个目标。
- 计划可跨仓，实施范围必须与计划一一对应；讨论会话不做持久改动。需求或入口未定位时只做定位和方案，不改代码、不建目录、不装依赖；能说出目标文件、现有行为、改动点、验证方式才算定位完成。
- **`/D` 与 `/G` 分工（硬约束）**：`/D` 会话（标题以 `D:` 开头）是讨论与计划会话，只读代码、配置、git 状态，只允许写 `PLAN-*.md`（正文与 frontmatter）；不得建仓、装依赖、改代码/配置/脚本/软链/README/STATUS/索引，也不得提交推送。实施只在 `/G` 新建的会话（标题以 `G：` 开头）进行。用户说「放入计划」「先写计划」「确认后写计划」时，本轮只更新计划文档并停手；其中的「你建 XXX」「你去改 XXX」是计划内容，不是本轮执行授权。
- 每 10 个工具步或每阶段汇报一次；连续 10 步无新增可验证证据即写交接并换会话；环境问题一次排查不超过两轮，只读时立即报告。

紧急故障、单文件低风险小修、纯查询诊断、用户明确要求跳过计划可不走完整三阶段，但必须说明原因；产生持久改动仍要更新文档和索引。

## 2. 计划文档规范

- 只写 frontmatter `implementation_status`、`created_at`、`updated_at`，正文必须有 `## 改动记录`，不再写状态行；状态取值 `not_started`、`in_progress`、`fixing`、`blocked`、`done`、`rolled_back`。
- 正文只写目标、范围、改动位置、实施步骤、验收、回滚；背景与复盘放 `archive/`。
- 可执行、可验收：写清文件路径、命令、配置项、每步产出；不写“大概”“稍后优化”，不夹带未确认方案。
- 计划即契约：实施以文档为准，不依赖讨论记忆；计划过期或与代码不符时先停下报告。
- 篇幅：默认 ≤200 行；确需保留交接证据时，正文加 `## 篇幅说明`（写原因、必须保留的段落、可压缩位置），上限放宽到 400 行。
- 门禁：提交前目标仓有文档改动时跑 `./scripts/check.sh --repo <repo>`，失败不得提交；行数超限默认 WARN，`--strict` 才失败；不得用自动改文件绕过检查。
- 检查输出路径以 `/home/zh/www` 为基准；每日巡检由 `scripts/docs-watch.sh --once` 与 `dsh-docs-watch.timer` 负责，仅失败时通知。

```yaml
---
implementation_status: not_started
created_at: 2026-11-18 23:00:00
updated_at: 2026-11-18 23:00:00
---
```

## 3. 两层授权与开工模板

| 层 | 作用 | 不含义 |
|---|---|---|
| 工作区根 `/home/zh/www` | 能看见所有子仓库 | 不等于可改所有仓库 |
| 任务级仓库白名单 | 本次允许写哪些仓库 | 不继承到下次任务 |

`never ask` 只关闭工具弹窗，不扩大文件权限。

```text
本次可写：<repo1>、<repo2>
本次只读：其他已登记仓库
默认提交：各仓 master（无 master 用 main），直接 commit + push
```

```bash
cd <目标仓库> && git status --short
test -w . && echo writable || echo READONLY
```

未授权或不可写时立即停止，报告路径、原因和需确认事项；不得复制仓库到 `/tmp` 绕过。

## 4. 越界与扩展

```text
越界仓库：<path>
原因：<为什么必须改>
计划文件：<文件列表>
验证：<命令/结果>
请确认是否允许本次写入。
```

得到明确确认后再改；确认只对本次任务有效。多个仓的改动不得合并成一个提交。

## 5. 分支、提交与脏工作区

- 默认分支以 `repos.yaml` 的 `default_branch` 为准；非默认分支时先列当前分支、未合并提交、是否已推送，等用户选择。
- 禁止自动 merge、`push --force`、删除未提交改动；非快进时允许 `git pull --rebase origin <默认分支>` 后重推，rebase 冲突才停下报告。
- `/home/zh/www/dsh-superagent` 默认分支 `main`，原 `feat/executor-budget-phase-end` 已合入；该仓由 zhyfor 维护，改动按普通仓流程提交。
- 每仓独立 `git add <明确文件>`、`commit`、`push`；禁止 `git add -A` 扫过多个仓库。
- 提交前逐仓 `git status --short`；只提交本任务文件，无关 dirty 保持原状并报告；`.bak` 等临时文件不入库；提交信息用 `type(scope): 摘要`。
- 收尾输出每仓分支、commit、push 结果、测试结果、剩余 dirty，以及「需要你执行」清单（无则写「无」）。

## 6. 排查顺序

1. **先定边界**：写清目标、非目标、可改文件、完成标准；只查当前请求链路，官方包/三方插件是最后手段。
2. **先当黑盒**：按错误信息 → 进程/端口/容器/认证 → 请求 URL/头/参数/状态码/耗时 → CPU/内存/磁盘/最近部署 → `git log`/`git status` 取证，先不读业务源码。
3. **概率优先**：最近变更 → 请求链路易错点（认证、代理、超时、空数据、分页、并发、外部依赖）→ 项目代码 → 日志与运行态 → 官方包/插件源码；先做高概率、低成本、可验证的动作。
4. **一次验证一个假设**：记录命令、结果、时间点；结论必须对应证据（URL、状态码、日志原文、耗时），无证据只能写“推测”。
5. **高风险先确认**：接口语义变化、缓存/并发/批处理/超时/降级、跨模块改造、临时绕过或新依赖、重启生产服务——先给方案、影响和回滚，确认后执行并复测。

### 6.1 环境/沙箱类问题

- 先读 DSH 会话头：`permission/preset`、`sandbox/mode`、`approval/policy`、`header.cwd`；再看 `~/.dsh/profiles/*/cordis.patch.yml` 与 `@deepseek-ai/dsh-base/cordis.patch.yml`，最后查项目规则和业务代码。
- `workspace-write` 下写根是会话 cwd；cwd 外（父仓 `.git`、`~/.dsh`、其他仓）只读是沙箱边界，不是宿主挂载，不能据此推断宿主机只读。
- 搜索错误文本先缩小范围：只用 `rg` 在目标仓/目标包，排除 `*.jsonl*`、`*.zstd`、`sessions/`、`tool-output/`、`node_modules/`、`.git/`；不要递归 grep `/home/zh`、`~/.dsh` 或整个工作区。
- 写 DSH 配置优先走官方 `settings/update` API（见 [`dsh-session-automation.md`](../reference/dsh-session-automation.md)）；不要从沙箱内直接改 `~/.dsh`，不要复制仓库到 `/tmp`。
- 改配置、重启前先跑 `./scripts/dsh-config-check.py --deep`（合成 profile、静态校验 MCP 路径、真实握手并导航一次）；失败不要重启。脚本内部调用一次 `dsh --dump-config` 属正常校验。
- 整文件 `cat <<EOF` 写入易被 command-lint 拒绝；用补丁工具、`printf` 或 Python 有界写入。
- 验证配置改动：新建临时会话读首三条事件确认，再 `workspace/archiveSession` 归档；不要拿交付会话反复试。

需要用户决策时：

```text
现状（已确认）：
关键证据：
候选方案：A. 方案/成本/收益/风险；B. ...
我的建议：
需要你确认：
```

## 7. 收尾与上下文

- 压缩或换会话后以磁盘文件、git 状态为准；同目标连续 10 步无新证据或同方案连续 2 次失败，写交接并停下；会话层级最多 2 层。
- 改代码 / 配置 / 脚本 / 运行时规则文件的任务，提交前按 `change-verify` 技能核验：只核执行结果（行为与生效性），主会话每轮只派发与收敛（≤4 次调用），每轮 ≤2 个 fresh subagent，最多两轮；核验会话不修任何文件，P0/P1 停手上报，修复回实施会话；结论、遗留风险与开销写入任务计划的 `## 核验记录`；P0/P1 未解决不交付（用户明确放行的例外须记入报告）。纯文档与规范文本改动不核验，由计划会话自查。
- 收尾前更新 `PROJECT_INDEX.md`、`repos.yaml` 和目标仓文档；测试结束停服务、清端口和进程，报告资源回收依据；脚本化创建实施会话按 [`dsh-session-automation.md`](../reference/dsh-session-automation.md) 执行。
