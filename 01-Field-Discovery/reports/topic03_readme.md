# 课题 03 · 教学楼无线信号盲区测绘

ICEC-2026 第一阶段（基础素养实地测评）选考课题。

| 项目 | 内容 |
|---|---|
| 实验地点 | ICEC 校区 1 教学楼（商贸学院，近图书馆） |
| 实验日期 | 2026-10-28 17:05–17:37 |
| 采样点位 | **8 个**（与课题要求一致） |
| 采样组数 | **25 条记录 = 24 组有效测速**（要求 24 组）+ 1 张「无网络」佐证 |
| 主指标 | 下载速率 MB/s（1 MB/s = 8 Mbps） |
| 盲区判定 | 下载均值 < 1 MB/s 或 0 KB/s |

## 核心结论

| 点位 | 均值 | 占基准 | 判定 |
|---|---|---|---|
| 大厅（基准） | 9.84 MB/s | 100% | 正常 |
| 两楼连接处 | 8.76 MB/s | 89.0% | 正常 |
| 8 楼电梯口 | 9.23 MB/s | 93.8% | 正常 |
| 露台 | 8.09 MB/s | 82.2% | 正常（波动大） |
| 5 楼电梯口 | 7.65 MB/s | 77.7% | 正常 |
| 2 楼电梯口 | 4.54 MB/s | 46.1% | 偏弱（疑似容量受限） |
| **厕所** | **1.49 MB/s** | **15.1%** | **盲区** |
| **电梯运行中** | **0.00 MB/s** | **0%** | **重度盲区（App 报无网络）** |

## 目录结构（已按本仓库约定归档）

```
01-Field-Discovery/
├── reports/
│   ├── topic03_final_report.md          # ★ 课题03 主报告
│   └── figures-03/                      # ★ 三张图表 PNG + Excel 图表
│       ├── chart1_下载速率对比.png
│       ├── chart2_单次测量散点.png
│       ├── chart3_楼层对比.png
│       └── 课题03_图表.xlsx
├── raw_data/03-wireless-signal/
│   ├── 课题03_数据表.xlsx                # ★ 4 个工作表
│   ├── measurements.csv                 # ★ 原始数据（改这里重跑脚本）
│   ├── pose_points.csv                  #   8 个点位结构/材质
│   └── 截图/                             # ★ 24 张计入统计 + 3 张 2F 另一位置参考
├── photos/03-wireless-signal/
│   ├── P1–P9_*_同框.jpg                  # ★ 8 张本人现场同框照（含 EXIF 时间）
│   └── 环境补充/                         #   11 张环境全景照
├── ai_scripts/03-wireless-signal/
│   ├── make_workbook.py                 # csv → Excel
│   ├── make_charts.py                   # csv → 三张图
│   └── check_photos.py                  # 齐全性 / 重复 / 截图溯源自检
└── topic03_readme.md                    # 本文件（说明文档）
```

## 交付物对照课程要求

| 要求 | 对应文件 | 状态 |
|---|---|---|
| 8 个不同遮挡特征点位 | 8 个点位，见 `../raw_data/03-wireless-signal/pose_points.csv` | ✅ |
| 每点位连续测试 3 次 | `../raw_data/03-wireless-signal/measurements.csv`（P5 多测 1 次） | ✅ |
| 24 组网络测速原始数据 | `../raw_data/03-wireless-signal/课题03_数据表.xlsx`（24 组） | ✅ |
| 点位照片（本人同框） | `../photos/03-wireless-signal/P1–P9_*_同框.jpg` | ✅ 8 张 |
| 分析报告（含图表） | `课题03_分析报告.md` + `charts/` | ✅ |
| 墙体材质与多径衰减规律 | 报告第三章 | ✅ |
| 改进建议 | 报告第四章（P0–P3 优先级） | ✅ |
| 信号强度 dBm | `measurements.csv` 中保留空列 | ⚠️ 本组未采集，已写明局限 |

## 「信号强度与延迟」这一项怎么处理的

课题原文要求「信号强度与延迟」，但所用测速 App **只输出平均速率（MB/s）**，没有 RSSI(dBm) 和 Ping(ms)。

本项目的处理方式（**诚实优先，不编数字**）：

1. 主指标改用**下载速率**——它同样是"用户真实体感"的直接度量，且截图可逐条溯源；
2. 盲区判定口径改为 **< 1 MB/s 或 0 KB/s**；
3. `measurements.csv` 中 `信号强度(RSSI dBm)` / `Ping延迟(ms)` 两列**保留但留空**，Excel 中标黄提示补测；
4. 报告第五章「局限与改进方向」**主动写明这一缺口**。

**补测后**：把 dBm 填进 CSV → 重跑三个脚本 → 图表与判定自动更新 → 再 commit 一次，`git log` 里就有"补测 → 更新"的完整过程。

## 复现

```powershell
pip install openpyxl Pillow
cd "01-Field-Discovery/ai_scripts/03-wireless-signal"
python make_workbook.py
python make_charts.py
python check_photos.py
```

> 注意：脚本按「上一级目录的 raw_data / charts」定位文件，运行时请先 `cd` 到 `ai_scripts/03-wireless-signal`，或直接在该目录下运行。

全程无需联网、无需 matplotlib。