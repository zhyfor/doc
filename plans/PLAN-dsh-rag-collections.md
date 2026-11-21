---
implementation_status: blocked
created_at: 2026-11-21 17:36:56
updated_at: 2026-11-21 17:36:56
---

# PLAN：dsh-rag 集合分层与按仓索引

## 目标

- 索引改“按仓库建 project”，废弃 `/home/zh/www` 大根索引（www 只是软链接合集）。
- 索引写入集合元数据（`kind` / `weight` / `embed_profile`），`--all` 跨仓检索按权重合并；书库与项目检索分离。
- 增加 `.dsh-rag.json` 项目级配置：集合名、kind、权重、向量档位、排除规则。
- 修三个已定位缺陷：书库重复副本、思源导出只有 4/198 篇、安装的 0.7.0 与源码 0.8.0 不一致。
- 补 `workdir-rag/SPEC.md`，把索引模型、权重与检索契约固化下来。

## 非目标

- 本轮不索引 `project-experience`。当前审核流程和新经验体验都不好（每条都是完整文件 diff、重复标题多），等经验库改版后再作为最高权重集合单独立项。
- 不做 rerank / LLM 摘要 / 后台 watcher；不启用 gitnexus（当前 `disabled: true` 且无索引）。
- 不改 S3 协议；不做“大一统单索引”；不改 dsh-superagent 分支（仍在 `feat/executor-budget-phase-end`，不合并）。

## 前置条件（本计划阻塞于此）

- SA 项目迁移完成、`personalCloud` 与 SA 相关仓库落定后再开工。
- 届时 `dshSuperagentRepo` 可能已封档、`workdir-rag` 已迁走；目标仓路径以 `repos.yaml` 与 `PROJECT_INDEX.md` 为准，本计划随仓库迁移。

## 现状与依据

- 大根索引：3859 文件 / 50919 块 / **0 向量** / 104MB / 已截断；索引里是 `.tmpdiag` 会话副本、`.run` 状态文件、`superCreater` 数据，而 `personalCloud/task/notes`、`project-experience` 没进索引。
- `lab`：19 文件 / 11191 块 / 62MB；同一本书在 `books/` 与 `books/library/` 各一份（md5 相同）；思源只导出 4 篇，磁盘有 198 个 `.sy`；向量只有 512 维小模型。
- 二进制 0.7.0，源码 `internal/rag/types.go` 为 0.8.0；`dsh-rag web` 只有 0.8.0 有。
- MCP `search` 只有 `all/pull/snippet/project/path_prefix`，没有 kind/权重；`--all` 是等权 RRF。

## 设计

### 集合配置

每个索引根可放 `.dsh-rag.json`：

```json
{
  "name": "workdir-rag",
  "kind": "code",
  "weight": 1.0,
  "embed_profile": "small",
  "exclude": ["**/data/**", "**/.tmpdiag/**"]
}
```

- `name` 缺省用目录名；`kind` 取 `code|doc|note|book`；`weight` 缺省 1.0，仅 `--all` 使用；`embed_profile` 取 `small|m3|off`。
- `exclude` 为 glob 数组，叠加在默认忽略与根 `.gitignore` 之上（多仓工作区需要，因为它不再有单一根 `.gitignore`）。
- 集合元数据写进索引 `meta`/`Index`，`FormatVersion` 升到 3；`--all` 直接读各索引的权重，不依赖配置文件仍在。

### 文件 kind 判定

- 扩展名：`.go/.py/.ts/.js/.rs/.java/...` → `code`；`.md/.txt/.rst/.org` → `doc`；`.sh/.yml/.yaml/.toml/.json/.conf` → `doc`（配置当文档查）。
- 集合 `kind=book|note` 时目录内全部文件按集合 kind 计，不再按扩展名。
- kind 只做过滤与展示，不参与词法/向量打分，避免污染 BM25 语义。

### 权重与合并

- 单 project 内不做加权；权重只作用于 `--all` 的跨 project 合并：各 project 按排名归一 → 乘 `weight` → RRF(k=60) 合并。
- 默认 `--all` 不含 `book` 集合；查书必须显式 `--kind book` 或 `--collection books`，避免书摘稀释项目结果。
- 经验库将来接入时 `weight` 设 1.5，本轮留字段不启用。

### 接口变化

