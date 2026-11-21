---
implementation_status: done
created_at: 2026-11-21 05:25:00
updated_at: 2026-11-21 14:05:00
---

# PLAN：DSH MCP 采纳评估与 gitnexus / MySQL 只读接入

## 目标

1. 结论落地，避免重复评估 8 个候选 MCP（S1 已完成）。
2. `gitnexus` 单仓试点：`--index-only`、默认停用，验证「代码图」相对 `workdir-rag` + grep 的增量。
3. MySQL 不装 MCP，改用 bash + 只读账号。
4. `ZipVoice` 不是 MCP，本次不处理。

## 范围

- 本次实施 **S1–S6 全部**（2026-11-21 用户确认）。
- 不做：不改 DSH 源码；不装其余候选；不动 `context7` / `playwright` / `workdir-rag` 现状；不建 ZipVoice 环境；不索引整个 `/home/zh/www`。

## 前置事实（2026-11-21 实测）

- DSH MCP 客户端：stdio，工具名 `mcp__<server>__<tool>`，**启动即全量注册**，schema 每请求重发 → 常驻 token 税（[mcp-control](/home/zh/www/personalCloud/task/mcp-control/README.md)：207 工具时单请求 218k→296k）。
- 已启用：`workdir-rag`、`playwright`、`context7`；已停用的 MCP 条目：`rea`、`headroom`（后者对应的 `headroom-proxy` 本机已未安装、未接入，dsh 直连 DeepSeek）。
- 本机：Node `v24.22.2`（`/home/zh/opt/node24/bin/node`），满足 gitnexus `^22.18 || >=24.11`；Docker 运行中；MySQL 8 监听 `127.0.0.1:3306`；无 NVIDIA GPU；内存 46 GB；`/` 剩余 725 GB。

## 结论表

| 候选 | 版本与状态 | DSH 现状/替代 | 结论 |
|---|---|---|---|
| `context7-mcp` | 已装 `@upstash/context7-mcp`（npm 的 `context7-mcp` 为 404） | 唯一外部库文档源 | 保留现状 |
| `gitnexus` | 1.6.12，2026-11-20 | `workdir-rag` 只做文本/向量检索，答不了调用链与影响面 | 单仓试点（S2–S5） |
| `mysql-mcp-server` | 0.1.4，2026-09-22 | bash + `mysql` 客户端；MCP 需把库密码写进配置 | 不装，改 S6 |
| `mcp-server-docker` | 1.0.0，2025-06，MCP SDK 0.6.0 | bash `docker exec` 更灵活；需 docker.sock，无命令过滤 | 不装 |
| `@modelcontextprotocol/server-sequential-thinking` | 2.2.0，2026-11-18 | 推理 + `todo_write` + `goal` 已覆盖 | 不装 |
| `server-sequential-thinking` | 0.1.1-alpha.2，2025-04 | 第三方旧 fork | 不装 |
| `@modelcontextprotocol/server-memory` | 2.2.1，2026-11-18 | mnemon 已有 runtime memory + 项目 Documents | 不装 |
| `ZipVoice` | k2-fsa 123M TTS 模型，非 MCP | DSH 只有 STT；无 GPU | 单独立项 |

## 改动位置

1. `/home/zh/www/doc/plans/PLAN-dsh-mcp-adoption.md`（本文）。
2. `/home/zh/www/personalCloud/task/mcp-control/README.md`：登记 `gitnexus-mcp` 与「已评估未采纳」。
3. `/home/zh/.dsh/cordis.patch.yml`：`- insert:` 末尾新增 `gitnexus-mcp`（`disabled: true`）。
4. `/home/zh/.my.cnf` + MySQL 只读账号 `dsh_ro@127.0.0.1`（用户在宿主终端建）。

## 实施顺序与产出

