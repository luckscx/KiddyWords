# 汉字奇趣岛 - 看图认字游戏

一个专为5岁儿童设计的趣味识字游戏，通过看图认字的方式帮助孩子学习汉字。

## 游戏特色

- 🎨 **卡通风格界面**：色彩明快，界面友好
- 🔊 **语音引导**：每个题目都有语音提示
- ✨ **动画反馈**：正确答案有金光特效，错误答案有抖动提示
- 📱 **响应式设计**：支持手机、平板等不同设备
- 🎮 **简单操作**：只需点击即可，适合儿童操作

## 游戏玩法

1. 屏幕上会显示一张图片（如苹果）
2. 点击🔊按钮听语音提示
3. 从下方的汉字选项中选择正确答案
4. 答对获得分数，答错会有鼓励提示
5. 完成所有题目后查看最终得分

## 技术特点

- 纯HTML/CSS/JavaScript实现，无需额外依赖
- 使用Web Speech API实现语音功能
- SVG图片确保在不同设备上清晰显示
- 支持键盘快捷键操作

## 文件说明

- `app.py` - Flask web应用主文件
- `run.py` - 启动脚本
- `requirements.txt` - Python依赖文件
- `characters.json` - 汉字数据文件
- `templates/index.html` - 游戏主页面
- `static/style.css` - 样式文件
- `static/script.js` - 游戏逻辑
- `design.md` - 游戏设计文档

## API接口

### 获取所有分类
```
GET /api/categories
```

### 获取随机题目
```
GET /api/question?category=自然与宇宙&difficulty=easy
```

### 开始新游戏
```
GET /api/game/start?category=自然与宇宙
```

### 获取指定分类的汉字
```
GET /api/characters/自然与宇宙
```

### 提交答案
```
POST /api/game/submit
Content-Type: application/json

{
  "answer": "雨",
  "correctAnswer": "雨"
}
```

## 使用方法

### 方法一：Python Flask Web服务（推荐）

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务：
```bash
python3 app.py
# 或使用启动脚本
python3 run.py
```

3. 在浏览器中访问：http://localhost:8080

### 方法二：静态文件服务

1. 直接在浏览器中打开 `templates/index.html` 文件
2. 或者使用本地服务器运行：

```bash
# 使用Python简单服务器
python -m http.server 8000

# 或使用Node.js
npx serve .
```

## 键盘快捷键

- `Enter` - 下一题
- `R` - 重新开始
- `V` - 播放语音

## 浏览器兼容性

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## 未来扩展

- 添加更多汉字题目
- 增加音效文件
- 添加学习进度保存
- 增加更多游戏模式
