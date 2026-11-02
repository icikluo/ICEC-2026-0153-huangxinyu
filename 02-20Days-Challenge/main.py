# -*- coding: utf-8 -*-
"""
每日课表邮件提醒 v2（支持周次）
功能：读取 schedule.csv -> 按周次+星期筛选当天课程 -> QQ 邮箱发送 -> 追加日志
安全：
  1. 邮箱与授权码全部来自环境变量或本地 .env，不写死在代码中
  2. 日志只记录运行元数据（时间/周次/课程数/状态/耗时），不记录课程名、地点、教师
  3. 日志中邮箱脱敏；报错文本中若意外出现授权码，兜底替换为 ***
"""

import os
import sys
import time
import smtplib
import traceback
from datetime import datetime, timezone, timedelta, date
from email.mime.text import MIMEText
from email.header import Header

import pandas as pd

# ===== 路径配置 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "schedule.csv")
ENV_PATH = os.path.join(BASE_DIR, ".env")
LOG_DIR = os.path.join(BASE_DIR, "process_logs")
LOG_PATH = os.path.join(LOG_DIR, "daily_log.txt")

# ===== 学期配置：第 1 周周一 = 2026-09-07 =====
SEMESTER_START = date(2026, 9, 7)
MILITARY_WEEKS = {14, 15}   # 军训周：所有课程停课

# ===== 时间配置：显式使用北京时间，避免云端 UTC 判断错星期 =====
BJ_TZ = timezone(timedelta(hours=8))
WEEKDAY_MAP = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四",
               4: "星期五", 5: "星期六", 6: "星期日"}

# ===== 邮件配置 =====
SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SMTP_TIMEOUT = 30
MAX_RETRY = 2
REQUIRED_COLS = {"周次", "星期", "课程名", "开始时间", "结束时间", "地点", "教师"}


def load_dotenv_file():
    """本地运行时自动读取同目录 .env（该文件被 .gitignore 忽略，不会入库）。
    云端 GitHub Actions 不使用 .env，直接通过 Repository Secrets 注入环境变量。
    已存在的环境变量优先，不会被 .env 覆盖。
    """
    if not os.path.exists(ENV_PATH):
        return
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def mask_email(addr):
    """邮箱脱敏：3444545380@qq.com -> 3*********@qq.com"""
    if not addr or "@" not in addr:
        return "***"
    name, domain = addr.split("@", 1)
    if len(name) <= 1:
        return "*@" + domain
    return name[0] + "*" * (len(name) - 1) + "@" + domain


def sanitize(text, secrets):
    """兜底：把文本中出现的任何密钥替换成 ***，防止写进日志"""
    if not text:
        return text
    for s in secrets:
        if s and len(s) >= 6 and s in text:
            text = text.replace(s, "***")
    return text


def current_week(today):
    """计算今天是学期第几周"""
    return (today - SEMESTER_START).days // 7 + 1


def parse_weeks(cell):
    """解析周次表达式：'3;5-13;16-18' -> {3, 5..13, 16..18}"""
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


def load_today_courses(weekday_name, week_no):
    """读取课表，筛选当天当周课程；返回 (课程列表, 课表总条数, 是否军训周)"""
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError("schedule.csv 缺少列: %s" % ",".join(sorted(missing)))

    total = len(df)

    if week_no in MILITARY_WEEKS:
        return [], total, True

    df["_weeks"] = df["周次"].apply(parse_weeks)
    hit = df[(df["星期"] == weekday_name) & (df["_weeks"].apply(lambda s: week_no in s))]
    hit = hit.sort_values("开始时间")
    return hit.to_dict("records"), total, False


def build_body(courses, today_str, week_no, is_military):
    """生成邮件正文"""
    if is_military:
        return "军训期间，无课。\n\n日期：%s（第 %d 周）" % (today_str, week_no)

    if not courses:
        return "今天没有课，好好休息。\n\n日期：%s（第 %d 周）" % (today_str, week_no)

    lines = ["今日课表提醒", "日期：%s（第 %d 周）" % (today_str, week_no), ""]
    for c in courses:
        lines.append("· %s-%s  %s  %s  教师：%s" % (
            c["开始时间"], c["结束时间"], c["课程名"], c["地点"], c["教师"]))
    lines.append("")
    lines.append("共 %d 节课" % len(courses))
    return "\n".join(lines)


