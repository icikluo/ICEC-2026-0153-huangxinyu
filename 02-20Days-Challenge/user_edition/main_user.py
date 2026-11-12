# -*- coding: utf-8 -*-
"""
课表提醒 用户版 v1.1
====================
白色 + 浅粉 果冻风 · 圆角控件

v1.1 改进（基于 8 位用户反馈，详见 iterations/iteration-4.md）：
  1. CSV 编码自动识别（utf-8-sig / utf-8 / gbk / gb18030 / utf-16）
  2. 支持直接读取 Excel .xlsx（无编码问题）
  3. 课前 N 分钟二次提醒（可配置，默认 20 分钟）
  4. 界面视觉优化：白色+浅粉配色、圆角果冻控件、分段导航
  5. 课表预览（配置后可直接查看本周课表）
  6. 一键检测课表格式
  7. 程序内嵌使用帮助
  8. 失败重试可视化
  9. 发送记录本地保存（send_history.log）
"""

import os
import sys
import json
import time as _time
import smtplib
import traceback
from datetime import datetime, timezone, timedelta, date
from email.mime.text import MIMEText
from email.header import Header

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

try:
    import pandas as pd
except ImportError:
    pd = None

# 果冻控件库（与 main_user.py 同目录）
try:
    import jelly as J
except ImportError:
    J = None

APP_NAME = "课表提醒"
APP_VERSION = "v1.1"
APP_AUTHOR = "ICEC-2026-0153"

C_BG = J.C_BG if J else "#FFFFFF"
C_PINK = J.C_PINK if J else "#FFA6BD"
C_PINK_DEEP = J.C_PINK_DEEP if J else "#FF7A9C"
C_PINK_DARK = J.C_PINK_DARK if J else "#F26187"
C_PINK_PALE = J.C_PINK_PALE if J else "#FFF0F4"
C_PINK_LIGHT = J.C_PINK_LIGHT if J else "#FFE9EF"
C_TEXT = J.C_TEXT if J else "#4A3540"
C_TEXT_SOFT = J.C_TEXT_SOFT if J else "#8B7280"
C_TEXT_MUTED = J.C_TEXT_MUTED if J else "#C4AEB8"
C_BORDER = J.C_BORDER if J else "#FFDCE5"


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(app_dir(), "config.json")
HISTORY_PATH = os.path.join(app_dir(), "send_history.log")

BJ_TZ = timezone(timedelta(hours=8))
WEEKDAY_MAP = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四",
               4: "星期五", 5: "星期六", 6: "星期日"}

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SMTP_TIMEOUT = 30
MAX_RETRY = 2
REQUIRED_COLS = {"周次", "星期", "课程名", "开始时间", "结束时间", "地点", "教师"}
ENCODINGS = ("utf-8-sig", "utf-8", "gbk", "gb18030", "utf-16")

DEFAULT_CONFIG = {
    "sender_email": "",
    "auth_code": "",
    "receiver_email": "",
    "csv_path": "",
    "semester_start": "2026-09-07",
    "military_weeks": "",
    "remind_enabled": True,
    "remind_minutes": 20,
}


# ==================== 数据工具 ====================

def load_config():
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def parse_weeks(cell):
    weeks = set()
    for token in str(cell).replace("，", ";").replace(",", ";").split(";"):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            a, b = token.split("-", 1)
            try:
                weeks.update(range(int(a), int(b) + 1))
            except ValueError:
                continue
        else:
            try:
                weeks.add(int(token))
            except ValueError:
                continue
    return weeks


def current_week(semester_start_str):
    try:
        y, m, d = [int(x) for x in semester_start_str.split("-")]
        start = date(y, m, d)
    except Exception:
        start = date(2026, 9, 7)
    return (datetime.now(BJ_TZ).date() - start).days // 7 + 1


def read_schedule_file(path):
    """v1.1：兼容多种编码的 CSV，以及 Excel .xlsx"""
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path, dtype=str)

    last_err = None
    for enc in ENCODINGS:
        try:
            return pd.read_csv(path, encoding=enc, dtype=str)
        except (UnicodeDecodeError, UnicodeError) as e:
            last_err = e
            continue
    raise ValueError(
        "无法识别课表文件编码。\n\n"
        "建议：用 Excel 打开后「另存为」→ 选「Excel 工作簿(*.xlsx)」，"
        "然后在程序里选择该 xlsx 文件（推荐，不会有编码问题）。\n\n"
        "技术细节：%s" % last_err)


def normalize_df(df):
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()
    return df


