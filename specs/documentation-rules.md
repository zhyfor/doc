---
audience: shared
status: current
owner: workspace
scope: /home/zh/www
---

# 文档规范（spec）

- 适用范围：`/home/zh/www` 下所有 Markdown 文档的新增、修改、合并、删除与检查。
- 相关：[`AGENTS.md`](../../AGENTS.md)、[`PROJECT_INDEX.md`](../../PROJECT_INDEX.md)、[`task-workflow.md`](task-workflow.md)、[`PLAN-doc-slimming-and-tooling.md`](../archive/plans/PLAN-doc-slimming-and-tooling.md)

## 1. 文档层级与唯一源

| 类型 | 位置 | 作用 |
|---|---|---|
| AI 硬约束与路由 | `AGENTS.md` | 只写必须遵守的规则和去哪看 |
| 工作区导航 | `PROJECT_INDEX.md` | 只做入口和仓库索引 |
| 跨仓流程与硬约束 | `doc/specs/` | 任务流程、工程、运维、文档等长期规则 |
| 非必读参考 | `doc/reference/` | 稳定但不必背诵的操作事实 |
| 活跃计划 | 各仓 `plans/`、跨仓 `doc/plans/` | 一次性的实施计划 |
| 历史资料 | `doc/archive/` | 已完成计划与复盘，不要求 AI 必读 |
| 项目事实 | 各仓 `README.md`（定位与用法）/ `STATUS.md`（状态）/ `SPEC.md`（做法） | 只属于该项目的状态和做法 |

- 一个主题只有一份主文档；其他位置只留链接，不复制正文。
- 跨项目通用规则放共享规范；项目专属知识迁回对应仓库。
- 文档与磁盘、源码、服务状态冲突时，以现状为准，并立即修文档。

## 2. 写什么

- 只写：结论、硬约束、适用边界、例外、入口、必要命令、最小验收。
- 不写：背景论证、过程日志、重复示例、可现查的细节、已经过期的状态。
- 入口文档只回答三件事：必须知道什么、必须禁止什么、去哪看。
- 抓大放小，不求全；非显然事实和踩过的坑优先于完整教程。

## 3. 删除、合并、压缩

处理顺序：先合并，再迁走，最后删除；拿不准就只归档。

- **删除**：内容已过期或与现行规则冲突；同一事实已有唯一权威源且无独有细节；项目专属事实应迁回项目仓；一次性计划已完成并归档。
- **合并**：同一主题散落多份；通用规则写在项目文档里；同一规则在入口、流程、规范中重复出现。合并后只留一处主文档，其他位置用链接。
- **压缩**：只留结论、硬约束、边界、例外、入口和最小验收；删背景、推导、过程日志、重复示例、可现查的细节。超限文档用 `doc-slim` 技能精简。
- **保留**：安全红线、授权边界、非显然事实、失效条件、必要命令、跨项目通用规则。
- **不求全**：项目文档不要求全部符合本规范；只检查治理范围，行数超限先 `WARN`。

## 4. 计划文档

- 位置：单仓计划放 `<repo>/plans/PLAN-<主题>.md`，同仓文件名唯一，不用 `PLAN.md`；跨仓计划放 `doc/plans/PLAN-<主题>.md`。仓库根不再平铺计划文件。
- 首行 H1 必须是 `# PLAN：<简短标题>`，使用全角冒号。
- frontmatter 只保留：`implementation_status`、`created_at`、`updated_at`，时间格式 `Y-m-d H:i:s`。
- 状态枚举：`not_started | in_progress | fixing | blocked | done | rolled_back`。
- 正文必须有 `## 改动记录`，每条只写“时间 + 改动点”。
- 正文只写：目标、范围、改动位置、实施步骤、验收、回滚；不写复盘和过程流水。
- 允许计划正文唯一一个固定小节 `## 核验记录`：字段为轮次 / 对象 / 命令 / 结论 / 遗留风险 / 状态 / 开销，≤8 行，只写结论不写过程流水。
- 篇幅默认 ≤200 行；确需保留交接证据、命令清单等多行内容时，正文加 `## 篇幅说明` 写明原因、必须保留的段落和可压缩位置，上限放宽到 400 行。
- 计划完成后单仓移入 `<repo>/plans/archive/`、跨仓移入 `doc/archive/plans/`；活跃目录只留正在做或确实阻塞的计划。

