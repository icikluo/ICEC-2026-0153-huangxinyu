# 第二阶段方案：20 天挑战营 - 课表邮件提醒程序

## 项目四：解决校园真实痛点的轻量化实用程序研发

---

## 一、项目概述

### 1.1 痛点分析

**校园场景中的真实问题：**
- 学生经常忘记下一节课的时间和教室
- 早课需要提前出门，容易睡过头
- 不同课程在不同教学楼，容易走错或迟到
- 课程变动（调课、停课）难以及时通知

### 1.2 解决方案

开发一个**课表邮件提醒程序**，功能包括：
- 查看每日/每周课表
- 课前定时发送邮件提醒（提前 30 分钟/1 小时）
- 支持多邮箱配置（QQ 邮箱/163 邮箱/Gmail）
- 本地数据存储（JSON/SQLite）

### 1.3 技术栈

| 技术领域 | 选型 |
|---------|------|
| 编程语言 | Python 3.10+ |
| Web 框架 | Flask |
| 邮件服务 | SMTP (QQ 邮箱/163 邮箱) |
| 定时任务 | APScheduler |
| 数据存储 | JSON (基础版) / SQLite (完整版) |
| 前端模板 | Jinja2 + Bootstrap |

---

## 二、版本规划

### 基础版（第 1 周）

**核心功能：**
- ✅ 课表查看（按日/周）
- ✅ 邮件定时提醒
- ✅ JSON 数据存储
- ✅ 命令行界面

**交付要求：**
- 程序可运行
- 连续 7 天运行日志
- 至少 1 次迭代优化

### 完整版（第 2-3 周）

**扩展功能：**
- ✅ 用户登录系统
- ✅ 课表 CRUD 操作（增删改查）
- ✅ 数据库存储（SQLite）
- ✅ Web 界面
- ✅ 数据统计（出勤率、课程分布）
- ✅ 移动端适配

**交付要求：**
- 完整功能实现
- 连续 7 天运行日志（含迭代）
- 至少 3 次 Git 迭代
- 8 位用户使用反馈

---

## 三、系统架构

### 3.1 模块设计

```
┌─────────────────────────────────────────────────────┐
│                  课表邮件提醒程序                     │
├─────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Web 界面  │  │ 命令行   │  │  API 接口 │  ← 用户交互层
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │             │                │
│       └─────────────┼─────────────┘                │
│                     ▼                               │
│  ┌──────────────────────────────────────────────┐  │
│  │              业务逻辑层                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │  │
│  │  │ 课表管理  │  │ 提醒调度  │  │ 邮件发送  │   │  │
│  │  └──────────┘  └──────────┘  └──────────┘   │  │
│  └──────────────────────────────────────────────┘  │
│                     ▼                               │
│  ┌──────────────────────────────────────────────┐  │
│  │              数据持久层                       │  │
│  │      JSON 文件  /  SQLite 数据库               │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 3.2 目录结构

```
02-20Days-Challenge/
├── src/                        # 源代码
│   ├── app.py                  # Flask 应用入口
│   ├── config.py               # 配置文件
│   ├── models/                 # 数据模型
│   │   ├── schedule.py         # 课表模型
│   │   └── user.py             # 用户模型（完整版）
│   ├── services/               # 业务逻辑
│   │   ├── email_service.py    # 邮件服务
│   │   ├── scheduler.py        # 定时任务
│   │   └── schedule_service.py # 课表服务
│   └── utils/                  # 工具函数
│       └── helpers.py
├── templates/                  # HTML 模板（完整版）
│   ├── base.html
│   ├── index.html
│   └── schedule.html
├── static/                     # 静态文件
│   ├── css/
│   └── js/
├── data/                       # 数据存储
│   ├── schedules.json          # 课表数据
│   └── users.db                # 用户数据库（完整版）
├── logs/                       # 运行日志
│   ├── app.log
│   └── process_logs/           # 过程日志（必交）
│       ├── 2026-10-25.log
│       ├── 2026-10-26.log
│       └── ...
├── tests/                      # 测试文件
│   ├── test_email.py
│   └── test_scheduler.py
├── requirements.txt            # 依赖包
├── README.md                   # 项目说明
└── iterations/                 # 迭代记录
    ├── iteration-1.md
    ├── iteration-2.md
    └── iteration-3.md
