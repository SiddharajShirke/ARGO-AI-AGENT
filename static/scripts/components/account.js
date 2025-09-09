// User Account Management Component
class AccountPage {
    constructor(app) {
        this.app = app;
        this.api = app.api;
        this.state = app.state;
        this.currentTab = 'profile';
        this.isEditing = false;
        this.unsavedChanges = false;
    }

    async render(container) {
        const user = this.app.currentUser || this.state.get('currentUser');

        if (!user) {
            this.app.router.navigate('/auth');
            return;
        }

        container.innerHTML = `
            <div class="page-container" id="account-page">
                <div class="account-header">
                    <div class="user-info">
                        <div class="user-avatar">
                            <div class="avatar-circle">
                                ${this.getInitials(user.name)}
                            </div>
                            <button class="avatar-edit" id="change-avatar">📷</button>
                        </div>
                        <div class="user-details">
                            <h1>${user.name}</h1>
                            <p class="user-email">${user.email}</p>
                            <div class="user-meta">
                                <span class="user-role">${this.formatRole(user.role)}</span>
                                ${user.organization ? `<span class="user-org">${user.organization}</span>` : ''}
                                ${user.isDemoUser ? '<span class="demo-badge">Demo User</span>' : ''}
                            </div>
                        </div>
                    </div>
                    <div class="account-actions">
                        <button class="btn btn-outline" id="export-data">📤 Export Data</button>
                        <button class="btn btn-secondary" id="account-settings">⚙️ Settings</button>
                    </div>
                </div>
                
                <div class="account-nav">
                    <button class="nav-tab ${this.currentTab === 'profile' ? 'active' : ''}" data-tab="profile">
                        👤 Profile
                    </button>
                    <button class="nav-tab ${this.currentTab === 'preferences' ? 'active' : ''}" data-tab="preferences">
                        🎛️ Preferences
                    </button>
                    <button class="nav-tab ${this.currentTab === 'security' ? 'active' : ''}" data-tab="security">
                        🔒 Security
                    </button>
                    <button class="nav-tab ${this.currentTab === 'usage' ? 'active' : ''}" data-tab="usage">
                        📊 Usage
                    </button>
                    <button class="nav-tab ${this.currentTab === 'notifications' ? 'active' : ''}" data-tab="notifications">
                        🔔 Notifications
                    </button>
                </div>
                
                <div class="account-content">
                    <!-- Profile Tab -->
                    <div class="account-tab" id="profile-tab" style="display: ${this.currentTab === 'profile' ? 'block' : 'none'}">
                        <div class="tab-header">
                            <h2>Profile Information</h2>
                            <div class="tab-actions">
                                <button class="btn btn-outline" id="edit-profile" style="display: ${this.isEditing ? 'none' : 'inline-block'}">
                                    ✏️ Edit Profile
                                </button>
                                <button class="btn btn-primary" id="save-profile" style="display: ${this.isEditing ? 'inline-block' : 'none'}">
                                    💾 Save Changes
                                </button>
                                <button class="btn btn-outline" id="cancel-edit" style="display: ${this.isEditing ? 'inline-block' : 'none'}">
                                    ❌ Cancel
                                </button>
                            </div>
                        </div>
                        
                        <div class="profile-form">
                            <div class="form-section">
                                <h3>Basic Information</h3>
                                <div class="form-grid">
                                    <div class="form-group">
                                        <label for="profile-name">Full Name</label>
                                        <input 
                                            type="text" 
                                            id="profile-name" 
                                            value="${user.name}" 
                                            ${this.isEditing ? '' : 'readonly'}
                                        >
                                    </div>
                                    <div class="form-group">
                                        <label for="profile-email">Email Address</label>
                                        <input 
                                            type="email" 
                                            id="profile-email" 
                                            value="${user.email}" 
                                            readonly
                                        >
                                        <small class="field-help">Email cannot be changed. Contact support if needed.</small>
                                    </div>
                                    <div class="form-group">
                                        <label for="profile-organization">Organization</label>
                                        <input 
                                            type="text" 
                                            id="profile-organization" 
                                            value="${user.organization || ''}" 
                                            placeholder="University, Research Institute, etc."
                                            ${this.isEditing ? '' : 'readonly'}
                                        >
                                    </div>
                                    <div class="form-group">
                                        <label for="profile-title">Job Title</label>
                                        <input 
                                            type="text" 
                                            id="profile-title" 
                                            value="${user.title || ''}" 
                                            placeholder="Research Scientist, Professor, etc."
                                            ${this.isEditing ? '' : 'readonly'}
                                        >
                                    </div>
                                </div>
                            </div>
                            
                            <div class="form-section">
                                <h3>Research Interests</h3>
                                <div class="form-group">
                                    <label for="research-areas">Research Areas</label>
                                    <div class="tag-input" id="research-tags">
                                        ${this.renderResearchTags(user.researchAreas || [])}
                                        ${this.isEditing ? '<input type="text" placeholder="Add research area..." id="new-research-tag">' : ''}
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="profile-bio">Bio</label>
                                    <textarea 
                                        id="profile-bio" 
                                        rows="4" 
                                        placeholder="Tell us about your research background..."
                                        ${this.isEditing ? '' : 'readonly'}
                                    >${user.bio || ''}</textarea>
                                </div>
                            </div>
                            
                            <div class="form-section">
                                <h3>Contact Information</h3>
                                <div class="form-grid">
                                    <div class="form-group">
                                        <label for="profile-phone">Phone</label>
                                        <input 
                                            type="tel" 
                                            id="profile-phone" 
                                            value="${user.phone || ''}" 
                                            ${this.isEditing ? '' : 'readonly'}
                                        >
                                    </div>
                                    <div class="form-group">
                                        <label for="profile-location">Location</label>
                                        <input 
                                            type="text" 
                                            id="profile-location" 
                                            value="${user.location || ''}" 
                                            placeholder="City, Country"
                                            ${this.isEditing ? '' : 'readonly'}
                                        >
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Preferences Tab -->
                    <div class="account-tab" id="preferences-tab" style="display: ${this.currentTab === 'preferences' ? 'block' : 'none'}">
                        <div class="tab-header">
                            <h2>Application Preferences</h2>
                        </div>
                        
                        <div class="preferences-sections">
                            <div class="pref-section">
                                <h3>🎨 Appearance</h3>
                                <div class="pref-group">
                                    <label>Theme</label>
                                    <select id="theme-preference">
                                        <option value="light">Light</option>
                                        <option value="dark">Dark</option>
                                        <option value="auto">Auto (System)</option>
                                    </select>
                                </div>
                                <div class="pref-group">
                                    <label>Language</label>
                                    <select id="language-preference">
                                        <option value="en">English</option>
                                        <option value="es">Español</option>
                                        <option value="fr">Français</option>
                                        <option value="de">Deutsch</option>
                                        <option value="zh">中文</option>
                                    </select>
                                </div>
                                <div class="pref-group">
                                    <label>Font Size</label>
                                    <select id="font-size-preference">
                                        <option value="small">Small</option>
                                        <option value="medium">Medium</option>
                                        <option value="large">Large</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="pref-section">
                                <h3>📊 Dashboard</h3>
                                <div class="pref-group">
                                    <label>Default View</label>
                                    <select id="default-view">
                                        <option value="overview">Overview</option>
                                        <option value="search">Search</option>
                                        <option value="analytics">Analytics</option>
                                    </select>
                                </div>
                                <div class="pref-group">
                                    <label>Items per Page</label>
                                    <select id="page-size">
                                        <option value="25">25</option>
                                        <option value="50">50</option>
                                        <option value="100">100</option>
                                    </select>
                                </div>
                                <div class="pref-group checkbox-group">
                                    <label class="checkbox">
                                        <input type="checkbox" id="auto-refresh">
                                        <span>Auto-refresh data</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="pref-section">
                                <h3>🔬 Data Analysis</h3>
                                <div class="pref-group">
                                    <label>Default Region</label>
                                    <select id="default-region">
                                        <option value="">All Regions</option>
                                        <option value="atlantic">Atlantic Ocean</option>
                                        <option value="pacific">Pacific Ocean</option>
                                        <option value="indian">Indian Ocean</option>
                                    </select>
                                </div>
                                <div class="pref-group">
                                    <label>Temperature Unit</label>
                                    <select id="temp-unit">
                                        <option value="celsius">Celsius (°C)</option>
                                        <option value="fahrenheit">Fahrenheit (°F)</option>
                                        <option value="kelvin">Kelvin (K)</option>
                                    </select>
                                </div>
                                <div class="pref-group">
                                    <label>Depth Unit</label>
                                    <select id="depth-unit">
                                        <option value="meters">Meters (m)</option>
                                        <option value="feet">Feet (ft)</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="pref-actions">
                            <button class="btn btn-primary" id="save-preferences">💾 Save Preferences</button>
                            <button class="btn btn-outline" id="reset-preferences">🔄 Reset to Defaults</button>
                        </div>
                    </div>
                    
                    <!-- Security Tab -->
                    <div class="account-tab" id="security-tab" style="display: ${this.currentTab === 'security' ? 'block' : 'none'}">
                        <div class="tab-header">
                            <h2>Security Settings</h2>
                        </div>
                        
                        <div class="security-sections">
                            <div class="security-section">
                                <h3>🔐 Password</h3>
                                <div class="current-status">
                                    <span class="status-good">Password last changed: ${this.formatDate(user.passwordLastChanged)}</span>
                                </div>
                                <button class="btn btn-outline" id="change-password">Change Password</button>
                                
                                <div class="password-change-form" id="password-form" style="display: none;">
                                    <div class="form-group">
                                        <label for="current-password">Current Password</label>
                                        <input type="password" id="current-password" required>
                                    </div>
                                    <div class="form-group">
                                        <label for="new-password">New Password</label>
                                        <input type="password" id="new-password" required>
                                        <div class="password-strength" id="new-password-strength"></div>
                                    </div>
                                    <div class="form-group">
                                        <label for="confirm-new-password">Confirm New Password</label>
                                        <input type="password" id="confirm-new-password" required>
                                    </div>
                                    <div class="form-actions">
                                        <button class="btn btn-primary" id="update-password">Update Password</button>
                                        <button class="btn btn-outline" id="cancel-password">Cancel</button>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="security-section">
                                <h3>🔒 Two-Factor Authentication</h3>
                                <div class="current-status">
                                    <span class="status-${user.twoFactorEnabled ? 'good' : 'warning'}">
                                        ${user.twoFactorEnabled ? '✅ Enabled' : '⚠️ Disabled'}
                                    </span>
                                </div>
                                <p>Add an extra layer of security to your account with 2FA.</p>
                                <button class="btn ${user.twoFactorEnabled ? 'btn-outline' : 'btn-primary'}" id="toggle-2fa">
                                    ${user.twoFactorEnabled ? 'Disable 2FA' : 'Enable 2FA'}
                                </button>
                            </div>
                            
                            <div class="security-section">
                                <h3>📱 Active Sessions</h3>
                                <div class="sessions-list" id="sessions-list">
                                    <div class="session-item current">
                                        <div class="session-info">
                                            <div class="session-device">🖥️ Current Session</div>
                                            <div class="session-details">
                                                <span>Started: ${this.formatDate(user.loginTime)}</span>
                                                <span>${this.getBrowserInfo()}</span>
                                            </div>
                                        </div>
                                        <span class="session-status current">Current</span>
                                    </div>
                                </div>
                                <button class="btn btn-outline" id="logout-all">🚪 Logout All Other Sessions</button>
                            </div>
                            
                            <div class="security-section">
                                <h3>🗑️ Account Deletion</h3>
                                <p class="warning-text">
                                    ⚠️ Once you delete your account, there is no going back. 
                                    Please be certain. All your data will be permanently removed.
                                </p>
                                <button class="btn btn-danger" id="delete-account">Delete Account</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Usage Tab -->
                    <div class="account-tab" id="usage-tab" style="display: ${this.currentTab === 'usage' ? 'block' : 'none'}">
                        <div class="tab-header">
                            <h2>Usage Statistics</h2>
                        </div>
                        
                        <div class="usage-overview">
                            <div class="usage-metric">
                                <div class="metric-icon">📊</div>
                                <div class="metric-info">
                                    <div class="metric-value">${this.getRandomMetric(150, 500)}</div>
                                    <div class="metric-label">Queries This Month</div>
                                </div>
                            </div>
                            <div class="usage-metric">
                                <div class="metric-icon">⏱️</div>
                                <div class="metric-info">
                                    <div class="metric-value">${this.getRandomMetric(25, 100)}h</div>
                                    <div class="metric-label">Time Spent</div>
                                </div>
                            </div>
                            <div class="usage-metric">
                                <div class="metric-icon">💾</div>
                                <div class="metric-info">
                                    <div class="metric-value">${this.getRandomMetric(10, 50)}</div>
                                    <div class="metric-label">Data Exports</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="usage-charts">
                            <div class="chart-container">
                                <h3>Activity Over Time</h3>
                                <div class="activity-chart" id="activity-chart">
                                    <!-- Simple activity visualization -->
                                    ${this.renderActivityChart()}
                                </div>
                            </div>
                            
                            <div class="usage-breakdown">
                                <h3>Feature Usage</h3>
                                <div class="feature-list">
                                    <div class="feature-item">
                                        <span class="feature-name">AI Chat</span>
                                        <div class="feature-bar">
                                            <div class="bar-fill" style="width: 85%;"></div>
                                        </div>
                                        <span class="feature-percent">85%</span>
                                    </div>
                                    <div class="feature-item">
                                        <span class="feature-name">Dashboard</span>
                                        <div class="feature-bar">
                                            <div class="bar-fill" style="width: 70%;"></div>
                                        </div>
                                        <span class="feature-percent">70%</span>
                                    </div>
                                    <div class="feature-item">
                                        <span class="feature-name">Data Export</span>
                                        <div class="feature-bar">
                                            <div class="bar-fill" style="width: 45%;"></div>
                                        </div>
                                        <span class="feature-percent">45%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Notifications Tab -->
                    <div class="account-tab" id="notifications-tab" style="display: ${this.currentTab === 'notifications' ? 'block' : 'none'}">
                        <div class="tab-header">
                            <h2>Notification Settings</h2>
                        </div>
                        
                        <div class="notification-sections">
                            <div class="notif-section">
                                <h3>📧 Email Notifications</h3>
                                <div class="notif-options">
                                    <label class="checkbox">
                                        <input type="checkbox" id="email-system-updates" checked>
                                        <span>System updates and maintenance</span>
                                    </label>
                                    <label class="checkbox">
                                        <input type="checkbox" id="email-data-alerts" checked>
                                        <span>Data quality alerts</span>
                                    </label>
                                    <label class="checkbox">
                                        <input type="checkbox" id="email-analysis-complete">
                                        <span>Analysis completion notifications</span>
                                    </label>
                                    <label class="checkbox">
                                        <input type="checkbox" id="email-newsletter">
                                        <span>Monthly newsletter</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="notif-section">
                                <h3>🔔 Browser Notifications</h3>
                                <div class="notif-options">
                                    <label class="checkbox">
                                        <input type="checkbox" id="browser-chat-responses" checked>
                                        <span>AI chat responses</span>
                                    </label>
                                    <label class="checkbox">
                                        <input type="checkbox" id="browser-data-updates">
                                        <span>Real-time data updates</span>
                                    </label>
                                    <label class="checkbox">
                                        <input type="checkbox" id="browser-export-ready">
                                        <span>Export ready notifications</span>
                                    </label>
                                </div>
                                <button class="btn btn-outline" id="test-notification">🧪 Test Notification</button>
                            </div>
                            
                            <div class="notif-section">
                                <h3>⏰ Frequency</h3>
                                <div class="frequency-options">
                                    <label>
                                        <input type="radio" name="notification-frequency" value="immediate" checked>
                                        <span>Immediate</span>
                                    </label>
                                    <label>
                                        <input type="radio" name="notification-frequency" value="hourly">
                                        <span>Hourly digest</span>
                                    </label>
                                    <label>
                                        <input type="radio" name="notification-frequency" value="daily">
                                        <span>Daily digest</span>
                                    </label>
                                    <label>
                                        <input type="radio" name="notification-frequency" value="weekly">
                                        <span>Weekly digest</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                        
                        <div class="notif-actions">
                            <button class="btn btn-primary" id="save-notifications">💾 Save Notification Settings</button>
                        </div>
                    </div>
                </div>
                
                <!-- Unsaved Changes Warning -->
                <div class="unsaved-warning" id="unsaved-warning" style="display: none;">
                    <div class="warning-content">
                        <span>⚠️ You have unsaved changes</span>
                        <div class="warning-actions">
                            <button class="btn btn-sm btn-primary" id="save-changes">Save</button>
                            <button class="btn btn-sm btn-outline" id="discard-changes">Discard</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <input type="file" id="avatar-input" accept="image/*" style="display: none;">
        `;

        this.attachEventListeners();
        this.loadUserPreferences();
    }

    attachEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Profile editing
        document.getElementById('edit-profile').addEventListener('click', () => {
            this.toggleEditMode(true);
        });

        document.getElementById('save-profile').addEventListener('click', () => {
            this.saveProfile();
        });

        document.getElementById('cancel-edit').addEventListener('click', () => {
            this.cancelEdit();
        });

        // Avatar change
        document.getElementById('change-avatar').addEventListener('click', () => {
            document.getElementById('avatar-input').click();
        });

        document.getElementById('avatar-input').addEventListener('change', (e) => {
            this.handleAvatarChange(e.target.files[0]);
        });

        // Preferences
        document.getElementById('save-preferences').addEventListener('click', () => {
            this.savePreferences();
        });

        document.getElementById('reset-preferences').addEventListener('click', () => {
            this.resetPreferences();
        });

        // Security
        document.getElementById('change-password').addEventListener('click', () => {
            this.togglePasswordForm(true);
        });

        document.getElementById('cancel-password').addEventListener('click', () => {
            this.togglePasswordForm(false);
        });

        document.getElementById('update-password').addEventListener('click', () => {
            this.updatePassword();
        });

        // Other actions
        document.getElementById('export-data').addEventListener('click', () => {
            this.exportUserData();
        });

        document.getElementById('test-notification').addEventListener('click', () => {
            this.testNotification();
        });

