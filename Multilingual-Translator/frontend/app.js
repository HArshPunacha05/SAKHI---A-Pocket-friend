// ===================================
// Application State
// ===================================
const state = {
    ws: null,
    roomId: null,
    userName: null,
    userLanguage: null,
    friendLanguage: null,
    isConnected: false,
    isListening: false,
    recognition: null,
    synthesis: window.speechSynthesis,
    conversationHistory: []
};

// ===================================
// DOM Elements
// ===================================
const elements = {
    // Setup screen
    setupScreen: document.getElementById('setupScreen'),
    userName: document.getElementById('userName'),
    userLanguage: document.getElementById('userLanguage'),
    friendLanguage: document.getElementById('friendLanguage'),
    roomId: document.getElementById('roomId'),
    generateRoomBtn: document.getElementById('generateRoomBtn'),
    startBtn: document.getElementById('startBtn'),

    // Voice screen
    voiceScreen: document.getElementById('voiceScreen'),
    currentUserName: document.getElementById('currentUserName'),
    currentUserLang: document.getElementById('currentUserLang'),
    currentRoomCode: document.getElementById('currentRoomCode'),
    userAvatar: document.getElementById('userAvatar'),
    leaveBtn: document.getElementById('leaveBtn'),

    // Voice interface
    micButton: document.getElementById('micButton'),
    micStatus: document.getElementById('micStatus'),
    originalText: document.getElementById('originalText'),
    translatedText: document.getElementById('translatedText'),
    historyList: document.getElementById('historyList'),
    audioPlayer: document.getElementById('audioPlayer'),

    // Status
    connectionStatus: document.getElementById('connectionStatus'),
    toastContainer: document.getElementById('toastContainer')
};

// ===================================
// Utility Functions
// ===================================
function generateRoomCode() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
}

function getInitials(name) {
    return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getLanguageName(code) {
    const langMap = {
        'en-US': 'English',
        'hi-IN': 'Hindi',
        'es-ES': 'Spanish',
        'fr-FR': 'French',
        'de-DE': 'German',
        'zh-CN': 'Chinese',
        'ja-JP': 'Japanese',
        'ar-SA': 'Arabic',
        'pt-PT': 'Portuguese',
        'ru-RU': 'Russian',
        'it-IT': 'Italian',
        'ko-KR': 'Korean',
        'ta-IN': 'Tamil',
        'te-IN': 'Telugu',
        'bn-IN': 'Bengali',
        'mr-IN': 'Marathi'
    };
    return langMap[code] || code;
}

function getLanguageCode(fullCode) {
    // Convert en-US to en for API
    return fullCode.split('-')[0];
}

// ===================================
// Toast Notifications
// ===================================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="flex: 1;">${message}</div>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 1.2rem;">×</button>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastSlide 0.3s reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// ===================================
// Speech Recognition Setup
// ===================================
function initializeSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        showToast('Speech recognition not supported in this browser. Please use Chrome or Edge.', 'error');
        return false;
    }

    state.recognition = new SpeechRecognition();
    state.recognition.continuous = false;
    state.recognition.interimResults = true;
    state.recognition.lang = state.userLanguage;

    state.recognition.onstart = () => {
        state.isListening = true;
        elements.micButton.classList.add('listening');
        elements.micStatus.querySelector('.status-text').textContent = '🎤 Listening...';
        elements.originalText.textContent = 'Listening...';
    };

    state.recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        if (interimTranscript) {
            elements.originalText.textContent = interimTranscript;
        }

        if (finalTranscript) {
            elements.originalText.textContent = finalTranscript;
            handleSpeechResult(finalTranscript);
        }
    };

    state.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        state.isListening = false;
        elements.micButton.classList.remove('listening');
        elements.micStatus.querySelector('.status-text').textContent = 'Tap to speak';

        if (event.error === 'no-speech') {
            showToast('No speech detected. Please try again.', 'error');
        } else if (event.error === 'not-allowed') {
            showToast('Microphone access denied. Please allow microphone access.', 'error');
        } else {
            showToast(`Error: ${event.error}`, 'error');
        }
    };

    state.recognition.onend = () => {
        state.isListening = false;
        elements.micButton.classList.remove('listening');
        elements.micStatus.querySelector('.status-text').textContent = 'Tap to speak';
    };

    return true;
}

// ===================================
// Speech Synthesis (Text-to-Speech)
// ===================================
function speakText(text, language) {
    if (!state.synthesis) {
        console.error('Speech synthesis not supported');
        return;
    }

    // Cancel any ongoing speech
    state.synthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    utterance.rate = 0.9;
    utterance.pitch = 1;

    // Try to find a voice for the language
    const voices = state.synthesis.getVoices();
    const voice = voices.find(v => v.lang.startsWith(getLanguageCode(language)));
    if (voice) {
        utterance.voice = voice;
    }

    utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
    };

    state.synthesis.speak(utterance);
}

