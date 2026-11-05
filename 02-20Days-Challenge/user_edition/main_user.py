# -*- coding: utf-8 -*-
"""
课表提醒 用户版 v1.0
====================
供同学使用的图形界面版本：
  - 配置邮箱与授权码
  - 选择自己的课表 CSV
  - 发送测试邮件
配置保存在 exe 同目录的 config.json 中。
"""

import os
import sys
import json
import smtplib
import traceback
from datetime import datetime, timezone, timedelta, date
from email.mime.text import MIMEText
from email.header import Header

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import pandas as pd
except ImportError:
    pd = None

APP_NAME = "课表提醒"
APP_VERSION = "v1.0"
APP_AUTHOR = "ICEC-2026-0153"

# ===== 路径：兼容 PyInstaller 打包后的情况 =====
def app_dir():
    """返回 exe（或脚本）所在目录，用于存放配置文件"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(app_dir(), "config.json")

# ===== 时间 =====
BJ_TZ = timezone(timedelta(hours=8))
WEEKDAY_MAP = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四",
               4: "星期五", 5: "星期六", 6: "星期日"}

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SMTP_TIMEOUT = 30
REQUIRED_COLS = {"周次", "星期", "课程名", "开始时间", "结束时间", "地点", "教师"}

DEFAULT_CONFIG = {
    "sender_email": "",
    "auth_code": "",
    "receiver_email": "",
    "csv_path": "",
    "semester_start": "2026-09-07",
    "military_weeks": "14,15",
}


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
    """'3;5-13;16-18' -> set"""
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


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.title(f"{APP_NAME} {APP_VERSION}  -  {APP_AUTHOR}")
        self.geometry("560x520")
        self.resizable(False, False)

        self._build_ui()
        self._load_to_ui()

    # ---------- UI ----------
    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_mail = ttk.Frame(nb, padding=15)
        self.tab_csv = ttk.Frame(nb, padding=15)
        self.tab_send = ttk.Frame(nb, padding=15)
        nb.add(self.tab_mail, text="  1. 邮箱配置  ")
        nb.add(self.tab_csv, text="  2. 课表设置  ")
        nb.add(self.tab_send, text="  3. 发送测试  ")

        # --- 邮箱配置 ---
        f = self.tab_mail
        ttk.Label(f, text="发件邮箱（你自己的 QQ 邮箱）").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.e_sender = ttk.Entry(f, width=45)
        self.e_sender.grid(row=1, column=0, sticky="w", pady=(0, 12))

        ttk.Label(f, text="授权码（QQ 邮箱设置的 16 位授权码，不是登录密码）").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.e_code = ttk.Entry(f, width=45, show="*")
        self.e_code.grid(row=3, column=0, sticky="w", pady=(0, 12))

        ttk.Label(f, text="收件邮箱（接收课表提醒）").grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.e_recv = ttk.Entry(f, width=45)
        self.e_recv.grid(row=5, column=0, sticky="w", pady=(0, 12))

        ttk.Button(f, text="保存配置", command=self.on_save_mail).grid(row=6, column=0, sticky="w", pady=(0, 15))

        tip = ("如何获取授权码：\n"
               "1. 浏览器打开 mail.qq.com 并登录\n"
               "2. 设置 → 账户 → 找到「IMAP/SMTP服务」\n"
               "3. 点击「开启」，按提示用手机发短信验证\n"
               "4. 生成的 16 位字母就是授权码")
        ttk.Label(f, text=tip, foreground="#666", justify="left").grid(row=7, column=0, sticky="w")

        # --- 课表设置 ---
        f = self.tab_csv
        ttk.Label(f, text="课表文件（CSV 格式）").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.e_csv = ttk.Entry(f, width=38)
        self.e_csv.grid(row=1, column=0, sticky="w")
        ttk.Button(f, text="浏览...", command=self.on_browse_csv).grid(row=1, column=1, padx=5)

        ttk.Label(f, text="学期第一周的周一（格式 YYYY-MM-DD）").grid(row=2, column=0, sticky="w", pady=(15, 4))
        self.e_start = ttk.Entry(f, width=20)
        self.e_start.grid(row=3, column=0, sticky="w", pady=(0, 12))

        ttk.Label(f, text="军训周次（逗号分隔，无则留空）").grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.e_mil = ttk.Entry(f, width=20)
        self.e_mil.grid(row=5, column=0, sticky="w", pady=(0, 12))

        ttk.Button(f, text="保存配置", command=self.on_save_csv).grid(row=6, column=0, sticky="w", pady=(0, 15))

        tip2 = ("CSV 文件需包含以下列：\n"
                "周次, 星期, 课程名, 开始时间, 结束时间, 地点, 教师\n\n"
                "周次写法：3;5-13;16-18 表示第 3、5~13、16~18 周\n"
                "星期写法：星期一 ~ 星期日\n\n"
                "可参考随附的「课表模板.csv」")
        ttk.Label(f, text=tip2, foreground="#666", justify="left").grid(row=7, column=0, columnspan=2, sticky="w")

        # --- 发送测试 ---
        f = self.tab_send
        self.lbl_info = ttk.Label(f, text="", justify="left", foreground="#333")
        self.lbl_info.grid(row=0, column=0, sticky="w", pady=(0, 15))

        ttk.Button(f, text="立即发送今日课表", command=self.on_send).grid(row=1, column=0, sticky="w", pady=(0, 15))

        self.txt_log = tk.Text(f, height=14, width=62, state="disabled", bg="#f5f5f5")
        self.txt_log.grid(row=2, column=0, sticky="nsew")

        self.refresh_info()

    # ---------- 数据绑定 ----------
    def _load_to_ui(self):
        self.e_sender.insert(0, self.cfg.get("sender_email", ""))
        self.e_code.insert(0, self.cfg.get("auth_code", ""))
        self.e_recv.insert(0, self.cfg.get("receiver_email", ""))
        self.e_csv.insert(0, self.cfg.get("csv_path", ""))
        self.e_start.insert(0, self.cfg.get("semester_start", "2026-09-07"))
        self.e_mil.insert(0, self.cfg.get("military_weeks", "14,15"))

    def _collect(self):
        self.cfg["sender_email"] = self.e_sender.get().strip()
        self.cfg["auth_code"] = self.e_code.get().strip()
        self.cfg["receiver_email"] = self.e_recv.get().strip()
        self.cfg["csv_path"] = self.e_csv.get().strip()
        self.cfg["semester_start"] = self.e_start.get().strip()
        self.cfg["military_weeks"] = self.e_mil.get().strip()

    def on_save_mail(self):
        self._collect()
        if not self.cfg["sender_email"] or not self.cfg["auth_code"] or not self.cfg["receiver_email"]:
            messagebox.showwarning("提示", "请把三项邮箱配置都填写完整")
            return
        save_config(self.cfg)
        messagebox.showinfo("成功", "邮箱配置已保存")
        self.refresh_info()

    def on_save_csv(self):
        self._collect()
        save_config(self.cfg)
        messagebox.showinfo("成功", "课表设置已保存")
        self.refresh_info()

    def on_browse_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")])
        if path:
            self.e_csv.delete(0, "end")
            self.e_csv.insert(0, path)
            self._collect()
            save_config(self.cfg)
            self.refresh_info()

    def refresh_info(self):
        now = datetime.now(BJ_TZ)
        wk = current_week(self.cfg.get("semester_start", "2026-09-07"))
        csv_ok = "✅ 已选择" if self.cfg.get("csv_path") and os.path.exists(self.cfg["csv_path"]) else "❌ 未选择"
        mail_ok = "✅ 已填写" if all([self.cfg.get("sender_email"), self.cfg.get("auth_code"), self.cfg.get("receiver_email")]) else "❌ 未填写"
        txt = (f"今天：{now.strftime('%Y-%m-%d %H:%M')}  {WEEKDAY_MAP[now.weekday()]}  第 {wk} 周\n"
               f"邮箱配置：{mail_ok}    课表文件：{csv_ok}")
        self.lbl_info.config(text=txt)

    def log(self, msg):
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    # ---------- 发送 ----------
    def on_send(self):
        self._collect()
        save_config(self.cfg)

        if not all([self.cfg["sender_email"], self.cfg["auth_code"], self.cfg["receiver_email"]]):
            messagebox.showwarning("提示", "请先在「邮箱配置」里填写完整")
            return
        if pd is None:
            messagebox.showerror("错误", "缺少 pandas 库，无法读取课表")
            return
        csv_path = self.cfg["csv_path"]
        if not csv_path or not os.path.exists(csv_path):
            messagebox.showwarning("提示", "请先在「课表设置」里选择课表 CSV 文件")
            return

        try:
            now = datetime.now(BJ_TZ)
            weekday_name = WEEKDAY_MAP[now.weekday()]
            wk = current_week(self.cfg["semester_start"])
            mil = {int(x) for x in self.cfg["military_weeks"].replace("，", ",").split(",") if x.strip().isdigit()}

            df = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str)
            df.columns = [c.strip() for c in df.columns]
            for col in df.columns:
                df[col] = df[col].fillna("").astype(str).str.strip()

            missing = REQUIRED_COLS - set(df.columns)
            if missing:
                messagebox.showerror("课表格式错误",
                                     "CSV 缺少列：%s\n\n需要的列：%s" % (
                                         "、".join(sorted(missing)), "、".join(sorted(REQUIRED_COLS))))
                return

            if wk in mil:
                body = "军训期间，无课。\n\n日期：%s（第 %d 周）" % (now.strftime("%Y-%m-%d"), wk)
                courses = []
            else:
                df["_w"] = df["周次"].apply(parse_weeks)
                hit = df[(df["星期"] == weekday_name) & (df["_w"].apply(lambda s: wk in s))]
                hit = hit.sort_values("开始时间")
                courses = hit.to_dict("records")
                if not courses:
                    body = "今天没有课，好好休息。\n\n日期：%s（第 %d 周）" % (now.strftime("%Y-%m-%d"), wk)
                else:
                    lines = ["今日课表提醒", "日期：%s %s（第 %d 周）" % (
                        now.strftime("%Y-%m-%d"), weekday_name, wk), ""]
                    for c in courses:
                        lines.append("· %s-%s  %s  %s  教师：%s" % (
                            c["开始时间"], c["结束时间"], c["课程名"], c["地点"], c["教师"]))
                    lines += ["", "共 %d 节课" % len(courses)]
                    body = "\n".join(lines)

            subject = "今日课表提醒 %s" % now.strftime("%Y-%m-%d")
            self.log("正在发送...")
            self.update()

            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = Header(subject, "utf-8")
            msg["From"] = self.cfg["sender_email"]
            msg["To"] = self.cfg["receiver_email"]

            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT)
            try:
                server.login(self.cfg["sender_email"], self.cfg["auth_code"])
                server.sendmail(self.cfg["sender_email"], [self.cfg["receiver_email"]], msg.as_string())
            finally:
                try:
                    server.quit()
                except Exception:
                    pass

            self.log("✅ 发送成功！请到 %s 查收" % self.cfg["receiver_email"])
            for line in body.split("\n"):
                self.log("   " + line)
            messagebox.showinfo("发送成功", "邮件已发送，请到邮箱查收！")

        except smtplib.SMTPAuthenticationError:
            self.log("❌ 授权码错误或邮箱设置未开启")
            messagebox.showerror("认证失败",
                                 "授权码不正确，或 QQ 邮箱未开启 SMTP 服务。\n\n"
                                 "请检查：\n"
                                 "1. 是否用的是「授权码」而非登录密码\n"
                                 "2. QQ 邮箱 设置→账户→IMAP/SMTP服务 是否已开启")
        except Exception as e:
            self.log("❌ 发送失败：%s" % e)
            messagebox.showerror("发送失败", "%s\n\n详细信息见日志区" % e)


if __name__ == "__main__":
    app = App()
    app.mainloop()