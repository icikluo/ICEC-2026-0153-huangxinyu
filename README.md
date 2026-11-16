# ICEC-2026-0153-huangxinyu

<p style="color: #888; font-size: 14px;">
<strong>个人简介</strong><br/>
我叫黄心瑜，来自人工智能技术应用 c3 班，虽然之前没有这类的基础，但我觉得不断向前是一个很有趣的过程，我有做好的信心与决心。
</p>

<p style="color: #888; font-size: 14px;">
<strong>选题声明</strong><br/>
第一阶段：我选择了课题 03 和课题 10<br/>
第二阶段：我选择了项目四（具体方向：课表邮件提醒程序）
</p>

---

## 仓库导航

### 01-Field-Discovery · 第一阶段（基础素养实地测评，10 选 2）✅ 已完成

| 课题 | 报告 | 原始数据 | 现场照片 | 图表 | 脚本 |
|---|---|---|---|---|---|
| **课题 03**<br/>教学楼与宿舍<br/>无线信号盲区测绘 | [分析报告](01-Field-Discovery/reports/topic03_final_report.md)<br/>[课题说明](01-Field-Discovery/reports/topic03_readme.md) | [数据表](01-Field-Discovery/raw_data/03-wireless-signal/课题03_数据表.xlsx)<br/>[CSV](01-Field-Discovery/raw_data/03-wireless-signal/measurements.csv)<br/>[dBm截图](01-Field-Discovery/raw_data/03-wireless-signal/截图_dbm/)<br/>[测速截图](01-Field-Discovery/raw_data/03-wireless-signal/截图_测速/)<br/>[录屏](01-Field-Discovery/raw_data/03-wireless-signal/录屏/) | [同框照](01-Field-Discovery/photos/03-wireless-signal/) | [图表](01-Field-Discovery/reports/figures-03/) | [脚本](01-Field-Discovery/ai_scripts/03-wireless-signal/) |
| **课题 10**<br/>日常数字任务耗时<br/>审计与 AI 批处理实证 | [最终报告](01-Field-Discovery/reports/topic10_final_report.md)<br/>[实验文档](01-Field-Discovery/reports/topic10/) | [原始数据](01-Field-Discovery/raw_data/10-task-audit/) | [过程照片](01-Field-Discovery/photos/10-task-audit/) | — | [脚本](01-Field-Discovery/ai_scripts/) |

- 第一阶段方案（含计划 vs 实际对照）：[phase1-plan.md](01-Field-Discovery/phase1-plan.md)

### 02-20Days-Challenge · 第二阶段（工坊项目挑战营，8 选 1）✅ 已完成

**选题**：项目四 —— 解决校园真实痛点的轻量化实用程序研发与日常运行日志验证
**具体方向**：课表邮件提醒程序

**核心交付物**：

| 类别 | 内容 | 入口 |
|---|---|---|
| **主程序** | 每日课表邮件提醒（Python + QQ 邮箱 SMTP + GitHub Actions 定时）| [main.py](02-20Days-Challenge/main.py) ｜ [课表](02-20Days-Challenge/schedule.csv) |
| **自动化配置** | 每天北京时间 07:30 自动运行，并自动提交日志 | [daily_reminder.yml](.github/workflows/daily_reminder.yml) |
| **7 天运行日志** | 连续 7 天定时触发，全部成功 | [daily_log.txt](02-20Days-Challenge/process_logs/daily_log.txt) |
| **每日检查表** | 逐日核对邮件、日志、Actions 状态 | [checkin.md](02-20Days-Challenge/process_logs/checkin.md) |
| **4 次迭代记录** | 乱码修复 → 周次维度 → 行粘连 → 用户反馈驱动升级 | [iterations/](02-20Days-Challenge/iterations/) |
| **8 位用户反馈** | 含截图、原话、评分、共性问题分析 | [user_feedback.md](02-20Days-Challenge/user_feedback.md) |
| **用户版程序** | 图形界面分发版（白色+浅粉果冻风，支持 xlsx/多编码/课前提醒）| [user_edition/](02-20Days-Challenge/user_edition/) |
| **过程截图** | 运营截图、AI 对话证据、用户使用截图共 33 张 | [screenshots/](02-20Days-Challenge/process_logs/screenshots/) |
| **方案文档** | 初期规划 | [phase2-plan.md](02-20Days-Challenge/phase2-plan.md) |

**关键数据**：

| 指标 | 结果 |
|---|---|
| 7 天日志 | 11/02 – 11/08，**7/7 天全部成功**，`trigger=schedule` |
| 平均执行耗时 | 3168 ms（区间 2762–3770 ms）|
| Git 迭代次数 | **4 次**（要求 ≥3 次）|
| 用户反馈 | **8 位**，平均评分 4.25 / 5 |
| 采纳的用户建议 | CSV 编码自动识别、支持 xlsx、课前二次提醒、界面美化 |

### 03-AI-Collaboration · 全程 AI 协作与排障记录 ✅ 已完成

贯穿第一、第二阶段的 AI 协作过程记录，共 7 份排障文档 + 41 张证据截图。

