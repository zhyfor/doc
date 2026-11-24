# npm 包发布流程

- 适用范围：`/home/zh/www` 下所有发布到 npm 的包（当前：`@fenghoer/dsh-context-guard`、`dsh-workflow-shortcuts`、`dsh-workbench-panel`）。新增 npm 包时先在本行登记，再按本文流程发布。
- 相关：各仓 `PUBLISHING.md`（包内打包、Release 资产命名等专属细节）、[`github-collaboration.md`](github-collaboration.md) §1（GitHub 凭据）、[`task-workflow.md`](task-workflow.md)（授权与收尾）。
- 本文是 npm 发布流程与三条本机特殊约束的唯一权威源；其他位置只链接。

## 1. 硬约束（每次发布都适用）

1. **显式指定 npmjs registry**：本机 `~/.npmrc` 的 `registry` 指向华为云镜像 `https://repo.huaweicloud.com/repository/npm/`，裸 `npm publish` 会发到镜像并报错。所有发布、登录、查询命令都必须带 `--registry=https://registry.npmjs.org`。两仓 `package.json` 已设 `publishConfig.registry` 兜底，但不能代替命令里的显式参数。
2. **token 在 `~/.npmrc`**：npmjs 凭据存于 `~/.npmrc` 的 `//registry.npmjs.org/:_authToken`。禁止 `cat`/`echo` 该文件，禁止把 token 写进仓库、文档、脚本、日志或会话；核对登录只跑 `npm whoami --registry=https://registry.npmjs.org`。
3. **发布成功有延迟**：`npm publish` 返回成功不等于 registry 立即可查。`npm view` 通常要等 **3–5 分钟** 才有新版本，期间可能返回旧版本或 404。判定标准是「publish 成功 + 等待后 `npm view` 可观」，不要在等待窗口内重复发布。
4. **顺序**：有配套版本下限的包先发底层（先 `@fenghoer/dsh-context-guard`，再 `dsh-workflow-shortcuts`）。
5. **先提交后发布**：本地测试、`check.sh`、commit + push 全部通过再发布；发布成功后才打 tag 与 GitHub Release，避免半发布状态。
6. **不回退已发布版本**：不用 `npm unpublish`、不删版本；出错发修订版（详见 §7）。

## 2. 发布前检查

```bash
cd /home/zh/www
npm whoami --registry=https://registry.npmjs.org          # 未登录先看 §3
npm view <pkg> version --registry=https://registry.npmjs.org   # 确认线上 latest，别发重
cd <repo>
npm test                     # guard 用 node test.mjs
npm pack --dry-run           # 确认 files 清单与版本号
cd /home/zh/www && ./scripts/check.sh --repo <repo>
git status --short           # 只留本任务改动
```

- 版本号按语义化修订，发布前确认 `package.json` 已是目标版本且已提交。
- 记录发布前的线上版本（通常是上一版）到任务报告，便于回滚判断。

## 3. 登录与 2FA

```bash
npm login --registry=https://registry.npmjs.org
npm whoami --registry=https://registry.npmjs.org
```

- 登录会写 `~/.npmrc`；已登录且 `whoami` 正常可跳过。
- 账号开启 2FA 时，`npm publish` 会提示输入一次性验证码（OTP）；按提示在交互终端输入。
- 非交互环境用 `NPM_TOKEN` 注入时不得回显、不得落盘；本机自用可以直接交互登录。

## 4. 发布

```bash
cd /home/zh/www/<repo>
npm publish --registry=https://registry.npmjs.org --access public
```

- 成功输出形如 `+ @fenghoer/dsh-context-guard@0.5.0`。
- 失败常见三类：漏 `--registry`（发到华为云镜像，`404 Not Found - PUT`）、未登录/OTP 错（`E401`/`EOTP`）、版本已存在（`E403`/`EPUBLISHCONFLICT`）。

## 5. 验证（含传播延迟）

```bash
sleep 300   # 3–5 分钟；少于此窗口查到旧值是正常的
npm view <pkg> version --registry=https://registry.npmjs.org
npm view <pkg> dist-tags --registry=https://registry.npmjs.org
npm view <pkg> versions --registry=https://registry.npmjs.org | tail -3
```

- 期望：`version` 等于新版本，`dist-tags.latest` 指向新版本，`versions` 末尾出现新版本号。
- 5 分钟后仍查不到：先确认 publish 输出与 `whoami`，再查是否发到了别的 registry，不要直接重发同版本（会冲突）。
- 可选安装验证：`dsh plugin --profile web add <pkg>`，再 `dsh plugin --profile web list` 看解析到新版本。

## 5.5 插件市场条目（常驻事实，改描述只走这一步）

以下是不常变的事实，本机实测于 2026-11-24；执行时直接照此操作，不要重新搜索定位：

| 项 | 值 |
|---|---|
| 市场仓库 | `awesome-dsh-plugin/awesome-dsh-plugin`（默认分支 `main`） |
| 条目路径 | 通用规则 `data/plugins/<owner>__<repo>.yml`；本工作区各插件见下表「本工作区条目清单」 |
| 仓库内草稿 | `<repo>/market/person-clouds__<repo>.yml`，与市场条目逐字段对应 |
| 推送权限 | zhyfor 只有 read（`permissions.push=false`），必须走 fork `zhyfor/awesome-dsh-plugin` |
| 分支名 | `dsh/update-<owner>-<repo>-<version>`，PR 到 `main` |
| 标签 | 该组织仓库没有 `agent:dsh`，`--label` 会失败；PR 正文写 `@zhyfor` |
| tarball | 一律 `https://github.com/<owner>/<repo>/releases/latest/download/<repo>.tgz`（不带版本号） |

本工作区条目清单（2026-11-24 核对 `data/plugins/` 全量索引）：