def validate_schedule(df):
    """检查课表格式，返回 (是否通过, 问题列表, 统计)"""
    problems = []
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        return False, ["缺少必需的列：%s" % "、".join(sorted(missing))], {}

    weekdays = set(WEEKDAY_MAP.values())
    bad_wd, bad_tm, bad_wk, empty_course = set(), set(), set(), 0

    for _, row in df.iterrows():
        # 跳过特殊行（如军训、假期等占位行）
        if row.get("星期") in ("军训", "假期", "备注", "全部"):
            continue
        if row["星期"] not in weekdays:
            bad_wd.add(row["星期"])
        for key in ("开始时间", "结束时间"):
            v = row[key]
            ok = ":" in v
            if ok:
                try:
                    h, m = v.split(":")
                    ok = 0 <= int(h) <= 23 and 0 <= int(m) <= 59
                except Exception:
                    ok = False
            if not ok:
                bad_tm.add(v)
        if not parse_weeks(row["周次"]):
            bad_wk.add(row["周次"])
        if not row["课程名"]:
            empty_course += 1

    if bad_wd:
        problems.append("「星期」写法不规范（%d 种）：%s\n→ 应写作 星期一 / 星期二 … / 星期日"
                        % (len(bad_wd), "、".join(sorted(bad_wd)[:5])))
    if bad_tm:
        problems.append("「开始时间/结束时间」格式不对（%d 个）：%s\n→ 应写作 08:00 这种 24 小时制"
                        % (len(bad_tm), "、".join(sorted(bad_tm)[:5])))
    if bad_wk:
        problems.append("「周次」无法解析（%d 个）：%s\n→ 例：1-16、3;6;9、3-13;16-18"
                        % (len(bad_wk), "、".join(sorted(bad_wk)[:5])))
    if empty_course:
        problems.append("有 %d 行「课程名」为空" % empty_course)

    stats = {
        "总行数": len(df),
        "课程数": len({c for c in df["课程名"] if c}) if len(df) else 0,
        "有课的星期": "、".join(sorted(set(df["星期"]) & weekdays)) or "无",
    }
    return len(problems) == 0, problems, stats


def courses_of_day(df, weekday_name, week_no):
    d = df.copy()
    d["_w"] = d["周次"].apply(parse_weeks)
    hit = d[(d["星期"] == weekday_name) & (d["_w"].apply(lambda s: week_no in s))]
    return hit.sort_values("开始时间").to_dict("records")


def build_body(courses, today_str, week_no, is_military):
    if is_military:
        return "军训期间，无课。\n\n日期：%s（第 %d 周）" % (today_str, week_no)
    if not courses:
        return "今天没有课，好好休息。\n\n日期：%s（第 %d 周）" % (today_str, week_no)
    lines = ["今日课表提醒", "日期：%s（第 %d 周）" % (today_str, week_no), ""]
    for c in courses:
        lines.append("· %s-%s  %s  %s  教师：%s" % (
            c["开始时间"], c["结束时间"], c["课程名"], c["地点"], c["教师"]))
    lines += ["", "共 %d 节课" % len(courses)]
    return "\n".join(lines)


HELP_TEXT = [
    ("▍快速上手（三步）", "h"),
    ("1. 「① 邮箱配置」填写你的 QQ 邮箱、授权码、收件邮箱，点保存。", None),
    ("2. 「② 课表设置」选择课表文件（推荐 Excel .xlsx），填学期起始日期，点保存。", None),
    ("3. 「③ 发送与预览」点「立即发送今日课表」，收到邮件即成功。", None),
    ("", None),
    ("▍获取 QQ 邮箱授权码", "h"),
    ("1. 浏览器打开 mail.qq.com 并登录", None),
    ("2. 点右上角「设置」→「账户」", None),
    ("3. 找到「IMAP/SMTP服务」，点「开启」", None),
    ("4. 按提示用手机发短信验证", None),
    ("5. 页面出现的 16 位字母就是授权码（不是你的 QQ 密码）", None),
    ("", None),
    ("▍填写课表", "h"),
    ("表头必须是这 7 列：周次, 星期, 课程名, 开始时间, 结束时间, 地点, 教师", None),
    ("· 周次：1-16 表示第 1~16 周；3;6;9 表示第 3、6、9 周；3-13;16-18 表示两段", None),
    ("· 星期：必须写全称 星期一 / 星期二 / … / 星期日", None),
    ("· 时间：24 小时制，如 08:00、14:30", None),
    ("填写后可点「一键检测格式」，程序会帮你检查有没有写错。", None),
    ("", None),
    ("▍关于文件格式", "h"),
    ("支持 CSV 和 Excel(.xlsx)。推荐用 Excel 编辑后直接保存为 .xlsx —— 不会有任何编码问题。", None),
    ("若用 CSV，程序会自动尝试 UTF-8 / GBK 等多种编码，一般无需手动设置。", None),
    ("", None),
    ("▍课前二次提醒", "h"),
    ("在「② 课表设置」中可开启，默认提前 20 分钟。", None),
    ("开启后，发送邮件时会在日志里列出今天每节课的提醒时间点。", None),
    ("", None),
    ("▍常见问题", "h"),
    ("· 提示「授权码不正确」→ 确认用的是授权码而非密码，且已开启 IMAP/SMTP", None),
    ("· 提示「CSV 缺少列」→ 检查表头是否完整（共 7 列）", None),
    ("· 发送成功但收不到 → 先看垃圾邮件箱", None),
    ("", None),
    ("课表提醒 v1.1 · ICEC-2026-0153 · 依据 8 位同学的真实使用反馈迭代改进", "h"),
]


