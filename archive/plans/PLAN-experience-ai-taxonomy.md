---
implementation_status: done
created_at: 2026-11-19 07:50:00
updated_at: 2026-11-19 08:21:44
---

# PLAN：经验库 AI 分类与 www 架构同步

## 目标

把 `project-experience` 从“只有知识类型”升级为“知识类型 + 领域”两层检索，给 AI 相关经验一个单独入口；同时同步 `www` 已拆分出的 DSH 插件仓库与 SA 仓库角色，并把与 AI 对话开发的流程经验按脱敏规则收进候选/已验证条目。

## 已确认的取舍

- AI 类范围按 D：`ai-collaboration`（和 AI 对话协作开发）、`agent-capability`（RAG/MCP/模型/token/prompt）、`dsh-plugin`（DSH 插件开发本身）。
- 分类落点按推荐：不改 `entries/<type>/` 物理目录，新增领域字段 + `entries/INDEX.md`。
- 存量按备选：对候选做启发式领域标注，但**不改变 candidate 状态、不提升 verified**。
- 证据先脱敏：不写原始对话、家目录、内网 IP、token；证据不足的条目保留 candidate。

## 分类规范

```yaml
domain: ai
ai_topic: ai-collaboration   # 或 agent-capability / dsh-plugin
```

- `type` 仍表示知识形态（pitfall/pattern/decision/convention/workflow/checklist/reflection）。
- `domain` 是可选字段；目前只定义 `ai`，非 AI 条目不填。
- `domain: ai` 时 `ai_topic` 必填；`ai_topic` 不得脱离 `domain: ai` 单独出现。
- 候选可带领域字段，但检索默认仍只返回 verified。
- 现有 verified 中已属 AI 的条目补字段；其余条目不动。

## 改动位置

- `project-experience/schemas/entry.schema.json`：增加 `domain`、`ai_topic` 及枚举。
- `project-experience/tools/dsh-exp`：
  - `DOMAINS`、`AI_TOPICS`、校验规则、front matter 输出顺序；
  - `_infer_domain()` / `_infer_ai_topic()`，接入 `mine` 与 `propose`；
  - 新增 `classify --write [--dry-run] [--clear]` 批量回填；
  - 新增 `index --write` 生成 `entries/INDEX.md`；
  - `context` 增加 `--domain` / `--ai-topic` 过滤并输出字段。
- `project-experience/tools/dsh-exp-review`：候选/详情页显示领域标签，不改变入库目录。
- `project-experience/entries/INDEX.md`：AI 三类视图 + 类型目录计数；不手工罗列全部候选。
- `project-experience/entries/**`：verified 补领域字段；候选启发性标注。
- `project-experience/README.md`、`AGENTS.md`、`docs/curation.md`、`STATUS.md`、`entries/README.md`。
- `personalCloud/workspace/PROJECT_INDEX.md`：`project-experience` 入口说明补“AI 分类”。
- `project-experience/tests/`：领域校验、推断、过滤、index、候选状态不变。

## 实施步骤

1. 扩展 schema 与 `dsh-exp` 字段校验；旧条目不填 `domain` 保持兼容。
2. 增加领域/子类启发式：AI 对话、上下文、PLAN、/D /G 归 `ai-collaboration`；RAG、MCP、向量、模型、token、prompt 归 `agent-capability`；DSH 插件、侧栏、Client/Host、插件发布归 `dsh-plugin`。只在命中明确关键词时标注，避免把普通 `dsh` 运维条目全归 AI。
3. `mine`、`propose` 自动写入推断出的 `domain/ai_topic`；无法确定时留空。
4. `classify --write` 回填存量：已有 verified 仅补字段；候选只改领域字段并保持 `status: candidate`；`--dry-run` 先输出将改列表与不确定项。
5. `index --write` 生成 AI 索引：三类各自列出 verified 条目和候选数量，索引用相对路径。
6. 从 DSH 三个插件仓的 README/PLAN/提交/test 中提炼 3–4 条 AI 经验；先搜重，重复则合并到已有条目，不硬造新 id：
   - 讨论会话与实施会话分离（`/D` 出 PLAN、`/G` 新会话执行）；
   - 长工具输出先落盘再有界摘要，避免重复计费；
   - 插件只读单一事实源，不维护第二套状态；
   - 插件交付按安装/配置/重启/冒烟/check 清单闭环。
   新条目先写 candidate；证据能落到公开仓库文档/PR/commit/test 的再走审核，只有本地会话的保留 `review_reason` 待补。
7. 更新 README/AGENTS/curation/entries README：写清 AI 分类、候选不提升、对话脱敏规则和 `www` 新仓库角色。
8. 更新 STATUS 与 `PROJECT_INDEX`；确认 `repos.yaml` 已含 `dsh-workbench`、`dsh-context-guard`、`dsh-workflow-shortcuts`，watch-all 无需改采集清单。
9. 跑测试、`sync --check`、`check.sh`，同步提交到 `project-experience` 与 `doc`/`personalCloud` 对应仓。

## 验收

- `dsh-exp sync --check` 错误为 0；旧条目不因新增字段报错。
- `dsh-exp context --domain ai --task "上下文 预算" --json` 只返回 AI 条目；`--ai-topic ai-collaboration` 可再收窄。
- 所有 `domain: ai` 条目都有合法 `ai_topic`；所有被标注候选仍是 `candidate`。
- `entries/INDEX.md` 可由 `dsh-exp index --write` 稳定重建，AI 三类和类型计数正确。
- 新 AI 条目不含原始对话、家目录、内网 IP、token；证据不足项未标 verified。
- `python3 -m unittest discover -s tests -v`、`./scripts/check.sh --repo project-experience`、`./scripts/check.sh --repo personalCloud`、`./scripts/check.sh --repo doc` 通过。
- `repos.yaml` 的 13 个仓库角色与 README/PROJECT_INDEX 一致；watch-all 覆盖新插件仓。

## 不做

- 不把条目迁到 `entries/ai/` 顶层目录。
- 不批量把候选改成 verified，不降低机审门槛。
- 不提交原始 AI 对话记录，不抄入凭据、内网地址和客户信息。
- 不改 DSH 三个插件的业务代码；只改经验库、索引与跨仓文档。

## 回滚

- 字段和命令均为增量；不兼容时回退 `tools/dsh-exp`、schema、测试与 `INDEX.md`。
- 批量候选标注用 `classify --clear` 或按 Git 提交整体 revert，不影响条目正文与状态。
- 新 AI 条目可单独删除/降回候选；已 verified 条目按 `feedback` 流程复审，不直接改历史证据。
- 各仓分别 `git revert` 对应提交。

## 改动记录

- 2026-11-19：创建计划，确认 AI 三小类、字段+索引、候选启发式标注、对话证据先脱敏。
- 2026-11-19：完成 schema/CLI/存量回填/INDEX/4 条新经验/文档同步；36 tests、sync 0 错误，三个仓库 check.sh 通过。
