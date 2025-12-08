/**
 * Chat Interface - Real-time messaging with employers
 */

const Chat = {
    jobId: null,
    messages: [],

    async init() {
        // Check authentication
        if (!API.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }

        // Get job ID from URL
        const params = new URLSearchParams(window.location.search);
        this.jobId = parseInt(params.get('job_id'));

        if (!this.jobId) {
            alert('No job selected');
            window.location.href = 'applied.html';
            return;
        }

        await this.loadJobInfo();
        await this.loadMessages();
        this.bindEvents();

        // Auto-refresh messages every 5 seconds
        setInterval(() => this.loadMessages(true), 5000);
    },

    async loadJobInfo() {
        try {
            // Get job info from applied jobs
            const response = await fetch(`${API.baseUrl}/jobs/applied`, {
                headers: API.getHeaders()
            });

            const data = await response.json();
            const job = data.jobs.find(j => j.id === this.jobId);

            if (job) {
                document.getElementById('job-title').textContent = job.title;
                document.getElementById('job-company').textContent = job.company;
            }
        } catch (error) {
            console.error('Failed to load job info:', error);
        }
    },

    async loadMessages(silent = false) {
        try {
            const response = await fetch(`${API.baseUrl}/chat/${this.jobId}`, {
                headers: API.getHeaders()
            });

            if (response.status === 401) {
                if (!silent) {
                    localStorage.removeItem('token');
                    window.location.href = 'login.html';
                }
                return;
            }

            const data = await response.json();
            this.messages = data.messages || [];

            if (!silent) {
                this.renderMessages();
            } else {
                // Only render if there are new messages
                const currentCount = document.querySelectorAll('.message').length;
                if (this.messages.length > currentCount) {
                    this.renderMessages();
                }
            }
        } catch (error) {
            console.error('Failed to load messages:', error);
        }
    },

    renderMessages() {
        const container = document.getElementById('messages-container');
        container.innerHTML = '';

        this.messages.forEach(msg => {
            const msgEl = this.createMessageElement(msg);
            container.appendChild(msgEl);
        });

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    },

    createMessageElement(msg) {
        const div = document.createElement('div');
        div.className = `message ${msg.sender_type}`;

        const time = new Date(msg.created_at).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit'
        });

        div.innerHTML = `
            <div class="message-bubble">${this.escapeHtml(msg.message)}</div>
            <div class="message-time">${time}</div>
        `;

        return div;
    },

    bindEvents() {
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');

        sendBtn.addEventListener('click', () => this.sendMessage());

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    },

    async sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();

        if (!message) return;

        const sendBtn = document.getElementById('send-btn');
        sendBtn.disabled = true;
        input.value = '';

        try {
            const response = await fetch(`${API.baseUrl}/chat/${this.jobId}`, {
                method: 'POST',
                headers: API.getHeaders(),
                body: JSON.stringify({ message })
            });

            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = 'login.html';
                return;
            }

            if (response.ok) {
                await this.loadMessages();
            } else {
                alert('Failed to send message');
                input.value = message; // Restore message
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            alert('Failed to send message');
            input.value = message; // Restore message
        } finally {
            sendBtn.disabled = false;
            input.focus();
        }
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    Chat.init();
});
