# GitHub push 443 超时排障

- 时间：2026-10-21 20:38
- 使用模型：DeepSeek-Chat
- 环境：Windows 11 / Git 命令行 / 仓库 `D:\ICEC-2026-0153-huangxinyu`
- 结论：**已解决**（hosts 固定可用 IP）

## 1. 现象（原始报错）

本地已经 `git commit` 成功，历史里有 `184ff75 stage1: 课题10 耗时采样数据与记录说明`，
但推送一直失败：

```
fatal: unable to access 'https://github.com/xxxx/ICEC-2026-0153-huangxinyu.git/':
Failed to connect to github.com port 443 after 21000 ms: Couldn't connect to server
```

关键点：**本机浏览器能打开百度，说明不是断网**，只是 `github.com` 这个域名到不了。

## 2. 我的提问（原文，略作脱敏）

> 我是零基础大一新生，本地 commit 都成功了，push 一直报
> `Failed to connect to github.com port 443 after 21000 ms`。
> 我 hosts 里 github.com 对应的 IP 还是 `140.82.114.3`，请问怎么排查？

## 3. AI 给的方案

1. 先确认是 DNS/网络问题而不是账号权限问题：
   `ping github.com` 看解析到哪个 IP，`Test-NetConnection github.com -Port 443` 看端口是否通；
2. `github.com` 有多个可用 IP，可以在 hosts 里固定一个能连通的；
3. **写脚本时必须有回滚**：改 hosts 属于系统级修改，全部 IP 都失败时要能恢复原文件；
4. 改完必须 `ipconfig /flushdns`，否则系统还在用旧解析。

## 4. 我实际做了什么

1. 写 `fix-github-push.ps1`，脚本做四件事：
   - `Start-Transcript` 全程录日志；
   - 把原始 hosts 备份到 `hosts.backup.txt`；
   - 依次尝试 `20.205.243.166` → `140.82.121.4` → `20.27.177.113`，每次替换 `github.com` 那一行后 `flushdns` 再 `git push`；
   - 任一 IP 成功就 `break`，全部失败则**把 hosts 恢复成原始内容**。
2. 第 1 个 IP `20.205.243.166` 仍然超时；
3. 第 2 个 IP `140.82.121.4` 推送成功，脚本输出 `PUSH OK via 140.82.121.4`。

脚本关键片段：

```powershell
foreach ($ip in $ips) {
    $pattern = '(?m)^140\.82\.114\.3(?=\s+(?:www\.)?github\.com\s*$)'
    $new = $original -replace $pattern, $ip
    Set-Content -Path $hosts -Value $new -Encoding ASCII
    ipconfig /flushdns | Out-Null
    git -C $repo push origin main 2>&1 | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -eq 0) { $ok = $true; $used = $ip; break }
}
if (-not $ok) { Set-Content -Path $hosts -Value $original -Encoding ASCII }
```

## 5. 结果与证据

- 脚本日志：`fix-github-push.log`，结尾 `PUSH OK via 140.82.121.4`
- 备份留痕：`hosts.backup.txt`（原始 hosts 全文）
- 改动记录：`hosts-change.log`（内容 `OK`）
- 推送成功后仓库历史：

```
7485e3f chore: 补齐课题10 目录占位         2026-10-21 20:23
184ff75 stage1: 课题10 耗时采样数据与记录说明  2026-10-21 20:07
```

## 6. 复盘

- **根因**：`github.com` 的 DNS 解析到了一个本机不可达的 IP，属于网络层问题，和 Git 配置、账号密码无关。
- **AI 方案里哪条最有用**：第 3 条「必须带回滚」。第一次试完 IP 失败后，hosts 已经被改坏，如果没有回滚分支，我会把系统网络配置留在半残状态。
- **AI 方案里哪条不够**：它一开始建议的 `ping` 只能证明「不通」，不能直接给出可用 IP；真正解决问题是我把三组 IP 做成循环逐个实测，而不是靠猜。
- **下次遇到同类问题的动作**：先 `nslookup github.com` 看解析结果，再用固定 IP 方案，改 hosts 前先备份。
- **遗留**：hosts 里现在固定的是 `140.82.121.4`，若该 IP 后续失效，直接重跑 `fix-github-push.ps1` 即可，脚本会自动轮换并回滚。