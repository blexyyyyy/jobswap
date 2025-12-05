/**
 * Applied Jobs Page - Display user's applications
 */

const AppliedJobs = {
    jobs: [],

    async init() {
        // Check authentication
        if (!API.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }

        await this.loadAppliedJobs();
    },

    async loadAppliedJobs() {
        try {
            const response = await fetch(`${API.baseUrl}/jobs/applied`, {
                headers: API.getHeaders()
            });

            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = 'login.html';
                return;
            }

            const data = await response.json();
            this.jobs = data.jobs || [];

            document.getElementById('loading').style.display = 'none';

            if (this.jobs.length === 0) {
                document.getElementById('empty-state').style.display = 'flex';
            } else {
                document.getElementById('jobs-list').style.display = 'block';
                this.renderJobs();
            }
        } catch (error) {
            console.error('Failed to load applied jobs:', error);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('empty-state').style.display = 'flex';
        }
    },

    renderJobs() {
        const container = document.getElementById('jobs-list');
        container.innerHTML = '';

        this.jobs.forEach(job => {
            const jobEl = this.createJobElement(job);
            container.appendChild(jobEl);
        });
    },

    createJobElement(job) {
        const div = document.createElement('div');
        div.className = 'job-item';

        // Parse skills if string
        const skills = Array.isArray(job.skills)
            ? job.skills
            : (job.skills ? job.skills.split(',').map(s => s.trim()) : []);

        div.innerHTML = `
            <div class="job-item-header">
                <div class="job-item-logo">${job.logo_emoji || '💼'}</div>
                <div class="job-item-info">
                    <h3 class="job-item-title">${this.escapeHtml(job.title)}</h3>
                    <p class="job-item-company">${this.escapeHtml(job.company)}</p>
                    <p class="job-item-location">📍 ${this.escapeHtml(job.location || 'Remote')}</p>
                </div>
            </div>
            
            <div class="job-item-actions">
                <button class="btn-chat" onclick="AppliedJobs.openChat(${job.id})">
                    💬 Chat with Employer
                </button>
                <button class="btn-secondary" onclick="window.open('${job.url || '#'}', '_blank')">
                    View Posting
                </button>
            </div>
        `;

        return div;
    },

    openChat(jobId) {
        window.location.href = `chat.html?job_id=${jobId}`;
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    AppliedJobs.init();
});
