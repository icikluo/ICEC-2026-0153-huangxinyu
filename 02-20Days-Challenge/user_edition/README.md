# 课表提醒 用户版

这是「课表邮件提醒」程序的**分发给其他同学使用的版本**。

主程序（作者自用版）见上级目录 [`../main.py`](../main.py)。

> **当前版本：v1.1** —— 基于 8 位同学的真实使用反馈迭代改进，详见 [`../iterations/iteration-4.md`](../iterations/iteration-4.md)

---

## 有什么区别

| | 作者自用版（`../main.py`） | 用户版（本目录） |
|---|---|---|
| 运行方式 | 命令行 + GitHub Actions 定时 | **图形界面，双击运行** |
| 配置 | 编辑 `.env` 文件 | **界面填写，存 `config.json`** |
| 课表 | 固定 `schedule.csv` | **自由选择任意 CSV / xlsx** |
| 学期起始 | 硬编码 | **界面可设置** |
| 课前提醒 | 无 | **可配置提前 N 分钟** |
| 适用人群 | 开发者 | **普通同学** |

---

## v1.1 更新内容

依据 8 位同学的使用反馈，共实施 10 项改进：

| # | 改进 | 说明 |
|---|---|---|
| 1 | **CSV 编码自动识别** | 依次尝试 utf-8-sig / utf-8 / gbk / gb18030 / utf-16，用 Excel 存 CSV 也不会报错 |
| 2 | **支持 .xlsx** | 直接读 Excel 文件，彻底绕开编码问题（推荐） |
| 3 | **课前二次提醒** | 可配置提前 N 分钟（默认 20），发送时列出每节课的提醒时间点 |
| 4 | **界面美化** | 白色 + 浅粉配色，圆角果冻风控件 |
| 5 | 课表预览 | 查看本周每日课程安排 |
| 6 | 一键检测格式 | 指出具体哪个字段有问题 |
| 7 | 程序内嵌帮助 | 第四个标签页，不用翻外部文档 |
| 8 | 失败重试可视化 | 日志显示每次重试过程 |
| 9 | 发送记录本地保存 | `send_history.log` |
| 10 | 打包方式调整 | onefile → onedir（避免被 Defender 拦截）|

---

## 文件说明

| 文件 | 说明 |
|---|---|
| `main_user.py` | 用户版主程序（tkinter 图形界面，889 行）|
| `jelly.py` | 圆角果冻风格控件库（Canvas 手绘，314 行）|
| `课表模板.csv` | 课表格式模板 |
| `使用说明.md` | **给同学的完整教程**（授权码、课表填写、常见问题）|
| `v1.1-可执行程序/` | 打包好的程序（本地保留，不入库）|

---

## 打包成可执行程序

用户版通过 PyInstaller 打包，同学无需安装 Python。

### 打包命令

```powershell
pip install pyinstaller pandas openpyxl
python -m PyInstaller --onedir --windowed --name "课表提醒" `
  --hidden-import jelly --hidden-import openpyxl main_user.py
```

**产物**：`dist/课表提醒/`（含 `课表提醒.exe` 与 `_internal/` 依赖目录）

### 为什么用 onedir 而不是 onefile

| 方式 | 结果 | 原因 |
|---|---|---|
| `--onefile` | ❌ 启动报 `Could not create temporary directory!` | onefile 需将自身解压到 `%TEMP%`，被 Windows Defender 实时保护拦截 |
| `--onedir` | ✅ 正常运行 | 依赖文件直接放在目录中，无运行时解压 |

**代价**：分发给同学时需打包整个文件夹（含 `_internal`），不能只发 exe。

### 为什么不把可执行程序提交到仓库

- 体积较大（约 88 MB），会让仓库变重
- 二进制文件 Git 无法有效管理版本
- 已在 `.gitignore` 中排除，本地保留

---

## 同学的使用流程

```
1. 解压整个文件夹（不要只拷 exe）
2. 双击「课表提醒.exe」
   → 若弹出「Windows 已保护你的电脑」，点「更多信息」→「仍要运行」
3. 在「① 邮箱配置」填 QQ 邮箱、授权码、收件邮箱，保存
4. 在「② 课表设置」选课表文件（推荐 xlsx），填学期起始日期，保存
5. 点「一键检测格式」确认课表无误
6. 在「③ 发送与预览」点「立即发送今日课表」
```

完整教程见 **[使用说明.md](./使用说明.md)**。

---

## 技术实现

| 模块 | 说明 |
|---|---|
| GUI | tkinter（Python 标准库，无额外依赖）|
| 自定义控件 | `jelly.py`：Canvas 绘制的圆角按钮、输入框、卡片、分段选择器 |
| 配置存储 | `config.json`（与 exe 同目录，已 gitignore）|
| 课表解析 | pandas，支持 CSV（5 种编码）与 xlsx |
| 邮件发送 | `smtplib.SMTP_SSL`，QQ 邮箱 465 端口 |

### 关键实现

**多编码自动识别**：

```python
ENCODINGS = ("utf-8-sig", "utf-8", "gbk", "gb18030", "utf-16")
for enc in ENCODINGS:
    try:
        return pd.read_csv(path, encoding=enc, dtype=str)
    except (UnicodeDecodeError, UnicodeError):
        continue
```

**周次表达式**：支持 `3;5-13;16-18` 这种写法，表示第 3、5～13、16～18 周有课。

**学期周次计算**：

```python
current_week = (今天 - 学期第一周周一).days // 7 + 1
```

**滚动容器**：`ScrollableFrame` 类，内容超出窗口时自动显示滚动条。

---

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.1 | 2026-11-12 | **基于 8 位用户反馈升级**：多编码识别、xlsx 支持、课前提醒、界面重做、滚动支持 |
| v1.0 | 2026-11-05 | 首个图形界面版本，支持配置邮箱、选择课表、发送测试 |

---

*ICEC-2026-0153*