# ==================== 主窗口 ====================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.df = None
        self.title("%s %s  ·  %s" % (APP_NAME, APP_VERSION, APP_AUTHOR))
        self.geometry("900x700")
        self.minsize(860, 640)
        self.configure(bg=C_BG)
        self._build()
        self._load_to_ui()
        self.refresh_status()

    # ---------- 构建 ----------
    def _build(self):
        self._build_header()
        self._build_status()
        self._build_nav()
        self.body = tk.Frame(self, bg=C_BG)
        self.body.pack(fill="both", expand=True, padx=28, pady=(12, 16))
        self.pages = [self._page_mail(), self._page_sched(), self._page_send(), self._page_help()]
        for p in self.pages:
            p.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.pages[0].lift()

    def _build_header(self):
        head = tk.Canvas(self, height=92, bg=C_BG, highlightthickness=0, bd=0)
        head.pack(fill="x")

        def draw(e=None):
            w = e.width if e else head.winfo_width()
            head.delete("all")
            for i in range(92):
                head.create_line(0, i, w, i, fill=J.lerp("#FFF1F6", "#FFFFFF", i / 91))
            head.create_oval(w - 160, -70, w - 20, 70, fill="#FFEDF3", outline="")
            head.create_oval(w - 96, 8, w - 24, 80, fill="#FFE2EC", outline="")
            # 左侧圆角图标块（先画底块，再画文字）
            J.rrect(head, 22, 20, 70, 68, 14, fill=C_PINK)
            head.create_text(46, 46, text="课", fill="#FFFFFF",
                             font=("Microsoft YaHei UI", 17, "bold"))
            head.create_text(88, 32, text="%s %s" % (APP_NAME, APP_VERSION), fill=C_TEXT,
                             font=("Microsoft YaHei UI", 18, "bold"), anchor="w")
            head.create_text(90, 62, text="每天自动把当天课表发到你邮箱", fill=C_TEXT_MUTED,
                             font=("Microsoft YaHei UI", 10), anchor="w")

        head.bind("<Configure>", draw)

    def _build_status(self):
        bar = tk.Frame(self, bg=C_BG)
        bar.pack(fill="x", padx=28)
        self.status_cv = tk.Canvas(bar, height=40, bg=C_BG, highlightthickness=0, bd=0)
        self.status_cv.pack(fill="x")
        self.status_cv.bind("<Configure>", lambda e: self.refresh_status())

    def _build_nav(self):
        nav = tk.Frame(self, bg=C_BG)
        nav.pack(fill="x", padx=28, pady=(6, 0))
        self.seg = J.JellySegmented(nav, ["① 邮箱配置", "② 课表设置",
                                          "③ 发送与预览", "④ 使用帮助"],
                                    on_change=self._switch, height=46)
        self.seg.pack(fill="x")

    def _switch(self, i):
        self.pages[i].lift()

    # ---------- 状态条 ----------
    def refresh_status(self):
        if not hasattr(self, "status_cv"):
            return
        cv = self.status_cv
        cv.delete("all")
        w = cv.winfo_width() or 840
        J.rrect(cv, 1, 3, w - 1, 38, 18, fill=C_PINK_PALE, outline=C_BORDER)
        now = datetime.now(BJ_TZ)
        wk = current_week(self.cfg.get("semester_start", "2026-09-07"))
        mail_ok = all([self.cfg.get("sender_email"), self.cfg.get("auth_code"),
                       self.cfg.get("receiver_email")])
        p = self.cfg.get("csv_path", "")
        sched_ok = bool(p) and os.path.exists(p)
        cv.create_text(20, 21, anchor="w", fill=C_TEXT_SOFT, font=("Microsoft YaHei UI", 10),
                       text="📆  %s  %s          ✉  邮箱 %s          📄  课表 %s" % (
                           now.strftime("%Y-%m-%d"), WEEKDAY_MAP[now.weekday()],
                           "已就绪" if mail_ok else "未填写",
                           "已就绪" if sched_ok else "未选择"))
        J.rrect(cv, w - 104, 8, w - 12, 33, 12,
                fill="#FFFFFF" if (mail_ok and sched_ok) else "#FFF4E0",
                outline=C_BORDER)
        cv.create_text(w - 58, 20, text="第 %d 周" % wk, fill=C_PINK_DARK,
                       font=("Microsoft YaHei UI", 10, "bold"))

    def logw(self, msg, tag=None):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n", tag) if tag else self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    # ---------- 页 1：邮箱 ----------
    def _page_mail(self):
        f = tk.Frame(self.body, bg=C_BG)
        hd = tk.Frame(f, bg=C_BG)
        hd.pack(fill="x", pady=(2, 12))
        tk.Label(hd, text="邮箱配置", bg=C_BG, fg=C_TEXT,
                 font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w")
        tk.Label(hd, text="填写你自己的 QQ 邮箱与授权码，用于发送课表邮件",
                 bg=C_BG, fg=C_TEXT_MUTED, font=("Microsoft YaHei UI", 9)).pack(anchor="w", pady=(2, 0))

        card = J.SoftCard(f, fill="#FFFCFD")
        card.pack(fill="x")
        i = card.get_inner()
        tk.Frame(i, bg="#FFFCFD", height=6).pack()

        tk.Label(i, text="发件邮箱", bg="#FFFCFD", fg=C_TEXT,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(4, 4))
        self.e_sender = J.SoftEntry(i, width=600, height=44,
                                    placeholder="你的 QQ 邮箱，例如 123456@qq.com")
        self.e_sender.pack(anchor="w")

        tk.Label(i, text="授权码", bg="#FFFCFD", fg=C_TEXT,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(14, 4))
        self.e_code = J.SoftEntry(i, width=600, height=44, show="●",
                                  placeholder="QQ 邮箱设置中生成的 16 位授权码（不是登录密码）")
        self.e_code.pack(anchor="w")

        tk.Label(i, text="收件邮箱", bg="#FFFCFD", fg=C_TEXT,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(14, 4))
        self.e_recv = J.SoftEntry(i, width=600, height=44,
                                  placeholder="接收课表提醒的邮箱，可填你自己")
        self.e_recv.pack(anchor="w")

        self.var_show_code = tk.BooleanVar(value=False)
        tk.Checkbutton(i, text="显示授权码", variable=self.var_show_code,
                       command=self._toggle_code, bg="#FFFCFD", fg=C_TEXT_SOFT,
                       activebackground="#FFFCFD", font=("Microsoft YaHei UI", 9),
                       bd=0, highlightthickness=0).pack(anchor="w", pady=(10, 12))

        J.JellyButton(i, "保存邮箱配置", command=self.on_save_mail,
                      width=200, height=50).pack(anchor="w", pady=(0, 10))

        tip = J.SoftCard(f, fill="#FFF7FA", outline="#FFD9E4")
        tip.pack(fill="x", pady=(12, 0))
        ti = tip.get_inner()
        tk.Label(ti, text="💡  授权码怎么获取？", bg="#FFF7FA", fg=C_PINK_DARK,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w")
        tk.Label(ti, text="1. 浏览器打开 mail.qq.com 并登录\n"
                          "2. 点右上角「设置」→「账户」\n"
                          "3. 找到「IMAP/SMTP服务」，点「开启」\n"
                          "4. 按提示用手机发短信验证\n"
                          "5. 页面出现的 16 位字母就是授权码",
                 bg="#FFF7FA", fg=C_TEXT_SOFT, justify="left",
                 font=("Microsoft YaHei UI", 9)).pack(anchor="w", pady=(6, 4))
        return f

    def _toggle_code(self):
        self.e_code.set_show("" if self.var_show_code.get() else "●")

    # ---------- 页 2：课表 ----------
    def _page_sched(self):
        f = tk.Frame(self.body, bg=C_BG)
        hd = tk.Frame(f, bg=C_BG)
        hd.pack(fill="x", pady=(2, 12))
        tk.Label(hd, text="课表设置", bg=C_BG, fg=C_TEXT,
                 font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w")
        tk.Label(hd, text="支持 CSV 或 Excel(.xlsx)，编码自动识别",
                 bg=C_BG, fg=C_TEXT_MUTED, font=("Microsoft YaHei UI", 9)).pack(anchor="w", pady=(2, 0))

        card = J.SoftCard(f, fill="#FFFCFD")
        card.pack(fill="x")
        i = card.get_inner()
        tk.Frame(i, bg="#FFFCFD", height=4).pack()

        tk.Label(i, text="课表文件", bg="#FFFCFD", fg=C_TEXT,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(2, 4))
        r1 = tk.Frame(i, bg="#FFFCFD")
        r1.pack(anchor="w")
        self.e_csv = J.SoftEntry(r1, width=460, height=44, placeholder="选择 CSV 或 .xlsx 文件")
        self.e_csv.pack(side="left")
        J.JellyButton(r1, "浏览…", command=self.on_browse_csv, width=104, height=44,
                      c_top="#FFF2F6", c_bot="#FFDCE6", fg=C_PINK_DARK).pack(side="left", padx=10)

        r2 = tk.Frame(i, bg="#FFFCFD")
        r2.pack(anchor="w", pady=(14, 0))
        c1 = tk.Frame(r2, bg="#FFFCFD")
        c1.pack(side="left", padx=(0, 26))
        tk.Label(c1, text="学期第一周的周一", bg="#FFFCFD", fg=C_TEXT,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.e_start = J.SoftEntry(c1, width=180, height=42, placeholder="2026-09-07")
        self.e_start.pack(anchor="w")

        c2 = tk.Frame(r2, bg="#FFFCFD")
        c2.pack(side="left")
        tk.Label(c2, text="军训周次（无则留空）", bg="#FFFCFD", fg=C_TEXT,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.e_mil = J.SoftEntry(c2, width=180, height=42, placeholder="14,15")
        self.e_mil.pack(anchor="w")

        tk.Frame(i, bg="#FFFCFD", height=16).pack()
        rr = tk.Frame(i, bg="#FFFCFD")
        rr.pack(anchor="w", pady=(0, 12))
        J.JellyButton(rr, "保存课表设置", command=self.on_save_sched,
                      width=200, height=50).pack(side="left", padx=(0, 12))
        J.JellyButton(rr, "一键检测格式", command=self.on_check_format, width=160, height=50,
                      c_top="#FFE9EF", c_bot="#FFD3DF", fg=C_PINK_DARK).pack(side="left", padx=(0, 12))
        J.JellyButton(rr, "预览本周课表", command=self.on_preview_week, width=160, height=50,
                      c_top="#FFE9EF", c_bot="#FFD3DF", fg=C_PINK_DARK).pack(side="left")

        rc = J.SoftCard(f, fill="#FFF7FA", outline="#FFD9E4")
        rc.pack(fill="x", pady=(12, 0))
        ri = rc.get_inner()
        tk.Label(ri, text="⏰  课前二次提醒", bg="#FFF7FA", fg=C_PINK_DARK,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w")
        row = tk.Frame(ri, bg="#FFF7FA")
        row.pack(anchor="w", pady=(6, 2))
        self.var_remind = tk.BooleanVar(value=True)
        tk.Checkbutton(row, text="启用，提前", variable=self.var_remind, bg="#FFF7FA",
                       fg=C_TEXT, activebackground="#FFF7FA", font=("Microsoft YaHei UI", 10),
                       bd=0, highlightthickness=0).pack(side="left")
        self.var_remind_min = tk.IntVar(value=20)
        tk.Spinbox(row, from_=5, to=120, increment=5, width=5, textvariable=self.var_remind_min,
                   font=("Microsoft YaHei UI", 10), bd=0, relief="flat", bg="#FFFFFF",
                   fg=C_TEXT, justify="center", highlightthickness=1,
                   highlightbackground=C_BORDER).pack(side="left", padx=6)
        tk.Label(row, text="分钟", bg="#FFF7FA", fg=C_TEXT,
                 font=("Microsoft YaHei UI", 10)).pack(side="left")
        tk.Label(ri, text="（回应同学建议：早上看过课表，下午上课前仍需加一道提醒）",
                 bg="#FFF7FA", fg=C_TEXT_MUTED, font=("Microsoft YaHei UI", 9)).pack(anchor="w", pady=(2, 4))
        return f

    # ---------- 页 3：发送 ----------
    def _page_send(self):
        f = tk.Frame(self.body, bg=C_BG)
        hd = tk.Frame(f, bg=C_BG)
        hd.pack(fill="x", pady=(2, 12))
        tk.Label(hd, text="发送今日课表", bg=C_BG, fg=C_TEXT,
                 font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w")
        tk.Label(hd, text="点击下方按钮，程序会把今天的课程发送到你的邮箱",
                 bg=C_BG, fg=C_TEXT_MUTED, font=("Microsoft YaHei UI", 9)).pack(anchor="w", pady=(2, 0))

        J.JellyButton(f, "📤   立即发送今日课表", command=self.on_send,
                      width=300, height=58).pack(anchor="w", pady=(0, 16))

        tk.Label(f, text="运行日志", bg=C_BG, fg=C_TEXT,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        frame = tk.Frame(f, bg=C_PINK_LIGHT)
        frame.pack(fill="both", expand=True)
        inner = tk.Frame(frame, bg="#FFFFFF")
        inner.pack(fill="both", expand=True, padx=2, pady=2)
        self.log = ScrolledText(inner, wrap="word", bg="#FFFDFE", fg=C_TEXT,
                                font=("Consolas", 10), bd=0, relief="flat",
                                padx=14, pady=12)
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("ok", foreground="#3FA97A", font=("Consolas", 10, "bold"))
        self.log.tag_config("err", foreground="#E86060", font=("Consolas", 10, "bold"))
        self.log.tag_config("warn", foreground="#D99430")
        self.log.tag_config("dim", foreground=C_TEXT_SOFT)
        self.log.tag_config("info", foreground=C_PINK_DARK, font=("Consolas", 10, "bold"))
        self.log.config(state="disabled")
        return f

    # ---------- 页 4：帮助 ----------
    def _page_help(self):
        f = tk.Frame(self.body, bg=C_BG)
        tk.Label(f, text="使用帮助", bg=C_BG, fg=C_TEXT,
                 font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w", pady=(2, 12))
        frame = tk.Frame(f, bg=C_PINK_LIGHT)
        frame.pack(fill="both", expand=True)
        inner = tk.Frame(frame, bg="#FFFFFF")
        inner.pack(fill="both", expand=True, padx=2, pady=2)
        t = ScrolledText(inner, wrap="word", bg="#FFFDFE", fg=C_TEXT,
                         font=("Microsoft YaHei UI", 10), bd=0, relief="flat",
                         padx=16, pady=14)
        t.pack(fill="both", expand=True)
        t.tag_config("h", foreground=C_PINK_DARK, font=("Microsoft YaHei UI", 11, "bold"))
        for text, tag in HELP_TEXT:
            if tag:
                t.insert("end", text + "\n", tag)
            else:
                t.insert("end", text + "\n")
        t.config(state="disabled")
        return f

    # ---------- 数据 ----------
    def _load_to_ui(self):
        self.e_sender.set(self.cfg.get("sender_email", ""))
        self.e_code.set(self.cfg.get("auth_code", ""))
        self.e_recv.set(self.cfg.get("receiver_email", ""))
        self.e_csv.set(self.cfg.get("csv_path", ""))
        self.e_start.set(self.cfg.get("semester_start", "2026-09-07"))
        self.e_mil.set(self.cfg.get("military_weeks", ""))
        self.var_remind.set(bool(self.cfg.get("remind_enabled", True)))
        try:
            self.var_remind_min.set(int(self.cfg.get("remind_minutes", 20)))
        except Exception:
            self.var_remind_min.set(20)

    def _collect(self):
        self.cfg["sender_email"] = self.e_sender.get().strip()
        self.cfg["auth_code"] = self.e_code.get().strip()
        self.cfg["receiver_email"] = self.e_recv.get().strip()
        self.cfg["csv_path"] = self.e_csv.get().strip()
        self.cfg["semester_start"] = self.e_start.get().strip() or "2026-09-07"
        self.cfg["military_weeks"] = self.e_mil.get().strip()
        self.cfg["remind_enabled"] = bool(self.var_remind.get())
        try:
            self.cfg["remind_minutes"] = max(5, min(120, int(self.var_remind_min.get())))
        except Exception:
            self.cfg["remind_minutes"] = 20

    # ---------- 事件 ----------
    def on_save_mail(self):
        self._collect()
        if not all([self.cfg["sender_email"], self.cfg["auth_code"], self.cfg["receiver_email"]]):
            messagebox.showwarning("还差一点", "请把三项邮箱配置都填写完整")
            return
        if "@" not in self.cfg["sender_email"]:
            messagebox.showwarning("格式不对", "发件邮箱看起来不是有效的邮箱地址")
            return
        save_config(self.cfg)
        self.refresh_status()
        messagebox.showinfo("已保存", "邮箱配置已保存")

    def on_save_sched(self):
        self._collect()
        save_config(self.cfg)
        self.refresh_status()
        messagebox.showinfo("已保存", "课表设置已保存")

    def on_browse_csv(self):
        path = filedialog.askopenfilename(
            title="选择课表文件",
            filetypes=[("课表文件", "*.csv *.xlsx *.xls"),
                       ("CSV", "*.csv"), ("Excel", "*.xlsx *.xls"), ("所有文件", "*.*")])
        if path:
            self.e_csv.set(path)
            self._collect()
            save_config(self.cfg)
            self.refresh_status()
            self.df = None

    def _load_df(self, silent=False):
        p = self.cfg.get("csv_path", "")
        if not p or not os.path.exists(p):
            if not silent:
                messagebox.showwarning("还没选课表", "请先在「② 课表设置」选择课表文件")
            return None
        try:
            df = normalize_df(read_schedule_file(p))
            ok, problems, _ = validate_schedule(df)
            if not ok:
                if not silent:
                    messagebox.showerror("课表格式有问题",
                                         "\n\n".join(problems) +
                                         "\n\n请修正后重试，或点「一键检测格式」查看详情")
                return None
            self.df = df
            return df
        except Exception as e:
            if not silent:
                messagebox.showerror("读取失败", str(e))
            return None

    def on_check_format(self):
        self._collect()
        p = self.cfg.get("csv_path", "")
        if not p or not os.path.exists(p):
            messagebox.showwarning("还没选课表", "请先选择课表文件")
            return
        try:
            df = normalize_df(read_schedule_file(p))
        except Exception as e:
            messagebox.showerror("读取失败", str(e))
            return
        ok, problems, stats = validate_schedule(df)
        if ok:
            messagebox.showinfo("检测通过",
                                "课表格式正确，可以正常使用。\n\n"
                                "总行数：%s\n课程数：%s\n有课的星期：%s"
                                % (stats.get("总行数"), stats.get("课程数"), stats.get("有课的星期")))
        else:
            messagebox.showerror("发现问题", "\n\n".join(problems))

    def on_preview_week(self):
        self._collect()
        df = self._load_df()
        if df is None:
            return
        wk = current_week(self.cfg["semester_start"])
        mil = {int(x) for x in self.cfg["military_weeks"].replace("，", ",").split(",")
               if x.strip().isdigit()}
        win = tk.Toplevel(self)
        win.title("本周课表 · 第 %d 周" % wk)
        win.geometry("700x560")
        win.configure(bg=C_BG)
        tk.Label(win, text="第 %d 周课表预览" % wk, bg=C_BG, fg=C_TEXT,
                 font=("Microsoft YaHei UI", 14, "bold")).pack(pady=(16, 6))
        if wk in mil:
            tk.Label(win, text="本周为军训周，所有课程停课", bg=C_BG, fg="#D99430",
                     font=("Microsoft YaHei UI", 11)).pack(pady=30)
            return
        frame = tk.Frame(win, bg=C_PINK_LIGHT)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        inner = tk.Frame(frame, bg="#FFFFFF")
        inner.pack(fill="both", expand=True, padx=2, pady=2)
        t = ScrolledText(inner, wrap="word", bg="#FFFDFE", fg=C_TEXT,
                         font=("Microsoft YaHei UI", 10), bd=0, relief="flat", padx=14, pady=12)
        t.pack(fill="both", expand=True)
        t.tag_config("head", foreground=C_PINK_DARK, font=("Microsoft YaHei UI", 10, "bold"))
        t.tag_config("none", foreground=C_TEXT_MUTED)
        total = 0
        for wd in range(7):
            name = WEEKDAY_MAP[wd]
            cs = courses_of_day(df, name, wk)
            total += len(cs)
            t.insert("end", "【%s】  共 %d 节\n" % (name, len(cs)), "head")
            if not cs:
                t.insert("end", "    无课\n", "none")
            for c in cs:
                t.insert("end", "    %s-%s  %s\n        %s · %s\n" % (
                    c["开始时间"], c["结束时间"], c["课程名"], c["地点"], c["教师"]))
            t.insert("end", "\n")
        t.config(state="disabled")
        tk.Label(win, text="本周共 %d 节课" % total, bg=C_BG, fg=C_TEXT_SOFT,
                 font=("Microsoft YaHei UI", 9)).pack(pady=(0, 12))

    # ---------- 发送 ----------
    def _send_one(self, subject, body):
        last_err = None
        for attempt in range(MAX_RETRY + 1):
            try:
                msg = MIMEText(body, "plain", "utf-8")
                msg["Subject"] = Header(subject, "utf-8")
                msg["From"] = self.cfg["sender_email"]
                msg["To"] = self.cfg["receiver_email"]
                server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT)
                try:
                    server.login(self.cfg["sender_email"], self.cfg["auth_code"])
                    server.sendmail(self.cfg["sender_email"],
                                    [self.cfg["receiver_email"]], msg.as_string())
                finally:
                    try:
                        server.quit()
                    except Exception:
                        pass
                return True, None, attempt
            except smtplib.SMTPAuthenticationError:
                return False, "授权码错误或 QQ 邮箱未开启 IMAP/SMTP 服务", attempt
            except Exception as e:
                last_err = e
                if attempt < MAX_RETRY:
                    self.logw("   ↻ 第 %d 次发送失败（%s），3 秒后重试…"
                              % (attempt + 1, type(e).__name__), "warn")
                    self.update()
                    _time.sleep(3)
        return False, str(last_err), MAX_RETRY

    def _append_history(self, ok, detail):
        try:
            with open(HISTORY_PATH, "a", encoding="utf-8") as f:
                f.write("%s | %s | %s\n" % (
                    datetime.now(BJ_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                    "SUCCESS" if ok else "FAILED", detail))
        except Exception:
            pass

    def on_send(self):
        self._collect()
        save_config(self.cfg)
        self.refresh_status()
        if pd is None:
            messagebox.showerror("缺少组件", "缺少 pandas 库，无法读取课表")
            return
        if not all([self.cfg["sender_email"], self.cfg["auth_code"], self.cfg["receiver_email"]]):
            messagebox.showwarning("还没配置邮箱", "请先在「① 邮箱配置」里填写完整")
            self.seg.select(0)
            self.pages[0].lift()
            return

        df = self._load_df()
        if df is None:
            return

        now = datetime.now(BJ_TZ)
        wd = WEEKDAY_MAP[now.weekday()]
        wk = current_week(self.cfg["semester_start"])
        mil = {int(x) for x in self.cfg["military_weeks"].replace("，", ",").split(",")
               if x.strip().isdigit()}
        courses = [] if wk in mil else courses_of_day(df, wd, wk)
        body = build_body(courses, "%s %s" % (now.strftime("%Y-%m-%d"), wd), wk, wk in mil)
        subject = "今日课表提醒 %s" % now.strftime("%Y-%m-%d")

        self.logw("─" * 54, "dim")
        self.logw("正在发送…", "info")
        self.update()
        ok, err, retries = self._send_one(subject, body)

        if ok:
            self.logw("发送成功！请到 %s 查收" % self.cfg["receiver_email"], "ok")
            if retries:
                self.logw("   （重试 %d 次后成功）" % retries, "warn")
            for line in body.split("\n"):
                self.logw("   " + line, "dim")
            self._append_history(True, "第%d周 %s 课程数=%d retry=%d" % (wk, wd, len(courses), retries))

            if self.cfg.get("remind_enabled") and courses and wk not in mil:
                mins = int(self.cfg.get("remind_minutes", 20))
                upcoming = []
                for c in courses:
                    try:
                        h, m = c["开始时间"].split(":")
                        t_start = now.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
                        if t_start > now:
                            gap = int((t_start - now).total_seconds() // 60)
                            upcoming.append((c, t_start, gap))
                    except Exception:
                        continue
                if upcoming:
                    self.logw("   课前提醒已启用（提前 %d 分钟）" % mins, "info")
                    for c, t_start, gap in upcoming:
                        rt = t_start - timedelta(minutes=mins)
                        tag = "ok" if gap <= mins else "warn"
                        self.logw("      %s  %s  →  提醒时间 %s%s" % (
                            c["课程名"], t_start.strftime("%H:%M"), rt.strftime("%H:%M"),
                            "（已进入提醒窗口）" if gap <= mins else ""), tag)
            messagebox.showinfo("发送成功", "邮件已发送，请到邮箱查收！")
        else:
            self.logw("发送失败：%s" % err, "err")
            self._append_history(False, str(err)[:120])
            if "授权码" in str(err):
                messagebox.showerror("认证失败",
                                     "授权码不正确，或 QQ 邮箱未开启 SMTP 服务。\n\n"
                                     "请检查：\n"
                                     "1. 是否用的是「授权码」而不是 QQ 登录密码\n"
                                     "2. QQ 邮箱 → 设置 → 账户 → IMAP/SMTP服务 是否已开启")
            else:
                messagebox.showerror("发送失败", "%s\n\n详细信息见日志区" % err)


if __name__ == "__main__":
    App().mainloop()