/**
 * Hash-based SPA Router
 * Manages navigation between different components
 */
const router = {
    routes: new Map(),
    currentRoute: null,
    currentComponent: null,
    defaultRoute: '/',
    
    init() {
        console.log('🛣️ Initializing Router');
        
        // Setup event listeners
        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('load', () => this.handleRoute());
        
        // Handle browser back/forward
        window.addEventListener('popstate', () => this.handleRoute());
        
        // Handle initial route
        this.handleRoute();
    },
    
    addRoute(path, component) {
        this.routes.set(path, component);
        console.log(`📍 Route registered: ${path}`);
    },
    
    navigate(path, replace = false) {
        console.log(`🧭 Navigating to: ${path}`);
        
        // Update URL
        if (replace) {
            window.location.replace(`#${path}`);
        } else {
            window.location.hash = path;
        }
    },
    
    async handleRoute() {
        const path = this.getCurrentPath();
        const component = this.routes.get(path) || this.routes.get(this.defaultRoute);
        
        if (!component) {
            console.error(`❌ No component found for route: ${path}`);
            this.show404();
            return;
        }
        
        console.log(`🎯 Loading route: ${path}`);
        
        try {
            // Show loading state
            this.showLoadingState();
            
            // Cleanup previous component
            if (this.currentComponent && this.currentComponent.destroy) {
                this.currentComponent.destroy();
            }
            
            // Update navigation active state
            this.updateNavigation(path);
            
            // Load new component
            await this.loadComponent(component);
            
            this.currentRoute = path;
            this.currentComponent = component;
            
            // Update page title
            this.updatePageTitle(component.title || 'ARGO AI Agent');
            
        } catch (error) {
            console.error('❌ Route loading error:', error);
            this.showError('Failed to load page. Please try again.');
        }
    },
    
    getCurrentPath() {
        const hash = window.location.hash.replace('#', '');
        return hash || '/';
    },
    
    async loadComponent(component) {
        const appContainer = document.getElementById('app');
        
        if (!appContainer) {
            throw new Error('App container not found');
        }
        
        // Render component
        const html = component.render();
        appContainer.innerHTML = html;
        
        // Initialize component
        if (component.init) {
            await component.init();
        }
        
        // Hide loading state
        this.hideLoadingState();
        
        // Add route-specific class to body
        document.body.className = `route-${this.getCurrentPath().replace('/', 'home')}`;
    },
    
    updateNavigation(currentPath) {
        // Update navigation active states
        const navLinks = document.querySelectorAll('nav a[href^="#"]');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href').replace('#', '');
            const isActive = href === currentPath || 
                           (currentPath === '/' && href === '') ||
                           (currentPath === '/home' && href === '');
            
            if (isActive) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            } else {
                link.classList.remove('active');
                link.removeAttribute('aria-current');
            }
        });
        
        // Update mobile menu if exists
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu && mobileMenu.classList.contains('open')) {
            mobileMenu.classList.remove('open');
        }
    },
    
    updatePageTitle(title) {
        document.title = `${title} - ARGO AI Agent`;
        
        // Update meta description based on route
        const metaDescription = document.querySelector('meta[name="description"]');
        if (metaDescription) {
            const descriptions = {
                '/': 'Advanced Oceanographic Data Analysis & AI Assistant for Smart India Hackathon 2025',
                '/home': 'Advanced Oceanographic Data Analysis & AI Assistant for Smart India Hackathon 2025',
                '/chat': 'AI-powered chatbot for ocean data analysis and ARGO profile insights',
                '/dashboard': 'Interactive dashboard for ARGO float data visualization and analytics',
                '/auth': 'User authentication and account management',
                '/account': 'User account settings and profile management'
            };
            
            metaDescription.setAttribute('content', 
                descriptions[this.getCurrentPath()] || descriptions['/']
            );
        }
    },
    
    showLoadingState() {
        const appContainer = document.getElementById('app');
        if (appContainer) {
            appContainer.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p>Loading...</p>
                </div>
            `;
        }
        
        // Add loading class to body
        document.body.classList.add('loading');
    },
    
    hideLoadingState() {
        document.body.classList.remove('loading');
    },
    
    showError(message) {
        const appContainer = document.getElementById('app');
        if (appContainer) {
            appContainer.innerHTML = `
                <div class="error-container">
                    <div class="error-icon">❌</div>
                    <h2>Oops! Something went wrong</h2>
                    <p>${message}</p>
                    <div class="error-actions">
                        <button class="btn btn-primary" onclick="router.navigate('/')">
                            🏠 Go Home
                        </button>
                        <button class="btn btn-outline" onclick="window.location.reload()">
                            🔄 Reload Page
                        </button>
                    </div>
                </div>
            `;
        }
    },
    
    show404() {
        const appContainer = document.getElementById('app');
        if (appContainer) {
            appContainer.innerHTML = `
                <div class="error-container">
                    <div class="error-icon">🔍</div>
                    <h2>Page Not Found</h2>
                    <p>The page you're looking for doesn't exist.</p>
                    <div class="error-actions">
                        <button class="btn btn-primary" onclick="router.navigate('/')">
                            🏠 Go Home
                        </button>
                        <button class="btn btn-outline" onclick="history.back()">
                            ⬅️ Go Back
                        </button>
                    </div>
                </div>
            `;
        }
        
        this.updatePageTitle('Page Not Found');
    },
    
    // Utility methods for components
    getParam(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    },
    
    setParams(params) {
        const url = new URL(window.location);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                url.searchParams.set(key, value);
            } else {
                url.searchParams.delete(key);
            }
        });
        window.history.replaceState({}, '', url);
    },
    
    // Programmatic navigation helpers
    goBack() {
        if (window.history.length > 1) {
            window.history.back();
        } else {
            this.navigate('/');
        }
    },
    
    goForward() {
        window.history.forward();
    },
    
    reload() {
        window.location.reload();
    },
    
    // Route guards and middleware
    beforeNavigate(callback) {
        this.beforeNavigateCallback = callback;
    },
    
    afterNavigate(callback) {
        this.afterNavigateCallback = callback;
    },
    
    // Route information
    getCurrentRoute() {
        return {
            path: this.getCurrentPath(),
            component: this.currentComponent,
            title: this.currentComponent?.title || 'ARGO AI Agent'
        };
    },
    
    isCurrentRoute(path) {
        return this.getCurrentPath() === path;
    },
    
    // Debug helpers
    listRoutes() {
        console.log('📍 Registered routes:');
        this.routes.forEach((component, path) => {
            console.log(`  ${path} -> ${component.title || 'Component'}`);
        });
    }
};

// Make router available globally
window.router = router;
