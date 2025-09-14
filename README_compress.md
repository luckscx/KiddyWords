# 图片压缩脚本使用说明

## 功能
`compress_images.py` 脚本可以将指定目录下的所有图片文件压缩到指定大小以内（默认120KB）。

## 使用方法

### 基本用法
```bash
# 压缩 static/images 目录下的所有图片到120KB以内
python3 compress_images.py

# 或者直接运行（已添加执行权限）
./compress_images.py
```

### 高级用法
```bash
# 指定目录和大小限制
python3 compress_images.py --directory /path/to/images --max-size 100

# 不创建备份文件
python3 compress_images.py --no-backup

# 查看帮助
python3 compress_images.py --help
```

## 参数说明
- `--directory, -d`: 图片目录路径（默认：static/images）
- `--max-size, -s`: 最大文件大小，单位KB（默认：120）
- `--no-backup`: 不创建备份文件

## 功能特点
1. **智能压缩**：自动调整图片质量和尺寸以达到目标大小
2. **格式支持**：支持JPG、PNG、BMP、TIFF、WebP等格式
3. **自动备份**：默认会创建backup目录保存原始文件
4. **跳过小文件**：自动跳过已经小于目标大小的文件
5. **详细报告**：显示压缩前后的文件大小和节省的空间

## 压缩结果
- 原始总大小：25,120.6KB
- 压缩后总大小：12,236.5KB
- 节省空间：12,884.1KB（51.3%）
- 所有文件都已成功压缩到120KB以内

## 依赖要求
需要安装Pillow库：
```bash
pip install Pillow
```

## 注意事项
1. 压缩会直接覆盖原文件，建议先备份重要文件
2. 脚本会自动创建backup目录保存原始文件
3. 如果图片质量降到最低仍无法达到目标大小，会尝试缩小图片尺寸
4. 支持RGBA和P模式的图片，会自动转换为RGB格式
