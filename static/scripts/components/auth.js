// Authentication Component
class AuthPage {
    constructor(app) {
        this.app = app;
        this.api = app.api;
        this.state = app.state;
        this.currentMode = 'login'; // 'login', 'register', 'forgot'
        this.isSubmitting = false;
    }

    async render(container) {
        container.innerHTML = `
            <div class="page-container auth-page" id="auth-page">
                <div class="auth-container">
                    <div class="auth-header">
                        <div class="auth-logo">
                            <div class="logo-icon">🌊</div>
                            <h1>Argo AI Agent</h1>
                            <p>Ocean Data Analysis Platform</p>
                        </div>
                    </div>
                    
                    <div class="auth-content">
                        <!-- Login Form -->
                        <div class="auth-form" id="login-form" style="display: ${this.currentMode === 'login' ? 'block' : 'none'}">
                            <h2>Sign In</h2>
                            <p class="auth-subtitle">Access your ocean data analytics dashboard</p>
                            
                            <form id="login-form-element">
                                <div class="form-group">
                                    <label for="login-email">Email Address</label>
                                    <input 
                                        type="email" 
                                        id="login-email" 
                                        required 
                                        placeholder="Enter your email"
                                        autocomplete="email"
                                    >
                                    <div class="field-error" id="login-email-error"></div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="login-password">Password</label>
                                    <div class="password-input">
                                        <input 
                                            type="password" 
                                            id="login-password" 
                                            required 
                                            placeholder="Enter your password"
                                            autocomplete="current-password"
                                        >
                                        <button type="button" class="password-toggle" data-target="login-password">
                                            👁️
                                        </button>
                                    </div>
                                    <div class="field-error" id="login-password-error"></div>
                                </div>
                                
                                <div class="form-options">
                                    <label class="checkbox">
                                        <input type="checkbox" id="remember-me">
                                        <span>Remember me</span>
                                    </label>
                                    <button type="button" class="link-button" onclick="app.auth.switchMode('forgot')">
                                        Forgot password?
                                    </button>
                                </div>
                                
                                <button type="submit" class="btn btn-primary btn-full" id="login-submit">
                                    Sign In
                                </button>
                            </form>
                            
                            <div class="auth-divider">
                                <span>or</span>
                            </div>
                            
                            <div class="social-auth">
                                <button class="btn btn-outline btn-full social-btn" data-provider="google">
                                    <span class="social-icon">🔍</span>
                                    Continue with Google
                                </button>
                                <button class="btn btn-outline btn-full social-btn" data-provider="github">
                                    <span class="social-icon">📱</span>
                                    Continue with GitHub
                                </button>
                            </div>
                            
                            <div class="auth-footer">
                                <p>Don't have an account? 
                                    <button type="button" class="link-button" onclick="app.auth.switchMode('register')">
                                        Sign up
                                    </button>
                                </p>
                            </div>
                        </div>
                        
                        <!-- Register Form -->
                        <div class="auth-form" id="register-form" style="display: ${this.currentMode === 'register' ? 'block' : 'none'}">
                            <h2>Create Account</h2>
                            <p class="auth-subtitle">Join the ocean research community</p>
                            
                            <form id="register-form-element">
                                <div class="form-group">
                                    <label for="register-name">Full Name</label>
                                    <input 
                                        type="text" 
                                        id="register-name" 
                                        required 
                                        placeholder="Enter your full name"
                                        autocomplete="name"
                                    >
                                    <div class="field-error" id="register-name-error"></div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="register-email">Email Address</label>
                                    <input 
                                        type="email" 
                                        id="register-email" 
                                        required 
                                        placeholder="Enter your email"
                                        autocomplete="email"
                                    >
                                    <div class="field-error" id="register-email-error"></div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="register-password">Password</label>
                                    <div class="password-input">
                                        <input 
                                            type="password" 
                                            id="register-password" 
                                            required 
                                            placeholder="Create a password"
                                            autocomplete="new-password"
                                        >
                                        <button type="button" class="password-toggle" data-target="register-password">
                                            👁️
                                        </button>
                                    </div>
                                    <div class="password-strength" id="password-strength"></div>
                                    <div class="field-error" id="register-password-error"></div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="confirm-password">Confirm Password</label>
                                    <div class="password-input">
                                        <input 
                                            type="password" 
                                            id="confirm-password" 
                                            required 
                                            placeholder="Confirm your password"
                                            autocomplete="new-password"
                                        >
                                        <button type="button" class="password-toggle" data-target="confirm-password">
                                            👁️
                                        </button>
                                    </div>
                                    <div class="field-error" id="confirm-password-error"></div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="organization">Organization (Optional)</label>
                                    <input 
                                        type="text" 
                                        id="organization" 
                                        placeholder="University, Research Institute, etc."
                                        autocomplete="organization"
                                    >
                                </div>
                                
                                <div class="form-options">
                                    <label class="checkbox">
                                        <input type="checkbox" id="agree-terms" required>
                                        <span>I agree to the <a href="#" target="_blank">Terms of Service</a> and <a href="#" target="_blank">Privacy Policy</a></span>
                                    </label>
                                </div>
                                
                                <button type="submit" class="btn btn-primary btn-full" id="register-submit">
                                    Create Account
                                </button>
                            </form>
                            
                            <div class="auth-footer">
                                <p>Already have an account? 
                                    <button type="button" class="link-button" onclick="app.auth.switchMode('login')">
                                        Sign in
                                    </button>
                                </p>
                            </div>
                        </div>
                        
                        <!-- Forgot Password Form -->
                        <div class="auth-form" id="forgot-form" style="display: ${this.currentMode === 'forgot' ? 'block' : 'none'}">
                            <h2>Reset Password</h2>
                            <p class="auth-subtitle">Enter your email to receive reset instructions</p>
                            
                            <form id="forgot-form-element">
                                <div class="form-group">
                                    <label for="forgot-email">Email Address</label>
                                    <input 
                                        type="email" 
                                        id="forgot-email" 
                                        required 
                                        placeholder="Enter your email"
                                        autocomplete="email"
                                    >
                                    <div class="field-error" id="forgot-email-error"></div>
                                </div>
                                
                                <button type="submit" class="btn btn-primary btn-full" id="forgot-submit">
                                    Send Reset Link
                                </button>
                            </form>
                            
                            <div class="auth-footer">
                                <p>Remember your password? 
                                    <button type="button" class="link-button" onclick="app.auth.switchMode('login')">
                                        Sign in
                                    </button>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Demo Access Banner -->
                <div class="demo-banner">
                    <div class="demo-content">
                        <h3>🚀 Try Demo Access</h3>
                        <p>Explore the platform without registration</p>
                        <button class="btn btn-outline" id="demo-access">
                            Continue as Guest
                        </button>
                    </div>
                </div>
                
                <!-- Loading Overlay -->
                <div class="auth-loading" id="auth-loading" style="display: none;">
                    <div class="loading-spinner"></div>
                    <p>Processing...</p>
                </div>
            </div>
        `;

        this.attachEventListeners();
        this.setupValidation();
        this.checkExistingAuth();
    }

