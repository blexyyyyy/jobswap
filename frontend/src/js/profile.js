/**
 * Profile Page Logic
 */

const Profile = {
    skills: new Set(),

    async init() {
        if (!API.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }

        this.bindEvents();
        await this.loadProfile();
    },

    bindEvents() {
        // File Upload
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('resume-upload');

        if (!dropZone || !fileInput) {
            console.error("Drop zone or file input not found");
            return;
        }

        dropZone.addEventListener('click', () => fileInput.click());

        // Prevent default drag behaviors on window to prevent opening file in browser
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropZone.classList.add('dragover');
        }

        function unhighlight(e) {
            dropZone.classList.remove('dragover');
        }

        dropZone.addEventListener('drop', (e) => {
            console.log("File dropped", e.dataTransfer.files);
            const files = e.dataTransfer.files;
            if (files.length) this.handleFileUpload(files[0]);
        });


        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) this.handleFileUpload(e.target.files[0]);
        });

        // Skills Input
        const skillInput = document.getElementById('skill-input');
        skillInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.addSkill(skillInput.value);
                skillInput.value = '';
            }
        });

        // Form Submit
        document.getElementById('profile-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveProfile();
        });
    },

    async loadProfile() {
        try {
            const response = await fetch(`${API.baseUrl}/auth/me`, {
                headers: API.getHeaders()
            });

            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = 'login.html';
                return;
            }

            const user = await response.json();

            // Populate form
            document.getElementById('name').value = user.name || '';
            document.getElementById('email').value = user.email || '';
            document.getElementById('phone').value = user.phone || '';
            document.getElementById('experience').value = user.experience_years || 0;
            document.getElementById('location').value = user.preferred_location || '';
            document.getElementById('seniority').value = user.preferred_seniority || '';

            // Skills
            if (user.skills) {
                const skillsList = typeof user.skills === 'string'
                    ? user.skills.split(',')
                    : user.skills;

                skillsList.forEach(s => this.addSkill(s));
            }

        } catch (error) {
            console.error('Failed to load profile:', error);
            this.showToast('Failed to load profile', 'error');
        }
    },

    async handleFileUpload(file) {
        const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
        const isWord = file.type.includes('word') ||
            file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
            file.name.toLowerCase().endsWith('.docx');

        if (!isPdf && !isWord) {
            this.showToast('Please upload a PDF or DOCX file', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // Show progress UI
        document.getElementById('drop-zone').style.display = 'none';
        document.getElementById('upload-progress').style.display = 'flex';

        try {
            console.log('Uploading resume:', file.name);
            const response = await fetch(`${API.baseUrl}/resume/upload`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${API.getToken()}` },
                body: formData
            });

            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = 'login.html';
                return;
            }

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Upload failed:', response.status, errorText);
                throw new Error(`Server Error (${response.status}): ${errorText}`);
            }

            const data = await response.json();
            console.log('Resume upload response:', data);
            console.log('Parsed data:', data.parsed_data);
            this.showToast('Resume parsed successfully!', 'success');
            this.updateFormFromResume(data.parsed_data);

        } catch (error) {
            console.error('Upload error:', error);
            this.showToast('Failed to process resume: ' + error.message, 'error');
        } finally {
            document.getElementById('drop-zone').style.display = 'block';
            document.getElementById('upload-progress').style.display = 'none';
        }
    },

    updateFormFromResume(data) {
        console.log('updateFormFromResume called with:', data);
        if (!data || Object.keys(data).length === 0) {
            console.warn('No parsed data to populate!');
            return;
        }

        // Use undefined checks instead of truthy to handle 0 and empty strings
        if (data.name !== undefined) document.getElementById('name').value = data.name;
        if (data.email !== undefined) document.getElementById('email').value = data.email;
        if (data.phone !== undefined) document.getElementById('phone').value = data.phone;
        if (data.experience_years !== undefined) document.getElementById('experience').value = data.experience_years;
        if (data.preferred_location !== undefined) document.getElementById('location').value = data.preferred_location;
        if (data.preferred_seniority !== undefined) document.getElementById('seniority').value = data.preferred_seniority;

        // Handle skills as array or comma-separated string
        if (data.skills) {
            const skillsList = typeof data.skills === 'string'
                ? data.skills.split(',').map(s => s.trim()).filter(s => s)
                : Array.isArray(data.skills) ? data.skills : [];
            skillsList.forEach(skill => this.addSkill(skill));
        }

        console.log('Form updated successfully');
    },

    addSkill(skill) {
        const cleanSkill = skill.trim();
        if (!cleanSkill || this.skills.has(cleanSkill)) return;

        this.skills.add(cleanSkill);

        const container = document.getElementById('skills-list');
        const pill = document.createElement('div');
        pill.className = 'skill-tag';
        pill.innerHTML = `
            ${cleanSkill}
            <span class="remove-skill" onclick="Profile.removeSkill('${cleanSkill}', this)">×</span>
        `;
        container.appendChild(pill);
    },

    removeSkill(skill, element) {
        this.skills.delete(skill);
        element.parentElement.remove();
    },

    async saveProfile() {
        const btn = document.getElementById('save-btn');
        btn.disabled = true;
        btn.textContent = 'Saving...';

        const profileData = {
            name: document.getElementById('name').value,
            phone: document.getElementById('phone').value,
            skills: Array.from(this.skills).join(','),
            experience_years: parseInt(document.getElementById('experience').value) || 0,
            preferred_location: document.getElementById('location').value,
            preferred_seniority: document.getElementById('seniority').value
        };

        try {
            const response = await fetch(`${API.baseUrl}/auth/profile`, {
                method: 'PUT',
                headers: API.getHeaders(),
                body: JSON.stringify(profileData)
            });

            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = 'login.html';
                return;
            }

            if (!response.ok) throw new Error('Update failed');

            this.showToast('Profile updated successfully!', 'success');

        } catch (error) {
            console.error('Save error:', error);
            this.showToast('Failed to update profile', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Save Profile';
        }
    },

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span>${message}</span>`;
        document.getElementById('toast-container').appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
};

document.addEventListener('DOMContentLoaded', () => Profile.init());

// Expose to window for module scripts
window.Profile = Profile;
