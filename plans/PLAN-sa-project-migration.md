---
implementation_status: not_started
created_at: 2026-11-21 17:50:00
updated_at: 2026-11-21 18:10:00
---

# PLAN：SA 仓项目迁出与项目落点规范

## 目标

1. `dshSuperagentRepo` 不再当项目宿主：根级与 `task/` 下 9 项按「独立仓 / personalCloud task / 归档」迁出，SA 仓只留任务台账、交付说明、跨项目规则与脚本。
2. 在 [`doc/specs/project-registry.md`](../specs/project-registry.md) 落一条可判定的落点规则，让 AI 与人都不再靠记忆找代码。
3. 独立仓保留原 git 历史（`git subtree split`），功能等价后再删源目录。

## 范围

- 可写仓库：`dshSuperagentRepo`、`personalCloud`、`doc`、`project-experience`；新建 5 个独立仓。
- 非目标：不改 SA 代码；不修 `dsh-superagent.service`（记遗留）；不动 `project-experience` 现有 48 处 dirty、`personalCloud` 现有 4 处 dirty。

## 现状（2026-11-21 核实）

| 项目 | 运行物 / 外部耦合 | 去向 |
|---|---|---|
| `workdir-rag/` | Go MCP，`~/.local/bin/dsh-rag`；对 `dsh-ml` 仅 HTTP 软依赖 | 独立仓 |
| `dsh-local-vision/` | Python MCP+CLI，`install.sh` 复制 skill 到 `~/.dsh/skills/` | 独立仓 |
| `free-ai-router/` | skill + 脚本；`catalog.json` 内有两处本仓子目录链接 | 独立仓 |
| `python/` | uv workspace + `dsh-ml.service`（当前 inactive）；被 workdir-rag 引用 | 独立仓 `dsh-py-runtime` |
| `task/dsh-immersive-glass/` | DSH profile `link:` 依赖 | 独立仓 |
| `rag-sources/` | 无 install.sh，依赖思源/电子书数据 | `personalCloud/task/` |
| `experience-review/` | 只有 README、截图、unit；代码在 `project-experience/tools/` | 并入 `project-experience` |
| `task/image-ocr-phases/` | 只有 `STATUS.md` | 归档 |
| `task/project-experience-watch/` | 只有 `STATUS.md`，已被 `dsh-exp-watch-all` 取代 | 归档 |
| `task/project-experience/` | 空目录，git 未跟踪 | 删除 |

`dshSuperagentRepo` 被 `repos.yaml` 里 13 个仓登记为 `task_ledger`，角色是「SA 交付、说明与检查」。

## 目标布局

```text
www/
├── workdir-rag/           独立仓（Go RAG + MCP）
├── dsh-local-vision/      独立仓（本地图片能力）
├── free-ai-router/        独立仓（免费 AI 调度）
├── dsh-immersive-glass/   独立仓（DSH 插件）
├── dsh-py-runtime/        独立仓（uv 运行时 + dsh_ml）
├── project-experience/    经验库 + 审核网页（并入 experience-review）
├── personalCloud/task/
│   ├── rag-sources/       小任务
│   └── …
└── dshSuperagentRepo/     任务台账、SA 交付说明、doc/、scripts/、patches/
```

## 落点规则（写入 `doc/specs/project-registry.md` §8）

| 判据 | 去处 |
|---|---|
| 有独立运行物（systemd/MCP/DSH 插件/安装脚本）或独立发布、独立 PR、独立权限 | `/home/zh/www/<name>` 独立仓 |
| 一次性任务、小工具、调研记录、少量脚本 | `personalCloud/task/<name>` |
| 已完成，只留记录 | 各仓 `archive/` 或 `doc/work/` |

判定顺序：先看运行物，再看是否被其他项目按路径引用，最后看是否长期演进；三者皆否 → task 或归档。提升为独立仓时沿用 §8 门禁（`SPEC.md`、`check.sh --repo`、`repos.yaml` 的 `spec:`）。

## 安全关（发布前必过）

源仓 `zhyfor/dshSuperagentRepo` 是**私有仓**，迁到 `person-clouds` 等于首次面对公开风险。已按「工作树 + 全历史」扫过，结论：