    attachEventListeners() {
        // Form submissions
        document.getElementById('login-form-element').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        document.getElementById('register-form-element').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });

        document.getElementById('forgot-form-element').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleForgotPassword();
        });

        // Password toggle buttons
        document.querySelectorAll('.password-toggle').forEach(button => {
            button.addEventListener('click', (e) => {
                this.togglePasswordVisibility(e.target.dataset.target);
            });
        });

        // Social auth buttons
        document.querySelectorAll('.social-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleSocialAuth(e.target.dataset.provider);
            });
        });

        // Demo access
        document.getElementById('demo-access').addEventListener('click', () => {
            this.handleDemoAccess();
        });

        // Password strength checker
        const passwordInput = document.getElementById('register-password');
        if (passwordInput) {
            passwordInput.addEventListener('input', (e) => {
                this.checkPasswordStrength(e.target.value);
            });
        }

        // Password confirmation checker
        const confirmInput = document.getElementById('confirm-password');
        if (confirmInput) {
            confirmInput.addEventListener('input', () => {
                this.validatePasswordMatch();
            });
        }
    }

    setupValidation() {
        // Real-time validation for email fields
        document.querySelectorAll('input[type="email"]').forEach(input => {
            input.addEventListener('blur', () => {
                this.validateEmail(input);
            });
        });

        // Real-time validation for required fields
        document.querySelectorAll('input[required]').forEach(input => {
            input.addEventListener('blur', () => {
                this.validateRequired(input);
            });
        });
    }

    switchMode(mode) {
        if (this.isSubmitting) return;

        // Hide current form
        document.getElementById(`${this.currentMode}-form`).style.display = 'none';

        // Show new form
        document.getElementById(`${mode}-form`).style.display = 'block';

        this.currentMode = mode;

        // Clear any existing errors
        this.clearErrors();

        // Focus on first input
        setTimeout(() => {
            const firstInput = document.querySelector(`#${mode}-form input`);
            if (firstInput) firstInput.focus();
        }, 100);
    }

    async handleLogin() {
        if (this.isSubmitting) return;

        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        const rememberMe = document.getElementById('remember-me').checked;

        // Validate inputs
        if (!this.validateLoginForm(email, password)) {
            return;
        }

        this.setSubmitting(true);

        try {
            // For demo purposes, we'll simulate authentication
            // In a real app, this would call the API
            await this.simulateAuth('login', { email, password, rememberMe });

            // Set authentication state
            this.setAuthenticatedUser({
                id: 'demo_user_' + Date.now(),
                email: email,
                name: email.split('@')[0],
                role: 'user',
                loginTime: new Date().toISOString()
            });

            // Navigate to dashboard
            this.app.router.navigate('/dashboard');

        } catch (error) {
            console.error('Login failed:', error);
            this.showError('login', 'Invalid email or password. Please try again.');
        } finally {
            this.setSubmitting(false);
        }
    }

    async handleRegister() {
        if (this.isSubmitting) return;

        const name = document.getElementById('register-name').value.trim();
        const email = document.getElementById('register-email').value.trim();
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const organization = document.getElementById('organization').value.trim();
        const agreeTerms = document.getElementById('agree-terms').checked;

        // Validate inputs
        if (!this.validateRegisterForm(name, email, password, confirmPassword, agreeTerms)) {
            return;
        }

        this.setSubmitting(true);

        try {
            // Simulate registration
            await this.simulateAuth('register', { name, email, password, organization });

            // Set authentication state
            this.setAuthenticatedUser({
                id: 'new_user_' + Date.now(),
                email: email,
                name: name,
                organization: organization,
                role: 'user',
                registrationTime: new Date().toISOString()
            });

            // Show success message and navigate
            this.showSuccess('Account created successfully! Welcome to Argo AI Agent.');

            setTimeout(() => {
                this.app.router.navigate('/dashboard');
            }, 2000);

        } catch (error) {
            console.error('Registration failed:', error);
            this.showError('register', 'Registration failed. Please try again.');
        } finally {
            this.setSubmitting(false);
        }
    }

    async handleForgotPassword() {
        if (this.isSubmitting) return;

        const email = document.getElementById('forgot-email').value.trim();

        if (!this.validateEmail(document.getElementById('forgot-email'))) {
            return;
        }

        this.setSubmitting(true);

        try {
            // Simulate password reset
            await this.simulateAuth('forgot', { email });

            this.showSuccess('Password reset instructions have been sent to your email.');

            setTimeout(() => {
                this.switchMode('login');
            }, 3000);

        } catch (error) {
            console.error('Password reset failed:', error);
            this.showError('forgot', 'Failed to send reset email. Please try again.');
        } finally {
            this.setSubmitting(false);
        }
    }

    handleSocialAuth(provider) {
        if (this.isSubmitting) return;

        // Simulate social authentication
        this.setSubmitting(true);

        setTimeout(() => {
            this.setAuthenticatedUser({
                id: `${provider}_user_` + Date.now(),
                email: `user@${provider}.com`,
                name: `${provider.charAt(0).toUpperCase() + provider.slice(1)} User`,
                provider: provider,
                role: 'user',
                loginTime: new Date().toISOString()
            });

            this.app.router.navigate('/dashboard');
            this.setSubmitting(false);
        }, 2000);
    }

    handleDemoAccess() {
        // Set demo user state
        this.setAuthenticatedUser({
            id: 'demo_user',
            email: 'demo@argo-ai.com',
            name: 'Demo User',
            role: 'demo',
            isDemoUser: true,
            loginTime: new Date().toISOString()
        });

        // Navigate to dashboard
        this.app.router.navigate('/dashboard');
    }

    validateLoginForm(email, password) {
        let isValid = true;

        if (!email) {
            this.showFieldError('login-email', 'Email is required');
            isValid = false;
        } else if (!this.isValidEmail(email)) {
            this.showFieldError('login-email', 'Please enter a valid email address');
            isValid = false;
        }

        if (!password) {
            this.showFieldError('login-password', 'Password is required');
            isValid = false;
        }

        return isValid;
    }

    validateRegisterForm(name, email, password, confirmPassword, agreeTerms) {
        let isValid = true;

        if (!name) {
            this.showFieldError('register-name', 'Full name is required');
            isValid = false;
        }

        if (!email) {
            this.showFieldError('register-email', 'Email is required');
            isValid = false;
        } else if (!this.isValidEmail(email)) {
            this.showFieldError('register-email', 'Please enter a valid email address');
            isValid = false;
        }

        if (!password) {
            this.showFieldError('register-password', 'Password is required');
            isValid = false;
        } else if (!this.isStrongPassword(password)) {
            this.showFieldError('register-password', 'Password must be at least 8 characters with uppercase, lowercase, and numbers');
            isValid = false;
        }

        if (password !== confirmPassword) {
            this.showFieldError('confirm-password', 'Passwords do not match');
            isValid = false;
        }

        if (!agreeTerms) {
            this.showError('register', 'You must agree to the Terms of Service');
            isValid = false;
        }

        return isValid;
    }

    validateEmail(input) {
        const email = input.value.trim();
        const isValid = email && this.isValidEmail(email);

        if (!isValid) {
            this.showFieldError(input.id, 'Please enter a valid email address');
        } else {
            this.clearFieldError(input.id);
        }

        return isValid;
    }

    validateRequired(input) {
        const value = input.value.trim();
        const isValid = value.length > 0;

        if (!isValid) {
            this.showFieldError(input.id, 'This field is required');
        } else {
            this.clearFieldError(input.id);
        }

        return isValid;
    }

    validatePasswordMatch() {
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        if (confirmPassword && password !== confirmPassword) {
            this.showFieldError('confirm-password', 'Passwords do not match');
            return false;
        } else {
            this.clearFieldError('confirm-password');
            return true;
        }
    }

    checkPasswordStrength(password) {
        const strengthIndicator = document.getElementById('password-strength');
        if (!strengthIndicator) return;

        let strength = 0;
        let feedback = [];

        if (password.length >= 8) strength++;
        else feedback.push('At least 8 characters');

        if (/[a-z]/.test(password)) strength++;
        else feedback.push('Lowercase letter');

        if (/[A-Z]/.test(password)) strength++;
        else feedback.push('Uppercase letter');

        if (/[0-9]/.test(password)) strength++;
        else feedback.push('Number');

        if (/[^A-Za-z0-9]/.test(password)) strength++;
        else feedback.push('Special character');

        const strengthLevels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const strengthColors = ['#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#2ecc71'];

        strengthIndicator.innerHTML = `
            <div class="strength-bar">
                <div class="strength-fill" style="width: ${(strength / 5) * 100}%; background-color: ${strengthColors[strength - 1] || '#e74c3c'}"></div>
            </div>
            <div class="strength-text">
                ${strengthLevels[strength - 1] || 'Very Weak'}
                ${feedback.length > 0 ? ` - Missing: ${feedback.join(', ')}` : ''}
            </div>
        `;
    }

    togglePasswordVisibility(targetId) {
        const input = document.getElementById(targetId);
        const button = document.querySelector(`[data-target="${targetId}"]`);

        if (input.type === 'password') {
            input.type = 'text';
            button.textContent = '🙈';
        } else {
            input.type = 'password';
            button.textContent = '👁️';
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isStrongPassword(password) {
        // At least 8 characters, uppercase, lowercase, and number
        return password.length >= 8 &&
            /[a-z]/.test(password) &&
            /[A-Z]/.test(password) &&
            /[0-9]/.test(password);
    }

    showFieldError(fieldId, message) {
        const errorElement = document.getElementById(`${fieldId}-error`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }

        const input = document.getElementById(fieldId);
        if (input) {
            input.classList.add('error');
        }
    }

    clearFieldError(fieldId) {
        const errorElement = document.getElementById(`${fieldId}-error`);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }

        const input = document.getElementById(fieldId);
        if (input) {
            input.classList.remove('error');
        }
    }

    showError(form, message) {
        // Create or update error banner
        let errorBanner = document.getElementById('auth-error');
        if (!errorBanner) {
            errorBanner = document.createElement('div');
            errorBanner.id = 'auth-error';
            errorBanner.className = 'alert alert-error';

            const formElement = document.getElementById(`${form}-form`);
            formElement.insertBefore(errorBanner, formElement.firstChild);
        }

        errorBanner.innerHTML = `
            <span>❌ ${message}</span>
            <button onclick="this.parentElement.remove()" class="btn btn-sm">✕</button>
        `;
        errorBanner.style.display = 'block';
    }

    showSuccess(message) {
        // Create success banner
        const successBanner = document.createElement('div');
        successBanner.className = 'alert alert-success';
        successBanner.innerHTML = `
            <span>✅ ${message}</span>
        `;

        const container = document.getElementById('auth-page');
        container.insertBefore(successBanner, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            successBanner.remove();
        }, 5000);
    }

    clearErrors() {
        // Clear field errors
        document.querySelectorAll('.field-error').forEach(error => {
            error.textContent = '';
            error.style.display = 'none';
        });

        // Clear input error states
        document.querySelectorAll('input.error').forEach(input => {
            input.classList.remove('error');
        });

        // Clear form errors
        const errorBanner = document.getElementById('auth-error');
        if (errorBanner) {
            errorBanner.remove();
        }
    }

    setSubmitting(isSubmitting) {
        this.isSubmitting = isSubmitting;

        // Update submit buttons
        document.querySelectorAll('button[type="submit"]').forEach(button => {
            button.disabled = isSubmitting;
            if (isSubmitting) {
                button.textContent = 'Processing...';
            }
        });

        // Show/hide loading overlay
        const loadingOverlay = document.getElementById('auth-loading');
        if (loadingOverlay) {
            loadingOverlay.style.display = isSubmitting ? 'flex' : 'none';
        }

        // Restore original button text when not submitting
        if (!isSubmitting) {
            setTimeout(() => {
                document.getElementById('login-submit').textContent = 'Sign In';
                document.getElementById('register-submit').textContent = 'Create Account';
                document.getElementById('forgot-submit').textContent = 'Send Reset Link';
            }, 100);
        }
    }

    async simulateAuth(type, data) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Simulate random failures for demo
        if (Math.random() < 0.1) { // 10% failure rate
            throw new Error(`${type} failed`);
        }

        return { success: true, data };
    }

    setAuthenticatedUser(user) {
        // Store user in state
        this.state.set('currentUser', user);
        this.state.set('isAuthenticated', true);

        // Store in localStorage for persistence
        if (user.rememberMe !== false) {
            localStorage.setItem('argoUser', JSON.stringify(user));
        }

        // Update app state
        this.app.currentUser = user;
        this.app.isAuthenticated = true;

        console.log('User authenticated:', user);
    }

    checkExistingAuth() {
        // Check for existing authentication
        const storedUser = localStorage.getItem('argoUser');
        if (storedUser) {
            try {
                const user = JSON.parse(storedUser);

                // Check if session is still valid (e.g., within 30 days)
                const loginTime = new Date(user.loginTime || user.registrationTime);
                const now = new Date();
                const daysDiff = (now - loginTime) / (1000 * 60 * 60 * 24);

                if (daysDiff < 30) {
                    this.setAuthenticatedUser(user);
                    this.app.router.navigate('/dashboard');
                    return;
                }
            } catch (error) {
                console.error('Invalid stored user data:', error);
                localStorage.removeItem('argoUser');
            }
        }

        // Check state for current session
        const stateUser = this.state.get('currentUser');
        if (stateUser && this.state.get('isAuthenticated')) {
            this.app.currentUser = stateUser;
            this.app.isAuthenticated = true;
        }
    }

    logout() {
        // Clear authentication state
        this.state.set('currentUser', null);
        this.state.set('isAuthenticated', false);
        localStorage.removeItem('argoUser');

        // Update app state
        this.app.currentUser = null;
        this.app.isAuthenticated = false;

        // Navigate to login
        this.app.router.navigate('/auth');
    }

    destroy() {
        // Cleanup any timers or resources
        this.clearErrors();
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthPage;
}
