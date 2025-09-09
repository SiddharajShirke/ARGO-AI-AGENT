/**
 * Main Application Controller
 * Coordinates the entire SPA application
 */
class ArgoApp {
    constructor() {
        this.initialized = false;
        this.version = '1.0.0';
        this.buildInfo = {
            name: 'Indian Ocean ARGO AI Agent',
            description: 'Advanced Oceanographic Data Analysis & AI Assistant',
            author: 'Smart India Hackathon 2025',
            build: new Date().toISOString()
        };
    }

    async init() {
        if (this.initialized) {
            console.warn('⚠️ App already initialized');
            return;
        }

        console.log('🌊 Initializing Indian Ocean ARGO AI Agent...');
        console.log(`📦 Version: ${this.version}`);

        try {
            // Show initial loading
            this.showGlobalLoading();

            // Initialize core systems
            await this.initializeCore();

            // Initialize components
            await this.initializeComponents();

            // Initialize router
            this.initializeRouter();

            // Setup global event listeners
            this.setupGlobalEventListeners();

            // Load initial data
            await this.loadInitialData();

            // Finalize initialization
            this.finalizeInitialization();

            console.log('✅ Application initialized successfully');

        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.showInitializationError(error);
        }
    }

    async initializeCore() {
        console.log('🔧 Initializing core systems...');

        // Initialize theme system
        this.initializeTheme();

        // Initialize language system
        this.initializeLanguage();

        // Initialize state management
        appState.init();

        // Initialize API client
        api.init();

        // Initialize utilities
        utils.init();

        // Initialize DOM helpers
        domHelpers.init();
    }

    async initializeComponents() {
        console.log('🧩 Initializing components...');

        // Components are already loaded via script tags
        // Just verify they're available
        const requiredComponents = ['home', 'chatbot', 'dashboard'];
        const missingComponents = [];

        requiredComponents.forEach(componentName => {
            if (!window[componentName]) {
                missingComponents.push(componentName);
            }
        });

        if (missingComponents.length > 0) {
            throw new Error(`Missing components: ${missingComponents.join(', ')}`);
        }

        console.log('✅ All components loaded successfully');
    }

    initializeRouter() {
        console.log('🛣️ Initializing router...');

        // Router and routes are initialized via component registration
        router.init();
    }

