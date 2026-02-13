const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const newSessionBtn = document.getElementById('new-session-btn');
const sessionsList = document.getElementById('sessions-list');
const chatTitle = document.getElementById('chat-title');
const sessionIdDisplay = document.getElementById('session-id-display');

let currentSessionId = null;

document.addEventListener('DOMContentLoaded', () => {
    loadSessions();
});

messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
});

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);
newSessionBtn.addEventListener('click', startNewSession);

function startNewSession() {
    currentSessionId = null;
    chatTitle.textContent = 'New Conversation';
    sessionIdDisplay.textContent = '';
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <p>👋 Welcome! I'm your Library Desk Agent.</p>
            <p>I can help you with:</p>
            <ul>
                <li>🔍 Finding books by title or author</li>
                <li>🛒 Creating orders</li>
                <li>📦 Restocking books</li>
                <li>💰 Updating prices</li>
                <li>📋 Checking order status</li>
                <li>📊 Viewing inventory</li>
            </ul>
        </div>
    `;
    
    document.querySelectorAll('.session-item').forEach(el => el.classList.remove('active'));
    messageInput.focus();
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();

    appendMessage('user', message);
    messageInput.value = '';
    messageInput.style.height = 'auto';

    const typingEl = showTyping();

    sendBtn.disabled = true;
    messageInput.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to send message');
        }

        const data = await response.json();
        
        if (!currentSessionId) {
            currentSessionId = data.session_id;
            sessionIdDisplay.textContent = `Session: ${currentSessionId.slice(0, 8)}...`;
            chatTitle.textContent = message.slice(0, 40) + (message.length > 40 ? '...' : '');
        }

        typingEl.remove();

        if (data.tool_calls && data.tool_calls.length > 0) {
            data.tool_calls.forEach(tc => {
                appendToolCall(tc.name, tc.args);
            });
        }

        if (data.response) {
            appendMessage('assistant', data.response);
        }

        loadSessions();
    } catch (error) {
        typingEl.remove();
        appendMessage('assistant', `⚠️ Error: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

function appendMessage(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    
    let formatted = escapeHtml(content);
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
    formatted = formatted.replace(/\n/g, '<br>');
    
    div.innerHTML = formatted;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendToolCall(name, args) {
    const div = document.createElement('div');
    div.className = 'tool-indicator';
    div.innerHTML = `<span class="tool-icon">🔧</span> Called <strong>${escapeHtml(name)}</strong>(${escapeHtml(JSON.stringify(args))})`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const sessions = await response.json();
        
        if (sessions.length === 0) {
            sessionsList.innerHTML = '<p class="muted">No sessions yet</p>';
            return;
        }
        
        sessionsList.innerHTML = '';
        sessions.forEach(session => {
            const div = document.createElement('div');
            div.className = `session-item ${session.session_id === currentSessionId ? 'active' : ''}`;
            div.innerHTML = `
                <div class="session-preview">💬 Chat (${session.message_count} msgs)</div>
                <div class="session-date">${new Date(session.started).toLocaleDateString()}</div>
            `;
            div.addEventListener('click', () => loadSession(session.session_id));
            sessionsList.appendChild(div);
        });
    } catch (error) {
        console.error('Failed to load sessions:', error);
    }
}

async function loadSession(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}/messages`);
        const messages = await response.json();
        
        currentSessionId = sessionId;
        sessionIdDisplay.textContent = `Session: ${sessionId.slice(0, 8)}...`;
        
        const firstUserMsg = messages.find(m => m.role === 'user');
        chatTitle.textContent = firstUserMsg 
            ? firstUserMsg.content.slice(0, 40) + (firstUserMsg.content.length > 40 ? '...' : '')
            : 'Conversation';
        
        chatMessages.innerHTML = '';
        messages.forEach(msg => {
            if (msg.role === 'user' || msg.role === 'assistant') {
                appendMessage(msg.role, msg.content);
            }
        });
        
        document.querySelectorAll('.session-item').forEach(el => el.classList.remove('active'));
        event.currentTarget.classList.add('active');
    } catch (error) {
        console.error('Failed to load session:', error);
    }
}