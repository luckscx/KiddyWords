// 游戏数据 - 从API获取
let gameData = [];

// 游戏状态
let currentQuestionIndex = 0;
let score = 0;
let gameActive = true;
let currentQuestion = null; // 当前题目数据
let gameType = 'letter_recognition'; // 游戏类型
let difficulty = 'easy'; // 难度

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

// 游戏控制相关DOM元素
const gameTypeSelect = document.getElementById('game-type-select');
const difficultySelect = document.getElementById('difficulty-select');
const newGameBtn = document.getElementById('new-game-btn');

// 字母信息显示相关DOM元素
const pronunciationDisplay = document.getElementById('pronunciation-display');
const phoneticDisplay = document.getElementById('phonetic-display');
const wordsDisplay = document.getElementById('words-display');
const wordsList = document.getElementById('words-list');
const feedbackBtn = document.getElementById('feedback-btn');

// 设置相关DOM元素
const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const speechRateSlider = document.getElementById('speech-rate');
const rateValueDisplay = document.getElementById('rate-value');
const readWordsCheckbox = document.getElementById('read-words');
const readWordsStartCheckbox = document.getElementById('read-words-start');
const readLetterStartCheckbox = document.getElementById('read-letter-start');
const autoPlayCheckbox = document.getElementById('auto-play');
const testVoiceBtn = document.getElementById('test-voice');
const saveSettingsBtn = document.getElementById('save-settings');
const closeSettingsBtn = document.getElementById('close-settings');

// 字母歌相关DOM元素
const abcSongBtn = document.getElementById('abc-song-btn');
const abcSongModal = document.getElementById('abc-song-modal');
const songLyrics = document.getElementById('song-lyrics');
const alphabetDisplay = document.getElementById('alphabet-display');
const playSongBtn = document.getElementById('play-song');
const closeSongBtn = document.getElementById('close-song');

// 音频上下文
let audioContext = null;

// 设置相关变量
let gameSettings = {
    speechRate: 0.7,
    readWords: true,
    readWordsStart: true,
    readLetterStart: true,
    autoPlay: true
};

// 初始化音频上下文
function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
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
        console.log(`第${questionTimes.length}题用时: ${questionTime}ms, 累计总时间: ${totalTime}ms`);
        questionStartTime = 0;
        return questionTime;
    }
    console.log('停止计时器时 questionStartTime 为 0');
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
    const savedSettings = localStorage.getItem('english-alphabet-settings');
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
        localStorage.setItem('english-alphabet-settings', JSON.stringify(gameSettings));
        console.log('设置已保存');
    } catch (e) {
        console.error('保存设置失败:', e);
    }
}

function updateSettingsUI() {
    speechRateSlider.value = gameSettings.speechRate;
    rateValueDisplay.textContent = gameSettings.speechRate;
    readWordsCheckbox.checked = gameSettings.readWords;
    readWordsStartCheckbox.checked = gameSettings.readWordsStart;
    readLetterStartCheckbox.checked = gameSettings.readLetterStart;
    autoPlayCheckbox.checked = gameSettings.autoPlay;
}

function showSettings() {
    settingsModal.classList.add('show');
}

function hideSettings() {
    settingsModal.classList.remove('show');
}

function applySettings() {
    gameSettings.speechRate = parseFloat(speechRateSlider.value);
    gameSettings.readWords = readWordsCheckbox.checked;
    gameSettings.readWordsStart = readWordsStartCheckbox.checked;
    gameSettings.readLetterStart = readLetterStartCheckbox.checked;
    gameSettings.autoPlay = autoPlayCheckbox.checked;
    saveSettings();
    hideSettings();
}

// 获取最佳英语语音
function getBestEnglishVoice() {
    const voices = speechSynthesis.getVoices();
    
    // 优先选择的声音列表（按优先级排序）
    const preferredVoices = [
        'Google UK English Female',
        'Google UK English Male', 
        'Google US English Female',
        'Google US English Male',
        'Microsoft Zira Desktop - English (United States)',
        'Microsoft David Desktop - English (United States)',
        'Microsoft Hazel Desktop - English (Great Britain)',
        'Microsoft Susan Desktop - English (Great Britain)',
        'Alex',
        'Samantha',
        'Victoria',
        'Daniel'
    ];
    
    // 首先尝试找到优先声音
    for (const preferredName of preferredVoices) {
        const voice = voices.find(v => v.name === preferredName);
        if (voice) {
            console.log(`使用优先声音: ${voice.name}`);
            return voice;
        }
    }
    
    // 如果没有优先声音，选择任何英语声音
    const englishVoices = voices.filter(voice => 
        voice.lang.startsWith('en') && 
        !voice.name.includes('Enhanced') && // 避免增强版声音
        !voice.name.includes('Premium')     // 避免高级版声音
    );
    
    if (englishVoices.length > 0) {
        // 优先选择女性声音（通常更适合儿童）
        const femaleVoice = englishVoices.find(voice => 
            voice.name.toLowerCase().includes('female') ||
            voice.name.toLowerCase().includes('woman') ||
            voice.name.toLowerCase().includes('girl')
        );
        
        if (femaleVoice) {
            console.log(`使用女性英语声音: ${femaleVoice.name}`);
            return femaleVoice;
        }
        
        console.log(`使用英语声音: ${englishVoices[0].name}`);
        return englishVoices[0];
    }
    
    console.log('未找到合适的英语声音，使用默认声音');
    return null;
}

