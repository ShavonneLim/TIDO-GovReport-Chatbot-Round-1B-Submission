class ChatApp {
    constructor() {
        this.messages = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadMessages();
    }
    
    initializeElements() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.imageUpload = document.getElementById('imageUpload');
    }
    
    bindEvents() {
        this.messageInput.addEventListener('input', () => this.autoResize(this.messageInput));
        this.messageInput.addEventListener('keypress', (e) => this.handleKeyPress(e));
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.imageUpload.addEventListener('change', () => this.handleImageUpload());
    }
    
    handleKeyPress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }
    
    autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    async loadMessages() {
        try {
            const response = await fetch('/api/messages');
            const messages = await response.json();
            this.messages = messages;
            this.renderMessages();
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }
    
    renderMessages() {
        if (this.messages.length === 0) return;
        
        // Remove the welcome message if there are other messages
        const welcome = this.messagesContainer.querySelector('.welcome-message');
        if (welcome) {
            welcome.remove();
        }
        
        this.messagesContainer.innerHTML = this.messages.map(msg => {
            const avatar = msg.sender === 'user' ? '👤' : '🤖';
            const username = msg.sender === 'user' ? 'You' : 'Bot';
            const time = this.formatTime(msg.timestamp);

            let messageContentHtml = '';

            // Check the message type to render the correct content
            if (msg.type === 'image') {
                messageContentHtml = `<img src="${msg.content}" alt="Uploaded Image" class="message-image">`;
            } else {
                messageContentHtml = `<div class="message-text">${this.escapeHtml(msg.content)}</div>`;
            }

            return `
                <div class="message ${msg.sender}">
                    <div class="message-avatar ${msg.sender}">${avatar}</div>
                    <div class="message-content">
                        <div class="message-header">
                            <span class="message-username">${username}</span>
                            <span class="message-time">${time}</span>
                        </div>
                        ${messageContentHtml}
                    </div>
                </div>
            `;
        }).join('');
        
        this.scrollToBottom();
    }
    
    async sendMessage() {
        const content = this.messageInput.value.trim();
        if (!content) return;
        
        this.sendButton.disabled = true;
        this.typingIndicator.style.display = 'flex';
        
        try {
            const response = await fetch('/api/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: content })
            });
            
            if (response.ok) {
                this.messageInput.value = '';
                this.autoResize(this.messageInput);
                this.loadMessages();
            }
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            this.sendButton.disabled = false;
            this.messageInput.focus();
            this.typingIndicator.style.display = 'none';
        }
    }
    
    async handleImageUpload() {
        const file = this.imageUpload.files[0];
        if (!file) return;

        // Show typing indicator and disable buttons while uploading
        this.sendButton.disabled = true;
        this.typingIndicator.style.display = 'flex';

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                // Once the upload is successful, reload messages from the server
                await this.loadMessages();
            } else {
                console.error('Image upload failed.');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
        } finally {
            // Re-enable buttons and hide typing indicator
            this.sendButton.disabled = false;
            this.typingIndicator.style.display = 'none';
            this.messageInput.focus();
            // Clear the file input so you can upload the same file again if needed
            this.imageUpload.value = '';
        }
    }

    appendImageMessage(sender, imageUrl) {
        const timestamp = new Date().toISOString();
        const messageHtml = `
            <div class="message ${sender}">
                <div class="message-avatar ${sender}">${sender === 'user' ? '👤' : '🤖'}</div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-username">${sender === 'user' ? 'You' : 'Bot'}</span>
                        <span class="message-time">${this.formatTime(timestamp)}</span>
                    </div>
                    <div class="message-text">
                        <img src="${imageUrl}" alt="Uploaded Image" style="max-width: 100%; border-radius: 8px;">
                    </div>
                </div>
            </div>
        `;
        this.messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
    
    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});