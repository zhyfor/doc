---
audience: human
status: current
implementation_status: not_started
---
# PLAN: 文档受众分层试点（dshSuperagentRepo）
- 日期：2026-11-17
- 范围：根公共脚本 + `dshSuperagentRepo`；其他仓库只保留接入能力，不做迁移

## 目标

- 活跃 Markdown 用 frontmatter 标明 `audience: ai|shared|human`、`status: current|draft|archived`。
- AI 默认只读 `ai` + 目标仓 `shared`；`human` 仅在用户要求或接手时读。
- 根 `/home/zh/www/scripts/check.sh` 统一调度；每个仓自己维护 `docs-policy.json`。
- 分类和本地链接由脚本检查，文章内容不要求人工逐篇预读。

## 范围

纳入：

- 公共脚本：`personalCloud/workspace/scripts/check.sh`、`check_docs.py`（根 `scripts/` 是符号链接）。
- `dshSuperagentRepo/docs-policy.json` 及该仓 64 个 tracked Markdown（`workdir-rag/testdata/**` 的 5 个测试语料豁免）。
- `dshSuperagentRepo/AGENTS.md`、`PROJECT_INDEX.md` 的阅读路由；`doc/work` 模板与生成脚本。

不纳入：

- 其他仓库的文档迁移；只支持后续加 `docs-policy.json` 接入。
- 正文重写、目录大搬迁、历史文档内容审校。

## 路径与命令约定

- 每仓根目录：`docs-policy.json`。
- 公共入口：`/home/zh/www/scripts/check.sh`。
- 命令：

```bash
./scripts/check.sh --all                         # 所有登记仓，默认只检查
./scripts/check.sh --repo dshSuperagentRepo      # 单仓检查
./scripts/check.sh --repo dshSuperagentRepo --tag  # 按 policy 补/改 frontmatter
./scripts/check.sh --all --strict                # 缺 policy 或检查失败返回非 0
```

- 默认 `--all` 跳过无 policy 的仓并告警；显式 `--repo` 缺 policy 直接失败。
- `repos.yaml` 是仓库清单唯一来源；`--repo` 参数取其中的 `id`。

## 改动位置

- `personalCloud/workspace/scripts/check.sh`：参数解析、仓遍历、汇总、退出码。
- `personalCloud/workspace/scripts/check_docs.py`：frontmatter 校验/写入、链接检查、policy 匹配。
- `dshSuperagentRepo/docs-policy.json`：路径规则、排除项、必读约束。
- `dshSuperagentRepo/AGENTS.md`：AI 默认阅读规则与路由。
- `dshSuperagentRepo/PROJECT_INDEX.md`：区分 AI 入口与人类文档入口。
- `dshSuperagentRepo/scripts/new-work-record.sh`、`doc/work/TEMPLATE.md`：新文档带 frontmatter。

## 实施步骤

1. 写 `check_docs.py`：`git ls-files '*.md'` 取文档，解析/写入 YAML 头，检查枚举、必读约束、相对链接；支持 `--check`、`--tag`。
2. 写 `check.sh`：从 `repos.yaml` 取仓，按 `--all/--repo` 调度，输出每仓 PASS/FAIL/SKIP 和总退出码。
3. 写 `dshSuperagentRepo/docs-policy.json`：按路径给 59 个有效文档打标；测试语料排除。
4. 执行 `--tag` 后 `git diff --stat` 核对只改 Markdown 头部，不碰正文。
5. 更新 `AGENTS.md`、`PROJECT_INDEX.md`、工单模板和生成脚本。
6. 运行验收命令；`dshSuperagentRepo` 单独提交推送，公共脚本随 `personalCloud` 提交推送。

## 验收

```bash
cd /home/zh/www
./scripts/check.sh --repo dshSuperagentRepo
./scripts/check.sh --all
cd dshSuperagentRepo && ./scripts/check.sh && git diff --check
```

- `dshSuperagentRepo` 所有有效 Markdown 有合法 frontmatter，测试语料未改。
- `AGENTS.md` 为 `ai`，`STATUS.md` 为 `shared`，`doc/work/*` 与 `doc/PLAN-*` 为 `human`。
- `AGENTS.md` 必读链接不指向 `human` 文档；本地链接全部有效。
- 缺标签、非法枚举、断链时公共脚本返回非 0；补标签后通过。
- `--all` 对无 policy 仓告警跳过，`--strict` 下失败。

## 回滚

- 各仓 `git revert <提交号>`：移除 policy/frontmatter 和入口改动。
- 公共脚本回滚 `personalCloud` 对应提交；其他仓未接入，不受影响。
