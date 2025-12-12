/**
 * Auth Module - Handles login and registration
 */

const Auth = {
    API_URL: '/api',

    /**
     * Initialize auth page
     */
    init() {
        this.bindTabs();
        this.bindForms();
        this.checkExistingAuth();
    },

    /**
     * Check if user is already logged in
     */
    checkExistingAuth() {
        const token = localStorage.getItem('token');
        // Only redirect if we're actually on the login page
        const isLoginPage = window.location.pathname.endsWith('login.html') ||
            window.location.pathname.endsWith('login');

        if (token && isLoginPage) {
            // Do NOT auto-redirect. This causes loops.
            console.log('User already has token, but staying on login page to avoid refresh loop.');
            // Optionally, we could show a "Continue as User" button here, but for safety, let them log in again.
        }
    },

    /**
     * Bind tab switching
     */
    bindTabs() {
        const tabs = document.querySelectorAll('.auth-tab');
        const forms = document.querySelectorAll('.auth-form');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.dataset.tab;

                // Update tabs
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Update forms
                forms.forEach(form => {
                    form.classList.remove('active');
                    if (form.id === `${targetTab}-form`) {
                        form.classList.add('active');
                    }
                });

                // Clear errors
                document.querySelectorAll('.form-error').forEach(err => {
                    err.classList.remove('show');
                    err.textContent = '';
                });
            });
        });
    },

    /**
     * Bind form submissions
     */
    bindForms() {
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');

        // Login form - both form submit AND button click
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleLogin(loginForm);
            });

            // Also add click handler to button as fallback
            const loginBtn = loginForm.querySelector('.btn-submit');
            if (loginBtn) {
                loginBtn.addEventListener('click', async (e) => {
                    e.preventDefault();
                    await this.handleLogin(loginForm);
                });
            }
        }

        // Register form - both form submit AND button click
        if (registerForm) {
            registerForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleRegister(registerForm);
            });

            // Also add click handler to button as fallback
            const registerBtn = registerForm.querySelector('.btn-submit');
            if (registerBtn) {
                registerBtn.addEventListener('click', async (e) => {
                    e.preventDefault();
                    await this.handleRegister(registerForm);
                });
            }
        }
    },

    /**
     * Handle login
     */
    async handleLogin(form) {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const submitBtn = form.querySelector('.btn-submit');
        const errorDiv = document.getElementById('login-error');

        // Show loading
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        errorDiv.classList.remove('show');

        try {
            const response = await fetch(`${this.API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login failed');
            }

            // Save token and user
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            // Success animation
            submitBtn.classList.remove('loading');
            submitBtn.classList.add('success');
            submitBtn.innerHTML = '<span>✓ Success!</span>';

            // Redirect to app
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);

        } catch (error) {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            errorDiv.textContent = error.message;
            errorDiv.classList.add('show');
        }
    },

    /**
     * Handle registration
     */
    async handleRegister(form) {
        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const confirm = document.getElementById('register-confirm').value;
        const submitBtn = form.querySelector('.btn-submit');
        const errorDiv = document.getElementById('register-error');

        // Validate passwords match
        if (password !== confirm) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.classList.add('show');
            return;
        }

        // Show loading
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        errorDiv.classList.remove('show');

        try {
            const response = await fetch(`${this.API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, name })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Registration failed');
            }

            // Save token and user
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            // Success animation
            submitBtn.classList.remove('loading');
            submitBtn.classList.add('success');
            submitBtn.innerHTML = '<span>✓ Account Created!</span>';

            // Redirect to app
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);

        } catch (error) {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            errorDiv.textContent = error.message;
            errorDiv.classList.add('show');
        }
    },

    /**
     * Logout user
     */
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    },

    /**
     * Get auth token
     */
    getToken() {
        return localStorage.getItem('token');
    },

    /**
     * Get current user
     */
    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    /**
     * Check if authenticated
     */
    isAuthenticated() {
        return !!this.getToken();
    }
};

// Initialize on DOM ready or immediately if already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        Auth.init();
    });
} else {
    // DOM already loaded
    Auth.init();
}

// Expose to window for module scripts
window.Auth = Auth;
