---
audience: shared
status: current
---

# DSH 插件与工具索引

> 用途：集中登记本工作区产出的 **DSH 插件、MCP 工具、运行时服务与专项工具**，避免散落在各 `task/` 目录。
> 规则：新增/改名/发布/废弃 DSH 相关产物时，必须同步本文件与 `PROJECT_INDEX.md`。
> 最后核对：2026-11-17（`dsh-context-guard@0.4.1` 已加入单轮调用/输出门禁、硬上限自动继续、命令形态默认 deny 拦截与系统提示；DSH 插件 README 中英双语）

## 1. 清单

### 1.1 DSH Bundle 插件

| 插件 | 类型 | 本机目录 | 状态 | 发布入口 |
|---|---|---|---|---|
| `dsh-workbench`（交付台） | Host + Client UI bundle | [`task/dsh-workbench/`](../../personalCloud/task/dsh-workbench/README.md) | 开发/切换中；npm `dsh-workbench@0.2.x` | GitHub `person-clouds/dsh-workbench`；见 [PUBLISHING](../../personalCloud/task/dsh-workbench/PUBLISHING.md) |
| `dsh-context-guard`（原名 `dsh-compaction-archive`） | Host bundle + Web client | [`task/dsh-context-guard/`](../../personalCloud/task/dsh-context-guard/README.md) | 代码完成（风险 `ask`、单轮调用/输出门禁、硬上限自动继续、命令形态 deny/ask 与系统提示）；npm 目标版本 `@fenghoer/dsh-context-guard@0.4.1`；中文 README + 英文 `README.en.md`；待宿主机安装、迁移 profile 与 Web 实机验收 | [STATUS](../../personalCloud/task/dsh-context-guard/STATUS.md) / [PLAN](../../personalCloud/task/dsh-context-guard/PLAN.md) / [PUBLISHING](../../personalCloud/task/dsh-context-guard/PUBLISHING.md) / market PR #15266 |
| `dsh-workflow-shortcuts` | Client UI bundle（Host 空插件） | [`task/dsh-workflow-shortcuts/`](../../personalCloud/task/dsh-workflow-shortcuts/README.md) | 本地测试 3/3 通过；npm `dsh-workflow-shortcuts@0.1.0` 与 GitHub Release `v0.1.0` 已发布；待宿主机安装验收 | [PUBLISHING](../../personalCloud/task/dsh-workflow-shortcuts/PUBLISHING.md)；awesome-dsh-plugin PR #15389 |

### 1.2 DSH MCP 工具

| 工具 | 作用 | 本机位置/入口 | 状态 |
|---|---|---|---|
| `workdir-rag` / `dsh-rag` | 工作目录 RAG：索引、语义检索、状态 | 二进制 `~/.local/bin/dsh-rag`；DSH MCP `workdirrag` | 已接入 `~/.dsh/cordis.patch.yml` |
| `dsh-image` | 本地图片 OCR/元信息 MCP，容器无网络 | [`task/dsh-image/`](../../personalCloud/task/dsh-image/dsh-mcp-overlay.yml) | 按需启用 |
| `rea` | 小红书/抖音 APK 静态分析 MCP | [`task/rea-tool/`](../../personalCloud/task/rea-tool/README.md) | 按需启用 |
| `headroom` | 上下文压缩 MCP（旧方案） | `~/.local/bin/headroom mcp serve` | 默认禁用，仅考古 |
| MCP 管控 | 按需启停 MCP，避免工具 schema 常驻吃 token | [`task/mcp-control/`](../../personalCloud/task/mcp-control/README.md) | 工具可用 |

### 1.3 DSH 运行时服务与专项工具

