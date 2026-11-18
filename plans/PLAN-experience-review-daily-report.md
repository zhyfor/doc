---
implementation_status: in_progress
created_at: 2026-11-19 06:35:00
updated_at: 2026-11-19 06:35:00
---

# PLAN：经验库审核入口与每日飞书日报

## 目标

把 `/home/zh/www/project-experience` 的候选审核变成可一键启动、可由 `cloudctl` 管理的常驻网页；对存量候选先执行一次全量自动审核，低风险达标项直接入库；每天 21:00 通过现有「小A」飞书机器人私聊发送运行日报，并在新候选生成后继续自动审核低风险条目。

## 范围

- 改：`project-experience` 工具与文档、`personalCloud/services.conf`、用户级 systemd timer。
- 采集：以 `/home/zh/www/repos.yaml` 为清单覆盖全部已登记项目，排除 `project-experience` 自身。
- 存量候选先跑一次 `dsh-exp review --auto`：低风险且分数/硬门槛满足的直接 `verified`，其余进入人工审核或继续候选，不降低风险门槛。
- 当前存量候选的 `risk` 均为 `medium`，本轮自动通过预计为 0 条；仍需网页人工审核，这是预期结果。
- 不改飞书应用配置，复用 SA 已有 `lark-bot` 与私聊会话。
- 旧 `~/.dsh/experience` 仓库保留但不再作为审核/采集入口。

## 改动位置

- `project-experience/tools/dsh-exp-review-start`：一键启动审核网页，绑定 Tailscale IP，默认端口 8791。
- `project-experience/tools/dsh-exp-watch-all`：读取 `repos.yaml`，逐项目执行 `dsh-exp watch --once --auto-score --review-low-risk`。
- `project-experience/tools/dsh-exp-daily-report`：汇总 watch 状态、候选数、审核日志并发送飞书私聊。
- `personalCloud/services.conf`：注册 `experience-review`（proc）、`experience-watch`（user timer）、`experience-daily-report`（user timer）。
- `~/.config/systemd/user/dsh-exp-watch-all.{service,timer}`、`dsh-exp-daily-report.{service,timer}`：新增定时任务。
- `~/.config/dsh-exp/feishu-chat-id`：私聊 chat_id，权限 0600，不进 Git。
- `project-experience/README.md`、`STATUS.md`：同步入口与运行方式。

## 实施步骤

1. 新增审核启动脚本：解析仓库根、检测 `tailscale ip -4`、回退 `127.0.0.1`，`exec dsh-exp-review --repo <canonical> --bind <ip> --port 8791 --push`。
2. 停用并禁用旧 `dsh-exp-review.service`（当前指向 `/home/zh/.dsh/experience`，端口 8791）；保留其 unit 文件作回滚，改由 `cloudctl start experience-review` 启动。
3. 存量审核：确认工作树干净后执行一次 `dsh-exp review --auto --publish`；仅低风险且 `machine_verified` 的条目自动 verified，其余保留人工审核/候选状态，提交审核结果。
4. 新增 watch-all 包装：按 `repos.yaml` 遍历全部仓库，`personalCloud` 加 `--exclude 'task/*'` 避免子仓重复；单项目失败继续并最终返回非零。
5. 安装 `dsh-exp-watch-all.timer`，每 5 分钟跑一次，替换现有 `dsh-exp-watch.timer` 与 `dsh-exp-watch-personalcloud.timer`，命令带 `--review-low-risk`。
6. 新增日报脚本：读取 `~/.local/state/dsh-exp/watch/*.json`、`entries/candidates/` 当日新增、`review-log.jsonl` 当日通过/驳回、`last_error`；生成含 token 的审核 URL。
7. 日报通过 `task/superagent-feishu/bin/lark-bot api POST /open-apis/im/v1/messages` 发到私聊；支持 `--dry-run`、`--json`，失败写日志并返回非零。
8. 安装 `dsh-exp-daily-report.timer`，`OnCalendar=*-*-* 21:00:00`，`Persistent=true`。
9. 更新 README/STATUS，运行仓库校验。

## 验收

- `cloudctl start experience-review` 后状态为 running，Windows 通过 `http://100.84.98.28:8791/<token>/` 能打开并完成一次通过/驳回。
- `cloudctl stop/restart experience-review` 生效；旧 8791 上不再运行 `/home/zh/.dsh/experience` 实例。
- `systemctl --user start dsh-exp-watch-all.service` 遍历全部登记项目，状态文件均更新；修改任一项目文档后 5 分钟内产生候选。
- 存量全量机审已执行并提交；低风险且达 85 分的候选为 `verified`，其余未降低门槛、仍可网页审核。
- 低风险且达 85 分的本次新候选自动标记 `machine_verified`；中高风险仍留待人工。
- `dsh-exp-daily-report --dry-run` 输出当日运行状态、候选总数、当日新增、通过/驳回、错误、带 token 审核 URL。
- 手动发送一次日报可在飞书私聊收到；21:00 timer 下一次触发成功。
- `./scripts/check.sh --repo project-experience`、`./scripts/check.sh --repo doc` 通过。

## 回滚

- `cloudctl stop experience-review`，删除 `services.conf` 三条新增行，重新 `systemctl --user enable --now dsh-exp-review.service`。
- 停用并移除两个新 timer，恢复旧 `dsh-exp-watch*.timer`。
- 删除 `feishu-chat-id` 与日报脚本；已入库/已提交的审核记录按 Git 提交回退。
- 代码改动按仓库分别 revert。

## 改动记录

- 2026-11-19：创建计划，明确审核网页改由 cloudctl 管理、全项目 watch、21:00 飞书私聊日报。
- 2026-11-19：调整存量处理：先执行一次全量自动审核，低风险达标直接入库。
- 2026-11-19 06:34：完成审核台 cloudctl 托管、12 项目 watch-all、存量/新增候选机审、飞书日报真实发送与两个 timer 安装；31 项测试与 `check.sh` 通过。
