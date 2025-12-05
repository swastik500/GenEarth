// Chat functionality
let sessionId = null;
let currentLanguage = 'en';
let isQuizMode = false;

// Get elements
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const languageSelect = document.getElementById('languageSelect');
const quizStatus = document.getElementById('quizStatus');
const quizInfo = document.getElementById('quizInfo');
const voiceButton = document.getElementById('voiceButton');
const voiceStatus = document.getElementById('voiceStatus');

// Initialize
function init() {
    // Load language from URL or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    const savedLang = localStorage.getItem('ecomitra_language');
    
    currentLanguage = langParam || savedLang || 'en';
    languageSelect.value = currentLanguage;
    
    // Check for prefilled question
    const prefilledQuestion = localStorage.getItem('ecomitra_prefill_question');
    if (prefilledQuestion) {
        messageInput.value = prefilledQuestion;
        localStorage.removeItem('ecomitra_prefill_question');
        messageInput.focus();
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', handleKeyDown);
    languageSelect.addEventListener('change', handleLanguageChange);
    // Voice button
    if (voiceButton) {
        voiceButton.addEventListener('click', toggleVoiceInput);
        setupVoiceSupport();
    }
}

// Handle keyboard shortcuts
function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// Handle language change
function handleLanguageChange(e) {
    currentLanguage = e.target.value;
    localStorage.setItem('ecomitra_language', currentLanguage);
    
    // Add system message about language change
    const langNames = { en: 'English', hi: 'हिंदी', mr: 'मराठी', bn: 'বাংলা', ta: 'தமிழ்', te: 'తెలుగు', gu: 'ગુજરાતી' };
    addBotMessage(`Language changed to ${langNames[currentLanguage]}. I'll respond in this language from now on.`);
}

// Voice input using Web Speech API
let recognition = null;
let isRecognizing = false;

function setupVoiceSupport() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        voiceButton.style.display = 'none';
        return;
    }
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    updateRecognitionLang();

    recognition.onstart = () => {
        isRecognizing = true;
        voiceButton.classList.add('active');
        setVoiceStatus('Listening…');
    };
    recognition.onerror = (e) => {
        console.error('Voice error:', e);
        setVoiceStatus('Voice error. Try again.');
        stopRecognition();
    };
    recognition.onend = () => {
        isRecognizing = false;
        voiceButton.classList.remove('active');
        setVoiceStatus('Press mic to speak');
    };
    recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            if (result.isFinal) {
                finalTranscript += result[0].transcript;
            } else {
                interimTranscript += result[0].transcript;
            }
        }
        const text = (finalTranscript || interimTranscript).trim();
        messageInput.value = text;
        if (finalTranscript && finalTranscript.trim().length > 0) {
            // Auto-send when final result available
            sendMessage();
        }
    };
}

function updateRecognitionLang() {
    if (!recognition) return;
    const langMap = {
        en: 'en-IN',
        hi: 'hi-IN',
        mr: 'mr-IN',
        bn: 'bn-IN',
        ta: 'ta-IN',
        te: 'te-IN',
        gu: 'gu-IN'
    };
    recognition.lang = langMap[currentLanguage] || 'en-IN';
}

function toggleVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        setVoiceStatus('Voice not supported in this browser.');
        return;
    }
    if (!recognition) setupVoiceSupport();
    updateRecognitionLang();
    if (isRecognizing) {
        stopRecognition();
    } else {
        try {
            recognition.start();
        } catch (e) {
            // Ignore errors if already started
        }
    }
}

function stopRecognition() {
    if (recognition && isRecognizing) {
        try { recognition.stop(); } catch (_) {}
        isRecognizing = false;
        voiceButton.classList.remove('active');
    }
}

function setVoiceStatus(text) {
    if (voiceStatus) voiceStatus.textContent = `Press Enter to send • ${text}`;
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    messageInput.value = '';
    
    // Disable send button
    sendButton.disabled = true;
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                language: currentLanguage,
                session_id: sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Update session ID
        sessionId = data.session_id;
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Update quiz mode
        if (data.mode === 'quiz') {
            isQuizMode = true;
            updateQuizStatus(data.quiz_data);
        } else {
            isQuizMode = false;
            hideQuizStatus();
        }
        
        // Add bot response
        addBotMessage(data.reply);
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        addBotMessage('Sorry, I encountered an error. Please try again.');
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}

// Add user message to chat
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    // Convert markdown-style formatting to HTML
    const formattedText = formatBotMessage(text);
    
    messageDiv.innerHTML = `
        <div class="message-content">
            ${formattedText}
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Format bot message (simple markdown-like formatting)
function formatBotMessage(text) {
    // Escape HTML first
    text = escapeHtml(text);
    
    // Convert **bold** to <strong>
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert bullet points to lists
    const lines = text.split('\n');
    let html = '';
    let inList = false;
    
    for (let line of lines) {
        line = line.trim();
        
        if (line.startsWith('•') || line.startsWith('-')) {
            if (!inList) {
                html += '<ul>';
                inList = true;
            }
            html += `<li>${line.substring(1).trim()}</li>`;
        } else {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            if (line) {
                html += `<p>${line}</p>`;
            }
        }
    }
    
    if (inList) {
        html += '</ul>';
    }
    
    return html;
}

// Add typing indicator
function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = id;
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    return id;
}

// Remove typing indicator
function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

// Update quiz status
function updateQuizStatus(quizData) {
    if (quizData) {
        quizStatus.style.display = 'block';
        quizInfo.textContent = `Quiz Mode: Question ${quizData.question_num}/${quizData.total} | Score: ${quizData.score}`;
    }
}

// Hide quiz status
function hideQuizStatus() {
    quizStatus.style.display = 'none';
}

// Scroll to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Send quick message (from sidebar chips)
function sendQuickMessage(message) {
    messageInput.value = message;
    sendMessage();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