// 使用浏览器语音合成播放英语
function speakEnglish(text, lang = 'en-US') {
    if ('speechSynthesis' in window) {
        // 停止当前播放
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang;
        utterance.rate = gameSettings.speechRate;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // 获取最佳英语声音
        const bestVoice = getBestEnglishVoice();
        if (bestVoice) {
            utterance.voice = bestVoice;
        }
        
        // 添加语音事件监听
        utterance.onstart = function() {
            console.log(`开始播放: ${text}`);
        };
        
        utterance.onend = function() {
            console.log(`播放完成: ${text}`);
        };
        
        utterance.onerror = function(event) {
            console.error(`语音播放错误: ${event.error}`);
        };
        
        // 播放
        window.speechSynthesis.speak(utterance);
    } else {
        console.error('很抱歉，您的浏览器不支持语音合成！');
    }
}

// 语音测试功能
function testEnglishVoice() {
    const testWords = ['Apple', 'Ball', 'Cat', 'Dog', 'Elephant'];
    const randomWord = testWords[Math.floor(Math.random() * testWords.length)];
    
    console.log(`测试英语发音: ${randomWord}`);
    speakEnglish(randomWord);
}

// 获取所有可用的英语声音列表
function getAvailableVoices() {
    const voices = speechSynthesis.getVoices();
    const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
    
    console.log('可用的英语声音:');
    englishVoices.forEach((voice, index) => {
        console.log(`${index + 1}. ${voice.name} (${voice.lang})`);
    });
    
    return englishVoices;
}

// 显示相关单词
function displayWords(words) {
    if (!words || words.length === 0) {
        return;
    }
    
    // 清空现有单词
    wordsList.innerHTML = '';
    
    // 创建单词元素
    words.forEach((word, index) => {
        const wordElement = document.createElement('div');
        wordElement.className = 'word-item';
        wordElement.textContent = word;
        wordElement.dataset.index = index;
        wordsList.appendChild(wordElement);
    });
    
    // 显示单词区域
    wordsDisplay.style.display = 'flex';
}

// 隐藏单词显示
function hideWords() {
    wordsDisplay.style.display = 'none';
    wordsList.innerHTML = '';
}

// 高亮当前单词
function highlightCurrentWord(index) {
    // 移除所有高亮
    const wordItems = wordsList.querySelectorAll('.word-item');
    wordItems.forEach((item, i) => {
        item.classList.remove('current');
        if (i < index) {
            item.classList.add('completed');
        }
    });
    
    // 高亮当前单词
    if (index < wordItems.length) {
        wordItems[index].classList.add('current');
    }
}

// 按顺序朗读单词（用于游戏开始时）
function speakWordsSequentially(words, callback) {
    if (!words || words.length === 0) {
        if (callback) callback();
        return;
    }
    
    let currentIndex = 0;
    
    function speakNext() {
        if (currentIndex >= words.length) {
            // 所有单词读完后，标记最后一个为完成状态
            highlightCurrentWord(words.length);
            if (callback) callback();
            return;
        }
        
        const word = words[currentIndex];
        console.log('朗读单词:', word);
        
        // 高亮当前单词
        highlightCurrentWord(currentIndex);
        
        // 创建语音实例
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        utterance.rate = gameSettings.speechRate;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // 使用最佳英语声音
        const bestVoice = getBestEnglishVoice();
        if (bestVoice) {
            utterance.voice = bestVoice;
        }
        
        // 播放完成后继续下一个
        utterance.onend = function() {
            currentIndex++;
            // 添加短暂延迟，让单词之间有间隔
            setTimeout(speakNext, 300);
        };
        
        // 播放
        window.speechSynthesis.speak(utterance);
    }
    
    speakNext();
}

