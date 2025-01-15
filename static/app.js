// Global state
let messages = [];
let currentToken = null;

// Get base path from current URL
const basePath = window.location.pathname.replace(/\/$/, '');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check URL parameters for token
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
        document.getElementById('token').value = token;
        setToken();
    }

    // Add enter key handler for message input
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});

// Set token and initialize chat
async function setToken() {
    const tokenInput = document.getElementById('token');
    const token = tokenInput.value.trim();
    
    if (token.length !== 8) {
        showError('Token must be 8 characters long');
        return;
    }

    try {
        const response = await fetch(`${basePath}/user/stats/${token}`);
        if (!response.ok) {
            throw new Error(await response.text());
        }
        
        const userData = await response.json();
        currentToken = token;
        
        // Update UI
        updateUserStats(userData);
        document.getElementById('tokenInput').classList.add('hidden');
        document.getElementById('userStats').classList.remove('hidden');
        document.getElementById('chatInterface').classList.remove('hidden');
        
        // Add token to URL without reloading
        const url = new URL(window.location);
        url.searchParams.set('token', token);
        window.history.pushState({}, '', url);
    } catch (error) {
        showError('Invalid token or server error');
        console.error('Error:', error);
    }
}

// Send message
async function sendMessage() {
    if (!currentToken) {
        showError('Please set your token first');
        return;
    }

    const messageInput = document.getElementById('messageInput');
    const content = messageInput.value.trim();
    if (!content) return;

    const isProMode = document.getElementById('reasoningEffort').checked;
    const reasoningEffort = isProMode ? "high" : "medium";
    
    // Add user message to UI
    addMessage('user', content);
    messageInput.value = '';
    
    // Show loading state
    const loadingMessage = addLoadingMessage();
    
    try {
        const response = await fetch(`${basePath}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: [...messages, { role: 'user', content }],
                token: currentToken,
                reasoning_effort: reasoningEffort
            })
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();
        
        // Remove loading message
        loadingMessage.remove();
        
        // Add assistant message
        addMessage('assistant', data.content, data);
        
        // Update stats
        updateLastMessageInfo(data);
        await updateUserStats();
    } catch (error) {
        loadingMessage.remove();
        showError('Failed to send message: ' + error.message);
        console.error('Error:', error);
    }
}

// UI Helper functions
function formatThinkingTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    if (minutes > 0) {
        return `${minutes} min ${remainingSeconds} sec`;
    }
    return `${remainingSeconds} sec`;
}

function addMessage(role, content, data = null) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    if (role === 'assistant' && data) {
        // Add thinking time as a separate element
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'text-sm text-gray-500 mb-1';
        const thinkingTime = formatThinkingTime(data.thinking_time);
        const isProMode = document.getElementById('reasoningEffort').checked;
        thinkingDiv.textContent = `Thinking for ${thinkingTime}${isProMode ? ' (Pro Mode)' : ''}`;
        messageDiv.appendChild(thinkingDiv);
        
        // Add the actual message content
        const contentDiv = document.createElement('div');
        contentDiv.textContent = content;
        messageDiv.appendChild(contentDiv);
    } else {
        messageDiv.textContent = content;
    }
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Add to messages array
    messages.push({ role, content });
}

function addLoadingMessage() {
    const messagesDiv = document.getElementById('messages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant-message';
    loadingDiv.innerHTML = '<div class="loading"></div>';
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return loadingDiv;
}

function showError(message) {
    const container = document.querySelector('.container');
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    container.insertBefore(errorDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => errorDiv.remove(), 5000);
}

async function updateUserStats(userData) {
    if (!userData) {
        try {
            const response = await fetch(`${basePath}/user/stats/${currentToken}`);
            if (!response.ok) throw new Error('Failed to fetch user stats');
            userData = await response.json();
        } catch (error) {
            console.error('Error updating user stats:', error);
            return;
        }
    }
    
    document.getElementById('userName').textContent = userData.name;
    document.getElementById('totalCost').textContent = `$${userData.total_cost.toFixed(4)}`;
}

function updateLastMessageInfo(data) {
    const infoDiv = document.getElementById('lastMessageInfo');
    infoDiv.classList.remove('hidden');
    document.getElementById('lastTokens').textContent = 
        `Input: ${data.prompt_tokens}, Reasoning: ${data.reasoning_tokens}, Output: ${data.completion_tokens}`;
    document.getElementById('lastCost').textContent = data.cost.toFixed(6);
} 