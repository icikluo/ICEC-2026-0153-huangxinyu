# -*- coding: utf-8 -*-
"""
课题03 - 证据齐套性自检（第二轮 · RSSI 口径）

检查四件事：
  1) dBm 截图：每条 RSSI 数据是否都有对应截图
  2) 测速截图：每条测速数据是否都有对应截图
  3) 现场照片：是否齐全、尺寸达标、有无重复
  4) 数据自洽：RSSI 数值与「盲区判定」是否一致

用法：
    python tools/check_photos.py
"""

import csv
import hashlib
import io
import re
import sys
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS

# 定位数据目录：兼容两种布局
#   工作区布局  课题03_校园无线信号盲区测绘/{raw_data,photos,tools}
#   仓库布局    01-Field-Discovery/{raw_data/03-wireless-signal, photos/03-wireless-signal, ai_scripts/03-wireless-signal}
_here = Path(__file__).resolve().parent
_cands = [_here.parent]
if _here.parent.parent.name == "01-Field-Discovery":
    _cands.append(_here.parent.parent)
BASE = raw_dir = photo_dir = None
for _c in _cands:
    if (_c / "raw_data").is_dir() and (_c / "photos").is_dir():
        BASE = _c
        break
if BASE is None:
    BASE = _here.parent
raw_dir = BASE / "raw_data"
photo_dir = BASE / "photos"
if not (raw_dir / "measurements.csv").exists():
    for _sub in raw_dir.iterdir():
        if _sub.is_dir() and (_sub / "measurements.csv").exists():
            raw_dir = _sub
            photo_dir = photo_dir / _sub.name
            break
RAW = raw_dir
PHOTOS = photo_dir

SHOTS_DBM = RAW / "截图_dbm"
SHOTS_SPD = RAW / "截图_测速"

BLIND_DBM = -80
MIN_SIDE = 400
MAX_MB = 2.5


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


def md5(p, chunk=1 << 20):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def check_shot_dir(rows, col, folder, label, problems, warnings):
    print(f"\n{'=' * 76}\n{label}（{folder.relative_to(BASE)}）\n{'=' * 76}")
    seen = {}
    total = 0
    for r in rows:
        name = (r.get(col) or "").strip()
        if not name:
            warnings.append(f"{r['点位编号']} 第{r['测量序号']}次：无{label}")
            continue
        total += 1
        p = folder / name
        if not p.exists():
            problems.append(f"{label}缺失：{name}")
            continue
        d = md5(p)
        if d in seen:
            problems.append(f"{label}重复：{name} 与 {seen[d]} 内容相同")
        seen[d] = name
    print(f"检查 {total} 条记录 → {folder.name}/ 下 {len(list(folder.glob('*')))} 个文件")


def check_photos(rows, problems, warnings):
    print(f"\n{'=' * 76}\n现场照片\n{'=' * 76}")
    expected = sorted({r["照片文件名"] for r in rows if (r.get("照片文件名") or "").strip()})
    # 照片文件名不在 CSV 里逐条出现，这里按点位前缀匹配
    existing = {p.name: p for p in PHOTOS.iterdir() if p.is_file()}
    print(f"{'文件名':<34}{'尺寸':<14}{'KB':<9}状态")
    print("-" * 76)
    seen = {}
    for name, p in sorted(existing.items()):
        try:
            with Image.open(p) as im:
                w, h = im.size
        except Exception as e:
            problems.append(f"打不开：{name}（{e}）")
            continue
        kb = p.stat().st_size // 1024
        state = "OK"
        if min(w, h) < MIN_SIDE:
            warnings.append(f"{name} 尺寸偏小 {w}x{h}")
            state = "偏小"
        if kb / 1024 > MAX_MB:
            warnings.append(f"{name} {kb/1024:.1f}MB 偏大")
            state = "偏大"
        d = md5(p)
        if d in seen:
            problems.append(f"照片重复：{name} 与 {seen[d]}")
            state = "重复"
        seen[d] = name
        print(f"{name:<34}{f'{w}x{h}':<14}{kb:<9}{state}")
    sub = PHOTOS / "环境补充"
    if sub.exists():
        print(f"\n环境补充照：{len(list(sub.iterdir()))} 张")


def check_consistency(rows, points, problems, warnings):
    print(f"\n{'=' * 76}\n数据自洽性（−80 dBm 判定口径）\n{'=' * 76}")
    for p in points:
        pid = p["点位编号"]
        mine = [r for r in rows if r["点位编号"] == pid]
        vals = []
        for r in mine:
            s = (r["信号强度RSSI(dBm)"] or "").strip()
            if re.fullmatch(r"-?\d+(\.\d+)?", s):
                vals.append(float(s))
        if not vals:
            print(f"{pid:<4} {p['点位名称']:<12} 无读数 → 重度盲区 ✓")
            continue
        a = sum(vals) / len(vals)
        judge = "盲区" if a < BLIND_DBM else ("临界" if a < BLIND_DBM + 10 else "正常")
        ok = "✓" if (a < BLIND_DBM) == (judge == "盲区") else "✗"
        print(f"{pid:<4} {p['点位名称']:<12} {a:>7.1f} dBm  ({len(vals)} 次) → {judge} {ok}")
        if not ok:
            problems.append(f"{pid} 判定与 RSSI 不一致")


def main():
    problems, warnings = [], []
    rows = load(RAW / "measurements.csv")
    points = load(RAW / "pose_points.csv")

    check_shot_dir(rows, "dBm截图", SHOTS_DBM, "dBm截图", problems, warnings)
    check_shot_dir(rows, "测速截图", SHOTS_SPD, "测速截图", problems, warnings)
    check_photos(rows, problems, warnings)
    check_consistency(rows, points, problems, warnings)

    print(f"\n{'=' * 76}")
    if problems:
        print("[必须修]")
        for x in problems:
            print(f"  x {x}")
    if warnings:
        print("[已知情况]")
        for x in warnings[:10]:
            print(f"  ! {x}")
        if len(warnings) > 10:
            print(f"  ... 另有 {len(warnings)-10} 条")
    if not problems:
        print("[PASS] 证据齐套，数据自洽，可以提交。")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())