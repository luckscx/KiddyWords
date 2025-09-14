#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汉字图片下载脚本
根据characters.json中汉字的meaning搜索适合孩子看的图片并下载
"""

import json
import os
import requests
import time
from urllib.parse import quote
from pathlib import Path
from config import UNSPLASH_ACCESS_KEY, PIXABAY_API_KEY, IMAGES_DIR, REQUEST_DELAY

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
        
        # Unsplash API配置
        self.unsplash_access_key = UNSPLASH_ACCESS_KEY
        self.unsplash_base_url = "https://api.unsplash.com/search/photos"
        
        # Pixabay API配置
        self.pixabay_api_key = PIXABAY_API_KEY
        self.pixabay_base_url = "https://pixabay.com/api/"
        
        # 请求头
        self.headers = {
            "Authorization": f"Client-ID {self.unsplash_access_key}",
            "Accept-Version": "v1"
        }
        
        # 儿童友好的搜索关键词映射
        self.child_friendly_keywords = {
            "sun": "sun cartoon cute",
            "day": "sunny day bright",
            "moon": "moon cartoon cute",
            "month": "calendar month",
            "water": "water drop clean",
            "fire": "fire safe cartoon",
            "mountain": "mountain green nature",
            "stone": "rock stone smooth",
            "field": "farm field green",
            "soil": "dirt soil earth",
            "earth": "earth planet blue",
            "wood": "wood tree bark",
            "tree": "tree green nature",
            "grain": "wheat grain food",
            "seedling": "plant seedling green",
            "rain": "rain drop water",
            "wind": "wind air movement",
            "cloud": "cloud white fluffy",
            "sky": "sky blue clear",
            "person": "child kid happy",
            "mouth": "smile mouth happy",
            "hand": "hand wave friendly",
            "foot": "foot shoe walking",
            "ear": "ear listen hearing",
            "eye": "eye see looking",
            "tooth": "tooth smile clean",
            "heart": "heart love red",
            "head": "head face friendly",
            "big": "big large size",
            "small": "small tiny cute",
            "long": "long tall length",
            "tall": "tall high up",
            "high": "high up sky",
            "fish": "fish colorful swimming",
            "bird": "bird flying colorful",
            "horse": "horse friendly animal",
            "cow": "cow farm animal",
            "sheep": "sheep fluffy white",
            "insect": "butterfly colorful insect",
            "flower": "flower colorful beautiful",
            "grass": "grass green nature",
            "fruit": "fruit colorful healthy",
            "rice": "rice grain food",
            "melon": "watermelon fruit sweet",
            "one": "number one first",
            "two": "number two pair",
            "three": "number three group",
            "ten": "number ten many",
            "up": "up arrow sky",
            "on": "on top above",
            "down": "down arrow below",
            "under": "under below down",
            "middle": "middle center between",
            "in": "inside container box",
            "left": "left arrow direction",
            "right": "right arrow direction",
            "dad": "father dad family",
            "mom": "mother mom family",
            "door": "door house entrance",
            "car": "car vehicle toy",
            "vehicle": "car bus vehicle",
            "clothes": "clothes shirt dress",
            "food": "food healthy meal",
            "eat": "eating food meal",
            "live": "home house living",
            "book": "book reading story",
            "drawing": "drawing art colorful",
            "painting": "painting art creative",
            "knife": "safe knife tool",
            "work": "work job helping",
            "red": "red color bright",
            "white": "white color clean",
            "black": "black color dark",
            "many": "many lots group",
            "few": "few little small",
            "life": "life living growing",
            "grow": "growing plant life",
            "good": "good happy positive",
            "go out": "exit door leaving",
            "enter": "enter door coming",
            "walk": "walking person movement",
            "run": "running person fast",
            "fly": "flying bird airplane",
            "see": "seeing eye looking",
            "cry": "sad emotion comfort",
            "smile": "smile happy face",
            "laugh": "laughing happy joy",
            "shout": "shouting voice loud",
            "call": "phone calling hello",
            "drink": "drinking water cup",
            "speak": "speaking talking mouth",
            "sit": "sitting chair rest",
            "stand": "standing up tall",
            "come": "coming arrival welcome",
            "go": "going leaving goodbye",
            "love": "love heart caring"
        }
    
    def get_child_friendly_keyword(self, meaning):
        """
        根据meaning获取适合儿童搜索的关键词
        
        Args:
            meaning: 汉字的英文含义
            
        Returns:
            str: 适合儿童搜索的关键词
        """
        # 清理meaning，提取主要词汇
        meaning_clean = meaning.lower().strip()
        
        # 直接匹配
        if meaning_clean in self.child_friendly_keywords:
            return self.child_friendly_keywords[meaning_clean]
        
        # 部分匹配
        for key, value in self.child_friendly_keywords.items():
            if key in meaning_clean or meaning_clean in key:
                return value
        
        # 默认返回原始meaning加上儿童友好修饰词
        return f"{meaning_clean} cartoon cute child friendly"
    
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
                "per_page": 20,  # Pixabay API要求per_page在3-200之间
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
                    # 选择第一张图片
                    image_url = data["hits"][0]["largeImageURL"]
                    print(f"✅ Pixabay找到图片: {character}")
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
    
    def search_image(self, keyword, character, api_priority="unsplash"):
        """
        搜索图片，支持多个API源
        
        Args:
            keyword: 搜索关键词
            character: 汉字字符
            api_priority: API优先级，可选 "unsplash", "pixabay", "auto"
            
        Returns:
            str: 图片URL，如果搜索失败返回None
        """
        if api_priority == "auto":
            # 自动选择：先尝试Unsplash，失败后尝试Pixabay
            print(f"🔍 自动搜索图片: {character} - {keyword}")
            
            # 先尝试Unsplash
            image_url = self.search_unsplash_image(keyword, character)
            if image_url:
                return image_url
            
            # Unsplash失败，尝试Pixabay
            print(f"🔄 Unsplash未找到，尝试Pixabay: {character}")
            return self.search_pixabay_image(keyword, character)
            
        elif api_priority == "pixabay":
            return self.search_pixabay_image(keyword, character)
        else:  # 默认使用Unsplash
            return self.search_unsplash_image(keyword, character)
    
    def search_unsplash_image(self, keyword, character):
        """
        使用Unsplash API搜索图片
        
        Args:
            keyword: 搜索关键词
            character: 汉字字符
            
        Returns:
            str: 图片URL，如果搜索失败返回None
        """
        try:
            params = {
                "query": keyword,
                "per_page": 1,
                "orientation": "landscape"
            }
            
            print(f"正在搜索Unsplash图片: {character} - {keyword}")
            
            response = requests.get(
                self.unsplash_base_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "results" in data and data["results"]:
                    image_url = data["results"][0]["urls"]["regular"]
                    print(f"✅ Unsplash找到图片: {character}")
                    return image_url
                else:
                    print(f"❌ Unsplash未找到图片: {character}")
            else:
                print(f"❌ Unsplash API请求失败: {character} (状态码: {response.status_code})")
                print(f"错误信息: {response.text}")
            
            return None
            
        except Exception as e:
            print(f"Unsplash搜索图片时出错: {character} - {e}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return None
    
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
    
    def process_characters(self, api_priority="unsplash"):
        """
        处理所有汉字，下载图片并更新JSON
        
        Args:
            api_priority: API优先级，可选 "unsplash", "pixabay", "auto"
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
                
                total_characters += 1
                
                # 检查是否已经有图片（缓存检查）
                if self.has_cached_image(char_info, character, pinyin):
                    print(f"⏭️  跳过 (已有图片): {character}")
                    cached_count += 1
                    continue
                
                print(f"处理: {character} ({pinyin}) - {meaning}")
                
                # 获取搜索关键词
                keyword = self.get_child_friendly_keyword(meaning)
                print(f"搜索关键词: {keyword}")
                
                # 搜索图片
                image_url = self.search_image(keyword, character, api_priority)
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
        
        # 测试Unsplash API
        unsplash_ok = self.test_unsplash_connection()
        
        # 测试Pixabay API
        pixabay_ok = self.test_pixabay_connection()
        
        if unsplash_ok or pixabay_ok:
            print("✅ 至少有一个API可用")
            return True
        else:
            print("❌ 所有API都不可用")
            return False
    
    def test_unsplash_connection(self):
        """
        测试Unsplash API连接
        """
        print(f"测试Unsplash API...")
        print(f"API密钥: {self.unsplash_access_key[:10]}...{self.unsplash_access_key[-10:]}")
        
        try:
            test_params = {
                "query": "test",
                "per_page": 1
            }
            
            response = requests.get(
                self.unsplash_base_url,
                headers=self.headers,
                params=test_params,
                timeout=10
            )
            
            print(f"Unsplash测试状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Unsplash API连接正常")
                return True
            else:
                print("❌ Unsplash API连接失败")
                return False
                
        except Exception as e:
            print(f"❌ Unsplash API连接测试出错: {e}")
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

    def test_with_sample(self, api_priority="unsplash"):
        """
        测试功能，只处理前几个字符
        
        Args:
            api_priority: API优先级，可选 "unsplash", "pixabay", "auto"
        """
        print("测试模式：只处理前3个字符")
        
        # 读取JSON文件
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 只处理第一个分类的前3个字符
        first_category = data["basicChineseCharactersForKids"][0]
        test_characters = first_category["characters"][:3]
        
        for char_info in test_characters:
            character = char_info["character"]
            pinyin = char_info["pinyin"]
            meaning = char_info["meaning"]
            
            print(f"\n测试: {character} ({pinyin}) - {meaning}")
            
            # 检查缓存
            if self.has_cached_image(char_info, character, pinyin):
                print(f"⏭️  跳过 (已有图片): {character}")
                continue
            
            # 获取搜索关键词
            keyword = self.get_child_friendly_keyword(meaning)
            print(f"搜索关键词: {keyword}")
            
            # 搜索图片
            image_url = self.search_image(keyword, character, api_priority)
            if image_url:
                print(f"找到图片: {image_url}")
                # 下载图片
                image_filename = self.download_image(image_url, character, pinyin)
                if image_filename:
                    char_info["image_file"] = image_filename
            else:
                print(f"未找到图片: {character}")
            
            time.sleep(REQUEST_DELAY)

