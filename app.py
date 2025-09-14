from flask import Flask, render_template, jsonify, request
import json
import random
import os

app = Flask(__name__)

# 加载汉字数据
def load_characters():
    with open('characters.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 生成游戏题目
def generate_question(category=None, difficulty='easy'):
    characters_data = load_characters()
    
    # 如果指定了分类，只从该分类选择
    if category:
        target_category = None
        for cat in characters_data['basicChineseCharactersForKids']:
            if cat['category'] == category:
                target_category = cat
                break
        if not target_category:
            # 如果找不到指定分类，随机选择一个
            target_category = random.choice(characters_data['basicChineseCharactersForKids'])
    else:
        # 随机选择一个分类
        target_category = random.choice(characters_data['basicChineseCharactersForKids'])
    
    # 从选中的分类中随机选择一个汉字
    correct_char = random.choice(target_category['characters'])
    
    # 生成错误选项
    all_chars = []
    for cat in characters_data['basicChineseCharactersForKids']:
        all_chars.extend(cat['characters'])
    
    # 排除正确答案
    other_chars = [char for char in all_chars if char['character'] != correct_char['character']]
    
    # 根据难度选择选项数量
    if difficulty == 'easy':
        num_options = 2
    elif difficulty == 'medium':
        num_options = 3
    else:  # hard
        num_options = 4
    
    # 随机选择错误选项
    wrong_options = random.sample(other_chars, min(num_options - 1, len(other_chars)))
    
    # 组合所有选项
    all_options = [correct_char] + wrong_options
    random.shuffle(all_options)
    
    # 生成SVG图片（这里简化处理，实际可以更复杂）
    svg_image = generate_svg_image(correct_char['character'], correct_char['meaning'])
    
    return {
        'image': svg_image,
        'correctAnswer': correct_char['character'],
        'options': [char['character'] for char in all_options],
        'voiceText': f'请找出"{correct_char["character"]}"字',
        'pinyin': correct_char['pinyin'],
        'meaning': correct_char['meaning'],
        'category': target_category['category']
    }

def generate_svg_image(character, meaning):
    """生成简单的SVG图片"""
    # 根据汉字含义生成不同颜色的背景
    colors = {
        'sun': '#FFD700', 'moon': '#C0C0C0', 'water': '#87CEEB', 'fire': '#FF4500',
        'mountain': '#8B4513', 'stone': '#696969', 'field': '#90EE90', 'earth': '#D2691E',
        'wood': '#8B4513', 'grain': '#9ACD32', 'rain': '#4682B4', 'wind': '#F0F8FF',
        'cloud': '#F5F5F5', 'sky': '#87CEEB', 'person': '#FFB6C1', 'mouth': '#FF69B4',
        'hand': '#FFA07A', 'foot': '#DDA0DD', 'ear': '#F0E68C', 'eye': '#98FB98',
        'tooth': '#F5F5DC', 'heart': '#FFB6C1', 'head': '#FFA07A', 'big': '#FF6347',
        'small': '#87CEEB', 'long': '#98FB98', 'tall': '#DDA0DD', 'fish': '#20B2AA',
        'bird': '#FFD700', 'horse': '#8B4513', 'cow': '#F5DEB3', 'sheep': '#F0F8FF',
        'insect': '#32CD32', 'flower': '#FF69B4', 'grass': '#90EE90', 'fruit': '#FFA500',
        'rice': '#F5DEB3', 'melon': '#32CD32', 'one': '#FF0000', 'two': '#00FF00',
        'three': '#0000FF', 'ten': '#FFFF00', 'up': '#FF00FF', 'down': '#00FFFF',
        'middle': '#800080', 'left': '#FFA500', 'right': '#008000', 'dad': '#4169E1',
        'mom': '#FF69B4', 'door': '#8B4513', 'car': '#FF4500', 'clothes': '#9370DB',
        'food': '#FF6347', 'live': '#32CD32', 'book': '#8B4513', 'drawing': '#FF1493',
        'knife': '#C0C0C0', 'work': '#696969', 'red': '#FF0000', 'white': '#FFFFFF',
        'black': '#000000', 'many': '#FFD700', 'few': '#C0C0C0', 'life': '#32CD32',
        'good': '#00FF00', 'go out': '#FF4500', 'enter': '#00BFFF', 'walk': '#32CD32',
        'run': '#FF6347', 'fly': '#87CEEB', 'see': '#FFD700', 'cry': '#FF69B4',
        'smile': '#FFD700', 'shout': '#FF4500', 'eat': '#FF6347', 'drink': '#87CEEB',
        'speak': '#FF69B4', 'sit': '#8B4513', 'stand': '#32CD32', 'come': '#00FF00',
        'go': '#FF4500', 'love': '#FF69B4'
    }
    
    # 根据含义选择颜色
    bg_color = '#FFD700'  # 默认金色
    for key, color in colors.items():
        if key in meaning.lower():
            bg_color = color
            break
    
    svg_content = f'''<svg width="200" height="200" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="200" height="200" fill="#FFFFFF"/>
<circle cx="100" cy="100" r="80" fill="{bg_color}"/>
<circle cx="100" cy="100" r="60" fill="#FFFFFF"/>
<circle cx="100" cy="100" r="40" fill="{bg_color}"/>
<text x="100" y="110" text-anchor="middle" fill="#FF6B6B" font-size="48" font-family="Arial, sans-serif" font-weight="bold">{character}</text>
</svg>'''
    
    import base64
    return f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/characters')
def get_characters():
    """获取所有汉字数据"""
    return jsonify(load_characters())

@app.route('/api/categories')
def get_categories():
    """获取所有分类"""
    characters_data = load_characters()
    categories = [cat['category'] for cat in characters_data['basicChineseCharactersForKids']]
    return jsonify(categories)

@app.route('/api/question')
def get_question():
    """获取随机题目"""
    category = request.args.get('category')
    difficulty = request.args.get('difficulty', 'easy')
    return jsonify(generate_question(category, difficulty))

@app.route('/api/question/<category>')
def get_question_by_category(category):
    """根据分类获取题目"""
    difficulty = request.args.get('difficulty', 'easy')
    return jsonify(generate_question(category, difficulty))

@app.route('/api/characters/<category>')
def get_characters_by_category(category):
    """获取指定分类的汉字"""
    characters_data = load_characters()
    for cat in characters_data['basicChineseCharactersForKids']:
        if cat['category'] == category:
            return jsonify(cat)
    return jsonify({'error': 'Category not found'}), 404

@app.route('/api/game/start')
def start_game():
    """开始新游戏"""
    category = request.args.get('category')
    questions = []
    for _ in range(5):  # 生成5个题目
        questions.append(generate_question(category))
    return jsonify({
        'questions': questions,
        'totalQuestions': len(questions)
    })

@app.route('/api/game/submit', methods=['POST'])
def submit_answer():
    """提交答案"""
    data = request.get_json()
    user_answer = data.get('answer')
    correct_answer = data.get('correctAnswer')
    
    is_correct = user_answer == correct_answer
    
    return jsonify({
        'correct': is_correct,
        'message': '真棒！答对了！' if is_correct else '再试试看！'
    })

if __name__ == '__main__':
    # 创建templates目录
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # 将HTML文件移动到templates目录
    if os.path.exists('index.html'):
        import shutil
        shutil.move('index.html', 'templates/index.html')
    
    # 将CSS和JS文件移动到static目录
    if os.path.exists('style.css'):
        shutil.move('style.css', 'static/style.css')
    if os.path.exists('script.js'):
        shutil.move('script.js', 'static/script.js')
    
    app.run(debug=True, host='0.0.0.0', port=8080)
