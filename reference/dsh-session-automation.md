---
audience: shared
status: current
---

# 用 DSH 本地 API 创建实施会话

本机 DSH Web 监听 `127.0.0.1:3080` 时，可以直接用它的本地 API 创建可见、已挂到工作区的实施会话，不需要手工点 UI。

## 1. 取启动 token 并换 cookie

启动 token 是 DSH 进程凭据，只用于本机换取短期 cookie，**不要写进文档、脚本参数或提交历史**。

```bash
# 正常用户会话：
TOKEN=$(journalctl --user -u dsh-web -o cat | grep '^dsh web:' | tail -1 | sed 's/.*token=//')
# 没有用户总线（bwrap/沙箱）时，直接读 user journal 文件：
# TOKEN=$(journalctl --file /var/log/journal/<machine-id>/user-1000.journal -o cat \
#   | grep '^dsh web:' | tail -1 | sed 's/.*token=//')

mkdir -p "$HOME/.cache"
C="$HOME/.cache/dsh-cookie.txt"
curl -sS -c "$C" -o /dev/null "http://127.0.0.1:3080/?token=$TOKEN"
```

## 2. 必须用 workspaceId，不能用 cwd

`session/create` 的两种定位方式语义不同：

| 参数 | 结果 |
|---|---|
| `workspaceId` | 创建后自动挂到该工作区，侧栏可见 |
| `cwd` | 只设置会话工作目录，**不挂工作区，侧栏看不到** |

工作区 ID 从 `~/.dsh/storages/workspace.json` 的 `tables.workspaces` 中按 `path` 精确匹配取得。API 请求统一为 `POST /api/<endpoint>`，请求体是 `{"type":"client-request","rpcId":"...","method":"<endpoint>","payload":{"args":{...}}}`。

```bash
API=http://127.0.0.1:3080/api
WID=<workspace.json 中匹配目标目录的 workspaceId>

# 1. 创建并存进侧栏
SID=$(curl -sS -b "$C" -H 'Content-Type: application/json' \
  -X POST "$API/session/create" \
  --data "{\"type\":\"client-request\",\"rpcId\":\"create\",\"method\":\"session/create\",\"payload\":{\"args\":{\"request\":{\"workspaceId\":\"$WID\",\"agentPreset\":\"minimal\"}}}}" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["value"]["sessionId"])')

# 2. 命名（可选）
curl -sS -b "$C" -H 'Content-Type: application/json' \
  -X POST "$API/session/rename" \
  --data "{\"type\":\"client-request\",\"rpcId\":\"rename\",\"method\":\"session/rename\",\"payload\":{\"args\":{\"request\":{\"sessionId\":\"$SID\",\"title\":\"[实施] <任务名>\"}}}}"

# 3. 投递任务；requestId 客户端生成，mode 用 queue
curl -sS -b "$C" -H 'Content-Type: application/json' \
  -X POST "$API/session/prompt" \
  --data "{\"type\":\"client-request\",\"rpcId\":\"prompt\",\"method\":\"session/prompt\",\"payload\":{\"args\":{\"request\":{\"requestId\":\"req-$SID\",\"sessionId\":\"$SID\",\"mode\":\"queue\",\"content\":[{\"type\":\"text\",\"text\":\"按 <计划文档路径> 实施。先读计划与 AGENTS.md，按文档执行；需要改已确认决策时先停下来问。\"}]}}}}"

rm -f "$C"
```

## 3. 自检

- `session/list` 能查到 `SID`，且 `cwd` 为目标目录；
- UI 对应工作区侧栏能看到新会话；
- 会话标题不是空白，状态为运行中或已接受任务。

## 4. 常见坑

| 坑 | 现象 | 处理 |
|---|---|---|
| 只传 `cwd` | 会话已创建、能运行，但侧栏看不到 | 用 `workspaceId` 重建；旧会话可 `workspace/archiveSession` 加 `stopActivity:true` 归档 |
| cookie 文件被清理 | API 返回 `401 unauthorized` | 重新用启动 token 换 cookie |
| token 来自旧进程 | `401` | 取 journal 中最新一条 `dsh web:` |
| 请求体少 `args` 层 | `Remote payload must contain exactly one plain-object args field` | 包成 `payload.args.request` |

## 5. 修改 DSH 设置并验证

DSH 的 settings 由 `settingsController` 管理，写入会落到当前 profile 的 Cordis patch。不要在 `workspace-write` 会话里直接改 `~/.dsh`（会被沙箱判为只读），也不要把仓库复制到 `/tmp`。

```bash
# 先看所有 namespace（settings/describe 没有 ns 参数）
curl -sS -b "$C" -H 'Content-Type: application/json' \
  -X POST "$API/settings/describe" \
  --data '{"type":"client-request","rpcId":"desc","method":"settings/describe","payload":{"args":{}}}'

# 合并写入一个 namespace 的 user section
curl -sS -b "$C" -H 'Content-Type: application/json' \
  -X POST "$API/settings/update" \
  --data '{"type":"client-request","rpcId":"upd","method":"settings/update","payload":{"args":{"ns":"bash-sandbox","patch":{"timeoutMs":60000}}}}'
```

验证配置改动不要拿交付会话反复试：新建一个临时会话（`workspaceId` 必填），直接读会话日志前几条事件，再归档。

```bash
D="$HOME/.dsh/sessions/<workspace-encoded>/<session-id>"
zstd -dc "$D/session.v4.jsonl.zstd" | grep -E 'permission/preset|sandbox/mode|approval/policy' | head -5
```

确认事件符合预期后调用 `workspace/archiveSession`（`stopActivity: true`）归档验证会话。
