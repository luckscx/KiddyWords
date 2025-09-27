from flask import Flask, render_template, jsonify, request
import json
import random
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# 数据库初始化
def init_database():
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_time INTEGER NOT NULL,
            average_time INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            play_timestamp INTEGER NOT NULL,
            UNIQUE(nickname, created_at)
        )
    ''')
    
    # 检查是否需要添加play_timestamp字段（用于现有数据库的迁移）
    cursor.execute("PRAGMA table_info(scores)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'play_timestamp' not in columns:
        cursor.execute('ALTER TABLE scores ADD COLUMN play_timestamp INTEGER NOT NULL DEFAULT 0')
    
    # 创建反馈统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character TEXT NOT NULL,
            image_file TEXT NOT NULL,
            feedback_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(character, image_file)
        )
    ''')
    
    conn.commit()
    conn.close()

# 保存成绩到数据库
def save_score(nickname, score, total_time, average_time):
    print(f"[SAVE_SCORE] 开始保存成绩 - 昵称: '{nickname}', 分数: {score}, 总时间: {total_time}ms, 平均时间: {average_time}ms")
    
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    try:
        # 生成当前UNIX时间戳
        play_timestamp = int(datetime.now().timestamp())
        print(f"[SAVE_SCORE] 生成时间戳: {play_timestamp}")
        
        print(f"[SAVE_SCORE] 尝试插入新记录...")
        cursor.execute('''
            INSERT INTO scores (nickname, score, total_time, average_time, play_timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (nickname, score, total_time, average_time, play_timestamp))
        conn.commit()
        print(f"[SAVE_SCORE] 新记录插入成功")
        return True
    except sqlite3.IntegrityError as e:
        print(f"[SAVE_SCORE] 检测到重复记录，尝试更新...")
        # 如果昵称和时间重复，更新记录
        play_timestamp = int(datetime.now().timestamp())
        print(f"[SAVE_SCORE] 更新记录时间戳: {play_timestamp}")
        
        cursor.execute('''
            UPDATE scores 
            SET score = ?, total_time = ?, average_time = ?, play_timestamp = ?
            WHERE nickname = ? AND created_at = CURRENT_TIMESTAMP
        ''', (score, total_time, average_time, play_timestamp, nickname))
        conn.commit()
        print(f"[SAVE_SCORE] 记录更新成功")
        return True
    except Exception as e:
        print(f"[SAVE_SCORE] 保存成绩失败: {e}")
        print(f"[SAVE_SCORE] 异常类型: {type(e).__name__}")
        import traceback
        print(f"[SAVE_SCORE] 异常堆栈: {traceback.format_exc()}")
        return False
    finally:
        conn.close()
        print(f"[SAVE_SCORE] 数据库连接已关闭")

# 获取排行榜
def get_leaderboard(limit=20):
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT nickname, score, total_time, average_time, play_timestamp
        FROM scores
        ORDER BY score DESC, total_time ASC
        LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    
    leaderboard = []
    for i, row in enumerate(results, 1):
        
        leaderboard.append({
            'rank': i,
            'nickname': row[0],
            'score': row[1],
            'total_time': row[2],
            'average_time': row[3],
            'play_timestamp': row[4]
        })
    return leaderboard

# 获取用户排名
def get_user_rank(score, total_time):
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) + 1 as rank
        FROM scores
        WHERE score > ? OR (score = ? AND total_time < ?)
    ''', (score, score, total_time))
    rank = cursor.fetchone()[0]
    conn.close()
    return rank

# 提交反馈
def submit_feedback(character, image_file):
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    try:
        # 尝试插入新记录
        cursor.execute('''
            INSERT INTO feedback (character, image_file, feedback_count)
            VALUES (?, ?, 1)
        ''', (character, image_file))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 如果记录已存在，更新计数
        cursor.execute('''
            UPDATE feedback 
            SET feedback_count = feedback_count + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE character = ? AND image_file = ?
        ''', (character, image_file))
        conn.commit()
        return True
    except Exception as e:
        print(f"提交反馈失败: {e}")
        return False
    finally:
        conn.close()

