#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汉字图片下载脚本
根据characters.json中汉字的meaning搜索适合孩子看的图片并下载
"""

import json
import os
import random
import requests
import time
from urllib.parse import quote
from pathlib import Path
from config import PIXABAY_API_KEY, IMAGES_DIR, REQUEST_DELAY

class ImageDownloader:
    def __init__(self, json_file_path, images_dir=None):
        """
        初始化图片下载器
        
        Args:
            json_file_path: characters.json文件路径
            images_dir: 图片存储目录，默认使用配置文件中的设置
        """
        self.json_file_path = json_file_path
        self.images_dir = Path(images_dir or IMAGES_DIR)
        self.images_dir.mkdir(exist_ok=True)
        
        # Pixabay API配置
        self.pixabay_api_key = PIXABAY_API_KEY
        self.pixabay_base_url = "https://pixabay.com/api/"
        
    def has_cached_image(self, char_info, character, pinyin):
        """
        检查是否已经有缓存的图片
        
        Args:
            char_info: 字符信息字典
            character: 汉字字符
            pinyin: 拼音
            
        Returns:
            bool: 如果有缓存图片返回True，否则返回False
        """
        # 检查JSON中是否记录了图片文件
        if "image_file" in char_info and char_info["image_file"]:
            image_filename = char_info["image_file"]
            filepath = self.images_dir / image_filename
            
            # 检查文件是否真实存在
            if filepath.exists() and filepath.is_file():
                return True
            else:
                # 文件记录存在但实际文件不存在，清理记录
                print(f"⚠️  清理无效记录: {character} - {image_filename}")
                char_info.pop("image_file", None)
                return False
        
        # 检查是否有按命名规则存在的文件
        expected_filename = f"{character}_{pinyin}.jpg"
        filepath = self.images_dir / expected_filename
        
        if filepath.exists() and filepath.is_file():
            # 文件存在但JSON中没有记录，更新记录
            char_info["image_file"] = expected_filename
            print(f"🔄 发现缓存文件: {character} - {expected_filename}")
            return True
        
        return False
    
    def search_pixabay_image(self, keyword, character):
        """
        使用Pixabay API搜索图片
        
        Args:
            keyword: 搜索关键词
            character: 汉字字符
            
        Returns:
            str: 图片URL，如果搜索失败返回None
        """
        try:
            params = {
                "key": self.pixabay_api_key,
                "q": keyword,
                "image_type": "photo",
                "orientation": "horizontal",
                "safesearch": "true",
                "per_page": 5,  # Pixabay API要求per_page在3-200之间
                "min_width": 640,
                "min_height": 480
            }
            
            print(f"正在搜索Pixabay图片: {character} - {keyword}")
            
            response = requests.get(
                self.pixabay_base_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "hits" in data and data["hits"]:
                    count = len(data["hits"])
                    print(f"Pixabay找到图片: {character} - {count}张")
                    image_url = data["hits"][0]["largeImageURL"]
                    return image_url
                else:
                    print(f"❌ Pixabay未找到图片: {character}")
            else:
                print(f"❌ Pixabay API请求失败: {character} (状态码: {response.status_code})")
                print(f"错误信息: {response.text}")
            
            return None
            
        except Exception as e:
            print(f"Pixabay搜索图片时出错: {character} - {e}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return None
    
    def search_image(self, keyword, character):
        """
        搜索图片，使用Pixabay API
        
        Args:
            keyword: 搜索关键词
            character: 汉字字符
            
        Returns:
            str: 图片URL，如果搜索失败返回None
        """
        return self.search_pixabay_image(keyword, character)
    
    
    def download_image(self, image_url, character, pinyin):
        """
        下载图片
        
        Args:
            image_url: 图片URL
            character: 汉字字符
            pinyin: 拼音
            
        Returns:
            str: 下载的图片文件名，如果下载失败返回None
        """
        try:
            # 生成文件名
            filename = f"{character}_{pinyin}.jpg"
            filepath = self.images_dir / filename
            
            # 下载图片
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"下载成功: {character} -> {filename}")
            return filename
            
        except Exception as e:
            print(f"下载图片失败: {character} - {e}")
            return None
    
    def process_characters(self):
        """
        处理所有汉字，下载图片并更新JSON
        """
        # 读取JSON文件
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 统计信息
        total_characters = 0
        downloaded_count = 0
        cached_count = 0
        
        # 处理每个分类
        for category in data["basicChineseCharactersForKids"]:
            print(f"\n处理分类: {category['category']}")
            
            for char_info in category["characters"]:
                character = char_info["character"]
                pinyin = char_info["pinyin"]
                meaning = char_info["meaning"]
                chinese_meaning = char_info["chinese_meaning"]
                common_words = char_info["common_words"]

                
                total_characters += 1
                
                # 检查是否已经有图片（缓存检查）
                if self.has_cached_image(char_info, character, pinyin):
                    print(f"⏭️  跳过 (已有图片): {character}")
                    cached_count += 1
                    continue
                
                print(f"处理: {character} ({pinyin}) - {chinese_meaning} - {meaning}")
                
                # 获取搜索关键词
                keyword = meaning
                print(f"搜索关键词: {keyword}")
                
                # 搜索图片
                image_url = self.search_image(keyword, character)
                if not image_url:
                    print(f"未找到图片: {character}")
                    continue
                
                # 下载图片
                image_filename = self.download_image(image_url, character, pinyin)
                if image_filename:
                    # 更新JSON数据
                    char_info["image_file"] = image_filename
                    downloaded_count += 1
                
                # 避免请求过于频繁
                time.sleep(REQUEST_DELAY)
        
        # 保存更新后的JSON
        with open(self.json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n处理完成!")
        print(f"总字符数: {total_characters}")
        print(f"使用缓存: {cached_count}")
        print(f"成功下载: {downloaded_count}")
        print(f"图片保存在: {self.images_dir.absolute()}")
    
    def test_api_connection(self):
        """
        测试API连接
        """
        print("测试API连接...")
        
        # 测试Pixabay API
        pixabay_ok = self.test_pixabay_connection()
        
        if pixabay_ok:
            print("✅ Pixabay API可用")
            return True
        else:
            print("❌ Pixabay API不可用")
            return False
    
    
    def test_pixabay_connection(self):
        """
        测试Pixabay API连接
        """
        print(f"测试Pixabay API...")
        print(f"API密钥: {self.pixabay_api_key[:10]}...{self.pixabay_api_key[-10:]}")
        
        try:
            test_params = {
                "key": self.pixabay_api_key,
                "q": "test",
                "per_page": 3
            }
            
            response = requests.get(
                self.pixabay_base_url,
                params=test_params,
                timeout=10
            )
            
            print(f"Pixabay测试状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Pixabay API连接正常")
                return True
            else:
                print("❌ Pixabay API连接失败")
                return False
                
        except Exception as e:
            print(f"❌ Pixabay API连接测试出错: {e}")
            return False

def main():
    """主函数"""
    print("汉字图片下载脚本")
    print("=" * 50)
    
    # 检查API密钥
    downloader = ImageDownloader("characters.json")
    
    if downloader.pixabay_api_key == "YOUR_PIXABAY_API_KEY":
        print("错误: 请先设置Pixabay API密钥!")
        print("1. 访问 https://pixabay.com/api/docs/")
        print("2. 注册账号获取API Key")
        print("3. 在 config.py 中替换 YOUR_PIXABAY_API_KEY")
        return
    
    # 测试API连接
    print("\n正在测试API连接...")
    if not downloader.test_api_connection():
        print("\n❌ API连接失败，请检查:")
        print("1. API密钥是否正确")
        print("2. 网络连接是否正常")
        print("3. Pixabay API服务是否可用")
        return
    
    downloader.process_characters()

if __name__ == "__main__":
    main()
