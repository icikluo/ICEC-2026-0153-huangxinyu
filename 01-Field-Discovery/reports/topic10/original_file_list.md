# 原始文件名清单 - 课题 10 实验样本

**创建时间：** 2026-10-21  
**用途：** 人工操作和 AI 脚本对比实验的原始文件记录

> **口径说明（2026-10-25 校正）：** 本表以 `manual_timing_record.md` 的三张逐文件表为准。序号即"原文件名自然升序"——也就是资源管理器"名称升序"看到的顺序，与 `ai_scripts/batch_rename.py` 中 `files.sort()` 的排序一致，所以人工按 F2 逐张改和脚本批量跑，编号结果完全相同。
>
> 重命名目标一律**只替换主文件名、原样保留扩展名**（`.xlsx` 还是 `.xlsx`，`.ipynb` 还是 `.ipynb`）。命名规则写法统一为：`2026_报告_001`、`26版code_to001`（无空格）、`2026日常之001`（无空格）。

---

## 文件夹 1：文档资料（10 个文件）

| 序号 | 原始文件名 | 扩展名 | 重命名目标 |
|-----|-----------|-------|-----------|
| 1 | assignment.docx | .docx | 2026_报告_001.docx |
| 2 | budget_2026.xlsx | .xlsx | 2026_报告_002.xlsx |
| 3 | certificate.pdf | .pdf | 2026_报告_003.pdf |
| 4 | data_analysis.xlsx | .xlsx | 2026_报告_004.xlsx |
| 5 | meeting_notes.docx | .docx | 2026_报告_005.docx |
| 6 | presentation.pptx | .pptx | 2026_报告_006.pptx |
| 7 | project_plan.pdf | .pdf | 2026_报告_007.pdf |
| 8 | reading_notes.pdf | .pdf | 2026_报告_008.pdf |
| 9 | report_draft.docx | .docx | 2026_报告_009.docx |
| 10 | thesis_outline.docx | .docx | 2026_报告_010.docx |

---

## 文件夹 2：代码备份（10 个文件）

| 序号 | 原始文件名 | 扩展名 | 重命名目标 |
|-----|-----------|-------|-----------|
| 1 | api_client.py | .py | 26版code_to001.py |
| 2 | app.ipynb | .ipynb | 26版code_to002.ipynb |
| 3 | config.py | .py | 26版code_to003.py |
| 4 | data_processor.py | .py | 26版code_to004.py |
| 5 | database.py | .py | 26版code_to005.py |
| 6 | main.py | .py | 26版code_to006.py |
| 7 | models.py | .py | 26版code_to007.py |
| 8 | requirements.txt | .txt | 26版code_to008.txt |
| 9 | test_main.py | .py | 26版code_to009.py |
| 10 | utils.py | .py | 26版code_to010.py |

---

## 文件夹 3：日常杂物（10 个文件）

| 序号 | 原始文件名 | 扩展名 | 重命名目标 |
|-----|-----------|-------|-----------|
| 1 | avatar.jpg | .jpg | 2026日常之001.jpg |
| 2 | chart.png | .png | 2026日常之002.png |
| 3 | infographic.png | .png | 2026日常之003.png |
| 4 | meme.jpg | .jpg | 2026日常之004.jpg |
| 5 | music_playlist.mp3 | .mp3 | 2026日常之005.mp3 |
| 6 | recording.mp3 | .mp3 | 2026日常之006.mp3 |
| 7 | screenshot.png | .png | 2026日常之007.png |
| 8 | tutorial.mp4 | .mp4 | 2026日常之008.mp4 |
| 9 | vacation_photo.jpg | .jpg | 2026日常之009.jpg |
| 10 | video_clip.mp4 | .mp4 | 2026日常之010.mp4 |

---

## 文件统计

| 文件夹 | 文件数 | 扩展名类型 |
|-------|-------|-----------|
| 文档资料 | 10 | .docx (4), .pdf (3), .xlsx (2), .pptx (1) |
| 代码备份 | 10 | .py (8), .ipynb (1), .txt (1) |
| 日常杂物 | 10 | .jpg (3), .png (3), .mp3 (2), .mp4 (2) |
| **总计** | **30** | **11 种扩展名** |

---

## 实验记录

### 人工操作前检查

```
□ 确认 30 个文件已创建
□ 确认文件扩展名完整
□ 记录开始时间：18:43
```

### AI 脚本运行前检查

```
□ 确认文件已恢复到原始状态
□ 记录开始时间：18:12
```

---

## 备份与快照位置

**原始文件快照：** `01-Field-Discovery/raw_data/10-task-audit/samples/`

```
raw_data/10-task-audit/samples/
├── evidence-task10/     # 计时器截图、原始录屏、压缩版录屏
├── 文档资料/            # 重命名后的 10 个文件
├── 代码备份/            # 重命名后的 10 个文件
└── 日常杂物/            # 重命名后的 10 个文件
```

**快照方法：**

```bash
xcopy 文档资料 01-Field-Discovery\raw_data\10-task-audit\samples\文档资料 /E
xcopy 代码备份 01-Field-Discovery\raw_data\10-task-audit\samples\代码备份 /E
xcopy 日常杂物 01-Field-Discovery\raw_data\10-task-audit\samples\日常杂物 /E
```

---

**记录人：** 黄心瑜  
**日期：** 2026-10-21（2026-10-25 校正序号、原名顺序与扩展名）