// ===================================
// Translation
// ===================================
async function translateText(text, sourceLang, targetLang) {
    try {
        const response = await fetch('http://localhost:8000/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                source_lang: getLanguageCode(sourceLang),
                target_lang: getLanguageCode(targetLang)
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Translation API error:', errorText);
            throw new Error('Translation failed');
        }

        const result = await response.json();
        return result.translation;
    } catch (error) {
        console.error('Translation error:', error);
        showToast('Translation failed. Please try again.', 'error');
        return null;
    }
}

// ===================================
// Handle Speech Result
// ===================================
async function handleSpeechResult(text) {
    console.log('Speech result:', text);

    // Show translating status
    elements.translatedText.textContent = 'Translating...';

    // Translate the text
    const translation = await translateText(text, state.userLanguage, state.friendLanguage);

    if (translation) {
        // Display translation
        elements.translatedText.textContent = translation;

        // NOTE: Do NOT speak the translation here - it will be spoken on the friend's device
        // when they receive it via WebSocket

        // Add to history
        addToHistory(text, translation, state.userLanguage, state.friendLanguage);

        // Send via WebSocket to friend
        if (state.ws && state.ws.readyState === WebSocket.OPEN) {
            state.ws.send(JSON.stringify({
                type: 'voice_translation',
                original: text,
                translated: translation,
                sourceLang: state.userLanguage,
                targetLang: state.friendLanguage,
                speaker: state.userName
            }));
        }

        showToast('Translation sent!', 'success');
    }
}

// ===================================
// Conversation History
// ===================================
function addToHistory(original, translated, sourceLang, targetLang, isReceived = false) {
    // Remove empty state
    const emptyState = elements.historyList.querySelector('.history-empty');
    if (emptyState) {
        emptyState.remove();
    }

    const historyItem = document.createElement('div');
    historyItem.className = 'history-item';

    const time = formatTime(new Date());
    const direction = isReceived ? '📥 Received' : '📤 Sent';

    historyItem.innerHTML = `
        <div class="history-item-header">
            <span>${direction}</span>
            <span>${time}</span>
        </div>
        <div class="history-item-text">${isReceived ? translated : original}</div>
        <div class="history-item-translation">${isReceived ? original : translated}</div>
    `;

    elements.historyList.insertBefore(historyItem, elements.historyList.firstChild);

    // Keep only last 20 items
    while (elements.historyList.children.length > 20) {
        elements.historyList.removeChild(elements.historyList.lastChild);
    }

    // Store in state
    state.conversationHistory.unshift({
        original,
        translated,
        sourceLang,
        targetLang,
        time: new Date(),
        isReceived
    });
}

