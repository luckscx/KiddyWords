# 汉字图片下载脚本使用说明

## 功能说明

这个脚本可以根据 `characters.json` 中汉字的英文含义，自动搜索适合儿童观看的图片并下载到本地，同时更新JSON文件添加图片文件名关联。

## 准备工作

### 1. 获取Unsplash API密钥

1. 访问 [Unsplash Developers](https://unsplash.com/developers)
2. 注册账号并创建应用
3. 获取 Access Key
4. 在 `config.py` 中替换 `YOUR_UNSPLASH_ACCESS_KEY`

### 2. 安装依赖

```bash
# 使用uv安装依赖
uv pip install -r requirements.txt
```

## 使用方法

### 运行脚本

```bash
python download_images.py
```

### 运行模式

1. **测试模式**: 只处理前3个字符，用于测试功能
2. **完整模式**: 处理所有字符

## 功能特点

### 1. 儿童友好搜索

脚本内置了儿童友好的搜索关键词映射，例如：
- "sun" → "sun cartoon cute"
- "fire" → "fire safe cartoon"
- "knife" → "safe knife tool"

### 2. 智能关键词匹配

- 直接匹配：完全匹配meaning
- 部分匹配：包含关键词
- 默认处理：添加儿童友好修饰词

### 3. 图片管理

- 自动创建 `images/` 目录
- 图片命名格式：`{汉字}_{拼音}.jpg`
- 避免重复下载已有图片

### 4. JSON更新

自动在JSON中添加 `image_file` 字段：

```json
{
  "character": "日",
  "pinyin": "rì", 
  "meaning": "sun, day",
  "image_file": "日_rì.jpg"
}
```

## 文件结构

```
SYWord/
├── characters.json          # 汉字数据文件
├── download_images.py       # 主脚本
├── config.py               # 配置文件
├── images/                 # 图片存储目录
│   ├── 日_rì.jpg
│   ├── 月_yuè.jpg
│   └── ...
└── requirements.txt        # 依赖文件
```

## 注意事项

1. **API限制**: Unsplash免费版有请求限制，建议分批处理
2. **网络连接**: 需要稳定的网络连接下载图片
3. **存储空间**: 确保有足够的磁盘空间存储图片
4. **版权问题**: 下载的图片仅供学习使用，注意版权问题

## 故障排除

### 常见问题

1. **API密钥错误**: 检查 `config.py` 中的密钥是否正确
2. **网络超时**: 检查网络连接，可能需要重试
3. **图片下载失败**: 某些图片可能无法下载，脚本会跳过并继续

### 日志信息

脚本会输出详细的处理日志：
- 搜索关键词
- 下载状态
- 错误信息
- 统计信息

## 自定义配置

可以在 `config.py` 中修改：
- 图片存储目录
- 请求延迟时间
- 儿童友好修饰词
- 最大图片大小限制