    setupGlobalEventListeners() {
        console.log('👂 Setting up global event listeners...');

        // Global error handling
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.handleGlobalError(event.error);
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.handleGlobalError(event.reason);
        });

        // Online/offline status
        window.addEventListener('online', () => {
            appState.set('isOnline', true);
            appState.addNotification({
                type: 'success',
                title: 'Connection Restored',
                message: 'You are back online'
            });
        });

        window.addEventListener('offline', () => {
            appState.set('isOnline', false);
            appState.addNotification({
                type: 'warning',
                title: 'Connection Lost',
                message: 'You are now offline'
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            this.handleGlobalKeyboard(event);
        });

        // Mobile menu toggle
        const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', this.toggleMobileMenu);
        }

        // Language selector
        const languageSelector = document.getElementById('language-select');
        if (languageSelector) {
            languageSelector.addEventListener('change', (event) => {
                this.changeLanguage(event.target.value);
            });
        }

        // Theme toggle
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme);
        }

        // Notification close buttons
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('notification-close')) {
                const notification = event.target.closest('.notification');
                if (notification) {
                    appState.removeNotification(notification.dataset.id);
                }
            }
        });
    }

    async loadInitialData() {
        console.log('📊 Loading initial data...');

        try {
            // Test API connection
            const connectionTest = await api.testConnection();

            if (connectionTest.connected) {
                console.log('✅ API connection successful');
                appState.set('apiConnected', true);

                // Load system status
                const systemStatus = await api.getSystemStatus();
                appState.set('systemStatus', systemStatus);

            } else {
                console.warn('⚠️ API connection failed');
                appState.set('apiConnected', false);

                appState.addNotification({
                    type: 'warning',
                    title: 'API Connection',
                    message: 'Unable to connect to backend API. Some features may be limited.'
                });
            }

        } catch (error) {
            console.error('❌ Failed to load initial data:', error);
            appState.set('apiConnected', false);

            appState.addNotification({
                type: 'error',
                title: 'Initialization Error',
                message: 'Failed to load initial application data'
            });
        }
    }

    finalizeInitialization() {
        // Hide global loading
        this.hideGlobalLoading();

        // Mark as initialized
        this.initialized = true;

        // Set initial online status
        appState.set('isOnline', navigator.onLine);

        // Show welcome notification
        appState.addNotification({
            type: 'success',
            title: 'Welcome to ARGO AI Agent',
            message: 'Application loaded successfully. Explore ocean data with AI assistance!',
            duration: 5000
        });

        // Add initialization info to console
        console.log('🎉 Application ready for use');
        console.log('💡 Use router.listRoutes() to see available routes');
        console.log('🐛 Use appState.debug() to inspect application state');
    }

    initializeTheme() {
        const savedTheme = localStorage.getItem('argo-theme') || 'ocean';
        document.documentElement.setAttribute('data-theme', savedTheme);
        appState.set('theme', savedTheme);

        console.log(`🎨 Theme initialized: ${savedTheme}`);
    }

    initializeLanguage() {
        const savedLanguage = localStorage.getItem('argo-language') || 'en';
        const supportedLanguages = ['en', 'hi', 'bn', 'ta'];

        const language = supportedLanguages.includes(savedLanguage) ? savedLanguage : 'en';
        document.documentElement.setAttribute('lang', language);
        appState.set('language', language);

        console.log(`🌐 Language initialized: ${language}`);
    }

    toggleMobileMenu() {
        const mobileMenu = document.querySelector('.mobile-menu');
        const body = document.body;

        if (mobileMenu) {
            const isOpen = mobileMenu.classList.contains('open');

            if (isOpen) {
                mobileMenu.classList.remove('open');
                body.classList.remove('menu-open');
            } else {
                mobileMenu.classList.add('open');
                body.classList.add('menu-open');
            }
        }
    }

    toggleTheme() {
        const currentTheme = appState.get('theme') || 'ocean';
        const themes = ['ocean', 'dark', 'light'];
        const currentIndex = themes.indexOf(currentTheme);
        const nextTheme = themes[(currentIndex + 1) % themes.length];

        document.documentElement.setAttribute('data-theme', nextTheme);
        localStorage.setItem('argo-theme', nextTheme);
        appState.set('theme', nextTheme);

        appState.addNotification({
            type: 'info',
            title: 'Theme Changed',
            message: `Switched to ${nextTheme} theme`
        });
    }

    changeLanguage(language) {
        const supportedLanguages = ['en', 'hi', 'bn', 'ta'];

        if (!supportedLanguages.includes(language)) {
            console.warn(`Unsupported language: ${language}`);
            return;
        }

        document.documentElement.setAttribute('lang', language);
        localStorage.setItem('argo-language', language);
        appState.set('language', language);

        appState.addNotification({
            type: 'success',
            title: 'Language Changed',
            message: `Interface language updated to ${language}`
        });

        // Reload current component to apply language changes
        router.reload();
    }

    handleGlobalKeyboard(event) {
        // Global keyboard shortcuts
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'k':
                    event.preventDefault();
                    // Focus search input if available
                    const searchInput = document.querySelector('#search-input, #message-input');
                    if (searchInput) searchInput.focus();
                    break;

                case '/':
                    event.preventDefault();
                    router.navigate('/chat');
                    break;

                case 'd':
                    event.preventDefault();
                    router.navigate('/dashboard');
                    break;

                case 'h':
                    event.preventDefault();
                    router.navigate('/');
                    break;
            }
        }

        // Escape key handling
        if (event.key === 'Escape') {
            // Close mobile menu
            const mobileMenu = document.querySelector('.mobile-menu.open');
            if (mobileMenu) {
                this.toggleMobileMenu();
                return;
            }

            // Close modals, dropdowns, etc.
            const openDropdowns = document.querySelectorAll('.dropdown.open');
            openDropdowns.forEach(dropdown => {
                dropdown.classList.remove('open');
            });
        }
    }

    handleGlobalError(error) {
        console.error('Handling global error:', error);

        // Don't show too many error notifications
        const errorNotifications = document.querySelectorAll('.notification.error');
        if (errorNotifications.length >= 3) {
            return;
        }

        appState.addNotification({
            type: 'error',
            title: 'Application Error',
            message: 'An unexpected error occurred. Please refresh if problems persist.',
            duration: 10000
        });
    }

    showGlobalLoading() {
        const loadingHtml = `
            <div id="global-loading" class="global-loading">
                <div class="loading-content">
                    <div class="loading-logo">🌊</div>
                    <h2>ARGO AI Agent</h2>
                    <div class="loading-spinner"></div>
                    <p>Initializing ocean data analysis platform...</p>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('afterbegin', loadingHtml);
    }

    hideGlobalLoading() {
        const globalLoading = document.getElementById('global-loading');
        if (globalLoading) {
            globalLoading.style.opacity = '0';
            setTimeout(() => {
                globalLoading.remove();
            }, 300);
        }
    }

    showInitializationError(error) {
        this.hideGlobalLoading();

        const errorHtml = `
            <div id="init-error" class="initialization-error">
                <div class="error-content">
                    <div class="error-icon">❌</div>
                    <h2>Initialization Failed</h2>
                    <p>The application failed to start properly.</p>
                    <details>
                        <summary>Error Details</summary>
                        <pre>${error.message || 'Unknown error'}</pre>
                    </details>
                    <div class="error-actions">
                        <button class="btn btn-primary" onclick="window.location.reload()">
                            🔄 Reload Application
                        </button>
                        <button class="btn btn-outline" onclick="console.log('Error:', error)">
                            🐛 Log to Console
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.innerHTML = errorHtml;
    }

    // Public API for debugging and external use
    getInfo() {
        return {
            ...this.buildInfo,
            version: this.version,
            initialized: this.initialized,
            currentRoute: router.getCurrentRoute(),
            state: appState.getAll()
        };
    }

    debug() {
        console.group('🐛 ARGO AI Agent Debug Info');
        console.log('📦 Build Info:', this.buildInfo);
        console.log('🔧 Version:', this.version);
        console.log('✅ Initialized:', this.initialized);
        console.log('🛣️ Current Route:', router.getCurrentRoute());
        console.log('📊 App State:', appState.getAll());
        console.log('🌐 API Status:', api.getStatus());
        console.groupEnd();
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    console.log('📄 DOM loaded, starting application...');

    // Create global app instance
    window.app = new ArgoApp();

    // Initialize the application
    await window.app.init();
});
