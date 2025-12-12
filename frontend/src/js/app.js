/**
 * JobSwipe App - Main Controller
 */

class JobSwipeApp {
    constructor() {
        this.jobs = [];
        this.currentIndex = 0;
        this.stats = {
            viewed: 0,
            applied: 0,
            saved: 0,
            skipped: 0
        };

        this.swipeHandler = null;

        // DOM elements
        this.cardStack = document.getElementById('card-stack');
        this.loading = document.getElementById('loading');
        this.emptyState = document.getElementById('empty-state');
        this.toastContainer = document.getElementById('toast-container');

        // Action buttons
        this.btnSkip = document.getElementById('btn-skip');
        this.btnSave = document.getElementById('btn-save');
        this.btnApply = document.getElementById('btn-apply');

        this.init();
    }

    async init() {
        // Check authentication
        if (!API.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }

        this.bindEvents();
        this.bindKeyboard();
        await this.loadJobs();
    }

    bindEvents() {
        this.btnSkip.addEventListener('click', () => this.skip());
        this.btnSave.addEventListener('click', () => this.save());
        this.btnApply.addEventListener('click', () => this.apply());

        // Add ripple effect to buttons
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', this.createRipple.bind(this));
        });
    }

    bindKeyboard() {
        document.addEventListener('keydown', (e) => {
            if (this.currentIndex >= this.jobs.length) return;

            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.skip();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.apply();
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.save();
                    break;
            }
        });
    }

    async loadJobs() {
        this.showLoading(true);

        try {
            const data = await API.getJobFeed();
            this.jobs = data.jobs || [];
            this.renderCards();
        } catch (error) {
            console.error('Failed to load jobs:', error);
            this.showToast('Failed to load jobs', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    renderCards() {
        // Clear existing cards (except loading)
        const existingCards = this.cardStack.querySelectorAll('.job-card');
        existingCards.forEach(card => card.remove());

        if (this.jobs.length === 0 || this.currentIndex >= this.jobs.length) {
            this.showEmptyState();
            return;
        }

        // Render up to 3 cards (stacked)
        const cardsToRender = this.jobs.slice(this.currentIndex, this.currentIndex + 3);

        cardsToRender.forEach((job, index) => {
            const card = Cards.createCard(job);
            if (index === 0) {
                card.classList.add('entering');

                // Fetch explanation for the top card if needed
                if (!job.match_explanation || !job.match_explanation.match_reason) {
                    Cards.fetchExplanation(job.id, card);
                }

                // Add swipe handler to top card only
                setTimeout(() => {
                    this.attachSwipeHandler(card);
                }, 50);
            }
            this.cardStack.appendChild(card);
        });

        this.updateStats();
    }

    attachSwipeHandler(card) {
        if (this.swipeHandler) {
            this.swipeHandler.destroy();
        }

        this.swipeHandler = new SwipeHandler(card, {
            onSwipeLeft: () => this.handleSwipe('skip'),
            onSwipeRight: () => this.handleSwipe('apply'),
            onSwipeUp: () => this.handleSwipe('save')
        });
    }

    handleSwipe(action) {
        const currentCard = this.cardStack.querySelector('.job-card');
        if (!currentCard) return;

        const job = this.jobs[this.currentIndex];

        // Animate out
        const exitClass = {
            'skip': 'exit-left',
            'apply': 'exit-right',
            'save': 'exit-up'
        }[action];

        currentCard.classList.add(exitClass);

        // Record action
        API.recordSwipe(job.id, action);

        // Update stats
        this.stats.viewed++;
        if (action === 'apply') {
            this.stats.applied++;
            this.showToast(`Applied to ${job.company}! 🎉`, 'success');
            this.spawnConfetti();
        } else if (action === 'save') {
            this.stats.saved++;
            this.showToast(`Saved for later ⭐`, 'success');
        } else {
            this.stats.skipped++;
        }

        // Move to next card
        setTimeout(() => {
            this.currentIndex++;
            this.renderCards();

            // Explanation fetching for the new top card (index 0 relative to render)
            // is handled inside renderCards() now.
        }, 400);
    }

    skip() {
        const currentCard = this.cardStack.querySelector('.job-card');
        if (!currentCard) return;

        currentCard.classList.add('swiping-left');
        setTimeout(() => this.handleSwipe('skip'), 150);
    }

    apply() {
        const currentCard = this.cardStack.querySelector('.job-card');
        if (!currentCard) return;

        currentCard.classList.add('swiping-right');
        setTimeout(() => this.handleSwipe('apply'), 150);
    }

    save() {
        const currentCard = this.cardStack.querySelector('.job-card');
        if (!currentCard) return;

        this.handleSwipe('save');
    }

    updateStats() {
        document.getElementById('stat-viewed').textContent = this.stats.viewed;
        document.getElementById('stat-applied').textContent = this.stats.applied;
        document.getElementById('stat-saved').textContent = this.stats.saved;
    }

    showLoading(show) {
        this.loading.style.display = show ? 'flex' : 'none';
    }

    showEmptyState() {
        this.cardStack.style.display = 'none';
        document.querySelector('.action-bar').style.display = 'none';
        this.emptyState.style.display = 'block';
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
            <span>${message}</span>
        `;

        this.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    createRipple(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('span');
        ripple.className = 'ripple';

        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);

        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${e.clientY - rect.top - size / 2}px`;

        button.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    }

    spawnConfetti() {
        const colors = ['#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b', '#ef4444'];

        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'confetti-particle';
            particle.style.left = `${Math.random() * 100}vw`;
            particle.style.top = '50vh';
            particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            particle.style.transform = `rotate(${Math.random() * 360}deg)`;
            particle.style.animationDuration = `${0.5 + Math.random() * 0.5}s`;
            particle.style.animationDelay = `${Math.random() * 0.2}s`;

            document.body.appendChild(particle);
            setTimeout(() => particle.remove(), 1500);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new JobSwipeApp();
});