// ===================================
// WebSocket Connection
// ===================================
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/${state.roomId}`;

    try {
        state.ws = new WebSocket(wsUrl);

        state.ws.onopen = () => {
            console.log('WebSocket connected');
            state.isConnected = true;
            updateConnectionStatus('connected');
            showToast('Connected to room!', 'success');
        };

        state.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleIncomingMessage(data);
        };

        state.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            showToast('Connection error occurred', 'error');
        };

        state.ws.onclose = () => {
            console.log('WebSocket disconnected');
            state.isConnected = false;
            updateConnectionStatus('disconnected');
            showToast('Disconnected from room', 'error');
        };
    } catch (error) {
        console.error('Failed to create WebSocket:', error);
        showToast('Failed to connect. Please try again.', 'error');
    }
}

function handleIncomingMessage(data) {
    if (data.type === 'voice_translation') {
        console.log('Received translation:', data);

        // Add to history
        addToHistory(data.original, data.translated, data.sourceLang, data.targetLang, true);

        // Speak the received message in user's language
        speakText(data.translated, state.userLanguage);

        // Show notification
        showToast(`Message from ${data.speaker}`, 'info');
    }
}

function updateConnectionStatus(status) {
    const statusEl = elements.connectionStatus;
    const indicator = statusEl.querySelector('.status-indicator');
    const text = statusEl.querySelector('span');

    if (status === 'connected') {
        indicator.style.background = 'var(--success-color)';
        text.textContent = 'Connected';
    } else if (status === 'disconnected') {
        indicator.style.background = 'var(--error-color)';
        text.textContent = 'Disconnected';
    } else {
        indicator.style.background = 'var(--text-muted)';
        text.textContent = 'Ready';
    }
}

// ===================================
// Room Management
// ===================================
function startVoiceTranslation() {
    const userName = elements.userName.value.trim();
    const userLanguage = elements.userLanguage.value;
    const friendLanguage = elements.friendLanguage.value;
    const roomId = elements.roomId.value.trim().toUpperCase();

    // Validation
    if (!userName) {
        showToast('Please enter your name', 'error');
        elements.userName.focus();
        return;
    }

    if (!roomId) {
        showToast('Please enter or generate a room code', 'error');
        elements.roomId.focus();
        return;
    }

    if (userLanguage === friendLanguage) {
        showToast('Please select different languages for you and your friend', 'error');
        return;
    }

    // Store state
    state.userName = userName;
    state.userLanguage = userLanguage;
    state.friendLanguage = friendLanguage;
    state.roomId = roomId;

    // Initialize speech recognition
    if (!initializeSpeechRecognition()) {
        return;
    }

    // Update UI
    elements.currentUserName.textContent = userName;
    elements.currentUserLang.textContent = getLanguageName(userLanguage);
    elements.currentRoomCode.textContent = `Room: ${roomId}`;
    elements.userAvatar.textContent = getInitials(userName);

    // Switch screens
    elements.setupScreen.classList.add('hidden');
    elements.voiceScreen.classList.remove('hidden');

    // Connect WebSocket
    connectWebSocket();

    showToast('Voice translation ready! Tap the microphone to speak.', 'success');
}

function leaveRoom() {
    if (confirm('Are you sure you want to leave this room?')) {
        // Stop any ongoing speech
        if (state.recognition) {
            state.recognition.stop();
        }
        if (state.synthesis) {
            state.synthesis.cancel();
        }

        // Close WebSocket
        if (state.ws) {
            state.ws.close();
            state.ws = null;
        }

        // Reset state
        state.roomId = null;
        state.userName = null;
        state.userLanguage = null;
        state.friendLanguage = null;
        state.isConnected = false;
        state.isListening = false;
        state.conversationHistory = [];

        // Reset UI
        elements.originalText.textContent = 'Speak to start...';
        elements.translatedText.textContent = 'Translation will appear here...';
        elements.historyList.innerHTML = `
            <div class="history-empty">
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none" opacity="0.3">
                    <path d="M24 44C35.0457 44 44 35.0457 44 24C44 12.9543 35.0457 4 24 4C12.9543 4 4 12.9543 4 24C4 35.0457 12.9543 44 24 44Z" stroke="currentColor" stroke-width="3"/>
                    <path d="M24 14V24L30 30" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                </svg>
                <p>Your conversation will appear here</p>
            </div>
        `;

        // Switch screens
        elements.voiceScreen.classList.add('hidden');
        elements.setupScreen.classList.remove('hidden');

        updateConnectionStatus('ready');
        showToast('Left the room', 'info');
    }
}

// ===================================
// Microphone Control
// ===================================
function toggleMicrophone() {
    if (!state.recognition) {
        showToast('Speech recognition not initialized', 'error');
        return;
    }

    if (state.isListening) {
        state.recognition.stop();
    } else {
        try {
            state.recognition.start();
        } catch (error) {
            console.error('Failed to start recognition:', error);
            showToast('Failed to start microphone. Please try again.', 'error');
        }
    }
}

// ===================================
// Event Listeners
// ===================================
elements.generateRoomBtn.addEventListener('click', () => {
    elements.roomId.value = generateRoomCode();
});

elements.startBtn.addEventListener('click', startVoiceTranslation);

elements.leaveBtn.addEventListener('click', leaveRoom);

elements.micButton.addEventListener('click', toggleMicrophone);

// Allow starting with Enter key
elements.roomId.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        startVoiceTranslation();
    }
});

elements.userName.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        elements.userLanguage.focus();
    }
});

// ===================================
// Initialization
// ===================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('VoiceBridge initialized');

    // Auto-generate room code
    elements.roomId.value = generateRoomCode();

    // Load voices for speech synthesis
    if (state.synthesis) {
        state.synthesis.onvoiceschanged = () => {
            console.log('Voices loaded:', state.synthesis.getVoices().length);
        };
    }

    // Check for speech recognition support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        showToast('⚠️ Speech recognition not supported. Please use Chrome or Edge browser.', 'error');
    }
});

// ===================================
// Cleanup on page unload
// ===================================
window.addEventListener('beforeunload', () => {
    if (state.ws) {
        state.ws.close();
    }
    if (state.recognition) {
        state.recognition.stop();
    }
    if (state.synthesis) {
        state.synthesis.cancel();
    }
});
