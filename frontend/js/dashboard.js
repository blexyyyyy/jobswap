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
            const response = await fetch(`${API.baseUrl}/auth/me`, {
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
