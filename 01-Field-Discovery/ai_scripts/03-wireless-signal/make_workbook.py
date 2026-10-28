# -*- coding: utf-8 -*-
"""
课题03 - 原始数据表生成器（真实数据结构）

读取 raw_data/measurements.csv（21+ 组实测数据，抄自手机测速截图），
生成 raw_data/课题03_数据表.xlsx，含 4 个工作表：

  原始数据  —— 逐条记录（含未采集字段留空，便于后续补测）
  点位汇总  —— 各点位 3 次均值 / 最值 / 标准差 / 盲区判定
  截图对照  —— 每条数据 ↔ 手机截图文件 ↔ 现场照片，一一对应可溯源
  填写说明  —— 单位、口径、数据缺口说明

关键口径：
  - 主指标 = 下载速率 (MB/s)，取自手机测速 App 截图
  - 1 MB/s = 8 Mbps（App 的「相当于 xx 兆宽带」即按此换算）
  - RSSI(dBm) 与 Ping(ms) 本组未采集，留空；补测后填入即可自动纳入统计

用法：
    python tools/make_workbook.py
"""

import csv
import io
import re
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "raw_data"
MEASUREMENTS = RAW / "measurements.csv"
POINTS = RAW / "pose_points.csv"
OUT = RAW / "课题03_数据表.xlsx"

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor="1F4E79")
HEAD_FONT = Font(bold=True, color="FFFFFF", size=11)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
RED_FILL = PatternFill("solid", fgColor="F8CBAD")
GREEN_FILL = PatternFill("solid", fgColor="C6E0B4")
YELLOW_FILL = PatternFill("solid", fgColor="FFE699")

# 盲区判定阈值（课题统一口径）
BLIND_DBM = -80


def num(text):
    """把 '865KB/s'、'2.59'、'' 解析成 float；无数据返回 None。"""
    s = (text or "").strip()
    if not s or s in ("超时", "无服务", "无数据", "无网络", "-", "/"):
        return None
    try:
        return float(re.findall(r"-?\d+\.?\d*", s)[0])
    except IndexError:
        return None


def load(path):
    """自动识别编码：Excel 另存会变成 GBK，脚本自己存的是 UTF-8。"""
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "gbk", "gb18030"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise SystemExit(f"无法识别 {path} 的编码")
    return list(csv.DictReader(io.StringIO(text, newline="")))


