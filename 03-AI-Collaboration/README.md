# AI 协作排障记录

本目录保存 ICEC-2026 实施过程中，**关键提问与真实报错**的原始对话留痕。

原则：

- 只收录**真的卡住过**的故障，不收录顺手的问答；
- 保留**原始报错文本**，不改写、不翻译；
- 记录里同时写清「AI 给的方案」和「我实际执行后哪些不管用」；
- token、密码、内网 IP 一律脱敏。

## 索引

| 编号 | 日期 | 故障 | 使用模型 | 结论 | 记录 |
| --- | --- | --- | --- | --- | --- |
| 01 | 2026-10-21 | 请求 400：输入 + 预留输出超过 64K 上下文上限 | Qwen Code / DeepSeek-V4.1-Flash | 已定位，处置中 | [查看](AI排障记录-01_上下文超限400.md) |
| 02 | 2026-10-21 | GitHub push 443 超时 | DeepSeek-Chat | 已解决 | [查看](20261021-github-push-443超时.md) |
| 03 | 2026-10-21 | 中文文件名重命名脚本报错、计数不一致 | DeepSeek-Chat | 已解决（10/10） | [查看](20261021-中文文件名重命名脚本排障.md) |
| 04 | 2026-10-21 | VS Code 接入内网模型 qwen3.5-122b | Qwen / DeepSeek-Chat | 部分解决（配置就绪，网络受限） | [查看](20261021-vscode接入内网模型排障.md) |

截图统一放在 `evidence/`，命名 `排障NN-证据N.png`。

## 证据文件对照

| 文件 | 位置 | 说明 |
| --- | --- | --- |
| `排障01-证据1~4.png` | `03-AI-Collaboration/evidence/` | 上下文超限 400 的会话界面与报错原文 |
| `fix-github-push.ps1` | 本地工作区 | 自动轮换 hosts IP 并回滚的推送脚本 |
| `hosts.backup.txt` / `hosts-change.log` | 本地工作区 | hosts 修改前的备份与结果日志 |
| `verify-qwen-endpoint.ps1` | 本地工作区 | 用 vLLM `/metrics` 计数器验证请求是否真的到达端点 |
| `vscode-接入内网模型-操作手册.md` | 本地工作区 | 完整接入步骤 + 报错对照表 |
| `rename_mapping.csv` | `01-Field-Discovery/raw_data/10-task-audit/` | 人工与 AI 两次重命名的实际映射 |
| 现场同框照 | `01-Field-Discovery/photos/10-task-audit/` | 含一张过程报错照片 |

## 待办

- [ ] 排障 01 的「结果验证」一栏待补：新会话续写是否成功
- [ ] 排障 04 拿到内网访问后，跑一次 `verify-qwen-endpoint.ps1` 并补截图