// 按顺序朗读单词（用于答题正确后）
function speakWords(words, callback) {
    if (!words || words.length === 0) {
        if (callback) callback();
        return;
    }
    
    // 显示单词
    displayWords(words);
    
    let currentIndex = 0;
    
    function speakNext() {
        if (currentIndex >= words.length) {
            // 所有单词读完后，标记最后一个为完成状态
            highlightCurrentWord(words.length);
            if (callback) callback();
            return;
        }
        
        const word = words[currentIndex];
        console.log('朗读单词:', word);
        
        // 高亮当前单词
        highlightCurrentWord(currentIndex);
        
        // 创建语音实例
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        utterance.rate = gameSettings.speechRate;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // 使用最佳英语声音
        const bestVoice = getBestEnglishVoice();
        if (bestVoice) {
            utterance.voice = bestVoice;
        }
        
        // 播放完成后继续下一个
        utterance.onend = function() {
            currentIndex++;
            // 添加短暂延迟，让单词之间有间隔
            setTimeout(speakNext, 300);
        };
        
        // 播放
        window.speechSynthesis.speak(utterance);
    }
    
    speakNext();
}

// 生成正确音效
function playCorrectSound() {
    if (!gameSettings.autoPlay) return;
    
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
    if (!gameSettings.autoPlay) return;
    
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

// 初始化游戏
async function initGame() {
    // 清除自动切换定时器
    if (timeUpdateInterval) {
        clearInterval(timeUpdateInterval);
        timeUpdateInterval = null;
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
    
    // 获取游戏类型和难度
    gameType = gameTypeSelect.value;
    difficulty = difficultySelect.value;
    
    // 从API获取游戏数据
    try {
        const response = await fetch('/api/english/game/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                game_type: gameType,
                difficulty: difficulty
            })
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
    
    // 显示发音和音标
    pronunciationDisplay.textContent = `发音: ${question.pronunciation}`;
    phoneticDisplay.textContent = `音标: ${question.phonetic}`;
    
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
    hideWords(); // 隐藏单词显示区域
    resetFeedbackButton(); // 重置反馈按钮
    gameActive = true;
    
    // 开始计时
    startQuestionTimer();
    
    // 启动定时器实时更新时间显示
    if (timeUpdateInterval) {
        clearInterval(timeUpdateInterval);
    }
    timeUpdateInterval = setInterval(updateTotalTime, 100); // 每100ms更新一次
    
    // 根据设置决定是否朗读字母和关联单词
    if (gameSettings.readLetterStart) {
        setTimeout(() => {
            // 先朗读字母
            speakEnglish(question.correctAnswer);
            
            setTimeout(() => {
                const firstWord = question.words[0];
                speakEnglish(firstWord);

            }, 1500); // 字母读完后1.5秒开始读单词
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
        
        // 视觉反馈
        buttonElement.classList.add('correct');
        showFeedback('真棒！答对了！🎉 正在朗读相关单词...', 'correct');
        
        // 播放正确音效
        playCorrectSound();
        
        // 禁用所有按钮
        disableAllOptions();
        
        // 延迟播放字母发音，然后朗读相关单词
        setTimeout(() => {
            speakEnglish(question.correctAnswer);
            
            // 字母读完后朗读相关单词
            setTimeout(() => {
                if (gameSettings.readWords && question.words && question.words.length > 0) {
                    speakWords(question.words, () => {
                        // 所有单词读完后隐藏单词显示区域
                        hideWords();
                        showFeedback('朗读完成！准备下一题...', 'correct');
                        // 自动切换到下一题
                        setTimeout(() => {
                            nextQuestion();
                        }, 1500);
                    });
                } else {
                    // 没有相关单词或设置不朗读，直接切换到下一题
                    setTimeout(() => {
                        nextQuestion();
                    }, 1500);
                }
            }, 2000); // 等待字母朗读完成
        }, 800);
        
    } else {
        // 错误答案 - 不停止计时器，让用户继续答题
        buttonElement.classList.add('wrong');
        showFeedback('再试试看！', 'wrong');
        
        // 播放错误音效
        playWrongSound();

        // 重新启用游戏状态，让用户可以继续选择
        setTimeout(() => {
            gameActive = true;
            // 重置按钮状态
            buttonElement.classList.remove('wrong');
        }, 1000);
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

// 下一题
function nextQuestion() {
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
    
    // 确保停止当前题目的计时器
    if (questionStartTime > 0) {
        const finalQuestionTime = stopQuestionTimer();
        console.log('游戏结束时停止最后一题计时器，用时:', finalQuestionTime, 'ms');
    }
    
    // 计算最终时间统计
    const finalTime = totalTime;
    const averageTime = questionTimes.length > 0 ? Math.round(finalTime / questionTimes.length) : 0;
    
    console.log('游戏结束统计 - 总分:', score, '总时间:', finalTime, 'ms', '平均时间:', averageTime, 'ms', '答题次数:', questionTimes.length);
    
    finalScoreElement.textContent = score;
    finalTimeElement.textContent = formatTime(finalTime);
    averageTimeElement.textContent = formatTime(averageTime);
    
    // 显示游戏结束弹窗
    showGameOverModal();
}

// 显示游戏结束弹窗
function showGameOverModal() {
    gameOverModal.classList.add('show');
}

// 重新开始游戏
function restartGame() {
    initGame();
}

// 字母歌功能
async function loadAbcSong() {
    try {
        const response = await fetch('/api/english/abc-song');
        const data = await response.json();
        
        // 显示歌词
        songLyrics.textContent = data.song_lyrics;
        
        // 显示字母
        alphabetDisplay.innerHTML = '';
        data.alphabet.forEach(letter => {
            const letterElement = document.createElement('button');
            letterElement.className = 'alphabet-letter';
            letterElement.textContent = letter.letter;
            letterElement.onclick = () => speakEnglish(letter.letter);
            alphabetDisplay.appendChild(letterElement);
        });
    } catch (error) {
        console.error('加载字母歌失败:', error);
    }
}

function showAbcSong() {
    abcSongModal.classList.add('show');
    loadAbcSong();
}

function hideAbcSong() {
    abcSongModal.classList.remove('show');
}

function playAbcSong() {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const letters = alphabet.split('');
    
    let currentIndex = 0;
    
    function playNext() {
        if (currentIndex >= letters.length) {
            return;
        }
        
        const letter = letters[currentIndex];
        
        // 高亮当前字母
        const letterElements = alphabetDisplay.querySelectorAll('.alphabet-letter');
        letterElements.forEach((el, i) => {
            el.classList.remove('playing');
            if (i === currentIndex) {
                el.classList.add('playing');
            }
        });
        
        // 播放字母发音
        speakEnglish(letter);
        
        currentIndex++;
        
        // 延迟播放下一个字母
        setTimeout(playNext, 1000);
    }
    
    playNext();
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
    const letter = currentQuestion.correctAnswer;
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                character: letter,
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
            showFeedback('反馈已提交，感谢您的建议！', 'correct');
        } else {
            // 反馈提交失败
            showFeedback('反馈提交失败，请稍后重试', 'wrong');
        }
    } catch (error) {
        console.error('提交反馈时出错:', error);
        showFeedback('网络错误，请检查网络连接', 'wrong');
    }
}

// 重置反馈按钮状态
function resetFeedbackButton() {
    feedbackBtn.classList.remove('feedback-submitted');
    feedbackBtn.innerHTML = '<span class="feedback-icon">⚠️</span><span class="feedback-text">反馈图字不匹配</span>';
    feedbackBtn.disabled = false;
}

// 事件监听器
restartBtn.addEventListener('click', restartGame);
playAgainBtn.addEventListener('click', restartGame);
newGameBtn.addEventListener('click', initGame);

// 设置相关事件监听器
settingsBtn.addEventListener('click', showSettings);
closeSettingsBtn.addEventListener('click', hideSettings);
saveSettingsBtn.addEventListener('click', applySettings);
testVoiceBtn.addEventListener('click', testEnglishVoice);

// 字母歌相关事件监听器
abcSongBtn.addEventListener('click', showAbcSong);
closeSongBtn.addEventListener('click', hideAbcSong);
playSongBtn.addEventListener('click', playAbcSong);

// 反馈按钮事件监听
if (feedbackBtn) {
    feedbackBtn.addEventListener('click', submitFeedback);
}

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

// 点击弹窗外部关闭字母歌
abcSongModal.addEventListener('click', (e) => {
    if (e.target === abcSongModal) {
        hideAbcSong();
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
    
    // 初始化语音系统
    initVoiceSystem();
    
    // 检查是否有弹窗显示，如果没有才自动开始游戏
    const hasModalOpen = document.querySelector('.modal.show') || 
                        document.querySelector('.game-over-modal.show');
    
    if (!hasModalOpen) {
        await initGame();
    } else {
        console.log('检测到弹窗打开，跳过自动开始游戏');
    }
});

// 初始化语音系统
function initVoiceSystem() {
    // 等待语音列表加载完成
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = function() {
            console.log('语音列表已加载');
            getAvailableVoices();
        };
    } else {
        // 如果onvoiceschanged不可用，延迟获取声音列表
        setTimeout(() => {
            console.log('延迟获取语音列表');
            getAvailableVoices();
        }, 1000);
    }
}

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