| 插件仓 | 市场条目 `data/plugins/…` | 仓库内草稿 `market/…` | 状态 |
|---|---|---|---|
| `dsh-context-guard` | `person-clouds__dsh-context-guard.yml` | `person-clouds__dsh-context-guard.yml` | 已收录（描述更新 PR #18300） |
| `dsh-workflow-shortcuts` | `person-clouds__dsh-workflow-shortcuts.yml` | `person-clouds__dsh-workflow-shortcuts.yml` | 已收录 |
| `dsh-workbench-panel` | `person-clouds__dsh-workbench-panel.yml` | `person-clouds__dsh-workbench-panel.yml` | 已收录 |
| `dsh-workbench` | `person-clouds__dsh-workbench.yml` | `person-clouds__dsh-workbench.yml` | 未收录（旧工作台已存档，不提交） |
| `superagent-workbench` | `person-clouds__superagent-workbench.yml` | `person-clouds__superagent-workbench.yml` | 未收录（SA 内部工作台，按需再提） |

新增插件时在「插件仓 / 条目 / 草稿」三列登记一行，再按下面的流程提交；`<owner>__<repo>.yml` 里的 `<owner>` 是 GitHub 所有者，与 npm scope 无关。

改描述或 tarball 的流程（2026-11-24 实测可用）：

```bash
FORK=zhyfor/awesome-dsh-plugin
REPO=awesome-dsh-plugin/awesome-dsh-plugin
BRANCH=dsh/update-<owner>-<repo>-<version>
set -a; . ~/.config/dsh-gh.env; set +a                 # GH_TOKEN，见 github-collaboration.md §1
gh api -X POST repos/$REPO/forks --jq .full_name          # 首次才需要
gh api -X POST repos/$FORK/merge-upstream -f branch=main  # fork 先同步上游
BASE=$(gh api repos/$FORK/git/ref/heads/main --jq .object.sha)
SHA=$(gh api repos/$REPO/contents/data/plugins/<owner>__<repo>.yml --jq .sha)
gh api -X POST repos/$FORK/git/refs -f ref="refs/heads/$BRANCH" -f sha="$BASE"
gh api -X PUT repos/$FORK/contents/data/plugins/<owner>__<repo>.yml \
  -f message="docs(plugins): <owner>/<repo> 描述更新" \
  -f content="$(base64 -w0 market/person-clouds__<repo>.yml)" -f sha="$SHA" -f branch="$BRANCH"
gh pr create --repo $REPO --head zhyfor:$BRANCH --base main --title "..." --body "@zhyfor ..."
```

- 只改条目文件，不动 `url`/`name`/`category`；`tarball` 保持 `latest/download` 形式，发版不必改地址。
- 新增收录：仓库公开、创建满 1 天、加 topic `dsh-plugin`、已发 npm 或 Release tarball，再按上面流程提交新条目。
- 验证：`gh pr view <n> --repo $REPO --json additions,deletions,changedFiles` 应只有 1 个文件变更；合并后市场页随之更新。

## 6. tag 与 GitHub Release（发布确认之后）

```bash
cd /home/zh/www/<repo>
git pull --rebase origin <默认分支>
git tag v<X.Y.Z>
git push origin v<X.Y.Z>
GH_TOKEN=$(git credential fill <<< $'protocol=https\nhost=github.com\n') \
  gh release create v<X.Y.Z> --title v<X.Y.Z> --notes "npm: <pkg>@<X.Y.Z>"
```

- tag 在 `npm view` 确认新版本后才创建；只推送本次 tag，不推其它。
- Release 资产命名与上传细节见各仓 `PUBLISHING.md`（资产名不带版本号，避免 `releases/latest/download/` 404）。
- 凭据规则见 [`github-collaboration.md`](github-collaboration.md) §1：不 `cat` 凭据文件，`GH_TOKEN` 只在单条命令环境里传递。

## 7. 回滚

- 发布内容有问题：**不发 unpublish**，修代码后升修订号（如 `0.5.1` / `0.4.1`）重走本文流程。
- 已发布的坏版本仍在，消费者用 `overrides`/`resolutions` 指向旧版，或等修订版。
- 只是漏打 tag：补 tag 与 Release，不改 npm 版本。
- 错误的 npm 版本号（例如该发 `0.5.0` 却发了 `0.5.1`）：保留已发版本，下一版按语义化继续升，不改写历史。

## 8. 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `404 Not Found - PUT .../repo.huaweicloud.com/...` | 漏 `--registry`，发到了华为云镜像 | 加 `--registry=https://registry.npmjs.org` 重发 |
| `E401 Unauthorized` / `whoami` 失败 | 未登录、token 失效或登录到了镜像 | §3 重新在 npmjs 登录 |
| `EOTP` / 要求 OTP | 账号 2FA | 按提示输入验证码；确认终端可交互 |
| `E403 ... cannot publish over existing version` | 该版本已存在 | 升版本号，不覆盖 |
| `npm view` 返回旧版本或 404 | 传播延迟 | 等 3–5 分钟再查，勿重复发布 |
| `npm view` 一直 404 且 publish 成功 | 查错 registry / 包名大小写 | 加 `--registry` 且核对包名 |

## 9. 验收清单

- [ ] `npm whoami` 成功，且命令带 npmjs registry。
- [ ] 发布前线上版本已记录，`npm test` 与 `check.sh` 通过，改动已 commit + push。
- [ ] `npm publish` 输出新版本，且等待 3–5 分钟后 `npm view version` 与新版本一致。
- [ ] `dist-tags.latest` 指向新版本。
- [ ] 发布确认后才打 `v<X.Y.Z>` tag 并推送，Release 已创建。
- [ ] 报告中写明包名、版本、publish 输出、`npm view` 结果与回滚方式。