        // Track changes for unsaved warning
        this.trackFormChanges();
    }

    switchTab(tab) {
        if (this.unsavedChanges && !confirm('You have unsaved changes. Continue?')) {
            return;
        }

        // Hide current tab
        document.getElementById(`${this.currentTab}-tab`).style.display = 'none';
        document.querySelector(`[data-tab="${this.currentTab}"]`).classList.remove('active');

        // Show new tab
        document.getElementById(`${tab}-tab`).style.display = 'block';
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

        this.currentTab = tab;
        this.unsavedChanges = false;
        this.updateUnsavedWarning();
    }

    toggleEditMode(editing) {
        this.isEditing = editing;

        // Toggle readonly state
        document.querySelectorAll('#profile-tab input:not([readonly])').forEach(input => {
            input.readOnly = !editing;
        });

        document.getElementById('profile-bio').readOnly = !editing;

        // Toggle buttons
        document.getElementById('edit-profile').style.display = editing ? 'none' : 'inline-block';
        document.getElementById('save-profile').style.display = editing ? 'inline-block' : 'none';
        document.getElementById('cancel-edit').style.display = editing ? 'inline-block' : 'none';

        // Show/hide research tag input
        const tagInput = document.getElementById('new-research-tag');
        if (tagInput) {
            tagInput.style.display = editing ? 'inline-block' : 'none';
        }
    }

    async saveProfile() {
        const profileData = {
            name: document.getElementById('profile-name').value,
            organization: document.getElementById('profile-organization').value,
            title: document.getElementById('profile-title').value,
            bio: document.getElementById('profile-bio').value,
            phone: document.getElementById('profile-phone').value,
            location: document.getElementById('profile-location').value
        };

        try {
            // Update user object
            const user = this.app.currentUser;
            Object.assign(user, profileData);

            // Save to state
            this.state.set('currentUser', user);

            // Update localStorage
            localStorage.setItem('argoUser', JSON.stringify(user));

            this.toggleEditMode(false);
            this.showSuccess('Profile updated successfully');

        } catch (error) {
            console.error('Failed to save profile:', error);
            this.showError('Failed to save profile. Please try again.');
        }
    }

    cancelEdit() {
        if (confirm('Discard changes?')) {
            // Reset form values
            const user = this.app.currentUser;
            document.getElementById('profile-name').value = user.name;
            document.getElementById('profile-organization').value = user.organization || '';
            document.getElementById('profile-title').value = user.title || '';
            document.getElementById('profile-bio').value = user.bio || '';
            document.getElementById('profile-phone').value = user.phone || '';
            document.getElementById('profile-location').value = user.location || '';

            this.toggleEditMode(false);
        }
    }

    loadUserPreferences() {
        const prefs = this.state.get('userPreferences', {});

        // Load preferences into form
        Object.keys(prefs).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = prefs[key];
                } else {
                    element.value = prefs[key];
                }
            }
        });
    }

    savePreferences() {
        const preferences = {};

        // Collect all preference values
        document.querySelectorAll('#preferences-tab select, #preferences-tab input').forEach(input => {
            if (input.type === 'checkbox') {
                preferences[input.id] = input.checked;
            } else {
                preferences[input.id] = input.value;
            }
        });

        // Save to state
        this.state.set('userPreferences', preferences);

        // Apply theme changes
        if (preferences['theme-preference']) {
            this.app.setTheme(preferences['theme-preference']);
        }

        // Apply language changes
        if (preferences['language-preference']) {
            this.app.setLanguage(preferences['language-preference']);
        }

        this.showSuccess('Preferences saved successfully');
    }

    resetPreferences() {
        if (confirm('Reset all preferences to default values?')) {
            this.state.set('userPreferences', {});
            this.loadUserPreferences();
            this.showSuccess('Preferences reset to defaults');
        }
    }

    handleAvatarChange(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                // Update avatar display
                const avatarCircle = document.querySelector('.avatar-circle');
                avatarCircle.style.backgroundImage = `url(${e.target.result})`;
                avatarCircle.style.backgroundSize = 'cover';
                avatarCircle.textContent = '';

                // Save to user data
                const user = this.app.currentUser;
                user.avatar = e.target.result;
                this.state.set('currentUser', user);
                localStorage.setItem('argoUser', JSON.stringify(user));
            };
            reader.readAsDataURL(file);
        }
    }

    togglePasswordForm(show) {
        document.getElementById('password-form').style.display = show ? 'block' : 'none';

        if (!show) {
            // Clear form
            document.getElementById('current-password').value = '';
            document.getElementById('new-password').value = '';
            document.getElementById('confirm-new-password').value = '';
        }
    }

    async updatePassword() {
        const currentPassword = document.getElementById('current-password').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-new-password').value;

        if (!currentPassword || !newPassword || !confirmPassword) {
            this.showError('All password fields are required');
            return;
        }

        if (newPassword !== confirmPassword) {
            this.showError('New passwords do not match');
            return;
        }

        if (newPassword.length < 8) {
            this.showError('New password must be at least 8 characters');
            return;
        }

        try {
            // Simulate password update
            await new Promise(resolve => setTimeout(resolve, 1000));

            const user = this.app.currentUser;
            user.passwordLastChanged = new Date().toISOString();
            this.state.set('currentUser', user);

            this.togglePasswordForm(false);
            this.showSuccess('Password updated successfully');

        } catch (error) {
            this.showError('Failed to update password');
        }
    }

    exportUserData() {
        const userData = {
            profile: this.app.currentUser,
            preferences: this.state.get('userPreferences', {}),
            chatHistory: this.state.get('chatMessages', []),
            exportDate: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(userData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `argo-user-data-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    testNotification() {
        if ('Notification' in window) {
            if (Notification.permission === 'granted') {
                new Notification('Test Notification', {
                    body: 'This is a test notification from Argo AI Agent',
                    icon: '/favicon.ico'
                });
            } else if (Notification.permission !== 'denied') {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        this.testNotification();
                    }
                });
            }
        } else {
            alert('Your browser does not support notifications');
        }
    }

    trackFormChanges() {
        // Track changes in forms to show unsaved warning
        document.querySelectorAll('#account-page input, #account-page textarea, #account-page select').forEach(input => {
            input.addEventListener('input', () => {
                this.unsavedChanges = true;
                this.updateUnsavedWarning();
            });
        });
    }

    updateUnsavedWarning() {
        const warning = document.getElementById('unsaved-warning');
        warning.style.display = this.unsavedChanges ? 'block' : 'none';
    }

    // Utility methods
    getInitials(name) {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }

    formatRole(role) {
        const roles = {
            'admin': 'Administrator',
            'user': 'User',
            'demo': 'Demo User',
            'researcher': 'Researcher'
        };
        return roles[role] || role;
    }

    formatDate(dateString) {
        if (!dateString) return 'Never';
        return new Date(dateString).toLocaleDateString();
    }

    getBrowserInfo() {
        const ua = navigator.userAgent;
        let browser = 'Unknown';

        if (ua.includes('Chrome')) browser = 'Chrome';
        else if (ua.includes('Firefox')) browser = 'Firefox';
        else if (ua.includes('Safari')) browser = 'Safari';
        else if (ua.includes('Edge')) browser = 'Edge';

        return `${browser} on ${navigator.platform}`;
    }

    getRandomMetric(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    renderResearchTags(tags) {
        return tags.map(tag => `
            <span class="research-tag">
                ${tag}
                ${this.isEditing ? '<button class="remove-tag">×</button>' : ''}
            </span>
        `).join('');
    }

    renderActivityChart() {
        const days = 30;
        let chart = '<div class="chart-days">';

        for (let i = days - 1; i >= 0; i--) {
            const height = Math.random() * 80 + 10;
            chart += `
                <div class="chart-day" style="height: ${height}%;" 
                     title="Day ${days - i}: ${Math.floor(height)}% activity">
                </div>
            `;
        }

        chart += '</div>';
        return chart;
    }

    showSuccess(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success';
        alert.innerHTML = `✅ ${message}`;

        const container = document.getElementById('account-page');
        container.insertBefore(alert, container.firstChild);

        setTimeout(() => alert.remove(), 5000);
    }

    showError(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-error';
        alert.innerHTML = `❌ ${message}`;

        const container = document.getElementById('account-page');
        container.insertBefore(alert, container.firstChild);

        setTimeout(() => alert.remove(), 5000);
    }

    destroy() {
        // Cleanup any timers or event listeners
        if (this.unsavedChanges && confirm('You have unsaved changes. Save before leaving?')) {
            this.saveProfile();
        }
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccountPage;
}
