# -*- coding: utf-8 -*-
"""
课题03 - 原始数据表生成器（第二轮 · 带 RSSI 与延迟）

读取 raw_data/measurements.csv（10月30日 实采，含 dBm / 延迟 / 抖动 / 丢包），
生成 raw_data/课题03_数据表.xlsx，5 个工作表：

  原始数据  —— 逐条记录
  点位汇总  —— RSSI / 下载 / 延迟 的均值与极值、盲区判定
  盲区判定  —— 按 -80 dBm 口径逐点位判定
  截图对照  —— 每条数据 ↔ dBm 截图 ↔ 测速截图（可溯源）
  填写说明  —— 单位、口径、两轮实验说明

判定口径（课题统一）：RSSI < -80 dBm → 盲区；无读数/无网络 → 重度盲区
"""

import csv
import io
import re
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.data_source import StrRef
from openpyxl.chart.series import DataPoint
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "raw_data"
OUT = RAW / "课题03_数据表.xlsx"

BLIND_DBM = -80

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor="1F4E79")
HEAD_FONT = Font(bold=True, color="FFFFFF", size=11)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
RED_FILL = PatternFill("solid", fgColor="F8CBAD")
GREEN_FILL = PatternFill("solid", fgColor="C6E0B4")
YELLOW_FILL = PatternFill("solid", fgColor="FFE699")


def num(text):
    s = (text or "").strip()
    if not s or s in ("无网络", "无服务", "无读数", "未连接", "超时", "-", "/"):
        return None
    try:
        return float(re.findall(r"-?\d+\.?\d*", s)[0])
    except IndexError:
        return None