## 5. 生命周期与 AI 责任

- 流程：讨论收敛 → 写计划 → 用户确认 → 实施 → 同步文档 → 分仓提交。
- 修改行为、入口、仓库状态后，必须同步 `README.md` / `STATUS.md` / `PROJECT_INDEX.md`。
- AI 负责按检查报告修文档；用户不手工整改文档。
- 输出文档、提交、报告时附本地链接：链接名用相对 `/home/zh/www` 的路径，地址用本机全路径。

## 6. README / npm / 插件市场文案

### 6.1 硬规则

1. 前 10 行讲清三件事：是什么、给谁用、关键差异。不从背景、愿景、技术栈开头。
2. 紧跟「先说最要紧的 3–5 件事」，一条一句：能做什么、不能做什么、前提和风险；宁短勿全。
3. 「完整功能」放后面，编号列表，一条一句；用法和教程外链 `docs/`。
4. README 首句、npm description、market 文案用同一句定位，不各写一套。

### 6.2 README 结构

标题 + 一句话 → 先说最要紧的 3–5 件事 → 最短上手（可复制，≤15 行）→ 完整功能 → 边界与限制 → 去哪看（STATUS / docs / 市场页）。

- 篇幅 ≤150 行；超出先删教程、流水账、重复安装说明，细节移 `docs/`。
- 安装命令只出现一次；不写状态、实测日期、计划、环境安装记录，这些归 `STATUS.md`。
- 中英双份只做等价翻译；有 `README.en.md` 就必须同步，不新增内容；没有不强制新建。
- 语气：术语准确 + 句子口语化，用「你」；不用「赋能、一站式、生态、极致」。

### 6.3 npm 说明

- `package.json` 的 `description`：一句话，≤100 字符，写「给谁 + 干什么 + 关键差异」，功能最多点 3 个。
- `keywords` 5–10 个，必含 `dsh-plugin`；同名包先核对 `npm view <pkg> repository` 指向本仓。
- npm 页面正文就是 README，不另写一份；改 description 必须发版，发版后 `npm view <pkg> description` 复核。
- 发布状态写 `STATUS.md`，不在 README / PUBLISHING 写死「尚未发布」。

### 6.4 插件市场说明

- `market/<owner>__<repo>.yml` 必备：`url`、`name`、`category`、`description.zh`、`description.en`；`tarball` 与 `icon` 至少一项。
- description 一句，中文 ≤80 字、英文 ≤200 字符；写「做什么 + 2–3 个关键能力」，不写安装。
- 中英同义同信息量，以中文为基准，不各删一半。
- `category` 用市场已有枚举（当前见过 `ui`、`tools`、`workflow`），不造新词；新类别先确认。
- 文案改动与 README、`package.json` 同一次提交，再走发布流程（`engineering-rules.md` §6）。

### 6.5 检查

- 新增或大改 README 时按 6.1–6.4 自查；`check.sh` 只查断链和行数（README 150 行 WARN），不判断重点是否清楚。
- 现有超限 README 在下次改动时收敛，不单独开批量重写。

## 7. 检查约定

- `scripts/check.sh` 是唯一检查入口；`FAIL` 阻断：断链、非法计划状态、计划元数据或改动记录缺失。
- 行数超限默认 `WARN`；计划含 `## 篇幅说明` 且 ≤400 行时不报 WARN；`--strict` 才返回失败。
- `--slim` 只列 `[SLIM]` 超限清单与 doc-slim 步骤、不改文件，超限时退出码 1；精简后仍用 `--strict` 复核。
- `scripts/docs-watch.sh` 每日只读巡检，失败才通知；不自动改文档。
- 批量规范化：`./scripts/plan-tool.py normalize <仓>...` 修正计划 frontmatter（只留三键、`created_at` 取 git 首次提交）与 H1 / `## 改动记录`；`relink <仓>...` 按 git 重命名记录改写被移动文档的 md 引用（跳过 archive）。两者都支持 `--dry-run`，改完仍用 `check.sh --strict` 复核。
- 检查策略只有 `scripts/docs-policy.json` 一份；各仓不再放 `docs-policy.json`。
- 过渡期已有普通文档的 `audience` / `status` 可暂留，检查器切换后统一移除。
