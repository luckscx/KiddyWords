// 游戏数据 - 从API获取
let gameData = [];

// 游戏状态
let currentQuestionIndex = 0;
let score = 0;
let gameActive = true;

// DOM 元素
const currentImage = document.getElementById('current-image');
const voiceText = document.getElementById('voice-text');
const optionsGrid = document.getElementById('options-grid');
const feedbackMessage = document.getElementById('feedback-message');
const feedbackContainer = document.getElementById('feedback-container');
const imageOverlay = document.getElementById('image-overlay');
const scoreElement = document.getElementById('score');
const levelElement = document.getElementById('level');
const nextBtn = document.getElementById('next-btn');
const restartBtn = document.getElementById('restart-btn');
const gameOverModal = document.getElementById('game-over-modal');
const finalScoreElement = document.getElementById('final-score');
const playAgainBtn = document.getElementById('play-again-btn');
const voiceBtn = document.getElementById('voice-btn');
const categorySelect = document.getElementById('category-select');
const newGameBtn = document.getElementById('new-game-btn');

// 音频元素
const correctAudio = document.getElementById('correct-audio');
const wrongAudio = document.getElementById('wrong-audio');
const voiceAudio = document.getElementById('voice-audio');

// 加载分类选项
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();
        
        // 清空现有选项
        categorySelect.innerHTML = '<option value="">随机分类</option>';
        
        // 添加分类选项
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categorySelect.appendChild(option);
        });
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

// 初始化游戏
async function initGame() {
    currentQuestionIndex = 0;
    score = 0;
    gameActive = true;
    updateScore();
    
    // 从API获取游戏数据
    try {
        const selectedCategory = categorySelect.value;
        const url = selectedCategory ? `/api/game/start?category=${encodeURIComponent(selectedCategory)}` : '/api/game/start';
        const response = await fetch(url);
        const data = await response.json();
        gameData = data.questions;
        loadQuestion();
    } catch (error) {
        console.error('获取游戏数据失败:', error);
        showFeedback('游戏加载失败，请刷新页面重试', 'wrong');
    }
    
    hideFeedback();
    nextBtn.disabled = true;
    gameOverModal.classList.remove('show');
}

// 加载题目
function loadQuestion() {
    if (currentQuestionIndex >= gameData.length) {
        endGame();
        return;
    }

    const question = gameData[currentQuestionIndex];
    
    // 设置图片
    currentImage.src = question.image;
    currentImage.alt = question.correctAnswer;
    
    // 设置语音文本
    voiceText.textContent = question.voiceText;
    
    // 清空选项
    optionsGrid.innerHTML = '';
    
    // 创建选项按钮
    question.options.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'option-button';
        button.textContent = option;
        button.onclick = () => selectOption(option, button);
        optionsGrid.appendChild(button);
    });
    
    // 更新关卡显示
    levelElement.textContent = currentQuestionIndex + 1;
    
    // 重置状态
    hideFeedback();
    nextBtn.disabled = true;
    gameActive = true;
}

// 选择选项
function selectOption(selectedOption, buttonElement) {
    if (!gameActive) return;
    
    gameActive = false;
    const question = gameData[currentQuestionIndex];
    const isCorrect = selectedOption === question.correctAnswer;
    
    if (isCorrect) {
        // 正确答案
        score += 10;
        updateScore();
        
        // 视觉反馈
        buttonElement.classList.add('correct');
        imageOverlay.classList.add('correct');
        showFeedback('真棒！答对了！🎉', 'correct');
        
        // 播放正确音效
        playAudio(correctAudio);
        
        // 禁用所有按钮
        disableAllOptions();
        
    } else {
        // 错误答案
        buttonElement.classList.add('wrong');
        imageOverlay.classList.add('wrong');
        showFeedback('再试试看！💪', 'wrong');
        
        // 播放错误音效
        playAudio(wrongAudio);
        
        // 禁用所有按钮
        disableAllOptions();
    }
    
    // 显示下一题按钮
    nextBtn.disabled = false;
}

// 禁用所有选项
function disableAllOptions() {
    const buttons = optionsGrid.querySelectorAll('.option-button');
    buttons.forEach(button => {
        button.classList.add('disabled');
        button.onclick = null;
    });
}

// 显示反馈
function showFeedback(message, type) {
    feedbackMessage.textContent = message;
    feedbackMessage.className = `feedback-message ${type} show`;
}

// 隐藏反馈
function hideFeedback() {
    feedbackMessage.classList.remove('show', 'correct', 'wrong');
    imageOverlay.classList.remove('correct', 'wrong');
}

// 更新分数
function updateScore() {
    scoreElement.textContent = score;
}

// 播放音频
function playAudio(audioElement) {
    if (audioElement) {
        audioElement.currentTime = 0;
        audioElement.play().catch(e => {
            console.log('音频播放失败:', e);
        });
    }
}

// 下一题
function nextQuestion() {
    currentQuestionIndex++;
    loadQuestion();
}

// 结束游戏
function endGame() {
    finalScoreElement.textContent = score;
    gameOverModal.classList.add('show');
}

// 重新开始游戏
function restartGame() {
    initGame();
}

// 播放语音
function playVoice() {
    const question = gameData[currentQuestionIndex];
    if (question && question.voiceText) {
        // 使用Web Speech API播放语音
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(question.voiceText);
            utterance.lang = 'zh-CN';
            utterance.rate = 0.8;
            utterance.pitch = 1.2;
            speechSynthesis.speak(utterance);
        } else {
            // 备用方案：显示提示
            showFeedback('请查看屏幕上的提示文字', 'correct');
        }
    }
}

// 事件监听器
nextBtn.addEventListener('click', nextQuestion);
restartBtn.addEventListener('click', restartGame);
playAgainBtn.addEventListener('click', restartGame);
voiceBtn.addEventListener('click', playVoice);
newGameBtn.addEventListener('click', initGame);

// 键盘支持
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !nextBtn.disabled) {
        nextQuestion();
    } else if (e.key === 'r' || e.key === 'R') {
        restartGame();
    } else if (e.key === 'v' || e.key === 'V') {
        playVoice();
    }
});

// 页面加载完成后初始化游戏
document.addEventListener('DOMContentLoaded', async () => {
    await loadCategories();
    await initGame();
});

// 防止图片拖拽
document.addEventListener('dragstart', (e) => {
    if (e.target.tagName === 'IMG') {
        e.preventDefault();
    }
});

// 触摸设备优化
if ('ontouchstart' in window) {
    document.body.classList.add('touch-device');
}
