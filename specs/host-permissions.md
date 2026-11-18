---
audience: shared
status: current
owner: workspace
scope: /home/zh/www
---

# 主机检查：权限与可见性（spec）

- 适用范围：任何关于宿主机「大小 / 数量 / 存在性 / 是否启用」的结论，以及宿主与容器/沙箱视图不一致的场景。
- 相关：[`operations-safety.md`](operations-safety.md)
- 结论一句话：**命令成功返回但结果为空或偏小，先怀疑「读不到」，不要下「没问题」的结论。**

## 1.「看不见」的三个来源

| 来源 | 表现 | 判定 |
|---|---|---|
| 权限不足 | 命令成功，但输出为空、全 0 或只有 4K | 用 `id` 确认身份；需要 root 的项应降级为「无法确认」 |
| UID 映射 | 宿主侧看到属主是 `nobody:nogroup`、大小偏小 | 容器数据从容器内查（`docker exec`），宿主侧视图不可信 |
| 工具沙箱 namespace | 工具内看到 `/mnt/...` 只读、路径不同、甚至不存在 | 不代表宿主机状态；以用户在宿主 shell 的操作为准 |

三者的共同点：**操作没有报错**。一旦把「无输出」当成「无问题」，后续所有判断都建立在空集上。

## 2. 已踩过的五类误判

| 现象 | 成因 | 正确做法 |
|---|---|---|
| `du -sh /data/*` 全是 4K | 子目录属主 `nobody:nogroup` + 750，普通用户读不到 | `docker exec <容器> du -sh <容器内路径>`；真实值 3.9G |
| `ufw status` 像「未启用」 | 只有 root 能运行 ufw，普通用户得到的是报错文本 | 判为「无法确认」，需要 `sudo bash 12-verify.sh` |
| `mysql -uroot` 报 Access denied | root 走 `auth_socket`，不是密码认证 | `sudo mysql` |
| `command -v ufw` 找不到 | 普通用户 PATH 不含 `/usr/sbin` | 脚本内 `export PATH="${PATH}:/usr/sbin:/sbin"` |
| 系统文件属主显示 `nobody:nogroup` | 可能是 UID 映射的显示效果 | 不据此判断「被篡改」，先查映射 |

## 3. 检查脚本怎么降级（`ubuntuInit/12-verify.sh` 参考实现）

1. **补 PATH**：普通用户的 PATH 通常不含 `/usr/sbin`，而 `ufw`/`sshd`/`nft` 都在那里。`export PATH="${PATH}:/usr/sbin:/sbin"`。
2. **抓 stderr 判权限**，而不是把报错文本当结论：

   ```bash
   UFW_OUT="$(ufw status 2>&1 || true)"
   if grep -q "Status: active" <<<"${UFW_OUT}"; then
     row ok "UFW" "已启用"
   elif grep -qiE "be root|permission denied|只有 root|需要 root|must be root" <<<"${UFW_OUT}"; then
     row warn "UFW" "需要 root 才能检查（sudo bash 12-verify.sh）"
   else
     row fail "UFW" "未启用 → sudo bash 01-harden.sh"
   fi
   ```

   SSH 密码登录、rdp-guard 等需要 root 的项用同样模式。
3. **WARN 是独立状态**，既不是 PASS 也不是 FAIL：退出码 `0` = 无 FAIL，`1` = 有 FAIL，`2` = `--strict` 且存在 WARN。这样「读不到」不会把整体判成通过，也不会误判为故障。

## 4. 工具视图 vs 宿主机视图：复核流程

1. `id` —— 我是普通用户还是 root？结论是否可能被权限截断？
2. 这个命令跑在工具沙箱里，还是用户的宿主 shell 里？
3. 数字对不上 → 换视角复核：容器内 `du`、宿主 `du`、`df` 三者对照。
4. 仍不可确认 → **不要给结论**，输出可在宿主机执行的命令清单，由用户跑完回填。

推论（容易违反的三条）：

- 工具内 `findmnt` 显示 `ro` + `test -w` 失败，**不能**推出宿主机只读，更不能建议 `sudo mount -o remount,rw`。
- Docker 的 bind mount 由 daemon 所在 mount namespace 解析，CLI/工具视图与 daemon 视图可能不同；启动容器前让用户在宿主机执行 `docker compose config` 和最小写入测试。
- 工具内写入/删除失败时，不声称宿主操作失败，也不擅自扩权。

## 5. 最小检查命令

```bash
id
test -w "$TARGET"
findmnt -no SOURCE,TARGET,FSTYPE,OPTIONS "$TARGET"
sudo -n true 2>/dev/null || echo "sudo 不可用或需要密码"
```

需要 root 才能确认的项，结论一律写成「需要 root 才能确认」，并附上让用户执行的命令。

## 验收方式

- 新增体检类脚本：无 root 时相关项输出 `WARN` 且带 `sudo` 提示，不输出 PASS；`--strict` 下存在 WARN 时退出码为 `2`。
- 任何「大小 / 数量 / 存在性」结论，报告里能指出取证命令与身份（`id` 输出或容器内执行方式）。
- `bash ubuntuInit/12-verify.sh` 在普通用户下可运行完成（无 root 项降级为 WARN）。

## 失效条件

- `ubuntuInit/12-verify.sh` 的降级实现方式改变（如改用 `sudo -n` 探测或 JSON 输出）时，第 3 节同步更新。
- 宿主权限模型变化（容器 UID 映射策略、sudoers 调整）后重跑一次案例，不沿用旧结论。