| 编号 | 主题 | 文档 |
|---|---|---|
| 01 | 上下文超限 400 排障 | [打开](03-AI-Collaboration/AI排障记录-01_上下文超限400.md) |
| 02 | 实验数据放错目录 | [打开](03-AI-Collaboration/AI排障记录-02_实验数据放错目录.md) |
| 03 | AI 代写报告编造与篡改 | [打开](03-AI-Collaboration/AI排障记录-03_AI代写报告编造与篡改.md) |
| 04 | exe 打包临时目录失败 | [打开](03-AI-Collaboration/AI排障记录-04_exe打包临时目录失败.md) |
| 05 | 千问命名规则空格失准 | [打开](03-AI-Collaboration/AI排障记录-05_千问命名规则空格失准.md) |
| 06 | 跨端 AI 方案改进 | [打开](03-AI-Collaboration/AI排障记录-06_跨端AI方案改进.md) |
| 07 | AI 过度执行自写秒表 | [打开](03-AI-Collaboration/AI排障记录-07_AI过度执行自写秒表.md) |

- 证据截图：[evidence/](03-AI-Collaboration/evidence/)

---

## 课题 03 核心结论速览

| 点位 | RSSI (dBm) | 下载 (Mbps) | 延迟 (ms) | 判定 |
|---|---|---|---|---|
| 两楼连接处 | **−41.0** | 86.2 | **42** | ✅ 正常（最强，波导效应） |
| 5 楼大厅 | −48.2 | 81.5 | 121 | ✅ 正常（基准） |
| 露台 | −53.8 | 109.4 | 66 | ✅ 正常 |
| 5 楼电梯口 | −65.5 | 74.8 | 353 | ✅ 正常 |
| 8 楼电梯口 | −71.0 | 70.0 | 378 | ⚠️ 临界 |
| 2 楼电梯口 | −71.0 | 23.6 | **794** | ⚠️ 临界（延迟最差） |
| **5 楼厕所** | **−82.0** | 18.2 | 610 | ❌ **盲区** |
| **电梯运行中** | 无读数 | 未连接 | 未连接 | ❌ **重度盲区** |
| **2 楼电梯内部** | **−87.5** | 未连接 | 未连接 | ❌ **盲区** |

**三个关键发现：**
1. **厕所 −82.0 dBm** = 墙体类盲区（多重隔断 + 金属管道）；
2. **电梯 = 屏蔽类盲区**：5 楼完全读不到信号；2 楼 −87.5 dBm 有信号但测速 3 次全部失败（"有 Wi-Fi 图标、无业务"）；
3. **信号达标 ≠ 体验达标**：2 楼电梯口 RSSI −71 按教材不算盲区，但延迟 794 ms → 属**容量盲区**，与覆盖盲区是两种不同的病。

---

## 目录约定

```
ICEC-2026-0153-huangxinyu/
├── .github/workflows/
│   └── daily_reminder.yml         # 第二阶段：每天 07:30 定时发课表并提交日志
├── 01-Field-Discovery/
│   ├── phase1-plan.md             # 第一阶段方案
│   ├── reports/                   # 报告（每课题一份 *_final_report.md）
│   │   ├── topic03_final_report.md
│   │   ├── topic10_final_report.md
│   │   ├── figures-03/            # 课题03 图表
│   │   ├── figures-03-v1-20261028/# 第一轮图表（归档）
│   │   └── topic10/               # 课题10 实验文档
│   ├── raw_data/<课题名>/          # 原始数据，按课题分目录
│   ├── photos/<课题名>/            # 现场同框照 / 环境照，按课题分目录
│   └── ai_scripts/<课题名>/        # 数据处理脚本（可复现）
├── 02-20Days-Challenge/           # 第二阶段
│   ├── phase2-plan.md             # 初期方案
│   ├── main.py                    # 主程序（作者自用版，GitHub Actions 调用）
│   ├── schedule.csv               # 课表数据（7 列，支持周次表达式）
│   ├── .env.example               # 密钥模板（真实 .env 不入库）
│   ├── iterations/                # 迭代记录 iteration-1 ~ 4
│   ├── process_logs/
│   │   ├── daily_log.txt          # 运行日志（每行一次执行记录）
│   │   ├── checkin.md             # 每日人工检查表
│   │   └── screenshots/           # 过程截图
│   │       ├── day*-mail.png      # 每日收到的邮件
│   │       ├── evidence/          # AI 对话过程证据
│   │       └── users/             # 8 位同学的使用截图
│   ├── user_edition/              # 用户版（图形界面分发包）
│   │   ├── main_user.py           # 用户版主程序
│   │   ├── jelly.py               # 圆角果冻风格控件库
│   │   ├── 使用说明.md
│   │   ├── 课表模板.csv
│   │   └── v1.1-可执行程序/        # 打包产物（本地保留，不入库）
│   └── user_feedback.md           # 8 位用户反馈汇总
└── 03-AI-Collaboration/           # 全程 AI 协作与排障记录
    ├── AI排障记录-01 ~ 07.md
    └── evidence/                  # 对应证据截图
```

**设计原则**：
- 每个课题独立成目录，`raw_data` / `photos` / `ai_scripts` 三者按课题名一一对应；
- 数据可溯源：每条记录都能对应回截图或录屏；
- **实验做两轮时，第一轮完整归档**（`*-v1-YYYYMMDD`），不删除——保留"发现问题 → 改进方法 → 重测"的完整过程。
- **密钥与二进制不入库**：`.env`、`config.json`、`.exe` 及打包依赖目录均由 `.gitignore` 排除，本地保留。

---

## 数据规范

| 约定 | 说明 |
|---|---|
| 测不出就写「未连接」 | 不填 0、不编造 |
| 截图逐条溯源 | 数据表「截图对照」页可查每条记录对应的文件 |
| 照片保留 EXIF | 拍摄时间未剥离，可验证现场真实性 |
| 录屏压缩入库 | 720p、总 3.6 MB，dBm 数字清晰可读 |