```

---

## 四、核心功能实现

### 4.1 课表数据结构

```python
# data/schedules.json 示例
{
    "schedules": [
        {
            "id": 1,
            "course_name": "人工智能导论",
            "teacher": "张老师",
            "location": "信通学院 431",
            "day_of_week": 1,      # 0=周一，1=周二，...
            "start_time": "08:00",
            "end_time": "09:35",
            "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
            "reminder提前量": 30     # 分钟
        },
        {
            "id": 2,
            "course_name": "Python 程序设计",
            "teacher": "李老师",
            "location": "信通学院 429",
            "day_of_week": 3,
            "start_time": "14:00",
            "end_time": "15:35",
            "weeks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
            "reminder提前量": 60
        }
    ]
}
```

### 4.2 邮件服务（email_service.py）

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_reminder(self, receiver_email, course_info):
        """发送课表提醒邮件"""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"⏰ 课程提醒：{course_info['course_name']}"
        
        body = f"""
        亲爱的同学：
        
        提醒您即将上课：
        
        📚 课程：{course_info['course_name']}
        👨‍🏫 教师：{course_info['teacher']}
        📍 地点：{course_info['location']}
        ⏰ 时间：{course_info['start_time']} - {course_info['end_time']}
        
        请提前做好准备！
        
        —— 课表邮件提醒系统
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
```

### 4.3 定时调度（scheduler.py）

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
import schedule

class ScheduleScheduler:
    def __init__(self, email_service, schedule_service):
        self.scheduler = BackgroundScheduler()
        self.email_service = email_service
        self.schedule_service = schedule_service
    
    def start(self):
        """启动定时任务"""
        # 每天检查课表
        self.scheduler.add_job(self.check_daily_reminders, 'cron', hour=7, minute=0)
        self.scheduler.start()
    
    def check_daily_reminders(self):
        """检查当天需要发送的提醒"""
        today = datetime.now().weekday()
        courses = self.schedule_service.get_courses_today(today)
        
        for course in courses:
            # 计算提醒时间
            reminder_time = self.calculate_reminder_time(course)
            self.scheduler.add_job(
                self.send_course_reminder,
                'date',
                run_date=reminder_time,
                args=[course]
            )
    
    def send_course_reminder(self, course):
        """发送课程提醒"""
        self.email_service.send_reminder("student@example.com", course)
```

---

## 五、开发计划（20 天）

### 第 1 周（10/23 - 10/29）：基础版开发

| 日期 | 任务 | 交付物 |
|-----|------|-------|
| 10/23 | 需求分析、技术选型、环境搭建 | 项目架构设计文档 |
| 10/24 | 课表数据结构设计、JSON 存储实现 | models/schedule.py |
| 10/25 | 邮件服务模块开发、测试 | services/email_service.py |
| 10/26 | 定时调度模块开发 | services/scheduler.py |
| 10/27 | 命令行界面整合、功能测试 | 可运行程序 |
| 10/28 | 部署到服务器、开始运行日志 | logs/process_logs/2026-10-28.log |
| 10/29 | 第一轮迭代优化 | iterations/iteration-1.md |

### 第 2 周（10/30 - 11/05）：完整版开发

| 日期 | 任务 | 交付物 |
|-----|------|-------|
| 10/30 | 用户登录系统设计 | models/user.py |
| 10/31 | SQLite 数据库迁移 | data/users.db |
| 11/01 | Flask Web 界面开发 | templates/*.html |
| 11/02 | 课表 CRUD 功能实现 | services/schedule_service.py |
| 11/03 | 数据统计功能开发 | 数据报表页面 |
| 11/04 | 移动端适配、UI 优化 | static/css/mobile.css |
| 11/05 | 第二轮迭代优化 | iterations/iteration-2.md |

### 第 3 周（11/06 - 11/12）：测试与优化

| 日期 | 任务 | 交付物 |
|-----|------|-------|
| 11/06 | 功能测试、Bug 修复 | tests/ |
| 11/07 | 用户体验优化 | iterations/iteration-3.md |
| 11/08 | 收集 8 位用户反馈 | user_feedback.md |
| 11/09 | 完善文档、README | README.md |
| 11/10 | 整理过程日志、提交 | logs/process_logs/ |
| 11/11 | 最终测试、准备答辩 | 演示视频 |
| 11/12 | 项目总结报告 | final_report.md |

---

## 六、必交交付物清单

### 6.1 GitHub 过程数据（防摆拍要求）

#### ✅ ① 连续不少于 7 天的程序自动化运行日志（25 分）

```
logs/process_logs/
├── 2026-10-28.log  # 第 1 天
├── 2026-10-29.log  # 第 2 天
├── 2026-10-30.log  # 第 3 天
├── 2026-10-31.log  # 第 4 天
├── 2026-11-01.log  # 第 5 天
├── 2026-11-02.log  # 第 6 天
└── 2026-11-03.log  # 第 7 天
```

**日志格式示例：**
```
[2026-10-28 07:00:01] INFO - 启动课表提醒服务
[2026-10-28 07:00:02] INFO - 加载课表数据：共 12 门课程
[2026-10-28 07:00:02] INFO - 今日课程：3 节
[2026-10-28 07:00:03] INFO - 已调度提醒任务：08:00 人工智能导论
[2026-10-28 07:00:03] INFO - 已调度提醒任务：14:00 Python 程序设计
[2026-10-28 07:30:00] INFO - 发送邮件提醒：人工智能导论 -> user@example.com
[2026-10-28 07:30:01] INFO - 邮件发送成功
```

#### ✅ ② 基于日志的至少 3 次 Git 迭代 Diff 记录（20 分）

```
iterations/
├── iteration-1.md  # 问题：邮件发送失败 → 解决：修复 SMTP 配置
├── iteration-2.md  # 问题：提醒时间不准 → 解决：优化时区处理
└── iteration-3.md  # 问题：移动端显示错乱 → 解决：添加响应式 CSS
```

#### ✅ ③ 完整源码与 8 位真实用户使用反馈（15 分）

```
user_feedback.md

