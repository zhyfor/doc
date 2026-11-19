# 仓库与项目登记维护

- 适用范围：新增、删除、移动仓库/项目/服务/脚本/文档/配置，或改默认分支、远程、入口、端口时。
- 索引：[`../../PROJECT_INDEX.md`](../../PROJECT_INDEX.md)、[`../../repos.yaml`](../../repos.yaml)；服务清单以 `personalCloud/services.conf` 为准，索引不重复维护。

## 1. 何时必须更新

任一发生即必须同步：

- 在 `/home/zh/www` 下新增或删除独立 git 仓库；
- 仓库改远程、默认分支、入口或验证命令；
- 新增/删除/移动工作区内的脚本、文档、配置（`task/`、`ubuntuInit/`、`doc/`、根 `cloudctl*` 等）；
- 新增/改名服务，或改端口、绑定地址、启动命令、数据目录：先改 `services.conf`，再补索引中的项目入口；
- 项目归档、恢复或迁移，改变独立仓库归属，或根约束文档、授权规则变化。

要求：与改动放在同一次任务收尾中，不留给“下次”；至少更新对应章节和顶部「最后核对」日期。

## 2. `repos.yaml` 字段

```yaml
- id: repo-id                 # 稳定短名
  path: /home/zh/www/<repo>   # 绝对路径
  remote: <git remote url>
  default_branch: master      # 或 main
  role: 一句话定位
  verify: "测试命令"           # 没有就留空
  note: 可选说明
```

## 3. 布局硬约束

- 一个仓库一个目录，各自带 `.git` 与远端；**不做 submodule、不做 gitlink**。
- 嵌套仓库必须被父仓库 `.gitignore` 显式排除（如 `personalCloud` 已排除 `task/xctl/`、`task/superCreater/`）。
- 父仓库不追踪子仓库文件，也不跨仓库做原子提交；每个仓库独立 `git add/commit/push`。
- 大仓库靠各自 `.gitignore` 控制体积（如 `superCreater` 约 8.8G，含 `.gomodcache`、`.go-build-cache`），缓存不入库。
- 跨项目文档统一放 `/home/zh/www/doc`（独立仓），不散落在各仓库 `doc/`。
- 编辑器 Git 扩展默认只扫描打开目录的一层子目录：管理多个嵌套仓时打开共同父目录 `personalCloud/task`，日常不使用多根工作区。

## 4. 新增仓库

1. 确认是独立 git 仓：`git -C <path> rev-parse --git-dir`。
2. 仓库放到 `task/<name>/` 或 `/home/zh/www/<name>`，自带 `.git`，不要复制成普通目录。
3. `personalCloud/.gitignore` 增加 `task/<name>/` 并写一行说明。
4. 在 `repos.yaml` 增加一条；在 `PROJECT_INDEX.md` 的工作区地图和独立仓库表增加一行。
5. 跑 `./scripts/repo-status.sh` 确认能识别；如有项目级 `AGENTS.md`/`README`/`STATUS`，在索引入口列指向它。
6. 外部仓库用 `setup.sh` clone 到 gitignored 的 `workspace/`，不要把外部仓库复制进来。

## 5. 新增项目

1. 从模板开始：`cp -r task/_template task/<小写-连字符名>`。
2. 写 `README.md`，至少包含：一句话定位、状态、入口/端口、关键文件、常用命令、数据位置、依赖与回滚方式。
3. 对外服务：在 `services.conf` 加一行（`名字|类型|目标|描述|端口`），跑 `./cloudctl list` 确认能识别；绑定地址只能是 `127.0.0.1` 或 Tailscale IP，禁止 `0.0.0.0`。
4. 用到数据：按 [`engineering-rules.md`](engineering-rules.md) 第 8 节建独立 MySQL database + user。
5. 更新 `PROJECT_INDEX.md` 的目录/项目表与「最后核对」日期。
6. 根仓库与独立仓库分别提交；提交信息沿用 `type(scope): 摘要`。

## 6. 项目卡片与状态词

`PROJECT_INDEX.md` 只放导航，不写长卡片。项目细节写进自己的 `README.md`，索引里只保留一行：

```markdown
| [`task/<名字>/`](../../personalCloud/task/<名字>/README.md) | 一句话定位 | 运行中/按需/工具/已完成/归档 | `README.md` |
```

状态词：运行中（systemd/compose 常驻）、按需（手工启动）、工具（只读诊断/一次性）、已完成（一次性任务保留备查）、历史归档（不参与运行）、模板（复制使用）。

## 7. 自检

```bash
cd /home/zh/www
./scripts/repo-status.sh                     # 缺失路径、dirty、分支异常、ahead/behind
python3 -c 'import yaml; yaml.safe_load(open("repos.yaml"))'

cd /home/zh/www/personalCloud
for d in task/*/; do                          # task 目录是否都在索引中出现
  name=${d#task/}; name=${name%/}
  grep -q "task/$name" PROJECT_INDEX.md || echo "未登记: $name"
done
```

- `repo-status.sh` 发现缺失路径、dirty、分支异常、ahead/behind。
- 索引只做导航；仓库细节以各仓 `README`/`STATUS` 为准；自检只发现漏登记和失效链接，不判断描述是否过期。

## 8. `task/` 项目提升为独立仓

`personalCloud/task/<name>` 成熟到需要独立发布、独立 PR 或独立权限时，提升为 `/home/zh/www/<name>` 独立仓。

**提升门禁**（缺一不可）：

1. 仓根有 `SPEC.md`，包含：目标、用户、范围、非目标、接口、运行方式、验收命令、约束；
2. 仓根文档纳入中央策略，且可通过 `./scripts/check.sh --repo <name>`；
3. `repos.yaml` 该条带 `spec: SPEC.md`；
4. 历史用 `git subtree split --prefix=task/<name> -b split/<name>` 保留，新仓 `git log --follow` 能看到原提交；
5. 安装/引用路径全部改为 `/home/zh/www/<name>`，`personalCloud` 内不留旧目录与旧引用。

**路径约定**：

- 新仓：`/home/zh/www/<name>`，默认分支 `main`；
- 远端：优先复用 `https://github.com/person-clouds/<name>.git` 同名仓（公开）；新建仓后补齐 `origin` 与 upstream；
- `personalCloud/task/` 只留仍跟随 personalCloud 版本节奏的项目；
- 根 `PROJECT_INDEX.md` 独立仓库表登记，`personalCloud/PROJECT_INDEX.md` 删除对应行；
- 跨仓文档里的旧路径统一改为 `<name>/...`（相对 `/home/zh/www`）。