- CLI：`search` 增 `--kind code,doc`、`--collection <name>`；`index` 读 `.dsh-rag.json`；`status` 输出集合名/kind/weight/向量档位。
- MCP：`search` 增 `kind`、`collection`；`all` 语义改为“已索引集合（不含 book）”；`index`/`status` 增 `root` 的集合回显。
- Web（8766 只读页）：加集合筛选下拉；书库页固定 `collection=books`。

### 按仓索引

- `repos.yaml` 登记的 13 个仓库各建一个索引；`personalCloud` 通过 `exclude` 去掉 `task/superCreater/data`、`task/zipvoice`、`task/archive`、`.tmpdiag`、`.run`。
- 未登记仓库（`dsh-local-vision`、`free-ai-router` 等）需要时先登记再索引。
- 向量档位：`code`/`doc` 用 `small`（512 维，快）；`note`/`book` 用 `bge-m3`（语料小，值得准）。
- 大根 `/home/zh/www` 索引停用：不删文件，目录改名为 `legacy-www`，MCP/skill 不再默认指向它。

### 三个缺陷

1. **书重复**：`sync-sources.py` 同时写 `books/` 顶层与 `books/library/`。改为单份（保留顶层，删除 `library/` 副本），补测试断言无重复路径。
2. **思源 4/198**：`newest_doc` 只取每个文档目录里最新的 `.sy` 并跳过子文档。改为遍历 `data/<notebook>/` 下全部 `.sy`（含子文档），manifest 记录 notebook 数与文档数、跳过原因。
3. **版本漂移**：用源码构建 0.8.0 安装到 `~/.local/bin/dsh-rag`，旧二进制备份；`README` 命令按 0.8.0 校正（0.7.0 无 `web` 子命令）。

## 实施步骤

### P0 数据与配置（不改 dsh-rag 代码）

1. 备份：二进制与 `~/.local/share/dsh-workdir-rag/indexes` 各留一份 `.bak-20261121`。
2. 构建安装 0.8.0，`dsh-rag --version` 校验，`go test ./...` 通过。
3. 修 `sync-sources.py` 两处缺陷，重跑 `sync-sources.py all`，核对 manifest 文档数与 `.sy` 数。
4. 逐仓 `dsh-rag index --root <repo>`；`note`/`book` 用 m3，其余 small。
5. 大根索引改名 `legacy-www`；确认 MCP 与 skill 不再默认使用。
6. 起 8766 只读页（systemd user unit），`curl` 健康检查。
7. 更新 `skills/workdir-rag/SKILL.md` 路由：项目→按仓、书→books、跨仓→`--all`（不含书）；更新 README。

### P1 代码

8. `FormatVersion=3` + `.dsh-rag.json` 解析 + 文件 kind + `--all` 加权 + MCP 参数 + Web 筛选。
9. 补单测与评测：kind 过滤、权重排序、exclude 生效、无配置时向后兼容。
10. 重建各仓索引（格式升级），抽样对比 `--all` 排序。

### P2 收尾

11. 补 `workdir-rag/SPEC.md`（本计划已先落草案，实施后校正）。
12. 更新 `PROJECT_INDEX.md` / `STATUS.md` / README；分仓提交推送。

## 验收

- 每个登记仓库：`dsh-rag status` 的 `Files>0`、`Truncated=false`、`EmbeddedChunks≈Chunks`。
- `search "RAG 方案"` 命中 `personalCloud/task/notes/RAG-PLAN.md`；`search "superCreater"` 不再返回 `.tmpdiag` 副本。
- `search --all` 返回多仓结果并标出集合名/权重；`--kind doc` 只回文档；默认结果不含书。
- `curl 127.0.0.1:8766/api/search?q=...` 返回 200 且能搜到书。
- `sync-sources.py all` 的文档数与 `.sy` 数一致或逐条记录跳过原因；`books/` 无重复文件。
- `dsh-rag --version` 为 0.8.0，README 里命令逐条可执行。
- `go test ./...`、`./scripts/check.sh --repo doc`、`--repo dshSuperagentRepo` 通过。

## 回滚

- 二进制与索引目录保留备份 7 天；回滚=恢复旧二进制 + 备份索引。
- P1 是格式 v3，旧二进制读不了 v2 之外的格式：回滚必须同时恢复二进制与索引；S3 按 project 快照保留上一版。
- `sync-sources.py` 与 `SKILL.md` 都是单文件，`git revert` 即可。

## 改动记录

- 2026-11-21 17:36 初稿：确定按仓索引、集合 kind/weight、经验库暂不索引、三个缺陷并入。
