# 运行安全与操作规范（spec）

- 适用范围：涉及宿主机、权限、磁盘、服务重启、长任务、测试和临时浏览器的操作。
- 相关：[`engineering-rules.md`](engineering-rules.md)、[`task-workflow.md`](../../personalCloud/workspace/_meta/doc/task-workflow.md)、[`SECURITY.md`](../../personalCloud/ubuntuInit/SECURITY.md)

## 1. 安全红线

- 不主动执行需要 root 的系统变更；需要 root 的操作生成脚本或命令清单，由用户在宿主终端执行。
- sudo 被安全策略拒绝或目标盘只读时，**立即停止**：不 remount、不换路径、不造替代环境、不在 `/tmp` 或仓外临时目录做替代实验、不用工具内视图推断宿主机状态；把完整可复制脚本/命令交给用户。
- 不在配置、文档、命令历史中硬编码密码、Token、私钥。
- 不生成将 Web 服务绑定到 `0.0.0.0` 并暴露公网的配置。
- 远程访问默认只通过 Tailscale。允许 Tailscale Funnel 暴露必要服务，但必须满足第 2 节。
- 软件优先用 Docker 安装；禁止在工作区创建 `.local` 等目录模拟系统环境。
- 软件体积大或预计占资源多时，先提示用户确认。

## 2. Tailscale Funnel

Funnel 会把服务发布到公网，必须同时满足：

- **不直连业务**：只能指向带鉴权与限流的边缘代理，不得直接指向业务进程。参考 `edge/supercreater/` + `supercreater-edge.service`。
- **端口收敛**：只 Funnel 443；禁止使用 10000 端口（明文 HTTP，Secure Cookie 会失效）。
- **限流与封禁**：公网登录/口令接口按 IP 与账号双维度限流，并具备失败计数与自动封禁。
- **强制 HTTPS**：不回退明文；鉴权 Cookie 必须带 `Secure` + `HttpOnly` + `SameSite`。
- **凭据不进公网**：只有 bearer token 的页面不得长期公网暴露；token 泄露立即轮换。
- **可核验**：变更前后用 `tailscale funnel status` 核对暴露清单，保留访问日志。
- **变更留痕**：开启/关闭前写明影响范围、回滚方式、验证方法。

部署与回滚操作见 [`supercreater-public.md`](../../personalCloud/ubuntuInit/docs/supercreater-public.md)。

## 3. 权限与可见性

判据：任何关于「大小 / 数量 / 存在性 / 是否启用」的结论，先确认当前身份读得到。命令成功但结果为空或偏小，通常是「看不见」，不是「没问题」。

| 来源 | 表现 | 判定 |
|---|---|---|
| 权限不足 | 输出为空、全 0 或只有 4K | 用 `id` 确认；需要 root 的项写成「无法确认」 |
| UID 映射 | 宿主侧属主 `nobody:nogroup`、大小偏小 | 容器数据从容器内查，宿主侧视图不可信 |
| 工具沙箱 namespace | 工具内 `/mnt` 只读、路径不同或不存在 | 不代表宿主机状态，以用户在宿主 shell 的操作为准 |
| DSH 工具沙箱 | 会话 cwd 内可写；父目录、`~/.dsh`、其他仓在工具内报“只读文件系统” | `workspace-write` 写根边界，不是宿主挂载；改用 DSH settings/API 或交用户执行 |

常见误判：`du` 全是 4K 是容器目录普通用户读不到；`ufw status` 报错是只有 root 能运行；`mysql -uroot` 失败是 root 走 `auth_socket`；`command -v ufw` 找不到是 PATH 缺 `/usr/sbin`。结论前交叉验证 `du`、`df`、容器内 `du`；权限不足时区分【已确认】与【未能确认（原因）】。

工具视图复核顺序：`id` → 命令跑在工具沙箱还是宿主 shell → 数字对不上换容器内/宿主视角 → 仍不可确认就输出可在宿主机执行的命令清单。工具内 `findmnt` 显示 `ro` + `test -w` 失败，不能推出宿主机只读，更不能建议 `sudo mount -o remount,rw`。

DSH 场景先读会话头的 `permission/preset`、`sandbox/mode`、`approval/policy` 和 `header.cwd`。`workspace-write` 的写根是会话 cwd（`dsh-sandbox-policy` 的 `resolveWorkspaceRoot(session.header.cwd)`），父仓库 `.git`、`~/.dsh` 必然在界外。写 `~/.dsh` 配置被拒时不要 `cp`/`chmod`/remount，也不要把仓库复制到 `/tmp`；用 DSH `settings/update` API（见 [`dsh-session-automation.md`](../reference/dsh-session-automation.md)）或让用户在宿主终端执行。

`ubuntuInit/12-verify.sh` 的降级基线：

1. 补 PATH：`export PATH="${PATH}:/usr/sbin:/sbin"`。
2. 抓 stderr 判权限，不把报错文本当结论。UFW 示例：`Status: active` → PASS；报 `be root|permission denied` → WARN；其余 → FAIL。
3. WARN 是独立状态：退出码 `0` = 无 FAIL，`1` = 有 FAIL，`2` = `--strict` 且存在 WARN。需要 root 的项绝不输出 PASS。

