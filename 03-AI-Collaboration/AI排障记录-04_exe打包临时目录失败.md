# AI 排障记录 04：用户版 exe 双击无反应 —— PyInstaller 打包方式与运行环境冲突

- **日期**：2026-11-12 23:00 ~ 23:40
- **场景**：第二阶段「课表提醒」第 4 次迭代完成，用 PyInstaller 打包用户版 v1.1
- **环境**：Windows 10/11，Python 3.14.7，PyInstaller 6.22.3
- **关键配置**：`--onefile --windowed` 打包，产物 34.8 MB

## 现象

第 4 次迭代（基于 8 位用户反馈的 v1.1 改造）完成后，执行打包：

```powershell
python -m PyInstaller --noconfirm --onefile --windowed `
  --name "课表提醒" --hidden-import jelly --hidden-import openpyxl `
  --add-data "jelly.py;." --clean main_user.py
```

打包日志显示 `Build complete!`，产物 `课表提醒.exe`（34.8 MB）生成成功。

**但双击 exe 后无任何窗口出现**，任务栏无图标，进程立即退出。用命令行调试版运行时输出：

```
[PYI-24040:ERROR] Could not create temporary directory!
```

### 证据截图

- ![排障04-证据1：首次假设"沙箱环境限制"](evidence/排障04-证据1.png)
- ![排障04-证据2：假设"SmartScreen 拦截"](evidence/排障04-证据2.png)
- ![排障04-证据3：解除 SmartScreen 后仍报真实错误](evidence/排障04-证据3.png)
- ![排障04-证据4：C 盘空间仅剩 1.3 GB](evidence/排障04-证据4.png)
- ![排障04-证据5：Defender 实时保护拦截解压行为](evidence/排障04-证据5.png)
- ![排障04-证据6：改用 onedir 后成功](evidence/排障04-证据6.png)

## 排查过程（五次假设，前四次被推翻）

### 假设 1：沙箱环境限制，真实电脑不会有此问题 ❌

**判断**：认为 exe 无法启动是当前执行环境无法写入临时目录造成，属于环境限制，用户真实电脑可正常运行。

**推理依据**：`Could not create temporary directory!` 是 PyInstaller 释放自身到临时目录时的报错。

**被推翻**：用户手动双击 exe，**同样出现错误对话框** → 证明真实环境同样失败，不是沙箱特有问题。

### 假设 2：Windows SmartScreen 拦截 ❌

**判断**：双击后弹出「Windows 已保护你的电脑 / Microsoft Defender SmartScreen 阻止了无法识别的应用启动」→ 判定为 SmartScreen 对未签名程序的拦截。

**推理依据**：v1.0 的 exe 可以运行，v1.1 是新编译的、无发行商签名。

**被推翻**：用户按提示点击「更多信息 → 仍要运行」后，**又弹出新错误**：`Could not create temporary directory!` → SmartScreen 只是第一道拦截，**解除后仍有真实故障**。

### 假设 3：磁盘空间不足 ✅（部分正确）

**判断**：回到原始报错字面含义，列出三个可能并逐一排查：

| 可能原因 | 排查结果 |
|---|---|
| **磁盘 C 盘空间不足** | ✅ **命中**：实测「已用 98.7 GB / 总 100.0 GB / **剩余 1.3 GB**」|
| TEMP 目录权限问题 | ❌ 排除：手动 `New-Item` 创建临时目录成功且可写 |
| 环境变量异常 | ❌ 排除：`TEMP` / `TMP` 均指向存在的可写目录 |

**关键推理**：PyInstaller `--onefile` 启动时需将自身解压到 `%TEMP%\_MEIxxxxxx`，约需 100~200 MB。

**处置**：清理 C 盘（Temp 临时文件、Edge 缓存、缩略图缓存），释放 **4.74 GB**，可用空间 1.28 GB → **6.02 GB**。

### 假设 4：Windows Defender 拦截 ✅（真实原因）

**背景**：清理磁盘后空间充足，**仍报同样错误** → 空间不是唯一原因。

**对照实验**：

| 实验项 | 结果 | 推论 |
|---|---|---|
| 手动创建临时目录 | ✅ 成功 | 目录权限正常 |
| 运行 exe 创建临时目录 | ❌ 失败 | 问题出在 exe 行为而非系统 |
| Defender 实时保护状态 | **True（开启）** | 存在拦截可能 |

