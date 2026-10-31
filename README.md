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

### 02-20Days-Challenge · 第二阶段（工坊项目挑战营，8 选 1）🚧 进行中

选题：**项目四** —— 解决校园真实痛点的轻量化实用程序研发与日常运行日志验证
具体方向：课表邮件提醒程序

- 方案：[phase2-plan.md](02-20Days-Challenge/phase2-plan.md)
- 源码：[src/](02-20Days-Challenge/src/) ｜ 运行日志：[process_logs/](02-20Days-Challenge/process_logs/) ｜ 迭代记录：[iterations/](02-20Days-Challenge/iterations/)

### 03-AI-Collaboration · 关键 AI 提问与排障对话记录

| 编号 | 主题 | 文档 |
|---|---|---|
| 01 | 上下文超限 400 排障 | [打开](03-AI-Collaboration/AI排障记录-01_上下文超限400.md) |
| 02 | 实验数据放错目录 | [打开](03-AI-Collaboration/AI排障记录-02_实验数据放错目录.md) |
| 03 | AI 代写报告编造与篡改 | [打开](03-AI-Collaboration/AI排障记录-03_AI代写报告编造与篡改.md) |

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
└── 03-AI-Collaboration/           # AI 排障记录
```

**设计原则**：
- 每个课题独立成目录，`raw_data` / `photos` / `ai_scripts` 三者按课题名一一对应；
- 数据可溯源：每条记录都能对应回截图或录屏；
- **实验做两轮时，第一轮完整归档**（`*-v1-YYYYMMDD`），不删除——保留"发现问题 → 改进方法 → 重测"的完整过程。

---

## 数据规范

| 约定 | 说明 |
|---|---|
| 测不出就写「未连接」 | 不填 0、不编造 |
| 截图逐条溯源 | 数据表「截图对照」页可查每条记录对应的文件 |
| 照片保留 EXIF | 拍摄时间未剥离，可验证现场真实性 |
| 录屏压缩入库 | 720p、总 3.6 MB，dBm 数字清晰可读 |