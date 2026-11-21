---
implementation_status: not_started
created_at: 2026-11-21 19:05:00
updated_at: 2026-11-21 19:05:00
---

# PLAN：5 个新仓转公开的安全关与执行

## 背景

SA 迁移把 5 个项目拆成 `person-clouds` 组织下的私有仓（2026-11-21 完成，见
[归档计划](/home/zh/www/doc/archive/plans/PLAN-sa-project-migration.md)）。原计划第 9 步：
“逐仓过安全关后转 public，并留台账”。本计划就是那道安全关，执行顺序为
`workdir-rag` → `dsh-local-vision` → `free-ai-router` → `dsh-immersive-glass` → `dsh-py-runtime`。

## 目标

- 5 个仓逐个满足公开条件：无凭据、无个人信息、无客户/内部数据、无本机路径与环境指纹。
- 每仓转公开前后各做一次复核，结论写进台账；任一仓不过关就停在私有，不整批转。
- 转公开用 `super-YF`（`gh-agent`，org owner）；代码提交仍用 `zhyfor` 身份。

## 非目标

- 不改代码功能、不重构、不补文档体系；只做公开所需的最小修补（如清绝对路径、补 LICENSE）。
- 不改 `repos.yaml` 里 5 仓的 `remote`/分支；转公开后只把 `protection`/`role` 等事实同步。
- 不处理 `dshSuperagentRepo`、`personalCloud` 等既有私有仓的可见性。

## 基线（2026-11-21 复核，仓库 HEAD）

| 仓 | 提交者邮箱（全历史） | 密钥/敏感文件 | `/home/zh` | 内网 IP/TS 域名 | 图片 EXIF | `.git` |
|---|---|---|---|---|---|---|
| `workdir-rag` | zhyfor + super-YF | 0 | 0 | 0 | 1 张，无 | 700K |
| `dsh-local-vision` | zhyfor + super-YF + `noreply@github.com` | 0 | 0 | 0 | 12 张，无 | 2.0M |
| `free-ai-router` | zhyfor + super-YF | 0 | 0 | 0 | 6 张，无 | 3.7M |
| `dsh-immersive-glass` | zhyfor | 0 | 0（本次已清） | 0 | 0 | 516K |
| `dsh-py-runtime` | zhyfor + super-YF | 0 | 0 | 0 | 0 | 800K |

扫描口径（对 `--all` 全历史，不只工作树）：

```bash
cd /home/zh/www/<repo>
git log --all --format='%ae|%ce' | tr '|' '\n' | sort -u          # 邮箱
git log --all -p --format= | grep -cE 'ghp_|gho_|github_pat_|sk-[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|xox[baprs]-|AIza[0-9A-Za-z_-]{30}'
git log --all --name-only --pretty=format: | sort -u | grep -E '\.(env|pem|key|p12|sqlite|db|csv|docx|xlsx|pdf|kdbx)$'
git grep -nE '/home/zh|100\.[0-9]+\.[0-9]+\.[0-9]+|[0-9]+\.ts\.net|192\.168\.' HEAD
git ls-files | grep -E '\.(png|jpg|jpeg|webp|gif)$' | while read f; do exiftool -q -GPS:all -Artist -Creator -Model "$f"; done
```

## 每仓门禁清单（全部满足才可转公开）

1. **凭据**：上表密钥扫描 0 命中；`git log --all -p` 里无 token、私钥、连接串。
2. **邮箱**：只有 `zhyfor@users.noreply.github.com`、`super-YF` 的 noreply、`noreply@github.com`；
   出现 `fenghoer@163.com` 或真实邮箱即阻断，先重写历史再谈公开。
3. **个人信息**：无手机号、身份证、真实姓名以外的联系方式；图片无 EXIF GPS/机型；截图不含
   聊天记录、内网地址、客户名。
4. **内部数据**：无公司/客户文档、无内部流程截图、无未公开的账号与地址。
5. **本机路径与指纹**：工作树与历史 `git grep '/home/zh'` 为 0；机器规格已改通用描述
   （`dsh-local-vision` 的实测数字必须标“本机实测参考”）。