def style_header(ws, widths):
    for c in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = CENTER
        cell.border = BORDER
    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 32
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def main():
    rows = load(MEASUREMENTS)
    points = load(POINTS)

    wb = Workbook()

    # ---------------- Sheet 1: 原始数据 ----------------
    ws = wb.active
    ws.title = "原始数据"
    headers = [
        "点位编号", "点位名称", "楼层", "遮挡特征", "测量序号",
        "信号强度 RSSI(dBm)", "Ping延迟(ms)", "下载速度(MB/s)", "下载速率(Mbps)",
        "截图时间", "证据截图文件名", "现场照片文件名", "备注",
    ]
    ws.append(headers)
    for r in rows:
        ws.append([
            r["点位编号"], r["点位名称"], r["楼层"], r["遮挡特征"], r["测量序号"],
            r["信号强度(RSSI dBm)"], r["Ping延迟(ms)"],
            r["下载速度(MB/s)"], r["下载速率(Mbps)"],
            r["截图时间"], r["截图文件名"], r["照片文件名"], r["备注"],
        ])
    style_header(ws, [10, 18, 6, 22, 10, 18, 14, 16, 16, 10, 20, 24, 26])
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORDER
            if cell.column not in (4, 12, 13):
                cell.alignment = CENTER
        # 没测到的字段标黄，提醒补测
        for idx in (6, 7):
            c = row[idx - 1]
            if c.value in ("", None):
                c.fill = YELLOW_FILL
    ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"

    # ---------------- Sheet 2: 点位汇总 ----------------
    ws2 = wb.create_sheet("点位汇总")
    ws2.append([
        "点位编号", "点位名称", "楼层", "遮挡特征",
        "下载均值(MB/s)", "下载最好(MB/s)", "下载最差(MB/s)", "标准差(MB/s)",
        "相对基准衰减", "连通性", "盲区判定", "判定依据",
    ])

    dl_rows = []
    base_avg = None
    for p in points:
        pid = p["点位编号"]
        mine = [r for r in rows if r["点位编号"] == pid]
        dl = [num(r["下载速度(MB/s)"]) for r in mine]
        # 0 表示测速为 0KB/s，也计入均值（这是真实的「零吞吐」）
        dl_ok = [v for v in dl if v is not None]
        avg = sum(dl_ok) / len(dl_ok) if dl_ok else None
        if pid == "P1":
            base_avg = avg
        std = None
        if len(dl_ok) > 1:
            std = (sum((x - avg) ** 2 for x in dl_ok) / (len(dl_ok) - 1)) ** 0.5
        dl_rows.append({"pid": pid, "avg": avg, "std": std})

    for p in points:
        pid = p["点位编号"]
        mine = [r for r in rows if r["点位编号"] == pid]
        dl = [num(r["下载速度(MB/s)"]) for r in mine]
        dl_ok = [v for v in dl if v is not None]
        avg = sum(dl_ok) / len(dl_ok) if dl_ok else None
        std = None
        if len(dl_ok) > 1:
            std = (sum((x - avg) ** 2 for x in dl_ok) / (len(dl_ok) - 1)) ** 0.5

        if not dl_ok:
            conn, blind, reason = "未采集", "无法判定", "本点位缺少测速截图，需补测"
        elif avg == 0:
            conn, blind, reason = "断开", "是", "测速 0KB/s 且 App 报「无网络」，吞吐为零"
        elif avg < 1.0:
            conn, blind, reason = "可用但极差", "是", f"均值 {avg:.2f} MB/s < 1 MB/s 阈值"
        else:
            conn, blind, reason = "正常", "否", f"均值 {avg:.2f} MB/s ≥ 1 MB/s"

        drop = ""
        if avg is not None and base_avg:
            drop = f"{avg / base_avg * 100:.1f}%"

        ws2.append([
            pid, p["点位名称"], p["楼层"], p["遮挡特征"],
            round(avg, 2) if avg is not None else "未采集",
            round(max(dl_ok), 2) if dl_ok else "未采集",
            round(min(dl_ok), 2) if dl_ok else "未采集",
            round(std, 2) if std is not None else "",
            drop, conn, blind, reason,
        ])

    style_header(ws2, [10, 18, 6, 24, 16, 16, 16, 14, 14, 14, 12, 46])
    for row in ws2.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORDER
            if cell.column not in (4, 12):
                cell.alignment = CENTER
        if row[10].value == "是":
            for i in (4, 6, 10):
                row[i].fill = RED_FILL
        elif row[10].value == "否":
            row[10].fill = GREEN_FILL
            row[4].fill = GREEN_FILL
        elif row[10].value == "无法判定":
            for i in (4, 6, 10):
                row[i].fill = YELLOW_FILL

    chart = BarChart()
    chart.type = "col"
    chart.title = "各点位下载速率均值（MB/s）— 红色为盲区"
    chart.y_axis.title = "下载速率 (MB/s)"
    chart.x_axis.title = "点位"
    data = Reference(ws2, min_col=5, min_row=1, max_row=ws2.max_row)
    cats = Reference(ws2, min_col=2, min_row=2, max_row=ws2.max_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 9
    chart.width = 22
    chart.legend = None
    ws2.add_chart(chart, "A14")

    # ---------------- Sheet 3: 截图对照 ----------------
    ws3 = wb.create_sheet("截图对照")
    ws3.append(["点位编号", "测量序号", "现场截图文件", "现场照片文件", "截图时间", "核对结果"])
    for r in rows:
        ok = "有截图" if r["截图文件名"] else "缺截图"
        if r["备注"] and "缺失" in r["备注"]:
            ok = "缺截图"
        ws3.append([r["点位编号"], r["测量序号"], r["截图文件名"], r["照片文件名"],
                    r["截图时间"], ok])
    style_header(ws3, [10, 10, 22, 26, 10, 12])
    for row in ws3.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORDER
            cell.alignment = CENTER
        if row[5].value == "缺截图":
            row[5].fill = YELLOW_FILL

    # ---------------- Sheet 4: 填写说明 ----------------
    ws4 = wb.create_sheet("填写说明")
    notes = [
        ["项目", "说明"],
        ["数据来源", "2026-10-28 17:05—17:37，小米 17 手机自带/第三方测速 App，界面截图见「截图对照」表"],
        ["主指标", "下载速度 MB/s，取自每张截图的「您的平均网速：x.xxMB/s」"],
        ["单位换算", "1 MB/s = 8 Mbps；截图中「相当于 xx 兆宽带」即 Mbps 值"],
        ["信号强度 RSSI(dBm)", "本组未采集（所用 App 只显示速率），列为空；补测后填入，汇总表自动重算"],
        ["Ping 延迟(ms)", "同上，本组未采集"],
        ["盲区判定", "以「下载均值 < 1 MB/s」或「测速 0KB/s」判定为盲区（RSSI 补测后可改为 < -80dBm）"],
        ["P5 说明", "电梯运行中 3 次测速均为 0KB/s，另有 1 张 App 报「无网络/网络连接已断开」"],
        ["组数", "课题要求 8 点位 × 3 次 = 24 组；本实验实测 8 点位 / 25 条记录（P5 多测 1 张「无网络」佐证）"],
        ["溯源", "每条数据都能对应回原始截图文件名，面试可当场打开核对"],
    ]
    for n in notes:
        ws4.append(n)
    style_header(ws4, [22, 96])
    for row in ws4.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=True)

    wb.save(OUT)
    print(f"[OK] 已生成: {OUT}")
    print(f"     原始记录 {len(rows)} 条，点位 {len(points)} 个")


if __name__ == "__main__":
    sys.exit(main())