---
implementation_status: not_started
created_at: 2026-11-21 05:25:00
updated_at: 2026-11-21 05:25:00
---

# PLAN：DSH MCP 工具采纳评估与 gitnexus 试点

## 目标

1. 把 8 个候选 MCP 工具的结论落到文档，避免以后重复评估。
2. 只试点 `gitnexus`：单仓、`--index-only`、默认停用，验证「代码图」相对 `workdir-rag` + grep 的增量。
3. MySQL 不装 MCP，改用 bash + 只读账号。
4. `ZipVoice` 不是 MCP，本次不处理。

## 范围

- 做：本计划、`personalCloud/task/mcp-control/README.md` 登记表、`~/.dsh/cordis.patch.yml` 新增 `gitnexus-mcp` 条目（`disabled: true`），以及 gitnexus 单仓试点验证。
- 不做：不改 DSH 源码；不装其余候选；不动 `context7` / `playwright` / `workdir-rag` 现状；不建 ZipVoice 环境；不索引整个 `/home/zh/www`。

## 现状（2026-11-21 实测）

- DSH MCP 客户端 `@deepseek-ai/dsh-mcp-client`：stdio，工具名 `mcp__<server>__<tool>`，**启动即全量注册**，schema 每请求重发 → 常驻 token 税（见 [mcp-control](/home/zh/www/personalCloud/task/mcp-control/README.md) 实测：207 工具时单请求 218k→296k）。
- 已启用：`workdir-rag`、`playwright`、`context7`；已停用：`rea`、`headroom`。
- 本机：Node `v24.22.2`（`/home/zh/opt/node24/bin/node`），满足 gitnexus `^22.18 || >=24.11`；Docker 运行中；MySQL 8 监听 `127.0.0.1:3306`；无 NVIDIA GPU；内存 46 GB；`/` 剩余 725 GB。

候选结论（npm 实测版本 / 最后更新）：

| 候选 | 版本与状态 | DSH 现状/替代 | 结论 |
|---|---|---|---|
| `context7-mcp` | 已装 `@upstash/context7-mcp`（npm 上的 `context7-mcp` 是 404） | 唯一外部库文档源 | 保留现状 |
| `gitnexus` | 1.6.12，2026-11-20 | `workdir-rag` 只做文本/向量检索，答不了调用链与影响面 | 单仓试点 |
| `mysql-mcp-server` | 0.1.4，2026-09-22 | bash + `mysql` 客户端；MCP 需把库密码写进配置 | 不装，见 S6 |
| `mcp-server-docker` | 1.0.0，2025-06，MCP SDK 0.6.0 | bash `docker exec` 更灵活；需 docker.sock，无命令过滤 | 不装 |
| `@modelcontextprotocol/server-sequential-thinking` | 2.2.0，2026-11-18 | 推理 + `todo_write` + `goal` 已覆盖；多一次往返且 thought 全文回灌 | 不装 |
| `server-sequential-thinking` | 0.1.1-alpha.2，2025-04 | 第三方旧 fork | 不装 |
| `@modelcontextprotocol/server-memory` | 2.2.1，2026-11-18 | mnemon 已有 runtime memory + 项目 Documents | 不装 |
| `ZipVoice` | k2-fsa 123M TTS 模型，非 MCP | DSH 只有 STT；无 GPU，需独立 Python 环境 | 单独立项 |

## 改动位置

1. `/home/zh/www/doc/plans/PLAN-dsh-mcp-adoption.md`（本文）。
2. `/home/zh/www/personalCloud/task/mcp-control/README.md`：`## 当前登记` 增加 `gitnexus-mcp` 行；新增 `## 已评估未采纳` 表。
3. `/home/zh/.dsh/cordis.patch.yml`：`- insert:` 列表末尾新增 `gitnexus-mcp`（`disabled: true`）。

## 实施步骤

### S1 落文档

改上述两处文档；`mcp-control` 只加表格行与一小节，不复述本计划正文。

### S2 安装

```bash
npm i -g gitnexus
gitnexus --version
gitnexus doctor          # 看原生依赖与平台能力
```