# 获取反馈统计
def get_feedback_stats():
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT character, image_file, feedback_count, updated_at
        FROM feedback
        ORDER BY feedback_count DESC, updated_at DESC
    ''')
    results = cursor.fetchall()
    conn.close()
    
    feedback_stats = []
    for row in results:
        feedback_stats.append({
            'character': row[0],
            'image_file': row[1],
            'feedback_count': row[2],
            'updated_at': row[3]
        })
    return feedback_stats

# 加载汉字数据
def load_characters():
    with open('data/characters.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载英语字母数据
def load_english_alphabet():
    with open('data/english_alphabet.json', 'r', encoding='utf-8') as f:
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
        'common_words': random.sample(correct_char.get('common_words', []), min(4, len(correct_char.get('common_words', [])))) if correct_char.get('common_words', []) else []
    }

# 生成避免重复汉字的题目
def generate_question_with_avoidance(category=None, difficulty='easy', used_characters=None):
    characters_data = load_characters()
    
    if used_characters is None:
        used_characters = set()
    
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
    
    # 从选中的分类中过滤掉已使用的汉字
    available_chars = [char for char in target_category['characters'] 
                      if char['character'] not in used_characters]
    
    # 如果该分类中没有可用的汉字，则从所有分类中选择
    if not available_chars:
        all_chars = []
        for cat in characters_data['basicChineseCharactersForKids']:
            all_chars.extend([char for char in cat['characters'] 
                            if char['character'] not in used_characters])
        if not all_chars:
            # 如果所有汉字都被使用过，清空已使用列表重新开始
            used_characters.clear()
            all_chars = []
            for cat in characters_data['basicChineseCharactersForKids']:
                all_chars.extend(cat['characters'])
        
        if all_chars:
            correct_char = random.choice(all_chars)
        else:
            # 最后的备用方案
            correct_char = random.choice(characters_data['basicChineseCharactersForKids'][0]['characters'])
    else:
        correct_char = random.choice(available_chars)
    
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
        'common_words': random.sample(correct_char.get('common_words', []), min(4, len(correct_char.get('common_words', [])))) if correct_char.get('common_words', []) else []
    }

# 生成英语字母游戏题目
def generate_english_question(game_type='letter_recognition', difficulty='easy'):
    alphabet_data = load_english_alphabet()
    
    if game_type == 'letter_recognition':
        # 字母识别游戏：显示图片，选择对应字母
        correct_letter = random.choice(alphabet_data['englishAlphabet'])
        
        # 生成错误选项
        other_letters = [letter for letter in alphabet_data['englishAlphabet'] 
                        if letter['letter'] != correct_letter['letter']]
        
        # 根据难度选择选项数量
        if difficulty == 'easy':
            num_options = 2
        elif difficulty == 'medium':
            num_options = 3
        else:  # hard
            num_options = 4
        
        # 随机选择错误选项
        wrong_options = random.sample(other_letters, min(num_options - 1, len(other_letters)))
        
        # 组合所有选项
        all_options = [correct_letter] + wrong_options
        random.shuffle(all_options)
        
        return {
            'image': f"/static/images/english/{correct_letter['image_file']}",
            'correctAnswer': correct_letter['letter'],
            'options': [letter['letter'] for letter in all_options],
            'voiceText': f'请找出字母"{correct_letter["letter"]}"',
            'pronunciation': correct_letter['pronunciation'],
            'phonetic': correct_letter['phonetic'],
            'words': correct_letter['words'],
            'description': correct_letter['description']
        }
    
    elif game_type == 'letter_pairing':
        # 大小写配对游戏
        correct_letter = random.choice(alphabet_data['englishAlphabet'])
        
        # 生成错误选项
        other_letters = [letter for letter in alphabet_data['englishAlphabet'] 
                        if letter['letter'] != correct_letter['letter']]
        
        if difficulty == 'easy':
            num_options = 2
        elif difficulty == 'medium':
            num_options = 3
        else:
            num_options = 4
        
        wrong_options = random.sample(other_letters, min(num_options - 1, len(other_letters)))
        all_options = [correct_letter] + wrong_options
        random.shuffle(all_options)
        
        return {
            'image': f"/static/images/english/{correct_letter['image_file']}",
            'correctAnswer': correct_letter['lowercase'],
            'options': [letter['lowercase'] for letter in all_options],
            'voiceText': f'请找出小写字母"{correct_letter["lowercase"]}"',
            'pronunciation': correct_letter['pronunciation'],
            'phonetic': correct_letter['phonetic'],
            'words': correct_letter['words'],
            'description': correct_letter['description']
        }
    
    elif game_type == 'word_matching':
        # 单词匹配游戏：显示字母，选择对应单词
        correct_letter = random.choice(alphabet_data['englishAlphabet'])
        correct_word = random.choice(correct_letter['words'])
        
        # 生成错误单词选项
        all_words = []
        for letter in alphabet_data['englishAlphabet']:
            all_words.extend(letter['words'])
        
        other_words = [word for word in all_words if word != correct_word]
        wrong_words = random.sample(other_words, min(3, len(other_words)))
        
        all_word_options = [correct_word] + wrong_words
        random.shuffle(all_word_options)
        
        return {
            'image': f"/static/images/english/{correct_letter['image_file']}",
            'correctAnswer': correct_word,
            'options': all_word_options,
            'voiceText': f'请找出以字母"{correct_letter["letter"]}"开头的单词',
            'pronunciation': correct_letter['pronunciation'],
            'phonetic': correct_letter['phonetic'],
            'words': correct_letter['words'],
            'description': correct_letter['description']
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

@app.route('/api/game/start', methods=['GET', 'POST'])
def start_game():
    """开始新游戏"""
    # 支持GET和POST请求
    if request.method == 'POST':
        data = request.get_json() or {}
        category = data.get('category') or request.args.get('category')
        recent_words = data.get('recent_words', [])
    else:
        category = request.args.get('category')
        recent_words = []
    
    questions = []
    used_characters = set(recent_words)  # 记录已使用的汉字
    
    for _ in range(10):  # 生成10个题目
        question = generate_question_with_avoidance(category, 'medium', used_characters)
        questions.append(question)
        # 将正确答案添加到已使用列表中
        used_characters.add(question['correctAnswer'])
    
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

@app.route('/api/leaderboard/submit', methods=['POST'])
def submit_score():
    """提交成绩"""
    try:
        # 记录请求开始
        print(f"[LEADERBOARD_SUBMIT] 收到成绩提交请求")
        
        data = request.get_json()
        if not data:
            print(f"[LEADERBOARD_SUBMIT] 错误: 请求数据为空")
            return jsonify({'error': '请求数据不能为空'}), 400
        
        nickname = data.get('nickname', '').strip()
        score = data.get('score', 0)
        total_time = data.get('total_time', 0)
        average_time = data.get('average_time', 0)
        
        # 记录接收到的数据
        print(f"[LEADERBOARD_SUBMIT] 接收数据 - 昵称: '{nickname}', 分数: {score}, 总时间: {total_time}ms, 平均时间: {average_time}ms")
        
        # 验证昵称
        if not nickname:
            print(f"[LEADERBOARD_SUBMIT] 错误: 昵称为空")
            return jsonify({'error': '昵称不能为空'}), 400
        
        # 验证数据有效性
        if not isinstance(score, int) or score < 0:
            print(f"[LEADERBOARD_SUBMIT] 错误: 无效分数 {score}")
            return jsonify({'error': '分数必须是非负整数'}), 400
        
        if not isinstance(total_time, int) or total_time < 0:
            print(f"[LEADERBOARD_SUBMIT] 错误: 无效总时间 {total_time}")
            return jsonify({'error': '总时间必须是非负整数'}), 400
        
        if not isinstance(average_time, int) or average_time < 0:
            print(f"[LEADERBOARD_SUBMIT] 错误: 无效平均时间 {average_time}")
            return jsonify({'error': '平均时间必须是非负整数'}), 400
        
        # 尝试保存成绩
        print(f"[LEADERBOARD_SUBMIT] 开始保存成绩到数据库...")
        save_result = save_score(nickname, score, total_time, average_time)
        
        if save_result:
            print(f"[LEADERBOARD_SUBMIT] 成绩保存成功")
            
            # 获取用户排名
            print(f"[LEADERBOARD_SUBMIT] 计算用户排名...")
            rank = get_user_rank(score, total_time)
            print(f"[LEADERBOARD_SUBMIT] 用户排名: 第{rank}名")
            
            response_data = {
                'success': True,
                'rank': rank,
                'message': f'恭喜！您获得了第{rank}名！'
            }
            
            print(f"[LEADERBOARD_SUBMIT] 成功响应: {response_data}")
            return jsonify(response_data)
        else:
            print(f"[LEADERBOARD_SUBMIT] 错误: 保存成绩失败")
            return jsonify({'error': '保存成绩失败'}), 500
            
    except Exception as e:
        print(f"[LEADERBOARD_SUBMIT] 异常: {str(e)}")
        print(f"[LEADERBOARD_SUBMIT] 异常类型: {type(e).__name__}")
        import traceback
        print(f"[LEADERBOARD_SUBMIT] 异常堆栈: {traceback.format_exc()}")
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/api/leaderboard')
def get_leaderboard_api():
    """获取排行榜"""
    limit = request.args.get('limit', 20, type=int)
    leaderboard = get_leaderboard(limit)
    return jsonify({'leaderboard': leaderboard})

@app.route('/leaderboard')
def leaderboard_page():
    """排行榜页面"""
    return render_template('leaderboard.html')

@app.route('/api/feedback', methods=['POST'])
def submit_feedback_api():
    """提交反馈"""
    data = request.get_json()
    character = data.get('character')
    image_file = data.get('image_file')
    
    if not character or not image_file:
        return jsonify({'error': '字符和图片文件不能为空'}), 400
    
    success = submit_feedback(character, image_file)
    if success:
        return jsonify({'message': '反馈提交成功'})
    else:
        return jsonify({'error': '反馈提交失败'}), 500

@app.route('/api/feedback/stats')
def get_feedback_stats_api():
    """获取反馈统计"""
    stats = get_feedback_stats()
    return jsonify({'feedback_stats': stats})

# 英语字母游戏路由
@app.route('/english')
def english_alphabet_page():
    """英语字母游戏页面"""
    return render_template('english_alphabet.html')

@app.route('/api/english/alphabet')
def get_english_alphabet():
    """获取所有英语字母数据"""
    return jsonify(load_english_alphabet())

@app.route('/api/english/question')
def get_english_question():
    """获取英语字母游戏题目"""
    game_type = request.args.get('game_type', 'letter_recognition')
    difficulty = request.args.get('difficulty', 'easy')
    return jsonify(generate_english_question(game_type, difficulty))

@app.route('/api/english/game/start', methods=['GET', 'POST'])
def start_english_game():
    """开始英语字母游戏"""
    if request.method == 'POST':
        data = request.get_json() or {}
        game_type = data.get('game_type', 'letter_recognition')
        difficulty = data.get('difficulty', 'easy')
    else:
        game_type = request.args.get('game_type', 'letter_recognition')
        difficulty = request.args.get('difficulty', 'easy')
    
    questions = []
    for _ in range(10):  # 生成10个题目
        question = generate_english_question(game_type, difficulty)
        questions.append(question)
    
    return jsonify({
        'questions': questions,
        'totalQuestions': len(questions),
        'gameType': game_type,
        'difficulty': difficulty
    })

@app.route('/api/english/abc-song')
def get_abc_song():
    """获取字母歌数据"""
    alphabet_data = load_english_alphabet()
    return jsonify({
        'alphabet': alphabet_data['englishAlphabet'],
        'song_lyrics': 'A B C D E F G, H I J K L M N O P, Q R S T U V, W X Y Z'
    })

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
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
    
    PORT = os.getenv('PORT', 8080)
    print(f"Starting server on port {PORT}")
    app.run(debug=True, host='0.0.0.0', port=PORT)