**结论**：**Windows Defender 实时保护拦截了 PyInstaller 的运行时解压行为**。

**推理链**：
1. `--onefile` 的 exe 启动瞬间，会向临时目录释放数十个文件（含 `python311.dll` 等）
2. Defender 的启发式规则将「未知程序批量释放 DLL 并执行」识别为可疑行为
3. 拦截后 PyInstaller 无法完成解压 → 报 `Could not create temporary directory!`

### 假设 5：更换打包方式 ✅（解决方案）

不再与 Defender 对抗，改用 `--onedir`：

```powershell
python -m PyInstaller --noconfirm --onedir --windowed `
  --name "课表提醒_文件夹版" --hidden-import jelly --hidden-import openpyxl `
  --add-data "jelly.py;." main_user.py
```

**验证结果**：文件夹版**双击正常启动**，四个标签页渲染正常，功能可用。

## 报错原文与含义

| 报错原文 | 含义 |
|---|---|
| `Could not create temporary directory!` | PyInstaller 无法创建 `%TEMP%\_MEIxxxxxx` 解压目录 |
| `Windows 已保护你的电脑` | SmartScreen 对未签名 exe 的默认拦截（与本故障无关，是独立的第一道门）|
| `[PYI-24040:ERROR]` | PyInstaller bootloader 层错误，非 Python 代码异常 |

## 根因

**根因有两层**：

1. **表层**：C 盘可用空间仅 1.3 GB，`--onefile` 需要 100~200 MB 临时空间解压自身，空间紧张导致首次解压失败。
2. **深层**：**Windows Defender 实时保护拦截 PyInstaller onefile 的运行时解压行为** —— 这是清理磁盘到 6.02 GB 后仍失败的原因。

**一句话**：`--onefile` 打包方式依赖运行时解压，而运行时解压同时受 **磁盘空间** 与 **安全软件** 两重约束。

## 处置方案

### 根本解决

改用 `--onedir`（文件夹版）打包：

| 项目 | `--onefile` | `--onedir` |
|---|---|---|
| 运行时行为 | 启动时解压到 `%TEMP%` | **直接加载同目录文件** |
| 临时目录依赖 | ✅ 强依赖 | ❌ 不依赖 |
| 杀软拦截风险 | 高（批量释放行为）| **低（无释放行为）** |
| 启动速度 | 慢（需解压 100~200 MB）| **快** |
| 分发方式 | 单个 exe | 文件夹（exe + `_internal/`）|

### 环境优化

清理 C 盘，释放 4.74 GB（对系统整体也有益，非仅为本项目）。

### 分发适配

使用说明中明确：**`_internal` 文件夹必须与 exe 一起分发**，不能只发 exe。

## 长期习惯（防复发）

1. **分发类打包优先用 `--onedir`**：分发体验稍差（是文件夹），但不受杀软误杀影响，启动也更快。
2. **保留 console 版用于排障**：`--windowed` 会吞掉错误信息，遇到启动失败先用 `--console` 打一个版本看真实输出。
3. **环境问题优先做对照实验**：手动操作 vs 程序操作、有杀软 vs 无杀软，最快锁定是系统限制还是程序问题。
4. **不要第一反应归因于"环境特殊"**：本次首次判断为"沙箱限制，你电脑上没问题"，但用户实测同样失败 —— **必须要求用户侧验证，不能替用户下结论**。
5. **C 盘空间要留余量**：临时目录、编译产物、包管理器缓存都吃 C 盘，建议长期保持 ≥10 GB 空闲。

## 结果验证

| 验证项 | 结果 |
|---|---|
| 文件夹版 exe 双击启动 | ✅ 窗口正常显示 |
| 四个标签页渲染 | ✅ 正常 |
| 界面配色（浅粉果冻风 v1.1）| ✅ 正常 |
| 课表文件选择 | ✅ 正常 |
| 5 种编码格式读取（UTF-8/BOM/GBK/GB18030）| ✅ 全部通过 |
| .xlsx 读取 | ✅ 通过 |
| 真实邮件发送 | ✅ 发送成功 |

**最终发布版**：PyInstaller `--onedir` 文件夹版，77.4 MB（exe 9.2 MB + `_internal` 68 MB）。