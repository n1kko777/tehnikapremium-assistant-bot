/**
 * TehnikaPremium Chat Widget
 * Встраиваемый виджет чата для сайта
 */

(function() {
    'use strict';

    const TehnikaPremiumWidget = {
        config: {
            apiUrl: '',
            position: 'right',
            primaryColor: '#00d9ff',
            secondaryColor: '#0f3460',
            title: 'Консультант',
            placeholder: 'Напишите ваш вопрос...',
            welcomeMessage: 'Здравствуйте! 👋 Я AI-консультант ТехникаПремиум. Помогу подобрать бытовую технику, расскажу о характеристиках и ценах. Чем могу помочь?'
        },
        sessionId: null,
        isOpen: false,
        messages: [],

        init: function(options) {
            this.config = { ...this.config, ...options };
            this.sessionId = this.getSessionId();
            this.injectStyles();
            this.createWidget();
            this.bindEvents();
        },

        getSessionId: function() {
            let id = localStorage.getItem('tp_chat_session');
            if (!id) {
                id = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('tp_chat_session', id);
            }
            return id;
        },

        injectStyles: function() {
            const styles = `
                @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700&display=swap');
                
                .tp-widget-container {
                    position: fixed;
                    bottom: 24px;
                    ${this.config.position}: 24px;
                    z-index: 999999;
                    font-family: 'Nunito', -apple-system, BlinkMacSystemFont, sans-serif;
                }

                .tp-chat-button {
                    width: 64px;
                    height: 64px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, ${this.config.primaryColor}, ${this.config.secondaryColor});
                    border: none;
                    cursor: pointer;
                    box-shadow: 0 8px 32px rgba(0, 217, 255, 0.35);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    animation: tp-pulse 2s infinite;
                }

                @keyframes tp-pulse {
                    0%, 100% { box-shadow: 0 8px 32px rgba(0, 217, 255, 0.35); }
                    50% { box-shadow: 0 8px 48px rgba(0, 217, 255, 0.5); }
                }

                .tp-chat-button:hover {
                    transform: scale(1.1);
                    box-shadow: 0 12px 40px rgba(0, 217, 255, 0.5);
                }

                .tp-chat-button svg {
                    width: 32px;
                    height: 32px;
                    fill: white;
                    transition: transform 0.3s ease;
                }

                .tp-chat-button.open svg {
                    transform: rotate(180deg);
                }

                .tp-chat-window {
                    position: absolute;
                    bottom: 80px;
                    ${this.config.position}: 0;
                    width: 380px;
                    height: 560px;
                    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
                    border-radius: 24px;
                    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    opacity: 0;
                    visibility: hidden;
                    transform: translateY(20px) scale(0.95);
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .tp-chat-window.open {
                    opacity: 1;
                    visibility: visible;
                    transform: translateY(0) scale(1);
                }

                .tp-chat-header {
                    padding: 20px 24px;
                    background: linear-gradient(135deg, rgba(0, 217, 255, 0.15), rgba(0, 255, 136, 0.1));
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    align-items: center;
                    gap: 14px;
                }

                .tp-avatar {
                    width: 48px;
                    height: 48px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, ${this.config.primaryColor}, #00ff88);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    box-shadow: 0 4px 16px rgba(0, 217, 255, 0.3);
                }

                .tp-header-info {
                    flex: 1;
                }

                .tp-header-title {
                    color: #fff;
                    font-size: 16px;
                    font-weight: 700;
                    margin-bottom: 2px;
                }

                .tp-header-status {
                    color: #00ff88;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }

                .tp-status-dot {
                    width: 8px;
                    height: 8px;
                    background: #00ff88;
                    border-radius: 50%;
                    animation: tp-blink 1.5s infinite;
                }

                @keyframes tp-blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }

                .tp-close-btn {
                    width: 36px;
                    height: 36px;
                    border: none;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 50%;
                    color: #fff;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s ease;
                }

                .tp-close-btn:hover {
                    background: rgba(255, 255, 255, 0.2);
                    transform: rotate(90deg);
                }

                .tp-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }

                .tp-messages::-webkit-scrollbar {
                    width: 6px;
                }

                .tp-messages::-webkit-scrollbar-track {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 3px;
                }

                .tp-messages::-webkit-scrollbar-thumb {
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 3px;
                }

                .tp-message {
                    max-width: 85%;
                    animation: tp-fadeIn 0.3s ease;
                }

                @keyframes tp-fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                .tp-message.bot {
                    align-self: flex-start;
                }

                .tp-message.user {
                    align-self: flex-end;
                }

                .tp-message-content {
                    padding: 14px 18px;
                    border-radius: 20px;
                    font-size: 14px;
                    line-height: 1.5;
                    word-wrap: break-word;
                }

                .tp-message.bot .tp-message-content {
                    background: rgba(255, 255, 255, 0.08);
                    color: #e0e0e0;
                    border-bottom-left-radius: 6px;
                }

                .tp-message.user .tp-message-content {
                    background: linear-gradient(135deg, ${this.config.primaryColor}, #0099cc);
                    color: #fff;
                    border-bottom-right-radius: 6px;
                }

                .tp-message-content strong {
                    color: ${this.config.primaryColor};
                    font-weight: 600;
                }

                .tp-message-content a {
                    color: ${this.config.primaryColor};
                    text-decoration: none;
                }

                .tp-message-content a:hover {
                    text-decoration: underline;
                }

                .tp-typing {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                    padding: 14px 18px;
                    background: rgba(255, 255, 255, 0.08);
                    border-radius: 20px;
                    border-bottom-left-radius: 6px;
                    width: fit-content;
                }

                .tp-typing span {
                    width: 8px;
                    height: 8px;
                    background: ${this.config.primaryColor};
                    border-radius: 50%;
                    animation: tp-typing 1.4s infinite;
                }

                .tp-typing span:nth-child(2) { animation-delay: 0.2s; }
                .tp-typing span:nth-child(3) { animation-delay: 0.4s; }

                @keyframes tp-typing {
                    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
                    30% { transform: translateY(-8px); opacity: 1; }
                }

                .tp-input-container {
                    padding: 16px 20px;
                    background: rgba(0, 0, 0, 0.3);
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    gap: 12px;
                    align-items: center;
                }

                .tp-input {
                    flex: 1;
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 24px;
                    padding: 14px 20px;
                    color: #fff;
                    font-size: 14px;
                    font-family: inherit;
                    outline: none;
                    transition: all 0.2s ease;
                }

                .tp-input::placeholder {
                    color: rgba(255, 255, 255, 0.4);
                }

                .tp-input:focus {
                    border-color: ${this.config.primaryColor};
                    box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.15);
                }

                .tp-send-btn {
                    width: 48px;
                    height: 48px;
                    border: none;
                    background: linear-gradient(135deg, ${this.config.primaryColor}, #0099cc);
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s ease;
                    box-shadow: 0 4px 16px rgba(0, 217, 255, 0.3);
                }

                .tp-send-btn:hover:not(:disabled) {
                    transform: scale(1.1);
                    box-shadow: 0 6px 20px rgba(0, 217, 255, 0.4);
                }

                .tp-send-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                .tp-send-btn svg {
                    width: 22px;
                    height: 22px;
                    fill: white;
                }

                @media (max-width: 480px) {
                    .tp-chat-window {
                        width: calc(100vw - 32px);
                        height: calc(100vh - 120px);
                        bottom: 76px;
                        ${this.config.position}: 16px;
                        border-radius: 20px;
                    }

                    .tp-widget-container {
                        bottom: 16px;
                        ${this.config.position}: 16px;
                    }

                    .tp-chat-button {
                        width: 56px;
                        height: 56px;
                    }
                }
            `;

            const styleSheet = document.createElement('style');
            styleSheet.textContent = styles;
            document.head.appendChild(styleSheet);
        },

        createWidget: function() {
            const container = document.createElement('div');
            container.className = 'tp-widget-container';
            container.innerHTML = `
                <div class="tp-chat-window" id="tp-chat-window">
                    <div class="tp-chat-header">
                        <div class="tp-avatar">🤖</div>
                        <div class="tp-header-info">
                            <div class="tp-header-title">${this.config.title}</div>
                            <div class="tp-header-status">
                                <span class="tp-status-dot"></span>
                                Онлайн
                            </div>
                        </div>
                        <button class="tp-close-btn" id="tp-close-btn">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="tp-messages" id="tp-messages"></div>
                    <div class="tp-input-container">
                        <input type="text" class="tp-input" id="tp-input" placeholder="${this.config.placeholder}" autocomplete="off">
                        <button class="tp-send-btn" id="tp-send-btn">
                            <svg viewBox="0 0 24 24">
                                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <button class="tp-chat-button" id="tp-chat-button">
                    <svg viewBox="0 0 24 24">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                    </svg>
                </button>
            `;

            document.body.appendChild(container);
            this.elements = {
                container,
                chatWindow: document.getElementById('tp-chat-window'),
                chatButton: document.getElementById('tp-chat-button'),
                closeBtn: document.getElementById('tp-close-btn'),
                messages: document.getElementById('tp-messages'),
                input: document.getElementById('tp-input'),
                sendBtn: document.getElementById('tp-send-btn')
            };
        },

        bindEvents: function() {
            this.elements.chatButton.addEventListener('click', () => this.toggleChat());
            this.elements.closeBtn.addEventListener('click', () => this.closeChat());
            this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
            this.elements.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        },

        toggleChat: function() {
            this.isOpen ? this.closeChat() : this.openChat();
        },

        openChat: function() {
            this.isOpen = true;
            this.elements.chatWindow.classList.add('open');
            this.elements.chatButton.classList.add('open');
            
            if (this.messages.length === 0) {
                this.addMessage(this.config.welcomeMessage, 'bot');
            }
            
            setTimeout(() => this.elements.input.focus(), 300);
        },

        closeChat: function() {
            this.isOpen = false;
            this.elements.chatWindow.classList.remove('open');
            this.elements.chatButton.classList.remove('open');
        },

        addMessage: function(text, type) {
            this.messages.push({ text, type });
            
            const messageEl = document.createElement('div');
            messageEl.className = `tp-message ${type}`;
            messageEl.innerHTML = `<div class="tp-message-content">${this.formatMessage(text)}</div>`;
            
            this.elements.messages.appendChild(messageEl);
            this.scrollToBottom();
        },

        formatMessage: function(text) {
            // Форматирование Markdown-подобного текста
            return text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>')
                .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        },

        showTyping: function() {
            const typingEl = document.createElement('div');
            typingEl.className = 'tp-message bot';
            typingEl.id = 'tp-typing';
            typingEl.innerHTML = `
                <div class="tp-typing">
                    <span></span><span></span><span></span>
                </div>
            `;
            this.elements.messages.appendChild(typingEl);
            this.scrollToBottom();
        },

        hideTyping: function() {
            const typingEl = document.getElementById('tp-typing');
            if (typingEl) typingEl.remove();
        },

        scrollToBottom: function() {
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
        },

        async sendMessage() {
            const text = this.elements.input.value.trim();
            if (!text) return;

            this.elements.input.value = '';
            this.elements.sendBtn.disabled = true;
            
            this.addMessage(text, 'user');
            this.showTyping();

            try {
                const response = await fetch(`${this.config.apiUrl}/api/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: this.sessionId,
                        message: text
                    })
                });

                const data = await response.json();
                this.hideTyping();
                
                if (data.message) {
                    this.addMessage(data.message, 'bot');
                    this.sessionId = data.session_id;
                    localStorage.setItem('tp_chat_session', this.sessionId);
                }
            } catch (error) {
                this.hideTyping();
                this.addMessage('Извините, произошла ошибка. Попробуйте позже.', 'bot');
                console.error('Chat error:', error);
            }

            this.elements.sendBtn.disabled = false;
            this.elements.input.focus();
        }
    };

    // Экспортируем в глобальную область
    window.TehnikaPremiumWidget = TehnikaPremiumWidget;
})();

