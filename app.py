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
    
    # 使用JSON文件中的图片路径
    image_path = f"/static/images/{correct_char['image_file']}" if 'image_file' in correct_char else None
    
    return {
        'image': image_path,
        'correctAnswer': correct_char['character'],
        'options': [char['character'] for char in all_options],
        'voiceText': f'请找出"{correct_char["character"]}"字',
        'pinyin': correct_char['pinyin'],
        'meaning': correct_char['meaning'],
        'category': target_category['category'],
        'common_words': correct_char.get('common_words', [])
    }


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
    for _ in range(10):  # 生成5个题目
        questions.append(generate_question(category, 'medium'))
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
