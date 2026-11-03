# 开发过程证据说明

本目录存放**开发过程中的 AI 对话与对比截图**，用于证明迭代过程真实。

## 迭代 2：课表从「按星期」升级为「按周次」

| 文件 | 内容 |
|---|---|
| `iter2-ai-dialog-01.png` | 指出课表只覆盖 11/02–11/08，需要完整周次信息 |
| `iter2-ai-dialog-02.png` | 明确每门课需要标注的字段（周次、节次、教师、地点） |
| `iter2-ai-dialog-03.png` | 提供完整学期课表（9 张单周截图）|
| `iter2-version-compare.png` | 新旧 CSV 结构对比 + 逐周课程数验证矩阵 |

## 迭代 3：日志追加时行粘连修复

| 文件 | 内容 |
|---|---|
| `iter3-ai-dialog-01.png` | 发现日志第 4、5 行粘连，提出修复方案 |
| `iter3-ai-dialog-02.png` | 分析根因：追加写入未检查文件末尾换行 |
| `iter3-ai-dialog-03.png` | 修复代码改动（`needs_newline` 保护逻辑）|
| `iter3-ai-dialog-04.png` | 修复前后日志数据对比 |

## 完整录屏

迭代 2、3 的完整 AI 对话过程另有录屏文件（约 55 MB）。

**因体积原因未提交至仓库**，仅本地保存。如需查看可另行提供。

## 相关文档

- 迭代说明：`../../iterations/iteration-2.md`、`../../iterations/iteration-3.md`
- 每日检查记录：`../checkin.md`
- 运行日志：`../daily_log.txt`