/**
 * Cards Module - Renders and manages job cards
 */

const Cards = {
    /**
     * Create a job card element
     */
    createCard(job) {
        const card = document.createElement('div');
        card.className = 'job-card';
        card.dataset.jobId = job.id;

        const skillsHtml = (job.skills || [])
            .slice(0, 5)
            .map(skill => `<span class="skill-tag">${this.escapeHtml(skill)}</span>`)
            .join('');

        card.innerHTML = `
            <div class="match-score">${job.match_score || 85}% Match</div>
            
            <div class="swipe-label like">APPLY</div>
            <div class="swipe-label nope">SKIP</div>
            
            <div class="card-header">
                <div class="company-logo">${job.logo_emoji || '🏢'}</div>
                <div class="card-title-group">
                    <h3 class="job-title">${this.escapeHtml(job.title)}</h3>
                    <div class="company-name">
                        <span>${this.escapeHtml(job.company)}</span>
                    </div>
                </div>
            </div>
            
            <div class="card-meta">
                <div class="meta-item">
                    <span class="meta-icon">📍</span>
                    <span>${this.escapeHtml(job.location)}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">💼</span>
                    <span>${this.escapeHtml(job.seniority || 'Mid-Level')}</span>
                </div>
            </div>
            
            <div class="skills-section">
                <div class="skills-label">Required Skills</div>
                <div class="skills-list">
                    ${skillsHtml}
                </div>
            </div>

            <!-- New Match Explanation Section -->
            <div class="match-explanation">
                <div class="explanation-title">💡 Why this matches you</div>
                <p class="explanation-text">
                    ${job.match_explanation?.match_reason || 'Good fit based on your profile.'}
                </p>
                ${job.match_explanation?.missing_skills?.length ? `
                    <div class="missing-skills">
                        <span class="missing-label">Missing:</span>
                        ${job.match_explanation.missing_skills.map(s =>
            `<span class="skill-tag missing">${this.escapeHtml(s)}</span>`
        ).join('')}
                    </div>
                ` : ''}
            </div>
            
            <p class="job-description">${this.escapeHtml(job.description || 'No description available.')}</p>
        `;

        return card;
    },

    /**
     * Create skeleton loading card
     */
    createSkeletonCard() {
        const card = document.createElement('div');
        card.className = 'job-card skeleton-card';
        card.innerHTML = `
            <div class="card-header">
                <div class="company-logo skeleton" style="width: 64px; height: 64px;"></div>
                <div class="card-title-group">
                    <div class="skeleton" style="width: 180px; height: 24px; margin-bottom: 8px;"></div>
                    <div class="skeleton" style="width: 120px; height: 16px;"></div>
                </div>
            </div>
            <div class="card-meta">
                <div class="skeleton" style="width: 100px; height: 16px;"></div>
                <div class="skeleton" style="width: 80px; height: 16px;"></div>
            </div>
            <div class="skills-section">
                <div class="skeleton" style="width: 100px; height: 12px; margin-bottom: 12px;"></div>
                <div style="display: flex; gap: 8px;">
                    <div class="skeleton" style="width: 60px; height: 28px; border-radius: 20px;"></div>
                    <div class="skeleton" style="width: 80px; height: 28px; border-radius: 20px;"></div>
                    <div class="skeleton" style="width: 50px; height: 28px; border-radius: 20px;"></div>
                </div>
            </div>
            <div class="skeleton" style="width: 100%; height: 80px; margin-top: auto;"></div>
        `;
        return card;
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};
