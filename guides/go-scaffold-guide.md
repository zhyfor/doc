---
audience: shared
status: current
---

# GoFrame 项目脚手架与部署规范

> personalCloud 工作区里 GoFrame 项目的组织方式、选型决策、脚本分工。

---

## 一、Git 仓库归属

personalCloud 是主仓库（`fenghoer/personalCloud`），每个 task 子项目里可以混住**主仓库文件**和**独立 git 仓库 clone 下来的副本**。独立仓库统一放在 `workspace/` 下，在主仓库 `.gitignore` 里屏蔽，不会被误提交。

```
personalCloud/                          ← 主仓库
├── .gitignore                          ← 屏蔽 /**/workspace/、project-template/gf-scaffold/
├── cloudctl                            ← 宿主机级服务管理脚本（主仓库）
├── services.conf                      ← 服务清单（主仓库）
├── project-template/
│   └── gf-scaffold/                    ← 独立仓库 fenghoer/gf-scaffold（模板源头）
└── task/
    ├── archive/                          ← 归档区（整目录 gitignore，仅本地保留）
    │   ├── content-discovery-task/
    │   │   ├── docker-compose.yml        ← 已归档（原 compose 入口）
    │   │   ├── app/                      ← 已归档（原 compose 上下文，Go 源码在这里）
    │   │   └── workspace/
    │   │       └── gf-scaffold/          ← 独立仓库副本（模板参考，可删可拉）
    │   └── ai-creater/
    │       ├── run.sh                    ← 已归档（原宿主机托管入口）
    │       ├── preview_server.py         ← 已归档（Python 辅助进程）
    │       ├── systemd/                  ← 已归档（systemd user 单元）
    │       └── workspace/
    │           └── AICreater/            ← 独立仓库 fenghoer/AICreater（Go 源码）
    └── superCreater/                     ← 现行项目（原 content-discovery + AICreater 合并）
```

**更新模板**：`cd project-template/gf-scaffold && git pull` 或 `cd task/xxx/workspace/gf-scaffold && git pull`。两份是独立副本，互不影响。

---

## 二、部署选型：容器化 vs 宿主机

| 维度 | 容器化（compose） | 宿主机（systemd user） |
|---|---|---|
| **适用场景** | 需要监听端口对外暴露（API / Web UI）；多容器编排；计划部署到云服务器 | 单 cron / worker 进程；只调外部 AI API 不对外监听；个人单机场景 |
| **文件读写** | 用 volume 挂进容器；MySQL socket 用只读挂载 | 直接读宿主机目录；本地 MySQL socket 天然可用 |
| **环境变量** | compose 的 `env_file` + `environment` | run.sh 里读 `.env` + 手动 `export` |
| **重启/自启** | `restart: unless-stopped` | `Restart=always` + `WantedBy=default.target` |
| **cloudctl 支持** | `start/stop/restart/rebuild` 全部可用 | `start/stop/restart` 可用，`rebuild` 跳过 |
| **新增脚本** | compose + Dockerfile 足够 | 需要 run.sh 包装 + systemd unit |
| **代表项目** | superCreater（原 content-discovery，已合并） | ai-creater（已归档，见 `task/archive/`） |

**决策规则**：有对外监听端口 → 容器化；没有 → 宿主机。不确定时先宿主机，对外暴露时再迁容器。

---

## 三、脚本分工：cloudctl / run.sh / Makefile

三个层次的脚本，各管各的，不重叠。

### cloudctl（宿主机级别，主仓库）

统一管理所有服务的生命周期，四种类型全覆盖：

| 类型 | 典型服务 | cloudctl 覆盖 |
|---|---|---|
| `system` | 系统级 systemd 服务 | ✅ |
| `user` | 用户级 systemd 服务（aicreater-cron、preview）| ✅ |
| `compose` | docker compose 项目（discovery、nextcloud）| ✅ rebuild 也支持 |
| `proc` | 手动拉起的常驻进程（headroom 等；dsh web 推荐用 `user`）| ✅ |

cloudctl **不做**的事：
- 不解析 `.env`（这是 run.sh 管的）
- 不调项目专属命令（`run.sh once`、`run.sh douyin` 这类）
- 不注入代理 / 不设置 PROJECT/ENV 环境变量

### run.sh（项目级别，主仓库）

compose 项目不需要 run.sh（compose 就是入口）。**宿主机项目必须有 run.sh**，它负责：

| 职责 | 示例（`task/archive/ai-creater/run.sh`）|
|---|---|
| 读 `.env` 并保留空格值 | `set -a && source "$ENV_FILE" && set +a` |
| 注入 GoFrame 必要变量 | `PROJECT=gf`、`ENV=prod` |
| 代理转发 / NO_PROXY 设置 | 检测本机 127.0.0.1:7897 有代理时自动开 |
| 业务专属命令 | `once` 手动跑一轮、`douyin` 发布、`douyin-verify` 提交验证码 |
| PID / 日志文件管理 | `creator-cron.pid`、`creator-cron.log` |
| systemd unit 安装检查 | 提示用户 `systemctl --user enable` |

