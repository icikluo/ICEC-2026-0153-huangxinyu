"""
创建测试文件样本 - 课题 10：日常数字任务耗时审计与 AI 批处理实证

功能：
1. 创建 3 个测试文件夹
2. 每个文件夹生成 10 个随机命名的测试文件
3. 覆盖 11 种扩展名（.docx/.pdf/.xlsx/.pptx、.py/.ipynb/.txt、.jpg/.png/.mp3/.mp4）

注意：列表内的名字与 `manual_timing_record.md`、`original_file_list.md` 完全一致。
`batch_rename.py` 会先 files.sort() 再编号，所以实际编号顺序 = 名称升序（列表顺序仅作记录）。

作者：黄心瑜
日期：2026-10-21
"""

import os


def create_test_files():
    """创建测试文件样本"""
    
    # 定义 3 个文件夹及其对应的文件类型
    folders_config = {
        '文档资料': [
            'assignment.docx',
            'budget_2026.xlsx',
            'certificate.pdf',
            'data_analysis.xlsx',
            'meeting_notes.docx',
            'presentation.pptx',
            'project_plan.pdf',
            'reading_notes.pdf',
            'report_draft.docx',
            'thesis_outline.docx'
        ],
        '代码备份': [
            'api_client.py',
            'app.ipynb',
            'config.py',
            'data_processor.py',
            'database.py',
            'main.py',
            'models.py',
            'requirements.txt',
            'test_main.py',
            'utils.py'
        ],
        '日常杂物': [
            'avatar.jpg',
            'chart.png',
            'infographic.png',
            'meme.jpg',
            'music_playlist.mp3',
            'recording.mp3',
            'screenshot.png',
            'tutorial.mp4',
            'vacation_photo.jpg',
            'video_clip.mp4'
        ]
    }
    
    # 创建文件夹并生成文件
    for folder_name, file_list in folders_config.items():
        # 创建文件夹
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"✅ 创建文件夹：{folder_name}")
        else:
            print(f"⚠️  文件夹已存在：{folder_name}")
        
        # 生成文件
        for file_name in file_list:
            file_path = os.path.join(folder_name, file_name)
            
            # 写入一些示例内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# 测试文件：{file_name}\n")
                f.write(f"# 创建时间：2026-10-21\n")
                f.write(f"# 用途：课题 10 实验样本\n")
                f.write("\n")
                f.write(f"This is a test file for {file_name}.\n")
                f.write("It contains some placeholder content for testing batch rename operations.\n")
            
            print(f"   📄 创建文件：{folder_name}/{file_name}")
    
    print("\n" + "=" * 60)
    print("🎉 测试文件创建完成！")
    print("=" * 60)
    print(f"总计：{sum(len(files) for files in folders_config.values())} 个文件")
    print(f"文件夹：{len(folders_config)} 个")
    print("=" * 60)


if __name__ == '__main__':
    create_test_files()
