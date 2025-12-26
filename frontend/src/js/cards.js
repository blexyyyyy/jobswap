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

        // Determine match category and styling
        const score = job.match_score || 0;
        let matchClass = 'medium';
        let explanationTitle = 'Why this matches you';
        let explanationIcon = '💡';

        if (score >= 90) {
            matchClass = 'high';
            explanationTitle = 'Perfect Match for you';
            explanationIcon = '✨';
        } else if (score < 30) {
            matchClass = 'low';
            explanationTitle = 'This is not the match for you';
            explanationIcon = '⚠️';
        } else {
            matchClass = 'medium';
            explanationTitle = 'Good Match';
            explanationIcon = '👍';
        }

        // Check if explanation exists or needs to be loaded
        const hasExplanation = job.match_explanation && job.match_explanation.match_reason;

        card.innerHTML = `
            <div class="match-score">${score}% Match</div>
            
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

            <!-- Match Explanation Section (Scrollable) -->
            <div class="match-explanation ${matchClass}" id="explanation-${job.id}">
                <div class="explanation-title">${explanationIcon} ${explanationTitle}</div>
                <div class="explanation-content">
                    ${hasExplanation ? `
                        <p class="explanation-text">${job.match_explanation.match_reason}</p>
                        ${job.match_explanation?.missing_skills?.length ? `
                            <div class="missing-skills">
                                <span class="missing-label">Missing:</span>
                                ${job.match_explanation.missing_skills.map(s =>
            `<span class="skill-tag missing">${this.escapeHtml(s)}</span>`
        ).join('')}
                            </div>
                        ` : ''}
                        ${job.match_explanation?.career_tip ? `
                            <div class="career-tip">💡 ${this.escapeHtml(job.match_explanation.career_tip)}</div>
                        ` : ''}
                    ` : `
                        <div class="explanation-loading">
                            <span class="loading-spinner"></span>
                            <span>Analyzing match...</span>
                        </div>
                    `}
                </div>
            </div>
            
            <p class="job-description">${this.escapeHtml(job.description || 'No description available.')}</p>
        `;

        // Lazy-load explanation is now handled by the controller (app.js)
        // when the card becomes active.

        return card;
    },

    /**
     * Fetch explanation for a job on-demand
     */
    async fetchExplanation(jobId, cardElement) {
        console.log(`[DEBUG] Fetching explanation for job ${jobId}`);
        console.log(`[DEBUG] API URL: ${API.baseUrl}/jobs/${jobId}/explanation`);
        console.log('[DEBUG] Auth headers:', API.getHeaders());

        try {
            const response = await fetch(`${API.baseUrl}/jobs/${jobId}/explanation`, {
                headers: API.getHeaders()
            });

            console.log(`[DEBUG] Response status: ${response.status}`);
            console.log(`[DEBUG] Response ok: ${response.ok}`);

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`[DEBUG] Error response: ${errorText}`);
                throw new Error(`Failed to fetch explanation: ${response.status} ${errorText}`);
            }

            const explanation = await response.json();
            console.log('[DEBUG] Received explanation:', explanation);

            // Update the card with the explanation
            const explanationDiv = cardElement.querySelector(`#explanation-${jobId} .explanation-content`);
            console.log('[DEBUG] Explanation div found:', !!explanationDiv);

            if (explanationDiv) {
                explanationDiv.innerHTML = `
                    <p class="explanation-text">${explanation.match_reason || 'Good fit based on your profile.'}</p>
                    ${explanation.missing_skills?.length ? `
                        <div class="missing-skills">
                            <span class="missing-label">Missing:</span>
                            ${explanation.missing_skills.map(s =>
                    `<span class="skill-tag missing">${this.escapeHtml(s)}</span>`
                ).join('')}
                        </div>
                    ` : ''}
                    ${explanation.career_tip ? `
                        <div class="career-tip">💡 ${this.escapeHtml(explanation.career_tip)}</div>
                    ` : ''}
                `;
                console.log('[DEBUG] Successfully updated explanation div');
            }
        } catch (error) {
            console.error('[ERROR] Explanation fetch failed:', error);
            console.error('[ERROR] Error details:', error.message, error.stack);
            const explanationDiv = cardElement.querySelector(`#explanation-${jobId} .explanation-content`);
            if (explanationDiv) {
                explanationDiv.innerHTML = `<p class="explanation-text">Good fit based on your profile.</p>`;
            }
        }
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
window.Cards = Cards;
