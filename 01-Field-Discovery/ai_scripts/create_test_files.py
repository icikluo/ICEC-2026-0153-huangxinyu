"""
创建测试文件样本 - 课题 10：日常数字任务耗时审计与 AI 批处理实证

功能：
1. 创建 3 个测试文件夹
2. 每个文件夹生成 10 个随机命名的测试文件
3. 包含多种文件扩展名（.docx, .pdf, .py, .txt, .xlsx, .jpg, .png, .ipynb, .csv, .mp4）

作者：黄心瑜
日期：2026-10-21
"""

import os


def create_test_files():
    """创建测试文件样本"""
    
    # 定义 3 个文件夹及其对应的文件类型
    folders_config = {
        '文档资料': [
            'report_draft.docx',
            'meeting_notes.docx',
            'project_plan.pdf',
            'budget_2026.xlsx',
            'data_analysis.xlsx',
            'thesis_outline.docx',
            'presentation.pptx',
            'reading_notes.pdf',
            'assignment.docx',
            'certificate.pdf'
        ],
        '代码备份': [
            'main.py',
            'utils.py',
            'config.py',
            'test_main.py',
            'data_processor.py',
            'api_client.py',
            'database.py',
            'models.py',
            'app.ipynb',
            'requirements.txt'
        ],
        '日常杂物': [
            'vacation_photo.jpg',
            'screenshot.png',
            'music_playlist.mp3',
            'video_clip.mp4',
            'avatar.jpg',
            'infographic.png',
            'recording.mp3',
            'tutorial.mp4',
            'meme.jpg',
            'chart.png'
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