| 步骤 | 动作 | 产出 | 验收 |
|---|---|---|---|
| S1 | 写本文与登记表 | 计划 + 表格 | 已完成（`doc` 044ea94 / `personalCloud` 0a8a17d） |
| S2 | 全局装 gitnexus | 可执行 `gitnexus` | `gitnexus --version` 输出 1.6.x；`gitnexus doctor` 无致命项 |
| S3 | 单仓索引 | 仓内 `.gitnexus/` 索引 | `gitnexus list` 见该仓；目标仓 `git status --short` 为空 |
| S4 | 注册 MCP | 配置条目（停用） | `mcpctl.sh check` 通过；`mcpctl.sh list` 含 `gitnexus-mcp` |
| S5 | 启用验证 + 量化 | 结论三选一 | 三个图问题答得上；记录工具数与 token 增量；恢复停用 |
| S6 | MySQL 只读 | 账号 + `~/.my.cnf` | `mysql --defaults-file=... -e 'SHOW DATABASES;'` 成功；写操作被拒 |

## S2 安装

```bash
npm i -g gitnexus
gitnexus --version
gitnexus doctor
```

- 只装全局包，不在工作区仓库产生 `node_modules` / `package.json`；License 为 PolyForm NC，仅个人非商用。

## S3 单仓索引

```bash
cd /home/zh/www/dsh-context-guard   # 仓库已从 personalCloud/task/ 拆出（personalCloud a15cf6b）
gitnexus analyze --index-only
gitnexus status
gitnexus list
git status --short
du -sh .gitnexus                    # 索引落在仓内 .gitnexus/，工具自动写入 .git/info/exclude
```

- `--index-only` 跳过 `AGENTS.md`/`CLAUDE.md` 写入与 skills/hooks 安装；本工作区 `AGENTS.md` 是治理入口，禁止被工具改写。
- gitnexus 以 **git 根**为索引单位：传子目录会索引整个仓。`dsh-context-guard` 真实仓库在 `/home/zh/www/dsh-context-guard`（`PROJECT_INDEX.md`、`repos.yaml` 均已登记）；`personalCloud/task/dsh-context-guard` 是拆分后残留的空目录，误跑会索引整个 `personalCloud`（909 文件），需 `gitnexus clean --force` 回收。
- 记录首次耗时、索引体积、语言支持与证据缺口（写进 S5 报告）；`git status --short` 非空 → `gitnexus clean` 排查，确需固定忽略规则再用仓内 `.gitnexusrc` 并随仓提交。

## S4 注册 MCP（默认停用）

`~/.dsh/cordis.patch.yml` 的 `- insert:` 列表末尾追加：

```yaml
    - id: gitnexus-mcp
      disabled: true
      name: "@deepseek-ai/dsh-mcp-client"
      config:
        serverName: gitnexus
        transport: stdio
        command: /home/zh/opt/node24/bin/node
        args:
          - /home/zh/.npm-global/lib/node_modules/gitnexus/dist/cli/index.js
          - mcp
        cwd: /home/zh/www
        env:
          HOME: /home/zh
          GITNEXUS_HOME: /home/zh/.gitnexus
          GITNEXUS_MCP_DEFAULT_MAX_TOKENS: "2000"
        toolCallTimeoutMs: 120000
```

```bash
bash personalCloud/task/mcp-control/mcpctl.sh check
systemctl --user restart dsh-web
```

- 写配置前先备份，便于回滚；条目保持 `disabled: true`，与 mcp-control 约定一致。

## S5 启用验证与量化

1. mcpctl 或 GUI 打开 `gitnexus-mcp`，新开临时会话（不拿交付会话试），问三类只有图能答的问题：谁调用某函数、改某模块影响哪些入口、两符号间路径；验完归档会话、不留后台进程。
2. 量化：工具数（实测 17）；开 MCP 前后各开一个**新会话**、发同一条消息，对比首个请求的 usage：
   `jq '.record.rows.tokenMeasurement.val.anchor.usage' ~/.dsh/storages/session_projcache/sessions/<id>.json`
   （无 `jq` 用 `python3 -c` 读同字段；`inputTokens + cacheReadTokens` 即 prompt 大小），再看回答是否优于 grep / `workdir-rag`。
