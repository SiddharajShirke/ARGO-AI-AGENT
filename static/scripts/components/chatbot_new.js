/**
 * Chatbot Component
 * AI-powered conversational interface for ocean data analysis
 */
const ChatbotComponent = {
    title: 'AI Assistant',
    messages: [],
    isTyping: false,
    websocket: null,
    maxMessages: 100,

    render() {
        return `
            <div class="chatbot-page">
                <!-- Chat Header -->
                <div class="chat-header">
                    <div class="chat-title">
                        <h1>🤖 AI Assistant</h1>
                        <p>Ask questions about ARGO ocean data and get intelligent insights</p>
                    </div>
                    <div class="chat-controls">
                        <button class="btn btn-outline" onclick="chatbot.clearChat()">
                            🗑️ Clear Chat
                        </button>
                        <button class="btn btn-outline" onclick="chatbot.exportChat()">
                            📤 Export
                        </button>
                        <div class="chat-status" id="chat-status">
                            <span class="status-indicator" id="ai-status-indicator"></span>
                            <span id="ai-status-text">AI Online</span>
                        </div>
                    </div>
                </div>
                
                <!-- Chat Container -->
                <div class="chat-container" id="chat-container">
                    <div class="chat-messages" id="chat-messages">
                        <!-- Welcome Message -->
                        <div class="message bot-message">
                            <div class="message-avatar">🤖</div>
                            <div class="message-content">
                                <div class="message-text">
                                    <p>Hello! I'm your AI assistant for oceanographic data analysis. 
                                    I can help you explore ARGO float profiles, analyze trends, 
                                    and answer questions about the Indian Ocean data.</p>
                                    
                                    <div class="welcome-examples">
                                        <h4>Try asking me:</h4>
                                        <div class="example-queries">
                                            <button class="example-query" onclick="chatbot.sendExample('Show me temperature profiles in the Arabian Sea')">
                                                🌡️ "Temperature profiles in Arabian Sea"
                                            </button>
                                            <button class="example-query" onclick="chatbot.sendExample('What are the latest salinity trends in Bay of Bengal?')">
                                                🧂 "Salinity trends in Bay of Bengal"
                                            </button>
                                            <button class="example-query" onclick="chatbot.sendExample('Find ARGO profiles near 10°N, 80°E')">
                                                📍 "Find profiles near coordinates"
                                            </button>
                                            <button class="example-query" onclick="chatbot.sendExample('Analyze seasonal variations in the equatorial Indian Ocean')">
                                                📊 "Seasonal variations analysis"
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div class="message-time">${utils.formatTime(new Date())}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Typing Indicator -->
                    <div class="typing-indicator" id="typing-indicator" style="display: none;">
                        <div class="message bot-message">
                            <div class="message-avatar">🤖</div>
                            <div class="message-content">
                                <div class="typing-animation">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Chat Input -->
                <div class="chat-input-container">
                    <div class="chat-input-wrapper">
                        <textarea 
                            id="message-input" 
                            class="chat-input" 
                            placeholder="Ask me about ocean data, ARGO profiles, or oceanographic trends..."
                            rows="1"
                            maxlength="2000"
                        ></textarea>
                        <div class="input-actions">
                            <button class="btn btn-icon" onclick="chatbot.toggleVoiceInput()" title="Voice Input">
                                🎤
                            </button>
                            <button class="btn btn-icon" onclick="chatbot.attachFile()" title="Attach File">
                                📎
                            </button>
                            <button 
                                id="send-button" 
                                class="btn btn-primary" 
                                onclick="chatbot.sendMessage()"
                                disabled
                            >
                                📤 Send
                            </button>
                        </div>
                    </div>
                    <div class="input-info">
                        <span class="char-count" id="char-count">0/2000</span>
                        <span class="input-hint">Press Ctrl+Enter to send</span>
                    </div>
                </div>
                
                <!-- Suggestions Panel -->
                <div class="suggestions-panel" id="suggestions-panel" style="display: none;">
                    <h4>💡 Quick Suggestions</h4>
                    <div class="suggestion-buttons" id="suggestion-buttons">
                        <!-- Dynamic suggestions will be added here -->
                    </div>
                </div>
            </div>
        `;
    },

    async init() {
        console.log('🤖 Initializing Chatbot Component');

        // Setup event listeners
        this.setupEventListeners();

        // Load previous messages
        await this.loadMessageHistory();

        // Initialize WebSocket connection
        this.initializeWebSocket();

        // Check for pending query from navigation
        this.checkPendingQuery();

        // Update AI status
        this.updateAIStatus();
    },

    setupEventListeners() {
        // Message input handling
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');

        if (messageInput) {
            messageInput.addEventListener('input', (e) => {
                this.handleInputChange(e);
            });

            messageInput.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    this.sendMessage();
                } else if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Auto-resize textarea
            messageInput.addEventListener('input', () => {
                messageInput.style.height = 'auto';
                messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
            });
        }

        // Focus input when component loads
        setTimeout(() => {
            if (messageInput) messageInput.focus();
        }, 100);
    },

    handleInputChange(e) {
        const input = e.target;
        const sendButton = document.getElementById('send-button');
        const charCount = document.getElementById('char-count');

        const length = input.value.length;

        // Update character count
        if (charCount) {
            charCount.textContent = `${length}/2000`;
            charCount.className = length > 1800 ? 'char-count warning' : 'char-count';
        }

        // Enable/disable send button
        if (sendButton) {
            sendButton.disabled = length === 0 || this.isTyping;
        }

        // Show/hide suggestions
        this.updateSuggestions(input.value);
    },

    updateSuggestions(inputText) {
        const suggestionsPanel = document.getElementById('suggestions-panel');
        const suggestionsContainer = document.getElementById('suggestion-buttons');

        if (!suggestionsPanel || !suggestionsContainer) return;

        if (inputText.length < 3) {
            suggestionsPanel.style.display = 'none';
            return;
        }

        const suggestions = this.generateSuggestions(inputText);

        if (suggestions.length > 0) {
            suggestionsContainer.innerHTML = suggestions
                .map(suggestion => `
                    <button class="suggestion-btn" onclick="chatbot.applySuggestion('${suggestion.replace(/'/g, "\\'")}')">
                        ${suggestion}
                    </button>
                `).join('');
            suggestionsPanel.style.display = 'block';
        } else {
            suggestionsPanel.style.display = 'none';
        }
    },

    generateSuggestions(inputText) {
        const suggestions = [];
        const keywords = inputText.toLowerCase().split(/\s+/);

        const suggestionTemplates = [
            { keywords: ['temperature', 'temp'], suggestion: 'Show temperature profiles for the Arabian Sea' },
            { keywords: ['salinity', 'salt'], suggestion: 'Analyze salinity trends in the Bay of Bengal' },
            { keywords: ['profile', 'profiles'], suggestion: 'Find ARGO profiles from the last 30 days' },
            { keywords: ['depth', 'deep'], suggestion: 'Show deep water measurements below 1000m' },
            { keywords: ['trend', 'trends'], suggestion: 'What are the recent oceanographic trends?' },
            { keywords: ['arabian', 'sea'], suggestion: 'Analyze Arabian Sea upwelling patterns' },
            { keywords: ['bay', 'bengal'], suggestion: 'Explore Bay of Bengal freshwater influence' },
            { keywords: ['equatorial'], suggestion: 'Study equatorial Indian Ocean dynamics' },
            { keywords: ['lat', 'lon', 'coordinate'], suggestion: 'Find profiles near specific coordinates' },
            { keywords: ['seasonal'], suggestion: 'Analyze seasonal variations in temperature' }
        ];

        suggestionTemplates.forEach(template => {
            if (template.keywords.some(keyword =>
                keywords.some(inputKeyword => inputKeyword.includes(keyword))
            )) {
                suggestions.push(template.suggestion);
            }
        });

        return suggestions.slice(0, 3); // Limit to 3 suggestions
    },

    applySuggestion(suggestion) {
        const messageInput = document.getElementById('message-input');
        const suggestionsPanel = document.getElementById('suggestions-panel');

        if (messageInput) {
            messageInput.value = suggestion;
            messageInput.focus();
            this.handleInputChange({ target: messageInput });
        }

        if (suggestionsPanel) {
            suggestionsPanel.style.display = 'none';
        }
    },

    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        if (!messageInput || this.isTyping) return;

        const message = messageInput.value.trim();
        if (!message) return;

        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        this.handleInputChange({ target: messageInput });

        // Hide suggestions
        const suggestionsPanel = document.getElementById('suggestions-panel');
        if (suggestionsPanel) suggestionsPanel.style.display = 'none';

        // Add user message
        this.addMessage({
            type: 'user',
            content: message,
            timestamp: new Date()
        });

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to API
            const response = await api.sendChatMessage(message);

            // Hide typing indicator
            this.hideTypingIndicator();

            // Add bot response
            this.addMessage({
                type: 'bot',
                content: response.message,
                data: response.data,
                timestamp: new Date()
            });

        } catch (error) {
            console.error('Chat error:', error);

            this.hideTypingIndicator();

            this.addMessage({
                type: 'bot',
                content: 'Sorry, I encountered an error processing your request. Please try again or contact support if the issue persists.',
                error: true,
                timestamp: new Date()
            });

            appState.addNotification({
                type: 'error',
                title: 'Chat Error',
                message: 'Failed to get AI response'
            });
        }
    },

    sendExample(exampleText) {
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.value = exampleText;
            this.sendMessage();
        }
    },

    addMessage(message) {
        this.messages.push(message);

        // Limit message history
        if (this.messages.length > this.maxMessages) {
            this.messages = this.messages.slice(-this.maxMessages);
        }

        // Render message
        this.renderMessage(message);

        // Save to storage
        this.saveMessageHistory();

        // Scroll to bottom
        this.scrollToBottom();
    },

    renderMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.type}-message${message.error ? ' error-message' : ''}`;

        const avatar = message.type === 'user' ? '👤' : '🤖';

        let contentHtml = `<p>${utils.escapeHtml(message.content)}</p>`;

        // Add data visualization if present
        if (message.data && message.data.length > 0) {
            contentHtml += `
                <div class="message-data">
                    <h4>📊 Related Data:</h4>
                    <div class="data-items">
                        ${message.data.slice(0, 3).map(item => `
                            <div class="data-item">
                                <strong>Profile ${item.profile_id || 'N/A'}:</strong>
                                ${item.temperature ? `Temp: ${item.temperature}°C` : ''}
                                ${item.salinity ? `Salinity: ${item.salinity}` : ''}
                                ${item.location ? `Location: ${item.location}` : ''}
                            </div>
                        `).join('')}
                    </div>
                    ${message.data.length > 3 ? `<p><em>... and ${message.data.length - 3} more results</em></p>` : ''}
                </div>
            `;
        }

        messageElement.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${contentHtml}</div>
                <div class="message-time">${utils.formatTime(message.timestamp)}</div>
            </div>
        `;

        messagesContainer.appendChild(messageElement);
    },

    showTypingIndicator() {
        this.isTyping = true;
        const typingIndicator = document.getElementById('typing-indicator');
        const sendButton = document.getElementById('send-button');

        if (typingIndicator) {
            typingIndicator.style.display = 'block';
        }

        if (sendButton) {
            sendButton.disabled = true;
        }

        this.scrollToBottom();
    },

    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        const sendButton = document.getElementById('send-button');
        const messageInput = document.getElementById('message-input');

        if (typingIndicator) {
            typingIndicator.style.display = 'none';
        }

        if (sendButton && messageInput) {
            sendButton.disabled = messageInput.value.trim().length === 0;
        }
    },

    scrollToBottom() {
        setTimeout(() => {
            const chatContainer = document.getElementById('chat-container');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 50);
    },

    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.messages = [];
            const messagesContainer = document.getElementById('chat-messages');
            if (messagesContainer) {
                // Keep only the welcome message
                const welcomeMessage = messagesContainer.querySelector('.bot-message');
                messagesContainer.innerHTML = '';
                if (welcomeMessage) {
                    messagesContainer.appendChild(welcomeMessage);
                }
            }

            this.saveMessageHistory();

            appState.addNotification({
                type: 'success',
                title: 'Chat Cleared',
                message: 'Chat history has been cleared'
            });
        }
    },

    exportChat() {
        if (this.messages.length === 0) {
            appState.addNotification({
                type: 'warning',
                title: 'No Messages',
                message: 'No chat messages to export'
            });
            return;
        }

        const chatData = {
            timestamp: new Date().toISOString(),
            messages: this.messages.map(msg => ({
                type: msg.type,
                content: msg.content,
                timestamp: msg.timestamp.toISOString(),
                data: msg.data ? msg.data.length : 0
            }))
        };

        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `argo-chat-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);

        appState.addNotification({
            type: 'success',
            title: 'Chat Exported',
            message: 'Chat history has been exported successfully'
        });
    },

    saveMessageHistory() {
        try {
            localStorage.setItem('argo-chat-history', JSON.stringify(
                this.messages.map(msg => ({
                    ...msg,
                    timestamp: msg.timestamp.toISOString()
                }))
            ));
        } catch (error) {
            console.warn('Failed to save chat history:', error);
        }
    },

    async loadMessageHistory() {
        try {
            const saved = localStorage.getItem('argo-chat-history');
            if (saved) {
                const messages = JSON.parse(saved);
                this.messages = messages.map(msg => ({
                    ...msg,
                    timestamp: new Date(msg.timestamp)
                }));

                // Render saved messages
                this.messages.forEach(message => this.renderMessage(message));
                this.scrollToBottom();
            }
        } catch (error) {
            console.warn('Failed to load chat history:', error);
        }
    },

    checkPendingQuery() {
        const pendingQuery = appState.get('pendingQuery');
        if (pendingQuery) {
            const messageInput = document.getElementById('message-input');
            if (messageInput) {
                messageInput.value = pendingQuery;
                this.handleInputChange({ target: messageInput });
            }
            appState.delete('pendingQuery');
        }
    },

    updateAIStatus() {
        const indicator = document.getElementById('ai-status-indicator');
        const statusText = document.getElementById('ai-status-text');

        if (this.isTyping) {
            if (indicator) indicator.className = 'status-indicator processing';
            if (statusText) statusText.textContent = 'AI Processing...';
        } else {
            if (indicator) indicator.className = 'status-indicator online';
            if (statusText) statusText.textContent = 'AI Online';
        }
    },

    toggleVoiceInput() {
        appState.addNotification({
            type: 'info',
            title: 'Voice Input',
            message: 'Voice input feature coming soon!'
        });
    },

    attachFile() {
        appState.addNotification({
            type: 'info',
            title: 'File Upload',
            message: 'File attachment feature coming soon!'
        });
    },

    initializeWebSocket() {
        // WebSocket implementation for real-time updates - TEMPORARILY DISABLED
        console.log('🔧 WebSocket temporarily disabled - backend WebSocket endpoints not implemented yet');
        return; // Disable WebSocket functionality temporarily

        try {
            const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/chat`;
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('WebSocket connected');
            };

            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'chat_response') {
                    this.handleWebSocketMessage(data);
                }
            };

            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.initializeWebSocket(), 5000);
            };

        } catch (error) {
            console.warn('WebSocket not available:', error);
        }
    },

    handleWebSocketMessage(data) {
        if (data.message) {
            this.hideTypingIndicator();
            this.addMessage({
                type: 'bot',
                content: data.message,
                data: data.data,
                timestamp: new Date()
            });
        }
    },

    destroy() {
        if (this.websocket) {
            this.websocket.close();
        }
    }
};

// Make component available globally
window.chatbot = ChatbotComponent;

// Register route
router.addRoute('/chat', ChatbotComponent);
router.addRoute('/chatbot', ChatbotComponent);
