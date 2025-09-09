/**
 * Home Page Component
 * Landing page with system overview and quick actions
 */
const HomeComponent = {
    title: 'Home',

    render() {
        return `
            <div class="home-page">
                <!-- Hero Section -->
                <div class="hero-section">
                    <h1 class="hero-title">🌊 Indian Ocean ARGO AI Agent</h1>
                    <p class="hero-subtitle">Advanced Oceanographic Data Analysis & AI Assistant for Smart India Hackathon 2025</p>
                    <div class="hero-actions">
                        <button onclick="router.navigate('/chat')" class="btn btn-primary">
                            🤖 Start AI Chat
                        </button>
                        <button onclick="router.navigate('/dashboard')" class="btn btn-secondary">
                            📊 View Dashboard
                        </button>
                    </div>
                </div>

                <!-- Feature Cards Grid -->
                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🤖</div>
                        <h3 class="feature-title">AI-Powered Analysis</h3>
                        <p class="feature-description">
                            Advanced machine learning algorithms analyze ARGO float data to provide 
                            intelligent insights about oceanographic conditions across the Indian Ocean.
                        </p>
                        <button onclick="router.navigate('/chat')" class="btn btn-primary" style="margin-top: 1rem;">
                            Try AI Chat
                        </button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">🌊</div>
                        <h3 class="feature-title">Real-time Ocean Data</h3>
                        <p class="feature-description">
                            Access comprehensive ARGO profile data covering temperature, salinity, 
                            and depth measurements from across the Arabian Sea, Bay of Bengal, 
                            and Equatorial Indian Ocean.
                        </p>
                        <button onclick="router.navigate('/dashboard')" class="btn btn-primary" style="margin-top: 1rem;">
                            Explore Data
                        </button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h3 class="feature-title">Interactive Dashboard</h3>
                        <p class="feature-description">
                            Monitor system performance, view regional statistics, and track 
                            oceanographic trends through our comprehensive dashboard interface.
                        </p>
                        <button onclick="router.navigate('/dashboard')" class="btn btn-primary" style="margin-top: 1rem;">
                            View Dashboard
                        </button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">🗺️</div>
                        <h3 class="feature-title">Regional Focus</h3>
                        <p class="feature-description">
                            Specialized analysis for three key regions: Arabian Sea upwelling zones, 
                            Bay of Bengal freshwater dynamics, and Equatorial Ocean thermal patterns.
                        </p>
                        <button onclick="home.showRegions()" class="btn btn-primary" style="margin-top: 1rem;">
                            Learn More
                        </button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">🌐</div>
                        <h3 class="feature-title">Multi-language Support</h3>
                        <p class="feature-description">
                            Available in English, Hindi, Bengali, and Tamil to serve diverse 
                            research communities across the Indian Ocean region.
                        </p>
                        <button onclick="home.changeLanguage()" class="btn btn-primary" style="margin-top: 1rem;">
                            Change Language
                        </button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <h3 class="feature-title">High Performance</h3>
                        <p class="feature-description">
                            Fast vector database searches, optimized API responses, and real-time 
                            processing of large-scale oceanographic datasets.
                        </p>
                        <div id="performance-stats" class="performance-stats" style="margin-top: 1rem;">
                            <div class="stat-item">
                                <span class="stat-label">Response Time:</span>
                                <span class="stat-value" id="avg-response-time">-- ms</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Success Rate:</span>
                                <span class="stat-value" id="success-rate">--%</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- System Status Section -->
                <div class="system-status-section">
                    <h2>🔧 System Status</h2>
                    <div class="status-grid">
                        <div class="status-card" id="backend-status-card">
                            <div class="status-indicator" id="backend-indicator"></div>
                            <div class="status-content">
                                <h3>Backend API</h3>
                                <p id="backend-status-text">Checking connection...</p>
                                <button onclick="home.refreshStatus()" class="btn btn-secondary btn-sm">
                                    🔄 Refresh
                                </button>
                            </div>
                        </div>

                        <div class="status-card" id="database-status-card">
                            <div class="status-indicator" id="database-indicator"></div>
                            <div class="status-content">
                                <h3>Database</h3>
                                <p id="database-status-text">Unknown</p>
                                <div id="profile-count-display">
                                    <small>ARGO Profiles: <span id="profile-count">--</span></small>
                                </div>
                            </div>
                        </div>

                        <div class="status-card" id="ai-status-card">
                            <div class="status-indicator" id="ai-indicator"></div>
                            <div class="status-content">
                                <h3>AI Agent</h3>
                                <p id="ai-status-text">Unknown</p>
                                <div id="ai-metrics">
                                    <small>Processing Time: <span id="ai-processing-time">--</span>s</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Start Section -->
                <div class="quick-start-section">
                    <h2>🚀 Quick Start</h2>
                    <div class="quick-actions">
                        <div class="quick-action" onclick="home.quickQuery('Arabian Sea temperature trends')">
                            <div class="action-icon">🌡️</div>
                            <div class="action-content">
                                <h4>Arabian Sea Temperature</h4>
                                <p>Analyze temperature trends and upwelling patterns</p>
                            </div>
                        </div>

                        <div class="quick-action" onclick="home.quickQuery('Bay of Bengal salinity patterns')">
                            <div class="action-icon">🧂</div>
                            <div class="action-content">
                                <h4>Bay of Bengal Salinity</h4>
                                <p>Explore salinity variations and freshwater influence</p>
                            </div>
                        </div>

                        <div class="quick-action" onclick="home.quickQuery('Equatorial Indian Ocean dynamics')">
                            <div class="action-icon">🌊</div>
                            <div class="action-content">
                                <h4>Equatorial Dynamics</h4>
                                <p>Study thermal structures and current patterns</p>
                            </div>
                        </div>

                        <div class="quick-action" onclick="home.quickQuery('Latest ARGO measurements')">
                            <div class="action-icon">📡</div>
                            <div class="action-content">
                                <h4>Latest Data</h4>
                                <p>View most recent ARGO profile measurements</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    async init() {
        console.log('🏠 Initializing Home Component');

        // Load system status
        await this.loadSystemStatus();

        // Load performance metrics
        await this.loadPerformanceMetrics();

        // Setup auto-refresh
        this.setupAutoRefresh();
    },

    async loadSystemStatus() {
        try {
            // Test backend connection
            const connectionTest = await api.testConnection();

            if (connectionTest.connected) {
                this.updateStatusCard('backend', 'connected', 'Connected ✅');

                // Load detailed status
                const systemStatus = await api.getSystemStatus();
                this.updateSystemStatus(systemStatus);
            } else {
                this.updateStatusCard('backend', 'error', 'Disconnected ❌');
            }
        } catch (error) {
            console.error('Failed to load system status:', error);
            this.updateStatusCard('backend', 'error', 'Connection Error ❌');
        }
    },

    updateSystemStatus(status) {
        // Update database status
        if (status.database_connected) {
            this.updateStatusCard('database', 'connected', 'Connected ✅');
            if (status.total_profiles) {
                document.getElementById('profile-count').textContent = status.total_profiles.toLocaleString();
            }
        } else {
            this.updateStatusCard('database', 'warning', 'Issues detected ⚠️');
        }

        // Update AI agent status
        if (status.ai_agent_operational) {
            this.updateStatusCard('ai', 'connected', 'Operational ✅');
        } else {
            this.updateStatusCard('ai', 'warning', 'Limited functionality ⚠️');
        }
    },

    updateStatusCard(type, status, text) {
        const indicator = document.getElementById(`${type}-indicator`);
        const statusText = document.getElementById(`${type}-status-text`);

        if (indicator) {
            indicator.className = `status-indicator status-${status}`;
        }

        if (statusText) {
            statusText.textContent = text;
        }
    },

    async loadPerformanceMetrics() {
        try {
            const metrics = api.getMetrics();

            document.getElementById('avg-response-time').textContent =
                `${metrics.averageResponseTime.toFixed(0)} ms`;
            document.getElementById('success-rate').textContent =
                `${metrics.successRate}%`;
        } catch (error) {
            console.warn('Failed to load performance metrics:', error);
        }
    },

    setupAutoRefresh() {
        // Refresh status every 30 seconds
        setInterval(() => {
            this.loadSystemStatus();
            this.loadPerformanceMetrics();
        }, 30000);
    },

    refreshStatus() {
        this.loadSystemStatus();
        this.loadPerformanceMetrics();

        appState.addNotification({
            type: 'info',
            title: 'Status Refreshed',
            message: 'System status updated successfully'
        });
    },

    quickQuery(query) {
        // Navigate to chat with pre-filled query
        appState.set('pendingQuery', query);
        router.navigate('/chat');
    },

    showRegions() {
        appState.addNotification({
            type: 'info',
            title: 'Regional Analysis',
            message: 'Our AI focuses on three key regions: Arabian Sea (upwelling), Bay of Bengal (freshwater), and Equatorial Ocean (thermal patterns)'
        });
    },

    changeLanguage() {
        const currentLang = appState.get('language') || 'en';
        const languages = { en: 'hi', hi: 'bn', bn: 'ta', ta: 'en' };
        const newLang = languages[currentLang];

        appState.set('language', newLang);
        appState.addNotification({
            type: 'success',
            title: 'Language Changed',
            message: `Interface language updated`
        });
    }
};

// Make component available globally
window.home = HomeComponent;

// Register route
router.addRoute('/', HomeComponent);
router.addRoute('/home', HomeComponent);