- 只装全局包，不在工作区仓库里加 `node_modules` / `package.json`。
- License 为 PolyForm Noncommercial 1.0.0：仅个人非商用。

### S3 单仓索引（先不接 MCP）

```bash
cd /home/zh/www/personalCloud/task/dsh-context-guard
gitnexus analyze --index-only     # 不写 AGENTS.md/CLAUDE.md、不装 hooks/skills
gitnexus status
gitnexus list
git status --short                # 必须为空
```

- 索引落在 `~/.gitnexus`（`GITNEXUS_HOME` 默认值），记录体积与首次耗时。
- 若 `git status --short` 非空，先 `gitnexus clean` 再查 `analyze` 是否漏写 `--index-only`。

### S4 注册 MCP（默认停用）

在 `~/.dsh/cordis.patch.yml` 的 `- insert:` 列表末尾追加：

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

改完先 `bash personalCloud/task/mcp-control/mcpctl.sh check`，再重启：

```bash
systemctl --user restart dsh-web
```

### S5 启用验证（只开一次，验完就关）

1. 用 mcpctl 或 GUI 打开 `gitnexus-mcp`，新开临时会话。
2. 问三个只有图能答的问题：某函数被谁调用、改某模块影响哪些入口、两个符号间路径。
3. 记：工具数（19）、单请求固定开销增量、回答是否优于 grep/`workdir-rag`。
4. 结论三选一（常开 / 默认停 / 移除），写回 `mcp-control`；不选常开就恢复 `disabled: true`。
5. `gitnexus-mcp` 常开时须配合 `GITNEXUS_MCP_DEFAULT_MAX_TOKENS`，避免大 JSON 回灌。

### S6 MySQL 只读替代（用户在宿主终端执行，计划不写密码）

```bash
# 1) 建只读账号（只给需要查的库，示例库名 <db>）
sudo mysql -e "CREATE USER 'dsh_ro'@'127.0.0.1' IDENTIFIED BY '<强密码>';
GRANT SELECT, SHOW VIEW ON \`<db>\`.* TO 'dsh_ro'@'127.0.0.1';
FLUSH PRIVILEGES;"

# 2) 凭据文件，权限 600
# ~/.my.cnf
# [client]
# host=127.0.0.1
# user=dsh_ro
# password=<强密码>
# default-character-set=utf8mb4
chmod 600 ~/.my.cnf

# 3) 查询（--defaults-file 必须是第一个参数）
mysql --defaults-file=$HOME/.my.cnf -e "SHOW DATABASES;"
mysql --defaults-file=$HOME/.my.cnf <db> -e "SELECT ... LIMIT 20;"
```

- 容器内库（如 `romm-db`）走 `docker exec -i romm-db mariadb ...`，不额外开端口。
- 结论：不装 `mysql-mcp-server`；若以后确有高频查库需求，再按本计划重评。

### S7 收尾

- 跑 `./scripts/check.sh --repo doc`、`./scripts/check.sh --repo personalCloud`。
- `doc`、`personalCloud` 分别提交推送；报提交号。
- 试点结束停掉 gitnexus MCP（`disabled: true`），不留后台进程。

## 验收

- 两个仓 `check.sh` 通过；`git status --short` 只含本任务文件。
- `gitnexus analyze --index-only` 后目标仓工作树干净；`gitnexus list` 能看到该仓。
- MCP 条目在 `mcpctl.sh list` 中可见且默认为停用。
- `mcp-control` 表格与实际配置一致；本文结论表可直接回答「这几个 MCP 要不要装」。

## 回滚

```bash
# 配置
cp -a ~/.dsh/cordis.patch.yml.bak.<时间戳> ~/.dsh/cordis.patch.yml
systemctl --user restart dsh-web

# 索引与包
cd /home/zh/www/personalCloud/task/dsh-context-guard && gitnexus clean
npm rm -g gitnexus
rm -rf /home/zh/.gitnexus

# 文档
git -C /home/zh/www/doc revert <commit>
git -C /home/zh/www/personalCloud revert <commit>
```

## 改动记录

- 2026-11-21 05:25 初稿：完成 8 项评估结论、gitnexus 试点步骤、MySQL 只读替代方案。
