# 迭代 1：日志中文乱码修复

- **日期**：2026-11-02
- **触发方式**：本地人工检查日志时发现
- **涉及文件**：`process_logs/daily_log.txt`（读取方式）、`main.py`（无代码改动）
- **证据**：`process_logs/screenshots/day1-log-bug.png`（修复前）、`day1-log.png`（修复后）

---

## 一、现象

程序运行正常，`process_logs/daily_log.txt` 已成功写入两行记录：

```
2026-11-01 23:56:39 +0800 | trigger=local | SUCCESS | 星期=星期日 | 课表总数=13 | ...
2026-11-02 00:03:50 +0800 | trigger=local | SUCCESS | 星期=星期一 | 课表总数=13 | ...
```

但在 PowerShell 中用 `Get-Content process_logs\daily_log.txt` 查看时，中文部分全部乱码：

```
2026-11-01 23:56:39 +0800 | trigger=local | SUCCESS | 甯濇湡=鍛戒竴 | 璇炬暟=13 | ...
```

## 二、定位过程

| 观察 | 推断 |
|---|---|
| `2026-11-01 23:56:39 +0800`、`trigger=local`、`SUCCESS` 显示正常 | 英文、数字、符号没问题 |
| 只有「星期」「课表总数」「收件人」「耗时」等中文字段乱码 | 属于**编码解释**问题，不是文件损坏 |
| 用 Python 打开日志文件仍能正确读到中文 | **写入端正确（UTF-8）**，问题在读取端 |
| 乱码形如 `甯濇湡`（"星期"按 GBK 解释 UTF-8 字节的典型结果） | PowerShell 默认按 ANSI/GBK 解码 UTF-8 内容 |

**结论**：日志文件本身是合法的 UTF-8，问题出在 PowerShell 的默认读取编码。

## 三、根因

- `main.py` 写日志时已显式使用 `encoding="utf-8"`，写入正确。
- Windows PowerShell 5.x 的 `Get-Content` 默认按系统 ANSI 代码页（简体中文系统为 GBK/CP936）解释文件。
- UTF-8 的中文是 3 字节，被 GBK 两两组合解释后成为乱码，因此出现「英文正常、中文全乱」的特征。

## 四、修复

### 方案

不改代码，修正**读取方式**（同时把正确的查看方式写进文档，避免以后再踩）：

```powershell
# 修复后：显式指定 UTF-8 读取
Get-Content process_logs\daily_log.txt -Encoding UTF8

# 若终端本身仍显示异常，先统一控制台输出编码
[Console]::OutputEncoding = [Text.Encoding]::UTF8
Get-Content process_logs\daily_log.txt -Encoding UTF8
```

### 验证

修复后读取结果：

```
2026-11-01 23:56:39 +0800 | trigger=local | SUCCESS | 星期=星期日 | 课表总数=13 | 今日课程数=0 | 邮件=SUCCESS | 收件人=3*********@qq.com | retry=0 | 耗时=1367ms
2026-11-02 00:03:50 +0800 | trigger=local | SUCCESS | 星期=星期一 | 课表总数=13 | 今日课程数=3 | 邮件=SUCCESS | 收件人=3*********@qq.com | retry=0 | 耗时=1099ms
```

中文字段全部正常，日志内容与程序执行结果一致。

## 五、对比

| 项 | 修复前 | 修复后 |
|---|---|---|
| 读取命令 | `Get-Content process_logs\daily_log.txt` | `Get-Content process_logs\daily_log.txt -Encoding UTF8` |
| 中文显示 | 乱码（`甯濇湡=鍛戒竴`） | 正常（`星期=星期日`） |
| 数据本身 | 正确（UTF-8） | 正确（UTF-8） |
| 证据截图 | `day1-log-bug.png` | `day1-log.png` |

## 六、经验与后续

1. **日志写入端已显式指定 UTF-8**，这一设计在本次问题中避免了数据损坏，无需改代码。
2. 在 Windows 上查看含中文的 UTF-8 文本，必须显式指定编码，否则默认按 ANSI 解码。
3. 同理，读取 `schedule.csv` 时已使用 `encoding="utf-8-sig"` 兼容带 BOM 的 Excel 导出文件。
4. GitHub Actions 运行在 Ubuntu 环境，默认 UTF-8，不受此问题影响；该问题仅出现在 Windows 本地查看环节。