### 3.1 已确认的网络事实

- mini 主机 `<主机名>` 的局域网地址 `<内网IP>` 已在路由器按 MAC（`<MAC>`）固定绑定，视同静态 IP；`ip addr` 的 `dynamic` 只是 DHCP 标志，不建议改静态地址或把“先固定 IP”列为前置条件。

## 4. 磁盘与文件操作预检

任何外部磁盘的读取、创建、修改、移动、删除前，先检查：

```bash
id
test -w "$TARGET"
findmnt -no SOURCE,TARGET,FSTYPE,OPTIONS "$TARGET"
sudo -n true 2>/dev/null || echo "sudo 不可用或需要密码"
```

- 目录属主是当前用户，不等于可写；`ro` 挂载即使属主正确也不能写。
- DSH 会话内 `test -w` 只证明当前 cwd 内可写，不能证明父目录、`~/.dsh` 或其他仓库可写。
- 只读挂载、无写权限或需 `sudo` 时，明说「当前无写权限」，生成脚本交用户执行。
- 批量移动前用 `rsync --dry-run` 或打印清单；移动用 `mv -n`。
- 删除前先列清单；默认移入隔离目录，只有用户明确要求永久删除时才 `rm`。
- 文件系统修复、挂载、格式化、权限变更，必须写明影响范围、回滚方式和验证命令。

## 5. 破坏性操作与重启

- 删除文件、大范围重构、跨模块改动，即便看起来是“优化”，用户没明确要求就不执行。
- 重启 `dsh-web` 或其他在线服务前，先报告原因、影响范围、预计中断和回滚方式，得到明确确认后执行；执行后复测并报告实际结果。
- 同一目标连续 10 步没有新增可验证证据，或同一方案连续 2 次失败，停止试错，按 [`task-workflow.md`](../../personalCloud/workspace/_meta/doc/task-workflow.md) 写会话交接。

## 6. 长任务后台执行

预计运行超过 5 分钟，或涉及 >10GB 数据搬运/构建/迁移的脚本，必须放后台执行。

- 启动方式任选：`nohup`、`systemd-run`、`tmux`；前台只跑短任务。
- 启动时同时给出：日志路径、PID/unit、进度查看命令、停止命令。
- 脚本自身落盘结果：结束时写 `.done`/`.failed` 标记或退出码文件。
- 验收以日志和产物为准，不靠终端回滚判断。

```bash
sudo nohup bash script.sh --apply > /var/log/script.log 2>&1 &
echo $! > "$HOME/.cache/script.pid"
tail -f /var/log/script.log
sudo kill "$(cat "$HOME/.cache/script.pid")"
```

## 7. 测试任务收尾

测试/基准/验证结束（含中途放弃）必须：

1. **落文档与报告**：目的、环境与版本、执行命令、验证结果、资源占用、异常与回滚方式；优先放项目 `docs/` 或 `TEST-REPORT.md`，并同步索引。
2. **停程序**：临时服务、测试实例、后台 job 全部停止；确认端口关闭、PID 退出、systemd scope/timer 清理。保留现场须报告 PID/unit、端口、原因和预计时长。
3. **测试产物不入库**：临时脚本、benchmark、模型/数据集放仓库外或 `.gitignore` 排除。
4. **报告资源占用**：测试前后对比 CPU、内存、磁盘、端口；清理后报实际回收量。
5. **不复用生产实例**：独立端口/模型目录/数据目录，禁止在线上服务或正式索引上做破坏性验证。
6. **日志与退出标记落盘**：长测试记录 PID/unit、日志路径、停止命令；结束后检查 `.done`/`.failed` 或退出码。

## 8. 临时浏览器自动化

- 临时 headless Chromium/Playwright 禁止 `nohup ... &` 或任何脱离当前命令生命周期的写法。
- 统一使用 `.dsh/skills/browser-debug/scripts/browser-session.sh`：负责临时 profile、硬超时、`trap` 清理，并按需套 `systemd-run --user --scope`。
- 用 Playwright 库时必须 `try/finally { await browser.close() }`，不能只 `disconnect`。
- 结束确认：命令退出、CDP 端口关闭、没有残留 `chrome-linux/chrome`。

完整规则见 [`.dsh/skills/browser-debug/SKILL.md`](../../.dsh/skills/browser-debug/SKILL.md)。

## 验收方式

- 任何 root/只读阻断场景，交付物是可复制脚本 + 影响说明，而不是绕过方案；不得出现以 `/tmp` 或仓外临时目录替代目标路径的做法。
- 公网暴露改动前后各留一次 `tailscale funnel status` 输出对照。
- 长任务、测试任务收尾必须有报告、端口/PID 清理证据和资源回收数据。
- 新增体检类脚本：无 root 时相关项输出 `WARN` 且带 `sudo` 提示；`--strict` 下存在 WARN 时退出码为 `2`。

## 失效条件

- 主机名、局域网地址、Funnel 拓扑、`ubuntuInit/12-verify.sh` 降级实现或浏览器调试脚本路径变化时同步修订；一次性事故复盘不留在本文件。