3. 结论三选一：常开 / 默认停 / 移除；写回 `mcp-control` 后恢复 `disabled: true`（除非选常开）。

## 实施结果（2026-11-21）

| 步骤 | 结果 |
|---|---|
| S2 | `gitnexus@1.6.12` 装到 `/home/zh/.npm-global`；`doctor` 无致命项；FTS/VECTOR 扩展离线不可用（`GITNEXUS_LBUG_EXTENSION_INSTALL=auto` 可补），不影响图查询 |
| S3 | `dsh-context-guard`：38 文件 / 1,126 节点 / 2,837 边 / 40 聚类 / 76 流程；首次 8.9s；索引 44 MB；`git status --short` 为空 |
| S4 | `gitnexus-mcp` 已注册并 `disabled: true`；`dsh-config-check.py --deep` 通过（6 条既有 profile patch 告警与本次无关）；`mcpctl check` 因既有 `!!js` 标签报错，属旧问题 |
| S5 | 17 个工具、schema 约 71 KB；新会话首个请求 15,523 → 32,335 tokens（+16.8k）；三类图问题答得上（impact/trace 带 uid、confidence、process）；结论**默认停** |
| S6 | 用户已建 `dsh_ro@127.0.0.1`（`SELECT, SHOW VIEW`）与 `~/.my.cnf`（600）；实测可列 7 个库、样例查询 61 表；`CREATE TEMPORARY TABLE` 报 `1044 Access denied`，只读成立。授权范围是 `*.*`，比计划建议的按库更宽（详见 S6 说明） |

S5 对比（同一问题、`dsh --profile headless`，无 MCP vs 临时 overlay 启用）：

- 简单查调用点：两者都能答对；MCP 组首个请求 +16.8k tokens，最终 prompt 累计 48k → 98k，无收益。
- 影响面 + 调用路径：MCP 组 21 次图查询、prompt 累计 475k；grep 组 11 次工具、303k。MCP 给出 `epistemic: exact`、uid、`no_path` 与流程归属，grep 需读源码自行拼推理。
- 因此按构型问题按需开启；日常保持停用。

## S6 MySQL 只读（已由用户在宿主终端执行，2026-11-21）

实际执行结果：

```bash
# 账号：dsh_ro@127.0.0.1，GRANT SELECT, SHOW VIEW ON *.*
# 凭据：~/.my.cnf（600），不提交、不进文档
mysql --defaults-file=$HOME/.my.cnf -e "SHOW DATABASES;"          # 7 个库
mysql --defaults-file=$HOME/.my.cnf -e "SELECT COUNT(*) FROM information_schema.TABLES;"  # 61 表
mysql --defaults-file=$HOME/.my.cnf <db> -e "CREATE TEMPORARY TABLE _p(i int);"  # 1044 拒绝
```

- 只读已成立：账号仅有 `SELECT, SHOW VIEW`，DDL/DML 全部报 `1044`。
- **授权范围偏大**：计划原意是按库授权，实际给了 `*.*`。副作用是 `dsh_ro` 能读 `mysql.user`（含口令哈希）与所有业务库。建议收敛（需要时执行）：

  ```sql
  REVOKE SELECT, SHOW VIEW ON *.* FROM 'dsh_ro'@'127.0.0.1';
  GRANT SELECT, SHOW VIEW ON `discovery`.* TO 'dsh_ro'@'127.0.0.1';
  GRANT SELECT, SHOW VIEW ON `gf_scaffold`.* TO 'dsh_ro'@'127.0.0.1';
  GRANT SELECT, SHOW VIEW ON `supercreater`.* TO 'dsh_ro'@'127.0.0.1';
  FLUSH PRIVILEGES;
  ```

- `SHOW GRANTS` 里还有一条 `ON \`<db>\`.*`，是模板占位符残留（库名就叫 `<db>` 时才生效），收敛时可一并 `REVOKE ... ON \`<db>\`.*`。
- 容器内库（如 `romm-db`）走 `docker exec -i romm-db mariadb ...`，不额外开端口。
- 结论：不装 `mysql-mcp-server`，用 `mysql` 客户端 + `~/.my.cnf` 直连。