run.sh 做的 start/stop 与 cloudctl 功能重叠，**实际运维用 cloudctl 即可**，run.sh 主要给 `.service` 文件的 `ExecStart` 调用。

### Makefile（GoFrame 项目内部，独立仓库）

Makefile 是 GoFrame 框架约定的入口，管项目内部构建：

| target | 说明 |
|---|---|
| `make service.start` | 前台启动 `main server` |
| `make service.restart` | 重启 service |
| `make docker.build` | 构建运行镜像 |
| `make docker.run` | build + 运行 |
| `make test` | 跑单元测试 |

compose 项目里 `make docker.run` 是给容器内用的，宿主机项目里直接 `make service.start`。cloudctl build/rebuild 会直接调 `go build` + `docker compose build`，绕过 Makefile——因为 Makefile 的 docker 逻辑可能包含推送镜像等额外步骤，cloudctl 只需要本地 build 即可。

若 compose 目录自带 `build.sh`（如 superCreater 的 `manifest/docker/build.sh`），则改为委托给它：`cloudctl build` 传 `--build-only`（只编译+镜像），`cloudctl rebuild` 跑全量（构建 + 重建容器 + 健康检查 + 清理）。

### shell/ 目录（GoFrame 项目内部）

gf-scaffold 模板自带的 shell 脚本，**compose 项目里没什么用**（cloudctl 覆盖了），**宿主机项目里的 run.sh 应该替代它们**（run.sh 更懂项目上下文）。

---

## 四、新建项目流程

### 容器化项目（有对外端口）

```bash
# 1. clone 模板
cd task/<新项目名>/workspace/   # .gitignore 已屏蔽 workspace/
git clone https://gitee.com/fenghoer/gf-scaffold.git <新项目名>

# 2. 把 gf-scaffold 源码复制到 app/（compose 上下文）
cp -r <新项目名>/ app/
# 改 app/go.mod 里的 module 名
# 改 app/internal/ 下的业务代码

# 3. 写 docker-compose.yml（参考 superCreater 的；content-discovery 已合并进它，仅作历史备份）
# 4. 加 services.conf 条目（compose 类型）
# 5. ./cloudctl rebuild <新项目名>   # go build → docker build → up -d
```

### 宿主机项目（只有 cron / worker）

```bash
# 1. clone 模板到 workspace/
cd task/<新项目名>/workspace/
git clone https://gitee.com/fenghoer/gf-scaffold.git <新项目名>

# 2. 改 <新项目名>/internal/ 下的业务代码
# 3. 写 run.sh（参考 task/archive/ai-creater/run.sh）
# 4. 写 systemd user 单元 → systemctl --user enable
# 5. 加 services.conf 条目（user 类型）
# 6. ./cloudctl start <新项目名>
```

---

## 五、进阶话题：模板代码回流

项目里写出通用工具（MySQL 封装、重试、pProf 中间件）后，想合并回 gf-scaffold。

**方案 A：手动 cherry-pick（当前只用这个）**

```bash
# 1. 在项目里找出那段通用代码
git diff task/<项目>/workspace/<项目>/internal/utility/
# 2. 切到 gf-scaffold 仓库
cd project-template/gf-scaffold/
git checkout -b feat/add-xxx-utility
# 3. 手动合并（或 git cherry-pick <commit>）
git push origin feat/add-xxx-utility
git checkout main && git merge feat/add-xxx-utility && git push
```

优点：简单，不破坏项目自己的提交历史；缺点：需手工对比，可能有冲突。

**方案 B：把 gf-scaffold 设为 upstream，定期 rebase**

```bash
git remote add gf-template https://gitee.com/fenghoer/gf-scaffold.git
git fetch gf-template
git rebase gf-template/main
```

缺点：项目改了模板自带代码（如 `internal/service/` 初始化）会大量冲突；`go.mod` module 名不同，每次 rebase 都要手动改回；改动量一大就是噩梦。

**方案 C：模板用 git subtree 引入**

```bash
git subtree add --prefix=project-template/gf-scaffold https://gitee.com/fenghoer/gf-scaffold.git main --squash
git subtree pull --prefix=project-template/gf-scaffold https://gitee.com/fenghoer/gf-scaffold.git main --squash
git subtree push --prefix=project-template/gf-scaffold https://gitee.com/fenghoer/gf-scaffold.git main
```

优缺点：主仓库能看到完整历史、回流基本自动；但要记 subtree 命令，且与 `.gitignore` 屏蔽独立仓库的思路冲突。

**结论**：目前只用方案 A。回流不是高频操作，手动 cherry-pick 够了；等 3 个以上项目在演进、模板更新变成日常需求时，再给模板仓库搭 CI（自动改 `go.mod` module 名、生成 `internal/service/init.go` 特化版本、同步 `shell/`）。
