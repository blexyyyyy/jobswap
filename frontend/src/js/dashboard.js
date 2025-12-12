/**
 * Dashboard Logic
 */

const Dashboard = {
    async init() {
        if (!API.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }

        await Promise.all([
            this.loadStats(),
            this.loadProfileStrength()
        ]);

        this.setupScraperModal();
    },

    async loadStats() {
        try {
            // Fetch applied jobs count
            const appliedResponse = await fetch(`${API.baseUrl}/jobs/applied`, {
                headers: API.getHeaders()
            });
            if (appliedResponse.status === 401) {
                localStorage.removeItem('token');
                window.location.href = 'login.html';
                return;
            }
            const appliedData = await appliedResponse.json();

            // Fetch saved jobs count
            const savedResponse = await fetch(`${API.baseUrl}/jobs/saved`, {
                headers: API.getHeaders()
            });
            const savedData = await savedResponse.json();

            // Update UI
            this.animateNumber('stats-applied', appliedData.jobs?.length || 0);
            this.animateNumber('stats-saved', savedData.jobs?.length || 0);

            // Mock viewed count for now (stored in local storage usually)
            const stats = JSON.parse(localStorage.getItem('jobswipe_stats') || '{"viewed": 0}');
            this.animateNumber('stats-viewed', stats.viewed || 0);

        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    },

    async loadProfileStrength() {
        try {
            const response = await fetch(`${API.baseUrl}/auth/profile/me`, {
                headers: API.getHeaders()
            });
            const user = await response.json();

            let score = 0;
            const checks = [
                { field: 'name', points: 10 },
                { field: 'email', points: 10 },
                { field: 'skills', points: 30 }, // High value
                { field: 'experience_years', points: 15 },
                { field: 'preferred_location', points: 15 },
                { field: 'preferred_seniority', points: 10 },
                { field: 'resume_text', points: 10 }
            ];

            checks.forEach(check => {
                if (user[check.field] && (
                    (Array.isArray(user[check.field]) && user[check.field].length > 0) ||
                    (!Array.isArray(user[check.field]) && user[check.field])
                )) {
                    score += check.points;
                }
            });

            // Cap at 100
            score = Math.min(100, score);

            // Update UI
            const bar = document.getElementById('profile-progress');
            bar.style.width = `${score}%`;

            const message = document.getElementById('profile-message');
            if (score === 100) {
                message.textContent = "Your profile is rock solid! 🚀";
                bar.style.backgroundColor = "#22c55e";
            } else if (score > 70) {
                message.textContent = "Great profile! Add a few details to reach 100%.";
            } else {
                message.textContent = `${score}% Complete. Upload your resume to boost this!`;
                bar.style.backgroundColor = "#eab308";
            }

        } catch (error) {
            console.error('Failed to load profile strength:', error);
        }
    },

    async setupScraperModal() {
        const modal = document.getElementById('scraper-modal');
        const openBtn = document.getElementById('open-scraper-btn');
        const closeBtns = document.querySelectorAll('.close-modal, .close-modal-btn');
        const startBtn = document.getElementById('start-scrape-btn');
        const statusDiv = document.getElementById('scrape-status');

        if (!modal || !openBtn) return;

        openBtn.addEventListener('click', () => {
            modal.style.display = 'flex';
            statusDiv.textContent = '';
            statusDiv.className = '';
        });

        const closeModal = () => {
            if (startBtn.disabled) return; // Prevent closing while scraping
            modal.style.display = 'none';
        };

        closeBtns.forEach(btn => btn.addEventListener('click', closeModal));

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        startBtn.addEventListener('click', async () => {
            const keywords = document.getElementById('scrape-keywords').value;
            const location = document.getElementById('scrape-location').value;
            const maxJobs = parseInt(document.getElementById('scrape-max').value) || 10;

            if (!keywords) {
                statusDiv.textContent = 'Please enter keywords.';
                statusDiv.style.color = 'red';
                return;
            }

            // UI Loading State
            startBtn.disabled = true;
            startBtn.textContent = 'Scraping... (this may take a minute)';
            statusDiv.textContent = 'Connecting to job sources...';
            statusDiv.style.color = '#666';

            try {
                const response = await fetch(`${API.baseUrl}/jobs/scrape`, {
                    method: 'POST',
                    headers: API.getHeaders(),
                    body: JSON.stringify({
                        keywords,
                        location,
                        max_jobs: maxJobs
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    statusDiv.textContent = data.message;
                    statusDiv.style.color = 'green';

                    // Refresh stats
                    await this.loadStats();

                    setTimeout(() => {
                        closeModal();
                        startBtn.disabled = false;
                        startBtn.textContent = 'Start Scraping';
                    }, 2000);
                } else {
                    throw new Error(data.detail || 'Scraping failed');
                }
            } catch (error) {
                console.error(error);
                statusDiv.textContent = `Error: ${error.message}`;
                statusDiv.style.color = 'red';
                startBtn.disabled = false;
                startBtn.textContent = 'Start Scraping';
            }
        });
    },

    animateNumber(elementId, finalValue) {
        const element = document.getElementById(elementId);
        let start = 0;
        const duration = 1000;
        const stepTime = 20;
        const steps = duration / stepTime;
        const increment = finalValue / steps;

        const timer = setInterval(() => {
            start += increment;
            if (start >= finalValue) {
                element.textContent = finalValue;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start);
            }
        }, stepTime);
    }
};

document.addEventListener('DOMContentLoaded', () => Dashboard.init());

// Expose to window for module scripts
window.Dashboard = Dashboard;
