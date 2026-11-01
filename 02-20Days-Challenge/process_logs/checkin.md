# 每日运行检查记录

每天北京时间 07:30 之后人工检查三项，确认程序真实在跑：

1. QQ 邮箱是否收到「今日课表提醒」邮件
2. GitHub 仓库 `process_logs/daily_log.txt` 是否新增一行
3. GitHub Actions 当天运行是否为绿色（红色说明有报错，需截图存档）

## 检查表

| 日期 | 星期 | 邮件收到 | 日志新增 | 运行方式 | 今日课程数 | 耗时(ms) | 截图 | 备注 |
|---|---|---|---|---|---|---|---|---|
| 2026-11-01 | 星期日 | ✅ 收到 | ✅ 第 1 行 | 本地测试 | 0 | 1367 | day1-mail-nowork.png | 无课日分支验证，邮件显示「今天没有课」 |
| 2026-11-02 | 星期一 | ✅ 收到 | ✅ 第 2 行 | 本地测试 | 3 | 1099 | day1-mail-workday.png | 有课日分支验证，邮件列出 3 节课 |

## 截图清单

| 文件 | 内容 | 说明 |
|---|---|---|
| `day1-terminal.png` | 终端运行输出 | `python main.py` 执行成功，显示 SUCCESS 与耗时 |
| `day1-log.png` | 日志文件内容（修复后） | `daily_log.txt` 内两行记录，UTF-8 正常显示 |
| `day1-log-bug.png` | 日志乱码现场（修复前） | PowerShell 默认按 ANSI 解码导致中文乱码，详见 `iterations/iteration-1.md` |
| `day1-mail-nowork.png` | 无课日邮件 | 周日：今天没有课，好好休息 |
| `day1-mail-workday.png` | 有课日邮件 | 周一：3 节课，含时间/地点/教师 |

## 迭代记录

| 迭代 | 日期 | 问题 | 状态 | 文档 |
|---|---|---|---|---|
| 迭代 1 | 2026-11-02 | 日志中文乱码（读取编码） | ✅ 已修复 | `iterations/iteration-1.md` |

## 说明

- 截图存放在 `process_logs/screenshots/`，命名规则 `dayN-<内容>.png`
- 若某天失败，**失败日志本身就是「报错记录」证据**，请截图并在备注写明错误类型
- 日志已做脱敏：不含课程名、教室、教师、完整邮箱；密钥不入日志
- 本地运行使用 `.env` 文件（已被 `.gitignore` 忽略），GitHub Actions 使用 Repository Secrets