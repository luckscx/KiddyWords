// 游戏数据 - 从API获取
let gameData = [];

// 游戏状态
let currentQuestionIndex = 0;
let score = 0;
let gameActive = true;
let autoNextTimer = null;
let currentQuestion = null; // 当前题目数据

// 最近三次的汉字记录，用于避免重复
let recentWords = [];

// 计时相关变量
let questionStartTime = 0;
let questionTimes = []; // 记录每题的答题时间（毫秒）
let totalTime = 0; // 总耗时
let timeUpdateInterval = null; // 时间更新定时器

// DOM 元素
const currentImage = document.getElementById('current-image');
const voiceText = document.getElementById('voice-text');
const optionsGrid = document.getElementById('options-grid');
const feedbackMessage = document.getElementById('feedback-message');
const feedbackContainer = document.getElementById('feedback-container');
const scoreElement = document.getElementById('score');
const levelElement = document.getElementById('level');
const totalTimeElement = document.getElementById('total-time');
const restartBtn = document.getElementById('restart-btn');
const gameOverModal = document.getElementById('game-over-modal');
const finalScoreElement = document.getElementById('final-score');
const finalTimeElement = document.getElementById('final-time');
const averageTimeElement = document.getElementById('average-time');
const playAgainBtn = document.getElementById('play-again-btn');

// 昵称弹窗相关DOM元素
const nicknameModal = document.getElementById('nickname-modal');
const finalScoreNicknameElement = document.getElementById('final-score-nickname');
const finalTimeNicknameElement = document.getElementById('final-time-nickname');
const averageTimeNicknameElement = document.getElementById('average-time-nickname');
const nicknameInput = document.getElementById('nickname-input');
const submitScoreBtn = document.getElementById('submit-score');
const skipSubmitBtn = document.getElementById('skip-submit');
const rankResultElement = document.getElementById('rank-result');
const categorySelect = document.getElementById('category-select');
const newGameBtn = document.getElementById('new-game-btn');
const pinyinDisplay = document.getElementById('pinyin-display');
const commonWordsDisplay = document.getElementById('common-words-display');
const wordsList = document.getElementById('words-list');
const feedbackBtn = document.getElementById('feedback-btn');

// 设置相关DOM元素
const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const speechRateSlider = document.getElementById('speech-rate');
const rateValueDisplay = document.getElementById('rate-value');
const readCommonWordsCheckbox = document.getElementById('read-common-words');
const readWordStartCheckbox = document.getElementById('read-word-start');
const saveSettingsBtn = document.getElementById('save-settings');
const closeSettingsBtn = document.getElementById('close-settings');

// 音频上下文
let audioContext = null;

// 设置相关变量
let gameSettings = {
    speechRate: 0.7,
    readCommonWords: true,
    readWordStart: true
};

// 初始化音频上下文
function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
}

// 更新最近汉字记录
function updateRecentWords(word) {
    // 添加新汉字到数组开头
    recentWords.unshift(word);
    // 只保留最近三次
    if (recentWords.length > 3) {
        recentWords = recentWords.slice(0, 3);
    }
}

// 开始题目计时
function startQuestionTimer() {
    questionStartTime = Date.now();
}

// 停止题目计时并记录
function stopQuestionTimer() {
    if (questionStartTime > 0) {
        const questionTime = Date.now() - questionStartTime;
        questionTimes.push(questionTime);
        totalTime += questionTime;
        questionStartTime = 0;
        return questionTime;
    }
    return 0;
}