| 产物 | 作用 | 位置 | 状态 |
|---|---|---|---|
| `dsh-web` | DSH Web 主服务 | `~/.config/systemd/user/dsh-web.service` | 运行中，127.0.0.1:3080 |
| `dsh-superagent` | DSH profile `web` 内的插件（宿主 `dsh-web`），GitHub/飞书机器人 | [`task/superagent-prototype/`](../../personalCloud/task/superagent-prototype/README.md) | 运行中，无独立端口（走 3080 / tailnet 8443） |
| `dsh-ml` | Python ML 运行时（embedding/PDF/OCR） | `~/.config/systemd/user/dsh-ml.service` | 运行中，127.0.0.1:8765 |
| `dsh-token-control` | 修 DSH/superagent 压缩阈值与预算 | [`task/dsh-token-control/`](../../personalCloud/task/dsh-token-control/README.md) | 已应用 |
| `dsh-health-check` | DSH 卡顿/上游延迟专项自检 | [`task/dsh-health-check/`](../../personalCloud/task/dsh-health-check/README.md) | 只读工具 |
| `superagent-console` | superagent 交付物只读网页工作台 | [`task/superagent-console/`](../../personalCloud/task/superagent-console/README.md) | 已退役（2026-11-15 停用；功能并入 dsh-workbench） |

## 2. 插件目录规范

后续新插件统一放 `task/dsh-<name>/`，最低结构：

```text
task/dsh-<name>/
├── package.json          # name=dsh-<name>，声明 dsh.bundle.patch；客户端插件再加 dsh.client
├── cordis.patch.yml      # 只负责 insert 自己的插件行
├── index.js              # Host 端；ESM
├── client.js             # 仅浏览器端插件；普通脚本，禁止顶层 import/export
├── README.md             # 功能 / 配置 / 安装 / 安全边界 / 限制
├── PUBLISHING.md         # GitHub、npm、DSH 市场投稿步骤
├── STATUS.md             # 当前状态、验证记录、待办
├── LICENSE
├── market/<owner>__<repo>.yml
└── test.mjs              # 无外部依赖或明确 npm test
```

硬性要求：

1. `package.json` 必须有 `dsh.bundle.patch`，市场才能识别为 bundle；
2. 客户端插件必须有 `dsh.client`，`client.js` 必须能被普通脚本加载：
   `node -e "new (require('vm').Script)(require('fs').readFileSync('client.js','utf8'))"`；
3. 默认路径不能写死本机个人目录；必须可由配置或 `DSH_HOME` 覆盖；
4. 不注册独立公网端口；优先复用 DSH 的 Web 服务、鉴权与 Host/Origin 校验；
5. 只读优先。需要写文件时限定到明确的 `DSH_HOME` 子目录，并说明失败不影响主流程；
6. 发布前必须跑 `npm pack --dry-run` / `npm test`，并更新本文件与 `PROJECT_INDEX.md`。

## 3. DSH 插件发布基线

与 `dsh-workbench` 保持一致：

1. `npm pack` 生成 `.tgz`，可上传 GitHub Release；
2. `npm publish --access public`；
3. GitHub 仓库加 topic `dsh-plugin`；
4. 仓库创建满 1 天后，向 `awesome-dsh-plugin` 提交 `data/plugins/<owner>__<repo>.yml`；
5. 条目写 `url`、`name`、`category`、中英 `description`，如有 tarball 写 `tarball`。

市场条目模板：

```yaml
url: https://github.com/<owner>/<repo>
name: <owner>/<repo>
category: workflow
description:
  en: '...'
  zh: '...'
tarball: https://github.com/<owner>/<repo>/releases/latest/download/<pkg>.tgz
```

## 4. 相关文档

- DSH 部署与运维：[`ubuntuInit/docs/dsh.md`](../../personalCloud/ubuntuInit/docs/dsh.md)
- 上下文压缩依据与调参：[`reference/dsh-context-compaction.md`](dsh-context-compaction.md)
- MCP 吃 token 的管控：[`task/mcp-control/README.md`](../../personalCloud/task/mcp-control/README.md)
- 交付台发布记录：[`task/dsh-workbench/PUBLISHING.md`](../../personalCloud/task/dsh-workbench/PUBLISHING.md)
- 上下文守卫方案与发布：[`task/dsh-context-guard/PLAN.md`](../../personalCloud/task/dsh-context-guard/PLAN.md)、[`PUBLISHING.md`](../../personalCloud/task/dsh-context-guard/PUBLISHING.md)