def send_mail(subject, body, sender, auth_code, receiver):
    """QQ 邮箱 SMTP_SSL(465) 发信，失败自动重试"""
    retry = 0
    last_err = None
    for attempt in range(MAX_RETRY + 1):
        retry = attempt
        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = Header(subject, "utf-8")
            msg["From"] = sender
            msg["To"] = receiver

            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT)
            try:
                server.login(sender, auth_code)
                server.sendmail(sender, [receiver], msg.as_string())
            finally:
                try:
                    server.quit()
                except Exception:
                    pass
            return True, None, retry
        except Exception as e:
            last_err = "%s: %s" % (type(e).__name__, e)
            if attempt < MAX_RETRY:
                time.sleep(5)
    return False, last_err, retry


def write_log(status, detail):
    """日志：一行一条，追加写入 process_logs/daily_log.txt"""
    os.makedirs(LOG_DIR, exist_ok=True)
    now = datetime.now(BJ_TZ).strftime("%Y-%m-%d %H:%M:%S %z")
    trigger = os.environ.get("GITHUB_EVENT_NAME", "local")
    line = "%s | trigger=%s | %s | %s\n" % (now, trigger, status, detail)

    # 追加前先检查文件末尾是否为换行符，避免新记录与上一行粘连
    needs_newline = False
    if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > 0:
        with open(LOG_PATH, "rb") as f:
            f.seek(-1, os.SEEK_END)
            needs_newline = f.read(1) != b"\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        if needs_newline:
            f.write("\n")
        f.write(line)


def main():
    load_dotenv_file()
    start = time.time()
    today = datetime.now(BJ_TZ)
    today_str = today.strftime("%Y-%m-%d")
    weekday_name = WEEKDAY_MAP[today.weekday()]
    week_no = current_week(today.date())

    sender = os.environ.get("SENDER_EMAIL")
    auth_code = os.environ.get("SENDER_AUTH_CODE")
    receiver = os.environ.get("RECEIVER_EMAIL")
    secrets_to_mask = [auth_code]

    if not all([sender, auth_code, receiver]):
        detail = "缺少环境变量 SENDER_EMAIL / SENDER_AUTH_CODE / RECEIVER_EMAIL"
        write_log("FAILED", detail)
        print(detail)
        sys.exit(1)

    try:
        courses, total, is_military = load_today_courses(weekday_name, week_no)
        body = build_body(courses, "%s %s" % (today_str, weekday_name), week_no, is_military)
        subject = "今日课表提醒 %s" % today_str

        ok, err, retry = send_mail(subject, body, sender, auth_code, receiver)
        duration_ms = int((time.time() - start) * 1000)

        # 注意：日志只写元数据，不写课程名/地点/教师，保护隐私
        mode = "军训周" if is_military else "正常"
        if ok:
            detail = ("周次=%d | 星期=%s | 模式=%s | 课表总数=%d | 今日课程数=%d | "
                      "邮件=SUCCESS | 收件人=%s | retry=%d | 耗时=%dms") % (
                week_no, weekday_name, mode, total, len(courses),
                mask_email(receiver), retry, duration_ms)
            write_log("SUCCESS", detail)
            print(detail)
        else:
            err = sanitize(err, secrets_to_mask)
            detail = ("周次=%d | 星期=%s | 模式=%s | 课表总数=%d | 今日课程数=%d | "
                      "邮件=FAILED | retry=%d | 耗时=%dms | error=%s") % (
                week_no, weekday_name, mode, total, len(courses), retry, duration_ms, err)
            write_log("FAILED", detail)
            print(detail)
            sys.exit(1)

    except Exception:
        err = sanitize(traceback.format_exc().replace("\n", " "), secrets_to_mask)
        duration_ms = int((time.time() - start) * 1000)
        detail = "异常 | 耗时=%dms | error=%s" % (duration_ms, err[:500])
        write_log("ERROR", detail)
        print(detail)
        sys.exit(1)


if __name__ == "__main__":
    main()