6. **测试**：`./scripts/check.sh --repo <name>` PASS，且该仓验证命令通过（见下表）。
7. **仓设置**：无 Actions secrets、无 deploy key、无 webhook 指向内网；`forkCount` 为 0。
8. **许可证**：公开仓应有 `LICENSE`（当前 5 仓都没有）。转公开前定一个统一许可证
   （建议 MIT，与既有 dsh 插件仓一致）并加进每仓，或明确决定“暂不加”并写进台账。

各仓验证命令：

| 仓 | 验证 |
|---|---|
| `workdir-rag` | `./scripts/check.sh --repo workdir-rag`；`go test ./...` |
| `dsh-local-vision` | `./scripts/check.sh --repo dsh-local-vision`；`python -m unittest discover -s tests -t .` |
| `free-ai-router` | `./scripts/check.sh --repo free-ai-router`；`./scripts/check.sh`（仓内自检） |
| `dsh-immersive-glass` | `./scripts/check.sh --repo dsh-immersive-glass`；`node --check client.js`；`node scripts/test-dsh-conversation-layout.mjs` |
| `dsh-py-runtime` | `./scripts/check.sh --repo dsh-py-runtime`；`./scripts/check.sh`（仓内自检） |

## 执行步骤（逐仓，不批量）

```bash
cd /home/zh/www
# 1) 复核（跑上面的扫描口径，结论写台账）
# 2) 跑门禁命令（check.sh + 该仓测试）
# 3) 确认工作树干净、HEAD 已推送
git -C <repo> status --short && git -C <repo> log --oneline -1
# 4) 转公开（需要 --accept-visibility-change-consequences）
gh-agent repo edit person-clouds/<repo> --visibility public --accept-visibility-change-consequences
# 5) 复核结果：匿名访问 README 与 clone
gh-agent repo view person-clouds/<repo> --json visibility,isPrivate,forkCount
# 6) 台账记一行（时间、仓、HEAD、扫描结论、执行人、是否加 LICENSE）
```

转公开后必须复验：未登录状态能打开仓首页、`git clone` 能从零拉下、README 渲染无断链。

## 台账

优先 `zhyfor/dshSuperagentRepo/issues`（按 AGENTS.md 的任务台账约定）。但 `gh` 当前未登录
zhyfor，只有 `gh-agent`（super-YF，无该仓 Issue 写权限），所以在 zhyfor 登录前先记在
[`dshSuperagentRepo/doc/visibility-ledger.md`](/home/zh/www/dshSuperagentRepo/doc/visibility-ledger.md)，
等凭据可用后补一条汇总 Issue 并把链接回填。

台账每行固定字段：时间 / 仓 / HEAD / 扫描结论（邮箱、凭据、路径、个人信息）/ 门禁命令结果 /
LICENSE 决定 / 执行账号 / 公开后复验结果。

## 回滚

- 转公开是单向可见性变更：GitHub 允许 public→private，但已被抓取/镜像的内容无法收回。
  因此只在前 8 条门禁全过且人工确认后执行，一仓一确认。
- 若要撤销：`gh-agent repo edit person-clouds/<repo> --visibility private --accept-visibility-change-consequences`；
  历史一旦公开，按“已泄露”处理并检查是否需轮换任何曾出现过的凭据（本次扫描结论为 0 命中）。
- 台账保留撤销记录与原因，不删行。

## 待定（执行前需用户拍板）

1. 许可证：5 仓统一加 MIT，还是不加？加则每仓一个 `LICENSE` 提交。
2. 转公开顺序是否按本计划顺序逐个来（推荐），还是一次性全转。
3. 公开后是否把 5 仓加进 `repos.yaml` 的 `protection`/`platform` 字段变更记录（只登记事实，不改远程）。

## 改动记录

- 2026-11-21 19:05 初稿：基线扫描（邮箱/凭据/敏感文件/路径/EXIF/仓大小）与门禁清单；
  确认 5 仓均无 CI secrets、无 Actions 工作流；`dsh-immersive-glass` 的
  `scripts/test-dsh-conversation-layout.mjs` 硬编码 `/home/zh/...` 已改为 `os.homedir()`。
