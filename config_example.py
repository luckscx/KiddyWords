# -*- coding: utf-8 -*-
"""
配置文件
"""

# Unsplash API配置
UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY"  # 需要替换为实际的API密钥

# Pixabay API配置
PIXABAY_API_KEY = "YOUR_PIXABAY_API_KEY"  # 需要替换为实际的API密钥

# 图片下载配置
IMAGES_DIR = "static/images"
MAX_IMAGE_SIZE = 1024 * 1024  # 1MB
REQUEST_DELAY = 2  # 请求间隔（秒）

# 儿童友好关键词配置
CHILD_FRIENDLY_MODIFIERS = [
    "cartoon", "cute", "child friendly", "colorful", 
    "simple", "bright", "happy", "safe"
]