| 检查项 | 结果 |
|---|---|
| 密钥/令牌（gh/sk-/AKIA/私钥/xox/AIza/凭据 URL） | 0 命中（唯一命中是 `scripts/check.sh` 自带的检测正则） |
| `.env`/`.pem`/`.key`/`.sqlite`/`.db`/`.csv`/`.docx`/`.pdf` | 历史上从未提交 |
| 手机号、身份证、真实邮箱 | 无；仅测试用 `test@example.com` |
| 内网 IP、Tailscale 域名、连接串 | 0；`uv.lock` 的命中是 PyPI 地址误报 |
| 图片 EXIF（GPS/机型/作者） | 无；29 张图都自造或生成，抽查 3 张无个人信息 |
| 提交者邮箱 | **55 次提交用 `fenghoer@163.com`**，公开即暴露 |
| 环境指纹 | 少量 `/home/zh/...`、`127.0.0.1:8766`、机器规格出现在 SPEC 与验收截图 |

必做门禁：

1. 阶段 2 第 3 步重写个人邮箱；推送前 `git log --format='%ae' | sort -u` 复核只剩 noreply。
2. 仓先建 private；转 public 前逐仓确认「无凭据、无个人信息、无客户数据」并在台账留记录。
3. 含内部路径/流程截图的目录（`experience-review/`）不随独立仓公开，只并入 `project-experience`。

## 实施步骤

### 阶段 0：基线

```bash
git -C /home/zh/www/dshSuperagentRepo tag pre-migration-20261121
git -C /home/zh/www/dshSuperagentRepo status --short   # 必须为空
```

记录功能基线：`dsh-rag mcp --help`、`dsh-vision --help`、`dsh-exp --help`、`systemctl --user list-unit-files 'dsh-*'`。

### 阶段 1：归档（零风险，先做）

1. `task/image-ocr-phases/STATUS.md` 要点合并进 `dsh-local-vision` 的阶段记录，原目录移入 `dshSuperagentRepo/doc/archive/`。
2. `task/project-experience-watch/STATUS.md` 与 `personalCloud/task/project-experience-watch/` 对比，保留一份，另一份改链接后归档。
3. 删除空目录 `dshSuperagentRepo/task/project-experience/`。
4. 同步 `dshSuperagentRepo/PROJECT_INDEX.md` 项目表与「最后核对」日期。

### 阶段 2：独立仓（5 个，同一套动作）

5 个私有空仓已在 `person-clouds` 建好（2026-11-21）：`workdir-rag`、`dsh-local-vision`、`free-ai-router`、`dsh-immersive-glass`、`dsh-py-runtime`。**先私有跑通，再逐仓决定是否转公开。**

每个仓重复以下 9 步（以 `workdir-rag` 为例）：

```bash
# 1. 拆历史
git -C /home/zh/www/dshSuperagentRepo subtree split -P workdir-rag -b split/workdir-rag
# 2. 本地建仓并导入
git init -b main /home/zh/www/workdir-rag
git -C /home/zh/www/workdir-rag pull /home/zh/www/dshSuperagentRepo split/workdir-rag
# 3. 重写提交邮箱（去掉个人邮箱 fenghoer@163.com）
FILTER_BRANCH_SQUELCH_WARNING=1 git -C /home/zh/www/workdir-rag filter-branch --env-filter '
GIT_AUTHOR_EMAIL=$(echo "$GIT_AUTHOR_EMAIL" | sed "s/^fenghoer@163\.com$/zhyfor@users.noreply.github.com/")
GIT_COMMITTER_EMAIL=$(echo "$GIT_COMMITTER_EMAIL" | sed "s/^fenghoer@163\.com$/zhyfor@users.noreply.github.com/")' -- --all
# 4. 关联远程并推送（仓为 private）
git -C /home/zh/www/workdir-rag remote add origin https://github.com/person-clouds/workdir-rag.git
git -C /home/zh/www/workdir-rag push -u origin main
# 5. 补 SPEC.md（≤60 行：目标/用户/范围/非目标/接口/运行/验收/约束），README 首段一句话
# 6. 迁移安装与引用路径（见下）
# 7. 验证
./scripts/check.sh --repo workdir-rag ; go test ./...
# 8. repos.yaml + 根 PROJECT_INDEX 登记，跑 ./scripts/repo-status.sh
# 9. 安全复核通过后才 `gh repo edit --visibility public`（逐仓，不在本计划内自动做）
```

各仓特有验证：