def load(path):
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


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None, None, None, None
    avg = sum(vals) / len(vals)
    sd = None
    if len(vals) > 1:
        sd = (sum((x - avg) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5
    return avg, min(vals), max(vals), sd


def style_header(ws, widths):
    for c in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill, cell.font, cell.alignment, cell.border = HEAD_FILL, HEAD_FONT, CENTER, BORDER
    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 32
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def main():
    rows = load(RAW / "measurements.csv")
    points = load(RAW / "pose_points.csv")

    wb = Workbook()

    # ---------- Sheet 1: 原始数据 ----------
    ws = wb.active
    ws.title = "原始数据"
    headers = ["点位编号", "点位名称", "楼层", "遮挡特征", "测量序号",
               "信号强度 RSSI(dBm)", "下载(Mbps)", "上传(Mbps)",
               "下行延迟(ms)", "上行延迟(ms)", "抖动(ms)", "丢包(%)",
               "dBm截图", "测速截图", "备注"]
    ws.append(headers)
    for r in rows:
        ws.append([r["点位编号"], r["点位名称"], r["楼层"], r["遮挡特征"], r["测量序号"],
                   r["信号强度RSSI(dBm)"], r["下载Mbps"], r["上传Mbps"],
                   r["下行延迟ms"], r["上行延迟ms"], r["抖动ms"], r["丢包%"],
                   r["dBm截图"], r["测速截图"], r["备注"]])
    style_header(ws, [10, 16, 7, 22, 10, 18, 13, 13, 14, 14, 12, 10, 24, 24, 24])
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORDER
            if cell.column not in (4, 13, 14, 15):
                cell.alignment = CENTER
    ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"

    # ---------- Sheet 2: 点位汇总 ----------
    ws2 = wb.create_sheet("点位汇总")
    ws2.append(["点位编号", "点位名称", "楼层", "遮挡特征",
                "RSSI均值(dBm)", "RSSI最好", "RSSI最差", "RSSI标准差",
                "下载均值(Mbps)", "延迟均值(ms)", "抖动均值(ms)", "丢包均值(%)",
                "判定", "判定依据"])

    for p in points:
        pid = p["点位编号"]
        mine = [r for r in rows if r["点位编号"] == pid]
        rssi = [num(r["信号强度RSSI(dBm)"]) for r in mine]
        dl = [num(r["下载Mbps"]) for r in mine]
        lat = [num(r["下行延迟ms"]) for r in mine]
        jit = [num(r["抖动ms"]) for r in mine]
        loss = [num(r["丢包%"]) for r in mine]

        a, lo, hi, sd = stats(rssi)
        dl_avg, _, _, _ = stats(dl)
        lat_avg, _, _, _ = stats(lat)
        jit_avg, _, _, _ = stats(jit)
        loss_avg, _, _, _ = stats(loss)

        if a is None:
            judge, why = "重度盲区", "App 无法读取 RSSI，测速报「未检测到网络连接」"
        elif a < BLIND_DBM:
            judge, why = "盲区", f"RSSI 均值 {a:.1f} < {BLIND_DBM} dBm"
        elif a < BLIND_DBM + 10:
            judge, why = "临界", f"RSSI 均值 {a:.1f} dBm，接近盲区线，延迟与丢包明显劣化"
        else:
            judge, why = "正常", f"RSSI 均值 {a:.1f} ≥ {BLIND_DBM} dBm"

        ws2.append([
            pid, p["点位名称"], p["楼层"], p["遮挡特征"],
            round(a, 1) if a is not None else "无读数",
            lo if lo is not None else "无读数",
            hi if hi is not None else "无读数",
            round(sd, 2) if sd is not None else "",
            round(dl_avg, 2) if dl_avg is not None else "未连接",
            round(lat_avg, 0) if lat_avg is not None else "未连接",
            round(jit_avg, 2) if jit_avg is not None else "未连接",
            round(loss_avg, 2) if loss_avg is not None else "未连接",
            judge, why,
        ])

    style_header(ws2, [10, 16, 7, 22, 16, 12, 12, 12, 16, 14, 13, 13, 12, 52])
    for row in ws2.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORDER
            if cell.column not in (4, 14):
                cell.alignment = CENTER
        j = row[12].value
        fill = RED_FILL if j in ("盲区", "重度盲区") else (YELLOW_FILL if j == "临界" else GREEN_FILL)
        row[12].fill = fill
        row[4].fill = fill

    # 图表：RSSI 柱状图（跌破 -80 标红）
    ch = BarChart()
    ch.type = "col"
    ch.title = "各点位信号强度 RSSI 均值"
    ch.y_axis.title = "RSSI (dBm)"
    ch.x_axis.title = "点位"
    ch.add_data(Reference(ws2, min_col=5, min_row=1, max_row=ws2.max_row), titles_from_data=True)
    ch.set_categories(Reference(ws2, min_col=1, min_row=2, max_row=ws2.max_row))
    try:
        ch.series[0].cat.strRef = StrRef(f"'点位汇总'!$A$2:$A${ws2.max_row}")
    except Exception:
        pass
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.y_axis.scaling.min = -100
    ch.y_axis.scaling.max = 0
    ch.gapWidth = 50
    ch.legend = None
    ch.height = 10
    ch.width = 24
    for i, r in enumerate(ws2.iter_rows(min_row=2, values_only=True)):
        if isinstance(r[4], (int, float)) and r[4] < BLIND_DBM:
            dp = DataPoint(idx=i)
            dp.graphicalProperties.solidFill = "C00000"
            ch.series[0].dPt.append(dp)
    ws2.add_chart(ch, "A16")

    # ---------- Sheet 3: 盲区判定 ----------
    ws3 = wb.create_sheet("盲区判定")
    ws3.append(["点位", "RSSI均值(dBm)", "判定", "下载(Mbps)", "延迟(ms)", "丢包(%)", "结论说明"])
    note_map = {
        "重度盲区": "金属轿厢屏蔽，链路完全不可用——典型法拉第笼",
        "盲区": "RSSI 跌破 -80 dBm，下载与延迟同时劣化",
        "临界": "信号尚在可用区但延迟明显偏高，属「覆盖够、体验差」",
        "正常": "覆盖良好，可作为对照基准",
    }
    summary = [r for r in ws2.iter_rows(min_row=2, values_only=True) if r[0]]
    for row in sorted(summary, key=lambda r: r[4] if isinstance(r[4], (int, float)) else -999):
        ws3.append([f"{row[0]} {row[1]}", row[4], row[12], row[8], row[9], row[11],
                    note_map[row[12]]])
    style_header(ws3, [22, 16, 12, 14, 12, 11, 52])
    for row in ws3.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORDER
            if cell.column not in (1, 7):
                cell.alignment = CENTER
        j = row[2].value
        row[2].fill = RED_FILL if j in ("盲区", "重度盲区") else (YELLOW_FILL if j == "临界" else GREEN_FILL)

    # ---------- Sheet 4: 截图对照 ----------
    ws4 = wb.create_sheet("截图对照")
    ws4.append(["点位", "序号", "dBm 截图", "测速截图", "备注"])
    for r in rows:
        ws4.append([f"{r['点位编号']} {r['点位名称']}", r["测量序号"],
                    r["dBm截图"], r["测速截图"], r["备注"]])
    style_header(ws4, [24, 8, 30, 30, 28])
    for row in ws4.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORDER
            if cell.column != 5:
                cell.alignment = CENTER
        if not row[3].value:
            row[3].fill = YELLOW_FILL

    # ---------- Sheet 5: 填写说明 ----------
    ws5 = wb.create_sheet("填写说明")
    notes = [
        ["项目", "说明"],
        ["实验轮次", "本轮为第二轮（2026-10-30），在第一轮基础上补充了 RSSI 与延迟；第一轮数据归档于 raw_data/03-wireless-signal-v1-20261028/"],
        ["实验时间", "2026-10-30 16:39–17:49"],
        ["SSID / 频段", "SZIT-WLAN，Wi-Fi 5（802.11ac）"],
        ["测量设备", "手机（荣耀 V30 Pro）+ 测速网 App + Wi-Fi 分析 App（读 RSSI）"],
        ["主指标", "信号强度 RSSI(dBm)，由 Wi-Fi 分析 App 直接读取"],
        ["辅指标", "下载/上传 Mbps、下行/上行延迟 ms、抖动 ms、丢包 %"],
        ["盲区判定", f"RSSI 均值 < {BLIND_DBM} dBm → 盲区；App 无读数或测速无网络 → 重度盲区"],
        ["采样密度", "每点位 RSSI 读 4 次；其中 3 次同步做了测速"],
        ["电梯点位", "P8 电梯运行中、P9 电梯内部：Wi-Fi 图标常在，但 App 读不到 RSSI 且测速报「未检测到网络连接」"],
        ["溯源", "每条数据都能对应回 dBm 截图与测速截图，见「截图对照」表"],
        ["编码", "measurements.csv 为 UTF-8；用 Excel 另存为 GBK 也可，脚本会自动识别"],
    ]
    for n in notes:
        ws5.append(n)
    style_header(ws5, [20, 100])
    for row in ws5.iter_rows(min_row=2):
        for cell in row:
            cell.border = BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=True)

    wb.save(OUT)
    print(f"[OK] 已生成: {OUT}")
    print(f"     原始记录 {len(rows)} 条，点位 {len(points)} 个")


if __name__ == "__main__":
    sys.exit(main())