def main():
    """主函数"""
    print("汉字图片下载脚本")
    print("=" * 50)
    
    # 检查API密钥
    downloader = ImageDownloader("characters.json")
    
    if downloader.unsplash_access_key == "YOUR_UNSPLASH_ACCESS_KEY":
        print("错误: 请先设置Unsplash API密钥!")
        print("1. 访问 https://unsplash.com/developers")
        print("2. 创建应用获取Access Key")
        print("3. 在 config.py 中替换 YOUR_UNSPLASH_ACCESS_KEY")
        return
    
    # 测试API连接
    print("\n正在测试API连接...")
    if not downloader.test_api_connection():
        print("\n❌ API连接失败，请检查:")
        print("1. API密钥是否正确")
        print("2. 网络连接是否正常")
        print("3. Unsplash API服务是否可用")
        return
    
    # 询问用户选择
    print("\n请选择运行模式:")
    print("1. 测试模式 (只处理前3个字符)")
    print("2. 完整模式 (处理所有字符)")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice in ["1", "2"]:
        # 询问API选择
        print("\n请选择图片搜索API:")
        print("1. Unsplash (默认)")
        print("2. Pixabay")
        print("3. 自动选择 (先Unsplash，失败后Pixabay)")
        
        api_choice = input("请输入选择 (1/2/3，默认1): ").strip()
        
        if api_choice == "2":
            api_priority = "pixabay"
        elif api_choice == "3":
            api_priority = "auto"
        else:
            api_priority = "unsplash"
        
        print(f"使用API: {api_priority}")
        
        if choice == "1":
            downloader.test_with_sample(api_priority)
        else:
            downloader.process_characters(api_priority)
    else:
        print("无效选择，退出程序")

if __name__ == "__main__":
    main()
