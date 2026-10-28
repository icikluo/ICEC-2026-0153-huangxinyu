# -*- coding: utf-8 -*-
"""
课题03 - 图表生成器（只用 openpyxl + Pillow，不需要 matplotlib）

产出两套图，报告和 Excel 都能直接用：

  charts/chart1_下载速率对比.png   各点位下载速率均值柱状图（红色=盲区）
  charts/chart2_单次测量散点.png   全部单次测量点，看同点位内部稳定性
  charts/chart3_楼层对比.png       2/5/8 楼电梯口对照（楼层垂直衰减）
  charts/课题03_图表.xlsx          Excel 原生图表（可点开继续调）

用法：
    python tools/make_charts.py
"""

import csv
import io
import math
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.data_source import StrRef
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "raw_data"
CHARTS = BASE / "charts"
CHARTS.mkdir(exist_ok=True)
OUT = CHARTS / "课题03_图表.xlsx"

BLIND_THRESHOLD = 1.0   # MB/s，低于此判定盲区
C_BLUE = "#2E75B6"
C_RED = "#C00000"
C_ORANGE = "#FF6600"
C_GRAY = "#A6A6A6"

W, H = 1600, 960
PAD_L, PAD_R, PAD_T, PAD_B = 140, 60, 110, 190

FONTS = [
    ("C:/Windows/Fonts/msyh.ttc", 0),
    ("C:/Windows/Fonts/simhei.ttf", 0),
    ("C:/Windows/Fonts/simsun.ttc", 0),
]


def font(size):
    for p, i in FONTS:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size, index=i)
            except Exception:
                continue
    return ImageFont.load_default()


def num(text):
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


