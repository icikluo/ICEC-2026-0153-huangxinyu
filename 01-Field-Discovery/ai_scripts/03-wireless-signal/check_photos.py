# -*- coding: utf-8 -*-
"""
课题03 - 证据自检器

课程要三样东西，这个脚本帮你把"机械性"的部分全查干净：
  1) 9 个点位的同框照是否齐全（本人 + 环境特征 + 手机屏幕）
  2) 照片是否重复（同一张改名充数）、尺寸是否达标、是否过大
  3) 每条测速数据是否都能对上原始截图（可溯源）

人工必须自己确认的（脚本做不到）：
  · 照片里是不是真的有人出镜
  · 手机屏幕上的数字和表格里填的是否一致

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

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "raw_data"
PHOTOS = BASE / "photos"
SHOTS = RAW / "截图"

MIN_SIDE = 720
MAX_MB = 2.0


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


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def exif_time(path):
    try:
        with Image.open(path) as im:
            for k, v in im.getexif().items():
                if TAGS.get(k) == "DateTimeOriginal":
                    return str(v)
    except Exception:
        pass
    return ""


def check_photos(problems, warnings):
    print("=" * 78)
    print("一、现场照片检查")
    print("=" * 78)
    rows = load(RAW / "measurements.csv")
    expected = sorted({r["照片文件名"] for r in rows if r.get("照片文件名")})
    exists = {p.name: p for p in PHOTOS.iterdir() if p.is_file()}

    print(f"{'文件名':<28}{'尺寸':<14}{'大小(KB)':<11}{'拍摄时间':<22}状态")
    print("-" * 78)
    seen = {}
    for name in expected:
        p = exists.get(name)
        if not p:
            problems.append(f"缺失同框照：{name}")
            continue
        try:
            with Image.open(p) as im:
                w, h = im.size
                fmt = im.format
        except Exception as e:
            problems.append(f"打不开：{name}（{e}）")
            continue
        kb = p.stat().st_size // 1024
        t = exif_time(p)
        state = "OK"
        if min(w, h) < MIN_SIDE:
            warnings.append(f"{name} 尺寸偏小 {w}x{h}")
            state = "尺寸偏小"
        if kb / 1024 > MAX_MB:
            warnings.append(f"{name} 体积 {kb/1024:.1f}MB > {MAX_MB}MB，建议压缩后再入库")
            state = "过大"
        if not t:
            warnings.append(f"{name} 无 EXIF 拍摄时间（压缩后可能已剥离），现场真实性靠文件名+同框自证")
        d = md5(p)
        if d in seen:
            problems.append(f"重复文件：{name} 与 {seen[d]} 内容完全相同")
            state = "重复"
        seen[d] = name
        print(f"{name:<28}{f'{w}x{h}':<14}{kb:<11}{t or '无':<22}{state}")

    extra = PHOTOS / "环境补充"
    if extra.exists():
        n = len([p for p in extra.iterdir() if p.is_file()])
        print(f"\n环境补充照：{n} 张（photos/环境补充/）")
    print()


def check_shots(problems, warnings):
    print("=" * 78)
    print("二、测速截图溯源检查")
    print("=" * 78)
    rows = load(RAW / "measurements.csv")
    print(f"{'点位':<16}{'序号':<6}{'截图文件':<28}状态")
    print("-" * 78)
    seen = {}
    for r in rows:
        name = r["截图文件名"]
        if not name:
            warnings.append(f"{r['点位编号']} 第{r['测量序号']}次：无截图，备注为「{r['备注'] or '未说明'}」")
            print(f"{r['点位编号']:<16}{r['测量序号']:<6}{'（无）':<28}缺截图（已在数据表标注）")
            continue
        p = SHOTS / name
        if not p.exists():
            problems.append(f"截图缺失：{name}（数据表引用了但文件不在 raw_data/截图/）")
            print(f"{r['点位编号']:<16}{r['测量序号']:<6}{name:<28}找不到")
            continue
        d = md5(p)
        seen.setdefault(d, []).append(name)
        print(f"{r['点位编号']:<16}{r['测量序号']:<6}{name:<28}OK")

    for d, names in seen.items():
        if len(names) > 1:
            warnings.append(f"截图重复：{' / '.join(names)}")

    # 截图中读出速率与表格是否一致（只能校验"截图里出现过的数字是否被转录"）
    print()
    print("说明：脚本无法 OCR 截图里的数字，请自行目视核对「表格数值 = 截图上的 x.xxMB/s」。")


def main():
    problems, warnings = [], []
    if not PHOTOS.exists():
        print("[!] photos/ 不存在")
        return 1
    check_photos(problems, warnings)
    check_shots(problems, warnings)

    print("=" * 78)
    if problems:
        print("[必须修]")
        for x in problems:
            print(f"  x {x}")
    if warnings:
        print("[建议看]")
        for x in warnings:
            print(f"  ! {x}")
    if not problems:
        print("[PASS] 文件层面全部齐套，可以提交。")
        print("       仍需你亲自确认：① 照片里有人出镜 ② 表格数字与截图一致")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())