反馈 1：张三 - 计算机 2301 班
"这个程序太实用了！每天早上都会收到邮件提醒，再也不会忘记课了。"
评分：⭐⭐⭐⭐⭐

反馈 2：李四 - 人工智能 2302 班
"建议可以增加短信提醒功能，有时候会忘记看邮件。"
评分：⭐⭐⭐⭐
...
```

---

## 七、评分要点（60 分）

| 评分项 | 分值 | 要求 |
|-------|-----|------|
| 运行日志真实性 | 25 分 | 连续 7 天，含时间戳、调用频次、报错记录 |
| Git 迭代记录 | 20 分 | 至少 3 次迭代，每次有明确问题和解决方案 |
| 功能完整性 | 10 分 | 基础版必做 + 完整版选做 |
| 用户反馈 | 5 分 | 8 位真实用户反馈 |

---

## 八、技术难点与解决方案

### 难点 1：邮件发送失败

**问题：** QQ 邮箱 SMTP 发送失败，提示认证错误

**解决方案：**
- 使用授权码而非登录密码
- 开启 SMTP 服务（QQ 邮箱设置 → 账户 → 开启 SMTP）
- 使用 SSL 加密连接（端口 465）

### 难点 2：定时任务准确性

**问题：** 提醒时间与时区不匹配

**解决方案：**
- 使用 `pytz` 处理时区
- 统一使用 UTC 时间存储，本地时间展示
- 添加日志记录每次任务执行时间

### 难点 3：数据持久化

**问题：** JSON 文件并发读写冲突

**解决方案：**
- 基础版：使用文件锁（`filelock` 库）
- 完整版：迁移到 SQLite 数据库
- 添加数据备份机制

---

## 九、风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|-----|-----|-----|---------|
| SMTP 服务限制 | 中 | 高 | 准备多个邮箱服务商（QQ/163/Gmail） |
| 数据丢失 | 低 | 高 | 每日自动备份到云端 |
| 用户反馈不足 | 中 | 中 | 提前联系同学，准备使用指南 |
| 时间不足 | 高 | 高 | 优先保证基础版，完整版作为加分项 |

---

## 十、项目亮点

1. **真实痛点**：解决学生课表提醒的实际需求
2. **技术完整**：涵盖 Web 开发、定时任务、邮件服务、数据存储
3. **过程透明**：7 天连续运行日志，防摆拍设计
4. **可扩展性**：预留 API 接口，可对接企业微信/钉钉
5. **实用价值**：8 位同学真实使用，持续迭代优化

---

## 附录：依赖包清单

```txt
# requirements.txt
Flask==3.0.0
APScheduler==3.10.4
pandas==2.1.0
python-dotenv==1.0.0
```