# ---------------------- 绘图基础 ----------------------
def axes(draw, img, labels, y_max, y_ticks, y_title, x_title, title):
    x0, y0 = PAD_L, PAD_T
    x1, y1 = W - PAD_R, H - PAD_B
    f_tick, f_title, f_head = font(24), font(26), font(38)

    draw.text(((x0 + x1) // 2, 45), title, font=f_head, fill="#1F3864", anchor="mm")

    for v in y_ticks:
        y = y1 - v / y_max * (y1 - y0)
        draw.line([(x0, y), (x1, y)], fill="#D9D9D9", width=2)
        draw.text((x0 - 15, y), f"{v:g}", font=f_tick, fill="#404040", anchor="rm")

    draw.line([(x0, y0), (x0, y1)], fill="#404040", width=3)
    draw.line([(x0, y1), (x1, y1)], fill="#404040", width=3)

    txt = Image.new("RGBA", (400, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    d.text((200, 30), y_title, font=f_title, fill="#1F3864", anchor="mm")
    txt = txt.rotate(90, expand=True)
    img.paste(txt, (18, (y0 + y1) // 2 - 200), txt)

    draw.text(((x0 + x1) // 2, H - 35), x_title, font=f_title, fill="#1F3864", anchor="mm")

    n = len(labels)
    step = (x1 - x0) / max(n, 1)
    for i, (pid, name) in enumerate(labels):
        cx = x0 + step * (i + 0.5)
        draw.text((cx, y1 + 30), pid, font=f_title, fill="#1F3864", anchor="mm")
        for k, ch in enumerate([name[j:j + 6] for j in range(0, len(name), 6)]):
            draw.text((cx, y1 + 62 + k * 28), ch, font=f_tick, fill="#404040", anchor="mm")
    return x0, y0, x1, y1, step


def nice_step(vmax, target=5):
    raw = max(vmax, 1e-6) / target
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if m * mag >= raw:
            return m * mag
    return 10 * mag


# ---------------------- 图1：下载速率柱状图 ----------------------
def chart_download(points, rows, out):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    labels, values = [], []
    for p in points:
        pid = p["点位编号"]
        vals = [num(r["下载速度(MB/s)"]) for r in rows if r["点位编号"] == pid]
        vals = [v for v in vals if v is not None]
        labels.append((pid, p["点位名称"]))
        values.append(sum(vals) / len(vals) if vals else None)

    vmax = max([v for v in values if v is not None] + [1]) * 1.2
    s = nice_step(vmax)
    y_max = s * 5
    x0, y0, x1, y1, step = axes(d, img, labels, y_max, [s * i for i in range(6)],
                                "下载速率 (MB/s)", "点位",
                                "课题03 · 各点位下载速率均值对比（红色 = 盲区）")
    bw = step * 0.6
    for i, v in enumerate(values):
        cx = x0 + step * (i + 0.5)
        shown = v if v is not None else 0
        top = y1 - shown / y_max * (y1 - y0)
        color = C_GRAY if v is None else (C_RED if v < BLIND_THRESHOLD else C_BLUE)
        if shown > 0:
            d.rectangle([cx - bw / 2, top, cx + bw / 2, y1], fill=color)
        label = "未采集" if v is None else f"{v:.2f}"
        ly = top - 20 if shown > 0 else y1 - 26
        d.text((cx, ly), label, font=font(22),
               fill="#7F7F7F" if v is None else "#1F1F1F", anchor="mm")

    yb = y1 - BLIND_THRESHOLD / y_max * (y1 - y0)
    for xs in range(x0, x1, 26):
        d.line([(xs, yb), (min(xs + 14, x1), yb)], fill=C_ORANGE, width=4)
    d.text((x1 - 12, yb + 20), f"盲区阈值 {BLIND_THRESHOLD} MB/s",
           font=font(22), fill=C_ORANGE, anchor="rs")
    img.save(out)


# ---------------------- 图2：单次散点 ----------------------
def chart_scatter(points, rows, out):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    labels = [(p["点位编号"], p["点位名称"]) for p in points]
    groups = []
    for p in points:
        vals = [num(r["下载速度(MB/s)"]) for r in rows if r["点位编号"] == p["点位编号"]]
        groups.append([v for v in vals if v is not None])

    allv = [v for g in groups for v in g]
    vmax = max(allv + [1]) * 1.2
    s = nice_step(vmax)
    y_max = s * 5
    x0, y0, x1, y1, step = axes(d, img, labels, y_max, [s * i for i in range(6)],
                                "下载速率 (MB/s)", "点位",
                                "课题03 · 单次测量分布（每点位 3–4 次，红线为均值）")
    colors = ["#2E75B6", "#70AD47", "#C00000", "#7030A0"]
    for i, g in enumerate(groups):
        if not g:
            cx = x0 + step * (i + 0.5)
            d.text((cx, y1 - 30), "无数据", font=font(22), fill="#7F7F7F", anchor="mm")
            continue
        cx = x0 + step * (i + 0.5)
        pts = []
        for j, v in enumerate(g):
            dx = (j - (len(g) - 1) / 2) * (step * 0.14)
            pts.append((cx + dx, y1 - v / y_max * (y1 - y0)))
        if len(pts) > 1:
            d.line(pts, fill="#BFBFBF", width=3)
        for j, (px, py) in enumerate(pts):
            r = 11
            d.ellipse([px - r, py - r, px + r, py + r], fill=colors[j % 4], outline="white", width=3)
        mean = sum(g) / len(g)
        ym = y1 - mean / y_max * (y1 - y0)
        d.line([(cx - step * 0.30, ym), (cx + step * 0.30, ym)], fill=C_RED, width=5)
        d.text((cx + step * 0.32, ym), f"{mean:.2f}", font=font(21), fill=C_RED, anchor="lm")

    yb = y1 - BLIND_THRESHOLD / y_max * (y1 - y0)
    for xs in range(x0, x1, 26):
        d.line([(xs, yb), (min(xs + 14, x1), yb)], fill=C_ORANGE, width=4)
    d.text((x0 + 14, yb - 20), f"盲区阈值 {BLIND_THRESHOLD} MB/s",
           font=font(22), fill=C_ORANGE, anchor="ls")

    lx, ly = x1 - 150, y0 + 130
    for j, t in enumerate(["第1次", "第2次", "第3次", "第4次", "点位均值"]):
        yy = ly + j * 32
        if j < 4:
            d.ellipse([lx, yy - 8, lx + 16, yy + 8], fill=colors[j])
        else:
            d.line([(lx, yy), (lx + 20, yy)], fill=C_RED, width=5)
        d.text((lx + 32, yy), t, font=font(21), fill="#404040", anchor="lm")
    img.save(out)


# ---------------------- 图3：楼层对照 ----------------------
def chart_floor(rows, out):
    """2F / 5F / 8F 电梯口对照：P8(2楼) P3(5楼) P9(8楼)。"""
    trio = [("P8", "2楼电梯口", "二楼"), ("P3", "5楼电梯口", "五楼电梯"), ("P9", "8楼电梯口", "八楼")]
    labels, values = [], []
    for pid, name, _ in trio:
        vals = [num(r["下载速度(MB/s)"]) for r in rows if r["点位编号"] == pid]
        vals = [v for v in vals if v is not None]
        labels.append((pid, name))
        values.append(sum(vals) / len(vals) if vals else None)

    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    vmax = max([v for v in values if v] + [1]) * 1.2
    s = nice_step(vmax)
    y_max = s * 5
    x0, y0, x1, y1, step = axes(d, img, labels, y_max, [s * i for i in range(6)],
                                "下载速率 (MB/s)", "楼层对照点",
                                "课题03 · 不同楼层电梯口下载速率对照（垂直衰减检验）")
    bw = step * 0.45
    for i, v in enumerate(values):
        cx = x0 + step * (i + 0.5)
        shown = v or 0
        top = y1 - shown / y_max * (y1 - y0)
        d.rectangle([cx - bw / 2, top, cx + bw / 2, y1], fill=C_BLUE)
        d.text((cx, top - 22), f"{v:.2f}" if v else "未采集", font=font(26), fill="#1F1F1F", anchor="mm")
    img.save(out)


def main():
    rows = load(RAW / "measurements.csv")
    points = load(RAW / "pose_points.csv")

    chart_download(points, rows, CHARTS / "chart1_下载速率对比.png")
    chart_scatter(points, rows, CHARTS / "chart2_单次测量散点.png")
    chart_floor(rows, CHARTS / "chart3_楼层对比.png")

    # ---------- Excel 原生图表 ----------
    wb = Workbook()
    ws = wb.active
    ws.title = "图1_下载速率"
    ws.append(["点位", "下载均值(MB/s)"])
    for p in points:
        pid = p["点位编号"]
        vals = [num(r["下载速度(MB/s)"]) for r in rows if r["点位编号"] == pid]
        vals = [v for v in vals if v is not None]
        ws.append([p["点位名称"], round(sum(vals) / len(vals), 2) if vals else 0])
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 18

    ch = BarChart()
    ch.type = "col"
    ch.title = "课题03 · 各点位下载速率均值（MB/s）"
    ch.y_axis.title = "MB/s"
    ch.x_axis.title = "点位"
    ch.add_data(Reference(ws, min_col=2, min_row=1, max_row=ws.max_row), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=2, max_row=ws.max_row))
    ch.series[0].cat.strRef = StrRef(f"'图1_下载速率'!$A$2:$A${ws.max_row}")
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.gapWidth = 40
    ch.legend = None
    ch.height = 10
    ch.width = 24
    ws.add_chart(ch, "D2")

    ws2 = wb.create_sheet("数据源")
    ws2.append(["点位编号", "点位名称", "楼层", "下载均值(MB/s)", "判定"])
    for p in points:
        pid = p["点位编号"]
        vals = [num(r["下载速度(MB/s)"]) for r in rows if r["点位编号"] == pid]
        vals = [v for v in vals if v is not None]
        avg = round(sum(vals) / len(vals), 2) if vals else None
        judge = "未采集" if avg is None else ("盲区" if avg < BLIND_THRESHOLD else "正常")
        ws2.append([pid, p["点位名称"], p["楼层"], avg if avg is not None else "", judge])
    for c in range(1, 6):
        ws2.cell(row=1, column=c).font = Font(bold=True)
        ws2.column_dimensions[get_column_letter(c)].width = 18

    wb.save(OUT)
    print(f"[OK] 图表已输出: {CHARTS}")


if __name__ == "__main__":
    main()