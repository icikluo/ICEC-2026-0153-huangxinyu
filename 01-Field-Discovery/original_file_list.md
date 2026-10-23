# 原始文件名清单 - 课题 10 实验样本

**创建时间：** 2026-10-21  
**用途：** 人工操作和 AI 脚本对比实验的原始文件记录

---

## 文件夹 1：文档资料（10 个文件）

| 序号 | 原始文件名 | 扩展名 | 重命名目标 |
|-----|-----------|-------|-----------|
| 1 | report_draft.docx | .docx | 2026_报告_001.docx |
| 2 | meeting_notes.docx | .docx | 2026_报告_002.docx |
| 3 | project_plan.pdf | .pdf | 2026_报告_003.pdf |
| 4 | budget_2026.xlsx | .xlsx | 2026_报告_004.xlsx |
| 5 | data_analysis.xlsx | .xlsx | 2026_报告_005.xlsx |
| 6 | thesis_outline.docx | .docx | 2026_报告_006.docx |
| 7 | presentation.pptx | .pptx | 2026_报告_007.pptx |
| 8 | reading_notes.pdf | .pdf | 2026_报告_008.pdf |
| 9 | assignment.docx | .docx | 2026_报告_009.docx |
| 10 | certificate.pdf | .pdf | 2026_报告_010.pdf |

---

## 文件夹 2：代码备份（10 个文件）

| 序号 | 原始文件名 | 扩展名 | 重命名目标 |
|-----|-----------|-------|-----------|
| 1 | main.py | .py | 26 版 code_to001.py |
| 2 | utils.py | .py | 26 版 code_to002.py |
| 3 | config.py | .py | 26 版 code_to003.py |
| 4 | test_main.py | .py | 26 版 code_to004.py |
| 5 | data_processor.py | .py | 26 版 code_to005.py |
| 6 | api_client.py | .py | 26 版 code_to006.py |
| 7 | database.py | .py | 26 版 code_to007.py |
| 8 | models.py | .py | 26 版 code_to008.py |
| 9 | app.ipynb | .ipynb | 26 版 code_to009.ipynb |
| 10 | requirements.txt | .txt | 26 版 code_to010.txt |

---

## 文件夹 3：日常杂物（10 个文件）

| 序号 | 原始文件名 | 扩展名 | 重命名目标 |
|-----|-----------|-------|-----------|
| 1 | avatar.jpg | .jpg | 2026 日常之 001.jpg |
| 2 | chart.png | .png | 2026 日常之 002.png |
| 3 | infographic.png | .png | 2026 日常之 003.png |
| 4 | meme.jpg | .jpg | 2026 日常之 004.jpg |
| 5 | music_playlist.mp3 | .mp3 | 2026 日常之 005.mp3 |
| 6 | recording.mp3 | .mp3 | 2026 日常之 006.mp3 |
| 7 | screenshot.png | .png | 2026 日常之 007.png |
| 8 | tutorial.mp4 | .mp4 | 2026 日常之 008.mp4 |
| 9 | vacation_photo.jpg | .jpg | 2026 日常之 009.jpg |
| 10 | video_clip.mp4 | .mp4 | 2026 日常之 010.mp4 |

---

## 文件统计

| 文件夹 | 文件数 | 扩展名类型 |
|-------|-------|-----------|
| 文档资料 | 10 | .docx (5), .pdf (3), .xlsx (2), .pptx (1) |
| 代码备份 | 10 | .py (8), .ipynb (1), .txt (1) |
| 日常杂物 | 10 | .jpg (3), .png (3), .mp3 (2), .mp4 (2) |
| **总计** | **30** | **10 种扩展名** |

---

## 实验记录

### 人工操作前检查

```
□ 确认 30 个文件已创建
□ 确认文件扩展名完整
□ 确认文件可以正常打开
□ 记录开始时间：__________
```

### AI 脚本运行前检查

```
□ 确认文件已恢复到原始状态
□ 确认 batch_rename.py 脚本可用
□ 记录开始时间：__________
```

---

## 备份说明

**原始文件备份位置：** `01-Field-Discovery/raw_data/samples/`

**备份方法：**
```bash
# 实验完成后，将原始文件复制到备份目录
xcopy 文档资料 01-Field-Discovery\raw_data\samples\文档资料_original /E
xcopy 代码备份 01-Field-Discovery\raw_data\samples\代码备份_original /E
xcopy 日常杂物 01-Field-Discovery\raw_data\samples\日常杂物_original /E
```

---

**记录人：** 黄心瑜  
**日期：** 2026-10-21
