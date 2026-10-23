"""
批量文件重命名工具 - 课题 10：日常数字任务耗时审计与 AI 批处理实证

功能：
1. 批量重命名指定文件夹中的所有文件
2. 保留原文件扩展名
3. 支持自动编号补零（如 001, 002, ...）
4. 生成修改日志文件（rename_log.txt）

作者：黄心瑜
日期：2026-10-21
"""

import os
import shutil
from datetime import datetime


def batch_rename(folder_path, prefix, start_num=1, padding=3):
    """
    批量重命名文件夹中的文件
    
    参数:
        folder_path: 目标文件夹路径
        prefix: 新文件名的前缀（如 "2026_报告_"）
        start_num: 起始编号（默认从 1 开始）
        padding: 编号的位数（默认 3 位，即 001, 002, ...）
    
    返回:
        log_list: 记录修改前后的文件名列表
    """
    # 验证文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"❌ 错误：文件夹不存在 - {folder_path}")
        return []
    
    # 验证文件夹路径是否为目录
    if not os.path.isdir(folder_path):
        print(f"❌ 错误：路径不是文件夹 - {folder_path}")
        return []
    
    log_list = []
    current_num = start_num
    
    # 获取文件夹中所有文件（排除隐藏文件和日志文件）
    files = [f for f in os.listdir(folder_path) 
             if os.path.isfile(os.path.join(folder_path, f)) 
             and not f.startswith('.') 
             and f != 'rename_log.txt']
    
    # 按原始文件名排序，保证可重复性
    files.sort()
    
    print(f"\n📁 开始处理文件夹：{folder_path}")
    print(f"📝 前缀：{prefix}, 起始编号：{start_num}, 编号位数：{padding}")
    print(f"📊 找到 {len(files)} 个文件")
    
    for old_name in files:
        # 分离文件名和扩展名
        name, ext = os.path.splitext(old_name)
        
        # 生成新文件名（编号自动补零）
        new_name = f"{prefix}{str(current_num).zfill(padding)}{ext}"
        
        # 构建完整路径
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        
        # 检查新文件名是否已存在
        if os.path.exists(new_path):
            print(f"⚠️  跳过：目标文件已存在 - {new_name}")
            current_num += 1
            continue
        
        try:
            # 执行重命名
            os.rename(old_path, new_path)
            
            # 记录日志
            log_entry = {
                'old_name': old_name,
                'new_name': new_name,
                'status': '成功'
            }
            log_list.append(log_entry)
            
            print(f"✅ 已重命名：{old_name} → {new_name}")
            
            current_num += 1
            
        except Exception as e:
            # 记录错误
            log_entry = {
                'old_name': old_name,
                'new_name': new_name,
                'status': f'失败：{str(e)}'
            }
            log_list.append(log_entry)
            print(f"❌ 重命名失败：{old_name} - {str(e)}")
    
    return log_list


def save_log(log_list, folder_path, timestamp):
    """
    保存重命名日志到文件
    
    参数:
        log_list: 日志列表（包含修改前后文件名）
        folder_path: 目标文件夹路径
        timestamp: 时间戳字符串
    """
    log_file = os.path.join(folder_path, 'rename_log.txt')
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("批量重命名日志\n")
        f.write(f"处理时间：{timestamp}\n")
        f.write(f"文件夹：{folder_path}\n")
        f.write("=" * 60 + "\n\n")
        
        # 统计信息
        success_count = sum(1 for log in log_list if log['status'] == '成功')
        fail_count = len(log_list) - success_count
        
        f.write(f"总计：{len(log_list)} 个文件\n")
        f.write(f"成功：{success_count} 个\n")
        f.write(f"失败：{fail_count} 个\n")
        f.write("\n" + "-" * 60 + "\n\n")
        
        # 详细记录
        f.write("详细记录：\n")
        f.write(f"{'原文件名':<40} {'新文件名':<40} {'状态'}\n")
        f.write("-" * 100 + "\n")
        
        for log in log_list:
            old_name = log['old_name'][:38]  # 截断过长的文件名
            new_name = log['new_name'][:38]
            status = log['status']
            f.write(f"{old_name:<40} {new_name:<40} {status}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("日志结束\n")
    
    print(f"\n📄 日志已保存到：{log_file}")


def main():
    """
    主函数：处理 3 个文件夹的批量重命名
    """
    # 生成时间戳（用于日志文件名）
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * 60)
    print("🚀 批量文件重命名工具")
    print(f"🕐 开始时间：{timestamp}")
    print("=" * 60)
    
    # 定义 3 个文件夹的配置
    # 注意：请根据实际情况修改这些路径
    configurations = [
        {
            'folder': '文档资料',  # 或完整路径如 r'D:\test\文档资料'
            'prefix': '2026_报告_',
            'start_num': 1
        },
        {
            'folder': '代码备份',
            'prefix': '26 版 code_to',
            'start_num': 1
        },
        {
            'folder': '日常杂物',
            'prefix': '2026 日常之',
            'start_num': 1
        }
    ]
    
    # 统计信息
    total_files = 0
    total_success = 0
    total_fail = 0
    
    # 逐个处理每个文件夹
    for config in configurations:
        folder_path = config['folder']
        prefix = config['prefix']
        start_num = config['start_num']
        
        # 执行批量重命名
        log_list = batch_rename(folder_path, prefix, start_num, padding=3)
        
        # 保存日志到对应文件夹
        if log_list:
            save_log(log_list, folder_path, timestamp)
        
        # 统计
        if log_list:
            total_files += len(log_list)
            total_success += sum(1 for log in log_list if log['status'] == '成功')
            total_fail += sum(1 for log in log_list if log['status'] != '成功')
    
    # 汇总统计
    print("\n" + "=" * 60)
    print("📊 处理完成！")
    print(f"🕐 结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"总计处理：{total_files} 个文件")
    print(f"✅ 成功：{total_success} 个")
    print(f"❌ 失败：{total_fail} 个")
    print("=" * 60)


if __name__ == '__main__':
    # 执行主函数
    main()