// 格式化时间显示（毫秒转换为秒）
function formatTime(milliseconds) {
    const seconds = Math.round(milliseconds / 1000);
    if (seconds < 60) {
        return `${seconds}秒`;
    } else {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}分${remainingSeconds}秒`;
    }
}

// 设置相关函数
function loadSettings() {
    const savedSettings = localStorage.getItem('syword-settings');
    if (savedSettings) {
        try {
            gameSettings = { ...gameSettings, ...JSON.parse(savedSettings) };
        } catch (e) {
            console.error('加载设置失败:', e);
        }
    }
    updateSettingsUI();
}

function saveSettings() {
    try {
        localStorage.setItem('syword-settings', JSON.stringify(gameSettings));
        console.log('设置已保存');
    } catch (e) {
        console.error('保存设置失败:', e);
    }
}

function updateSettingsUI() {
    speechRateSlider.value = gameSettings.speechRate;
    rateValueDisplay.textContent = gameSettings.speechRate;
    readCommonWordsCheckbox.checked = gameSettings.readCommonWords;
    readWordStartCheckbox.checked = gameSettings.readWordStart;
}

function showSettings() {
    settingsModal.classList.add('show');
}

function hideSettings() {
    settingsModal.classList.remove('show');
}

function applySettings() {
    gameSettings.speechRate = parseFloat(speechRateSlider.value);
    gameSettings.readCommonWords = readCommonWordsCheckbox.checked;
    gameSettings.readWordStart = readWordStartCheckbox.checked;
    saveSettings();
    hideSettings();
}

// 昵称弹窗相关函数
function showNicknameModal() {
    // 更新弹窗中的成绩显示
    finalScoreNicknameElement.textContent = score;
    finalTimeNicknameElement.textContent = formatTime(totalTime);
    const averageTime = questionTimes.length > 0 ? Math.round(totalTime / questionTimes.length) : 0;
    averageTimeNicknameElement.textContent = formatTime(averageTime);
    
    // 清空输入框和结果
    nicknameInput.value = '';
    rankResultElement.style.display = 'none';
    rankResultElement.className = 'rank-result';
    
    // 显示弹窗
    nicknameModal.classList.add('show');
    nicknameInput.focus();
}

function hideNicknameModal() {
    nicknameModal.classList.remove('show');
}

async function submitScore() {
    const nickname = nicknameInput.value.trim();
    
    if (!nickname) {
        showRankResult('请输入昵称', 'error');
        return;
    }
    
    if (nickname.length > 20) {
        showRankResult('昵称不能超过20个字符', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/leaderboard/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                nickname: nickname,
                score: score,
                total_time: totalTime, // 毫秒
                average_time: questionTimes.length > 0 ? Math.round(totalTime / questionTimes.length) : 0 // 毫秒
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showRankResult(data.message, 'success');
            // 3秒后自动关闭弹窗
            setTimeout(() => {
                hideNicknameModal();
                showGameOverModal();
            }, 3000);
        } else {
            showRankResult(data.error || '提交失败', 'error');
        }
    } catch (error) {
        console.error('提交成绩失败:', error);
        showRankResult('网络错误，请稍后重试', 'error');
    }
}

function showRankResult(message, type) {
    rankResultElement.textContent = message;
    rankResultElement.className = `rank-result ${type}`;
    rankResultElement.style.display = 'block';
}

function showGameOverModal() {
    gameOverModal.classList.add('show');
}

// 使用浏览器语音合成播放拼音
function speakPinyin(pinyinText) {
    // 检查浏览器是否支持
    if ('speechSynthesis' in window) {
        // 创建一个语音实例
        const utterance = new SpeechSynthesisUtterance(pinyinText);
        
        // 非常重要！设置语言为中文
        utterance.lang = 'zh-CN';
        
        // 可选：设置参数
        utterance.rate = gameSettings.speechRate; // 语速 (0.1 到 10)
        utterance.pitch = 1.1; // 音高 (0 到 2)
        utterance.volume = 1; // 音量 (0 到 1)
        
        // 尝试设置一个更友好的声音（取决于系统支持）
        const voices = speechSynthesis.getVoices();
        const chineseVoice = voices.find(voice => voice.lang === 'zh-CN' || voice.lang === 'zh');
        if (chineseVoice) {
            utterance.voice = chineseVoice;
        }
        
        // 播放
        window.speechSynthesis.speak(utterance);
    } else {
        console.error('很抱歉，您的浏览器不支持语音合成！');
        // 可以在这里安排一个降级方案，比如播放预录的音频
    }
}

// 使用浏览器语音合成播放中文词语
function speakChineseWord(chineseText) {
    // 检查浏览器是否支持
    if ('speechSynthesis' in window) {
        // 创建一个语音实例
        const utterance = new SpeechSynthesisUtterance(chineseText);
        
        // 设置语言为中文
        utterance.lang = 'zh-CN';
        
        // 设置参数
        utterance.rate = gameSettings.speechRate; // 语速稍快一些
        utterance.pitch = 1.0; // 音高
        utterance.volume = 1; // 音量
        
        // 尝试设置一个更友好的声音
        const voices = speechSynthesis.getVoices();
        const chineseVoice = voices.find(voice => voice.lang === 'zh-CN' || voice.lang === 'zh');
        if (chineseVoice) {
            utterance.voice = chineseVoice;
        }
        
        // 播放
        window.speechSynthesis.speak(utterance);
    } else {
        console.error('很抱歉，您的浏览器不支持语音合成！');
    }
}

// 显示常见词语
function displayCommonWords(commonWords) {
    if (!commonWords || commonWords.length === 0) {
        return;
    }
    
    // 清空现有词语
    wordsList.innerHTML = '';
    
    // 创建词语元素
    commonWords.forEach((word, index) => {
        const wordElement = document.createElement('div');
        wordElement.className = 'word-item';
        wordElement.textContent = word;
        wordElement.dataset.index = index;
        wordsList.appendChild(wordElement);
    });
    
    // 显示词语区域
    commonWordsDisplay.style.display = 'flex';
}

// 隐藏常见词语
function hideCommonWords() {
    commonWordsDisplay.style.display = 'none';
    wordsList.innerHTML = '';
}

// 高亮当前词语
function highlightCurrentWord(index) {
    // 移除所有高亮
    const wordItems = wordsList.querySelectorAll('.word-item');
    wordItems.forEach((item, i) => {
        item.classList.remove('current');
        if (i < index) {
            item.classList.add('completed');
        }
    });
    
    // 高亮当前词语
    if (index < wordItems.length) {
        wordItems[index].classList.add('current');
    }
}

// 按顺序朗读常见词语
function speakCommonWords(commonWords, callback) {
    if (!commonWords || commonWords.length === 0) {
        if (callback) callback();
        return;
    }
    
    // 显示词语
    displayCommonWords(commonWords);
    
    let currentIndex = 0;
    
    function speakNext() {
        if (currentIndex >= commonWords.length) {
            // 所有词语读完后，标记最后一个为完成状态
            highlightCurrentWord(commonWords.length);
            if (callback) callback();
            return;
        }
        
        const word = commonWords[currentIndex];
        console.log('朗读常见词语:', word);
        
        // 高亮当前词语
        highlightCurrentWord(currentIndex);
        
        // 创建语音实例
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'zh-CN';
        utterance.rate = gameSettings.speechRate;
        utterance.pitch = 1.0;
        utterance.volume = 1;
        
        // 设置声音
        const voices = speechSynthesis.getVoices();
        const chineseVoice = voices.find(voice => voice.lang === 'zh-CN' || voice.lang === 'zh');
        if (chineseVoice) {
            utterance.voice = chineseVoice;
        }
        
        // 播放完成后继续下一个
        utterance.onend = function() {
            currentIndex++;
            // 添加短暂延迟，让词语之间有间隔
            setTimeout(speakNext, 300);
        };
        
        // 播放
        window.speechSynthesis.speak(utterance);
    }
    
    speakNext();
}

// 播放完整拼音拼读（使用语音合成）
function playPinyinPronunciation(pinyin) {
    console.log('开始播放拼音拼读:', pinyin);
    speakPinyin(pinyin);
}

// 生成正确音效
function playCorrectSound() {
    initAudioContext();
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // 播放上升音调
    oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
    oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
    oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
}

// 生成错误音效
function playWrongSound() {
    initAudioContext();
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // 播放下降音调
    oscillator.frequency.setValueAtTime(392.00, audioContext.currentTime); // G4
    oscillator.frequency.setValueAtTime(349.23, audioContext.currentTime + 0.1); // F4
    oscillator.frequency.setValueAtTime(293.66, audioContext.currentTime + 0.2); // D4
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.6);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.6);
}

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
    // 清除自动切换定时器
    if (autoNextTimer) {
        clearTimeout(autoNextTimer);
        autoNextTimer = null;
    }
    
    currentQuestionIndex = 0;
    score = 0;
    gameActive = true;
    updateScore();
    
    // 重置计时变量
    questionTimes = [];
    totalTime = 0;
    questionStartTime = 0;
    
    // 清理时间更新定时器
    if (timeUpdateInterval) {
        clearInterval(timeUpdateInterval);
        timeUpdateInterval = null;
    }
    
    // 从API获取游戏数据
    try {
        const selectedCategory = categorySelect.value;
        const url = selectedCategory ? `/api/game/start?category=${encodeURIComponent(selectedCategory)}` : '/api/game/start';
        
        // 构建请求参数，包含最近三次的汉字
        const requestData = {
            recent_words: recentWords
        };
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        gameData = data.questions;
        loadQuestion();
    } catch (error) {
        console.error('获取游戏数据失败:', error);
        showFeedback('游戏加载失败，请刷新页面重试', 'wrong');
    }
    
    hideFeedback();
    gameOverModal.classList.remove('show');
}

// 加载题目
function loadQuestion() {
    if (currentQuestionIndex >= gameData.length) {
        endGame();
        return;
    }

    const question = gameData[currentQuestionIndex];
    currentQuestion = question; // 保存当前题目数据
    
    // 设置图片
    currentImage.src = question.image;
    currentImage.alt = question.correctAnswer;
    
    // 显示拼音
    pinyinDisplay.textContent = "拼音：" + question.pinyin;
    
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
    hideCommonWords(); // 隐藏词语显示区域
    resetFeedbackButton(); // 重置反馈按钮
    gameActive = true;
    
    // 清除自动切换定时器
    if (autoNextTimer) {
        clearTimeout(autoNextTimer);
        autoNextTimer = null;
    }
    
    // 开始计时
    startQuestionTimer();
    
    // 启动定时器实时更新时间显示
    if (timeUpdateInterval) {
        clearInterval(timeUpdateInterval);
    }
    timeUpdateInterval = setInterval(updateTotalTime, 100); // 每100ms更新一次
    
    // 根据设置决定是否朗读汉字
    if (gameSettings.readWordStart) {
        setTimeout(() => {
            speakChineseWord(question.correctAnswer);
        }, 500); // 延迟500毫秒朗读，让图片先显示
    }
}

// 选择选项
function selectOption(selectedOption, buttonElement) {
    if (!gameActive) return;
    
    gameActive = false;
    const question = gameData[currentQuestionIndex];
    const isCorrect = selectedOption === question.correctAnswer;
    
    if (isCorrect) {
        // 停止计时并记录
        const questionTime = stopQuestionTimer();
        
        // 停止时间更新定时器
        if (timeUpdateInterval) {
            clearInterval(timeUpdateInterval);
            timeUpdateInterval = null;
        }
        
        // 正确答案
        score += 10;
        updateScore();
        
        // 更新最近汉字记录
        updateRecentWords(question.correctAnswer);
        
        // 视觉反馈
        buttonElement.classList.add('correct');
        showFeedback('真棒！答对了！🎉 正在朗读常见词语...', 'correct');
        
        // 播放正确音效
        playAudio('correct');
        
        // 禁用所有按钮
        disableAllOptions();
        
        // 延迟播放拼音拼读，然后朗读常见词语
        setTimeout(() => {
            playPinyinPronunciation(question.pinyin);
            
            // 拼音读完后朗读常见词语
            setTimeout(() => {
                if (gameSettings.readCommonWords && question.common_words && question.common_words.length > 0) {
                    speakCommonWords(question.common_words, () => {
                        // 所有词语读完后隐藏词语显示区域
                        hideCommonWords();
                        showFeedback('朗读完成！准备下一题...', 'correct');
                        // 自动切换到下一题
                        setTimeout(() => {
                            nextQuestion();
                        }, 1500);
                    });
                } else {
                    // 没有常见词语或设置不朗读，直接切换到下一题
                    setTimeout(() => {
                        nextQuestion();
                    }, 1500);
                }
            }, 2000); // 等待拼音朗读完成
        }, 800);
        
    } else {
        // 错误答案
        buttonElement.classList.add('wrong');
        showFeedback('再试试看！', 'wrong');
        
        // 播放错误音效
        playAudio('wrong');

        gameActive = true;
    }
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
}

// 更新分数
function updateScore() {
    scoreElement.textContent = score;
}

// 更新总时间显示
function updateTotalTime() {
    const currentTime = questionStartTime > 0 ? Date.now() - questionStartTime : 0;
    const displayTime = totalTime + currentTime;
    totalTimeElement.textContent = formatTime(displayTime);
}

// 播放音频
function playAudio(type) {
    try {
        if (type === 'correct') {
            playCorrectSound();
        } else if (type === 'wrong') {
            playWrongSound();
        }
    } catch (e) {
        console.log('音频播放失败:', e);
    }
}

// 下一题
function nextQuestion() {
    // 清除自动切换定时器
    if (autoNextTimer) {
        clearTimeout(autoNextTimer);
        autoNextTimer = null;
    }
    
    currentQuestionIndex++;
    loadQuestion();
}

// 结束游戏
function endGame() {
    // 停止时间更新定时器
    if (timeUpdateInterval) {
        clearInterval(timeUpdateInterval);
        timeUpdateInterval = null;
    }
    
    // 计算最终时间统计
    const finalTime = totalTime;
    const averageTime = questionTimes.length > 0 ? Math.round(finalTime / questionTimes.length) : 0;
    
    finalScoreElement.textContent = score;
    finalTimeElement.textContent = formatTime(finalTime);
    averageTimeElement.textContent = formatTime(averageTime);
    
    // 显示昵称输入弹窗
    showNicknameModal();
}

// 重新开始游戏
function restartGame() {
    initGame();
}


// 测试拼音拼读功能
function testPinyinPronunciation() {
    const testPinyins = ['rì', 'yuè', 'shuǐ', 'huǒ', 'shān', 'mǎ', 'niǎo', 'huā'];
    const randomPinyin = testPinyins[Math.floor(Math.random() * testPinyins.length)];
    console.log('测试拼音:', randomPinyin);
    speakPinyin(randomPinyin);
}

// 事件监听器
restartBtn.addEventListener('click', restartGame);
playAgainBtn.addEventListener('click', restartGame);
newGameBtn.addEventListener('click', initGame);

// 设置相关事件监听器
settingsBtn.addEventListener('click', showSettings);
closeSettingsBtn.addEventListener('click', hideSettings);
saveSettingsBtn.addEventListener('click', applySettings);

// 昵称弹窗相关事件监听器
submitScoreBtn.addEventListener('click', submitScore);
skipSubmitBtn.addEventListener('click', () => {
    hideNicknameModal();
    showGameOverModal();
});

// 昵称输入框回车提交
nicknameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        submitScore();
    }
});

// 点击弹窗外部关闭昵称弹窗
nicknameModal.addEventListener('click', (e) => {
    if (e.target === nicknameModal) {
        hideNicknameModal();
        showGameOverModal();
    }
});

// 语速滑块实时更新显示
speechRateSlider.addEventListener('input', (e) => {
    rateValueDisplay.textContent = e.target.value;
});

// 点击弹窗外部关闭设置
settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        hideSettings();
    }
});

// 键盘支持
document.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R') {
        restartGame();
    }
});

// 页面加载完成后初始化游戏
document.addEventListener('DOMContentLoaded', async () => {
    loadSettings(); // 加载设置
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

// 反馈功能
async function submitFeedback() {
    if (!currentQuestion) {
        console.error('没有当前题目数据');
        return;
    }
    
    // 从图片路径中提取文件名
    const imagePath = currentQuestion.image;
    const imageFile = imagePath.split('/').pop();
    const character = currentQuestion.correctAnswer;
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                character: character,
                image_file: imageFile
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // 反馈提交成功
            feedbackBtn.classList.add('feedback-submitted');
            feedbackBtn.innerHTML = '<span class="feedback-icon">✅</span><span class="feedback-text">已反馈</span>';
            feedbackBtn.disabled = true;
            
            // 显示成功提示
            showFeedback('反馈已提交，感谢您的建议！', 'success');
        } else {
            // 反馈提交失败
            showFeedback('反馈提交失败，请稍后重试', 'error');
        }
    } catch (error) {
        console.error('提交反馈时出错:', error);
        showFeedback('网络错误，请检查网络连接', 'error');
    }
}

// 重置反馈按钮状态
function resetFeedbackButton() {
    feedbackBtn.classList.remove('feedback-submitted');
    feedbackBtn.innerHTML = '<span class="feedback-icon">⚠️</span><span class="feedback-text">反馈图字不匹配</span>';
    feedbackBtn.disabled = false;
}

// 反馈按钮事件监听
if (feedbackBtn) {
    feedbackBtn.addEventListener('click', submitFeedback);
}
