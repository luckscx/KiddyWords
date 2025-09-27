#!/usr/bin/env python3
"""
图片压缩脚本
将images目录下的所有图片压缩到120KB以内
支持JPEG和PNG格式
"""

import os
import sys
from PIL import Image
import argparse
from pathlib import Path

def get_file_size_kb(file_path):
    """获取文件大小（KB）"""
    return os.path.getsize(file_path) / 1024

def compress_image(input_path, output_path, max_size_kb=120, quality=85):
    """
    压缩单张图片到指定大小以内
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        max_size_kb: 最大文件大小（KB）
        quality: 初始质量（1-100）
    """
    try:
        with Image.open(input_path) as img:
            # 如果是RGBA模式，转换为RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 保存为JPEG格式
            current_quality = quality
            min_quality = 10
            
            while current_quality >= min_quality:
                img.save(output_path, 'JPEG', quality=current_quality, optimize=True)
                
                # 检查文件大小
                if get_file_size_kb(output_path) <= max_size_kb:
                    print(f"✓ {os.path.basename(input_path)}: {get_file_size_kb(output_path):.1f}KB (质量: {current_quality})")
                    return True
                
                # 如果还是太大，降低质量
                current_quality -= 10
            
            # 如果质量降到最低还是太大，尝试缩小尺寸
            if get_file_size_kb(output_path) > max_size_kb:
                scale_factor = 0.9
                while scale_factor > 0.3:
                    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                    resized_img.save(output_path, 'JPEG', quality=min_quality, optimize=True)
                    
                    if get_file_size_kb(output_path) <= max_size_kb:
                        print(f"✓ {os.path.basename(input_path)}: {get_file_size_kb(output_path):.1f}KB (缩放: {scale_factor:.1f}, 质量: {min_quality})")
                        return True
                    
                    scale_factor -= 0.1
                
                print(f"⚠ {os.path.basename(input_path)}: 无法压缩到{max_size_kb}KB以内，当前: {get_file_size_kb(output_path):.1f}KB")
                return False
            
    except Exception as e:
        print(f"✗ 压缩失败 {os.path.basename(input_path)}: {str(e)}")
        return False

def compress_images_in_directory(directory, max_size_kb=120, backup=True):
    """
    压缩目录中的所有图片
    
    Args:
        directory: 图片目录路径
        max_size_kb: 最大文件大小（KB）
        backup: 是否备份原文件
    """
    directory = Path(directory)
    if not directory.exists():
        print(f"错误: 目录 {directory} 不存在")
        return
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # 查找所有图片文件
    image_files = []
    for ext in image_extensions:
        image_files.extend(directory.glob(f'*{ext}'))
        image_files.extend(directory.glob(f'*{ext.upper()}'))
    
    if not image_files:
        print(f"在目录 {directory} 中没有找到图片文件")
        return
    
    print(f"找到 {len(image_files)} 个图片文件")
    print(f"目标大小: {max_size_kb}KB")
    print("-" * 50)
    
    # 创建备份目录
    if backup:
        backup_dir = directory / 'backup'
        backup_dir.mkdir(exist_ok=True)
        print(f"备份目录: {backup_dir}")
    
    success_count = 0
    total_original_size = 0
    total_compressed_size = 0
    
    for image_file in image_files:
        # 获取原始文件大小
        original_size = get_file_size_kb(image_file)
        total_original_size += original_size
        
        print(f"处理: {image_file.name} ({original_size:.1f}KB)", end=" -> ")
        
        # 如果文件已经小于目标大小，跳过
        if original_size <= max_size_kb:
            print(f"已满足要求，跳过")
            total_compressed_size += original_size
            success_count += 1
            continue
        
        # 备份原文件
        if backup:
            backup_path = backup_dir / image_file.name
            if not backup_path.exists():
                import shutil
                shutil.copy2(image_file, backup_path)
        
        # 压缩图片
        if compress_image(image_file, image_file, max_size_kb):
            success_count += 1
            total_compressed_size += get_file_size_kb(image_file)
        else:
            total_compressed_size += get_file_size_kb(image_file)
    
    print("-" * 50)
    print(f"压缩完成!")
    print(f"成功处理: {success_count}/{len(image_files)} 个文件")
    print(f"原始总大小: {total_original_size:.1f}KB")
    print(f"压缩后总大小: {total_compressed_size:.1f}KB")
    print(f"节省空间: {total_original_size - total_compressed_size:.1f}KB ({((total_original_size - total_compressed_size) / total_original_size * 100):.1f}%)")

def main():
    parser = argparse.ArgumentParser(description='压缩图片到指定大小以内')
    parser.add_argument('--directory', '-d', default='static/images', 
                       help='图片目录路径 (默认: static/images)')
    parser.add_argument('--max-size', '-s', type=int, default=120,
                       help='最大文件大小(KB) (默认: 120)')
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份文件')
    
    args = parser.parse_args()
    
    # 检查PIL是否安装
    try:
        from PIL import Image
    except ImportError:
        print("错误: 需要安装Pillow库")
        print("请运行: pip install Pillow")
        sys.exit(1)
    
    # 开始压缩
    compress_images_in_directory( directory="static/images", max_size_kb=120, backup=False)
    compress_images_in_directory( directory="static/images/english", max_size_kb=120, backup=False)

if __name__ == '__main__':
    main()
