---
implementation_status: done
created_at: 2026-11-20 18:10:00
updated_at: 2026-11-20 18:10:00
---

# PLAN：重新发布两个 DSH 插件到插件市场

## 目标

把 `dsh-context-guard` 0.4.1、`dsh-workflow-shortcuts` 0.2.0 发布到 npm 与 GitHub Release；
市场条目已合并且用 `releases/latest`，Release 更新后市场自动取到新包。

## 范围

- 写：`dsh-context-guard/`、`dsh-workflow-shortcuts/`、本计划文档。
- 发布身份：`zhyfor`（从 git credential 取 PAT 注入 `GH_TOKEN`，不回显）。
- 不改市场条目结构，不新提 awesome-dsh-plugin PR（两仓 PR #15266、#15389 已合并）。

## 关键事实（2026-11-20 核对）

| 项 | context-guard | workflow-shortcuts |
|---|---|---|
| 本地版本 | 0.4.1 | 0.2.0 |
| npm 最新 | 0.3.1 | 0.1.0 |
| 最新 Release | v0.3.1 | v0.1.0 |
| 市场条目 | 已合并，version-less | 已合并，version-less |

- npm 包名：`@fenghoer/dsh-context-guard`、`dsh-workflow-shortcuts`。
- npm token 现状：`npm whoami` 返回 403，发布时可能失败；失败则保留 Release 并报告。
- 打包产物文件名：`fenghoer-dsh-context-guard-0.4.1.tgz`、`dsh-workflow-shortcuts-0.2.0.tgz`；
  上传前改名为无版本号，保持市场链接稳定。

## 实施步骤

1. 预检：两仓 `npm test`、`npm pack --dry-run`；确认工作区干净。
2. 打包到仓外暂存目录 `~/.cache/dsh-plugin-release/`，改名为 `dsh-context-guard.tgz`、`dsh-workflow-shortcuts.tgz`。
3. npm 发布（逐包）：
   ```bash
   npm publish --registry=https://registry.npmjs.org --access public
   ```
   403/OTP 失败即停止 npm 分支，记录原始错误，继续 Release。
4. GitHub Release：
   ```bash
   export GH_TOKEN="$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p')"
   gh release create v0.4.1 ~/.cache/dsh-plugin-release/dsh-context-guard.tgz \
     --repo person-clouds/dsh-context-guard --target main --title v0.4.1 --notes-file <notes>
   gh release create v0.2.0 ~/.cache/dsh-plugin-release/dsh-workflow-shortcuts.tgz \
     --repo person-clouds/dsh-workflow-shortcuts --target main --title v0.2.0 --notes-file <notes>
   unset GH_TOKEN
   ```
   Release notes 用本仓 `git log` 归纳，不改代码。
5. 验证：
   - `npm view <pkg> version`（若发布成功）；
   - `curl -I .../releases/latest/download/<name>.tgz` 返回 200；
   - `gh release view` 资产名无版本号、大小非零。
6. 文档同步：
   - 两仓 `PUBLISHING.md` 状态与版本号；
   - 两仓 `STATUS.md` 版本行、待办、验证记录；
   - `PROJECT_INDEX.md` 仅在仓库状态变化时改（预计不改）。
7. 提交：两仓分别 `./scripts/check.sh --repo <repo>` 后 `git add` 指定文件、commit、push；
   `doc` 仓单独提交计划文档。

## 验收

- 两个 Release 为 `latest`，`releases/latest/download/*.tgz` 可下载；
- npm 上可见新版本（若 token 可用）；
- 两仓 STATUS/PUBLISHING 与实际发布一致；
- `scripts/check.sh` 对两仓和 doc 仓通过。

## 回滚

- Release：`gh release delete <tag> --yes`（保留 tag 则只删 Release）。
- npm：`npm deprecate <pkg>@<version> "已撤回"`；不删除已发布版本。
- 文档：`git revert <commit>` 后重推。

## 改动记录

- 2026-11-20 18:10：创建计划，确认发布 0.4.1 / 0.2.0，使用 zhyfor 身份。
- 2026-11-20 18:15：两仓 GitHub Release `v0.4.1`、`v0.2.0` 已发布并验证下载；npm 发布均返回 404（token 失效），待 `npm login` 后补发；已同步两仓 STATUS/PUBLISHING。