| 仓 | 额外动作 | 验证命令 |
|---|---|---|
| `workdir-rag` | 重装 `dsh-rag`；MCP 配置已走二进制，无需改 | `dsh-rag mcp --help`，一次真实检索 |
| `dsh-local-vision` | 重跑 `install.sh` 重装 skill 与 `dsh-vision` | `dsh-vision --help`，skill 列表可见 |
| `free-ai-router` | 改 `catalog.json` 两处链接为 `person-clouds/free-ai-router` | `catalog.json` 能解析，skill 可读 |
| `dsh-immersive-glass` | 改 `~/.dsh/profiles/web/package.json` 的 `link:` 路径 | DSH 重启后插件正常加载 |
| `python → dsh-py-runtime` | 目录名改 `dsh-py-runtime`；`install-runtime.sh` 检查写死路径 | `./scripts/check.sh`，不启用则跳过服务验证 |

阶段 2 期间**源目录不删**，新仓验证通过后再进入阶段 5。

### 阶段 3：并入 personalCloud/task

1. `rag-sources/`：`git subtree split` 导出后直接放到 `personalCloud/task/rag-sources/`，由 personalCloud 追踪；`repos.yaml` 不单列。
2. `experience-review/`：README 与截图移入 `/home/zh/www/project-experience/docs/`，`dsh-exp-review.service` 与 `project-experience/tools/dsh-exp-review*` 去重，只留一份并可安装；SA 仓删除该目录。

### 阶段 4：引用与文档收敛

逐项改并验证：

- `repos.yaml`：新增 5 条（含 `spec: SPEC.md`），删除 `dshSuperagentRepo` 相关旧描述。
- 根 `PROJECT_INDEX.md`：工作区地图 + 独立仓库表；`personalCloud/PROJECT_INDEX.md`：删 `experience-review`/`rag-sources` 迁出项、加 task 条目。
- `dshSuperagentRepo/PROJECT_INDEX.md`：项目表改为「SA 维护说明 + 新仓链接」。
- `dshSuperagentRepo/doc/`：写一段「这些项目由 zhyfor 与 SA 共同维护，代码在 `/home/zh/www/<name>`」的说明与链接。
- 系统引用：`dsh-exp-watch.service` 的 `WorkingDirectory` 与 `--project`（项目清单本身来自 `repos.yaml`）。
- `~/.dsh/skills/{dsh-local-vision,free-ai-router,workdir-rag}` 从新仓重装。

### 阶段 5：删源目录 + 收尾

1. `dshSuperagentRepo` 删除 8 个已迁出目录，只留 `doc/ plans/ scripts/ patches/` 与入口文件。
2. 跑 `./scripts/check.sh --repo doc`、`--repo personalCloud`、`--repo dshSuperagentRepo`。
3. 本计划移入 `doc/archive/plans/`，更新 `implementation_status: done`。

## 验收

- 5 个新仓：`git log --follow` 能看到原提交；`check.sh --repo <name>` 通过；各自测试命令通过。
- 安全：各仓 `git log --all --format='%ae' | sort -u` 不含 `fenghoer@163.com`；仓为 private，转公开有台账记录。
- `repos.yaml` 与两处 `PROJECT_INDEX` 一致；`./scripts/repo-status.sh` 无缺失路径。
- 功能：`dsh-rag` MCP 握手并完成一次检索；`dsh-vision` 可用；DSH 插件加载正常；`dsh-exp-review` 可启动。
- 找代码：只从根 `PROJECT_INDEX.md` 出发，两跳内到任意项目的 `README.md`。

## 回滚

- 源仓打 `pre-migration-20261121` tag；删源目录放在阶段 5，之前失败只回退新仓与引用，不动源。
- 每仓独立提交；`repos.yaml`/索引改动单独提交，可单点 revert。
- 安装类改动（skill、DSH 插件、systemd unit）改动前备份原文件，回滚即恢复备份并重装。

## 遗留

- `dsh-superagent.service` 的 `WorkingDirectory=/home/zh/src/dsh-superagent` 已不存在，SA 当前未运行；本次只记录，后续单开任务修，登记到 `zhyfor/dshSuperagentRepo/issues`。
- `dsh-superagent` 的 `feat/executor-budget-phase-end` 未合入 `main`，涉及 SA 时必须提醒，不自动合并。
- `project-experience` 48 处 dirty、`personalCloud` 4 处 dirty 属既有状态，本任务不处理。

## 改动记录

- 2026-11-21 17:50 初稿：确定 9 项去向、落点规则写入 project-registry §8、5 个独立仓与 subtree split 步骤。
- 2026-11-21 18:10 补安全关：密钥/隐私/EXIF 扫描结论、个人邮箱重写步骤、先私有后公开门禁；person-clouds 5 个私有空仓已建。