## S7 收尾

- `./scripts/check.sh --repo doc`、`--repo personalCloud`。
- `doc`、`personalCloud` 分别提交推送，报提交号。
- 停掉 gitnexus MCP，报告索引体积与 token 变化；不留后台进程。

## 风险与边界

| 风险 | 处理 |
|---|---|
| gitnexus 改写 `AGENTS.md`/hooks | 只用 `--index-only`；以 `git status --short` 为空作为门禁 |
| MCP 常驻 token 税 | 默认 `disabled: true`；临时开启并设 `GITNEXUS_MCP_DEFAULT_MAX_TOKENS` |
| 许可限制 | PolyForm NC，仅个人非商用；商用前重评 |
| 索引体积/耗时 | 单仓起步，记录 `du -sh <repo>/.gitnexus`；再决定是否扩仓 |
| DB 凭据泄露 | 只读账号 + `~/.my.cnf` 600；不写文档、不进 git |
| root 操作 | 建账号命令交用户在宿主终端执行 |

## 总验收

- 两仓 `check.sh` 通过；提交只含本任务文件。
- `gitnexus list` 可见目标仓；目标仓工作树干净。
- `mcpctl.sh list` 中 `gitnexus-mcp` 存在且默认停用。
- MySQL 只读账号可查、写被拒；`~/.my.cnf` 权限 600。
- 试点结论已写回 `mcp-control`。

## 回滚

```bash
cp -a ~/.dsh/cordis.patch.yml.bak.<时间戳> ~/.dsh/cordis.patch.yml
systemctl --user restart dsh-web
cd /home/zh/www/dsh-context-guard && gitnexus clean --force   # 索引在仓内 .gitnexus/
npm rm -g gitnexus
rm -rf /home/zh/.gitnexus                                      # 仅注册表
git -C /home/zh/www/doc revert <commit>
git -C /home/zh/www/personalCloud revert <commit>
```

MySQL 回滚：`sudo mysql -e "DROP USER 'dsh_ro'@'127.0.0.1';"`，删除 `~/.my.cnf`。

## 开放项（后续可能扩展，本次不做）

- gitnexus 扩到多仓 / `group_sync`，或改 `--http` 给 subagent 共享。
- 是否把 MySQL 查询沉淀成脚本或 skill。
- ZipVoice 本地 TTS 的独立方案（无 GPU，需评估 CPU/ONNX 延迟）。

## 篇幅说明

- 原因：本计划留作交接证据，需保留可复制命令与实测数据。必须保留：S2–S6 命令块、实施结果表、回滚命令；可压缩位置：S4 YAML 详情、S5 对比段落。
- 上限按 400 行执行。

## 改动记录

- 2026-11-21 05:25 初稿：8 项评估结论、gitnexus 试点、MySQL 只读替代。
- 2026-11-21 06:10 按确认补全 S1–S6：步骤产出/验收表、量化方法、风险表、开放项；明确本次全部实施、当前不开工。
- 2026-11-21 06:30 更正量化来源：本机已无 `headroom-proxy`（单元/二进制均不存在、`dsh-web` 直连），改用 DSH 会话缓存 usage；同步清理 `mcp-control`、`services.conf` 的过期描述。
- 2026-11-21 11:41 实施 S2–S5：实测 gitnexus 索引与 MCP 量化，补「实施结果」；S3 目标仓更正为已拆出的 `/home/zh/www/dsh-context-guard`，S6 待用户执行。
- 2026-11-21 12:45 更正回滚段残留的旧路径（改为 `/home/zh/www/dsh-context-guard`），澄清索引在仓内 `.gitnexus/`、`~/.gitnexus` 仅注册表。
- 2026-11-21 14:05 S6 完成：`dsh_ro` 只读验证通过（DDL 报 1044），记录 `*.*` 授权偏宽与收敛建议；S1–S7 全部收尾，状态改 `done`。
