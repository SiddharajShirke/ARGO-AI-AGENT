/**
 * Dashboard Component
 * Interactive data visualization and analysis interface
 */
const DashboardComponent = {
    title: 'Dashboard',
    currentView: 'overview',
    filters: {
        region: '',
        dateRange: '30d',
        profileType: 'all',
        searchQuery: ''
    },
    data: {
        profiles: [],
        regions: [],
        analytics: null,
        metrics: {}
    },
    refreshInterval: null,
    charts: {},
    
    render() {
        return `
            <div class="dashboard-page">
                <!-- Dashboard Header -->
                <div class="dashboard-header">
                    <div class="header-content">
                        <h1>📊 Ocean Data Dashboard</h1>
                        <p>Real-time analysis of ARGO float profiles and oceanographic data</p>
                    </div>
                    <div class="header-controls">
                        <div class="view-toggle">
                            <button class="btn ${this.currentView === 'overview' ? 'btn-primary' : 'btn-outline'}" 
                                    onclick="dashboard.switchView('overview')">
                                📈 Overview
                            </button>
                            <button class="btn ${this.currentView === 'search' ? 'btn-primary' : 'btn-outline'}" 
                                    onclick="dashboard.switchView('search')">
                                🔍 Search
                            </button>
                            <button class="btn ${this.currentView === 'analytics' ? 'btn-primary' : 'btn-outline'}" 
                                    onclick="dashboard.switchView('analytics')">
                                📊 Analytics
                            </button>
                        </div>
                        <button class="btn btn-secondary" onclick="dashboard.refreshData()">
                            🔄 Refresh
                        </button>
                        <button class="btn btn-secondary" onclick="dashboard.exportData()">
                            📤 Export
                        </button>
                    </div>
                </div>
                
                <!-- Dashboard Filters -->
                <div class="dashboard-filters">
                    <div class="filter-group">
                        <label for="region-filter">Region</label>
                        <select id="region-filter" onchange="dashboard.updateFilter('region', this.value)">
                            <option value="">All Regions</option>
                            <option value="arabian_sea">Arabian Sea</option>
                            <option value="bay_of_bengal">Bay of Bengal</option>
                            <option value="equatorial_indian_ocean">Equatorial Indian Ocean</option>
                            <option value="southern_indian_ocean">Southern Indian Ocean</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="date-range-filter">Date Range</label>
                        <select id="date-range-filter" onchange="dashboard.updateFilter('dateRange', this.value)">
                            <option value="7d">Last 7 Days</option>
                            <option value="30d" selected>Last 30 Days</option>
                            <option value="90d">Last 3 Months</option>
                            <option value="365d">Last Year</option>
                            <option value="all">All Time</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="profile-type-filter">Profile Type</label>
                        <select id="profile-type-filter" onchange="dashboard.updateFilter('profileType', this.value)">
                            <option value="all">All Profiles</option>
                            <option value="core">Core Profiles</option>
                            <option value="bgc">BGC Profiles</option>
                            <option value="deep">Deep Profiles</option>
                        </select>
                    </div>
                    
                    <div class="filter-group search-group">
                        <label for="search-input">Search</label>
                        <div class="search-input-wrapper">
                            <input 
                                type="text" 
                                id="search-input" 
                                placeholder="Search profiles, platforms, or parameters..."
                                onkeyup="dashboard.handleSearchInput(this.value)"
                            />
                            <button class="btn btn-icon" onclick="dashboard.clearSearch()">
                                ❌
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Dashboard Content -->
                <div class="dashboard-content" id="dashboard-content">
                    ${this.renderCurrentView()}
                </div>
            </div>
        `;
    },

    renderCurrentView() {
        switch (this.currentView) {
            case 'overview':
                return this.renderOverviewView();
            case 'search':
                return this.renderSearchView();
            case 'analytics':
                return this.renderAnalyticsView();
            default:
                return this.renderOverviewView();
        }
    },

    renderOverviewView() {
        return `
            <!-- Key Metrics Cards -->
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon">🌊</div>
                    <div class="metric-content">
                        <h3 class="metric-value" id="total-profiles">--</h3>
                        <p class="metric-label">Total Profiles</p>
                        <span class="metric-change" id="profiles-change">--</span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">📡</div>
                    <div class="metric-content">
                        <h3 class="metric-value" id="active-platforms">--</h3>
                        <p class="metric-label">Active Platforms</p>
                        <span class="metric-change" id="platforms-change">--</span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">🌡️</div>
                    <div class="metric-content">
                        <h3 class="metric-value" id="avg-temperature">--°C</h3>
                        <p class="metric-label">Avg Temperature</p>
                        <span class="metric-change" id="temperature-change">--</span>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-icon">🧂</div>
                    <div class="metric-content">
                        <h3 class="metric-value" id="avg-salinity">--</h3>
                        <p class="metric-label">Avg Salinity</p>
                        <span class="metric-change" id="salinity-change">--</span>
                    </div>
                </div>
            </div>
            
            <!-- Regional Overview -->
            <div class="dashboard-section">
                <h2>🗺️ Regional Overview</h2>
                <div class="regional-grid">
                    <div class="region-card" onclick="dashboard.selectRegion('arabian_sea')">
                        <h3>Arabian Sea</h3>
                        <div class="region-stats">
                            <div class="stat">
                                <span class="stat-label">Profiles:</span>
                                <span class="stat-value" id="arabian-profiles">--</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Avg Temp:</span>
                                <span class="stat-value" id="arabian-temp">--°C</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Upwelling Activity:</span>
                                <span class="stat-value" id="arabian-upwelling">--</span>
                            </div>
                        </div>
                        <div class="region-trend" id="arabian-trend">
                            <canvas id="arabian-chart" width="200" height="100"></canvas>
                        </div>
                    </div>
                    
                    <div class="region-card" onclick="dashboard.selectRegion('bay_of_bengal')">
                        <h3>Bay of Bengal</h3>
                        <div class="region-stats">
                            <div class="stat">
                                <span class="stat-label">Profiles:</span>
                                <span class="stat-value" id="bengal-profiles">--</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Avg Salinity:</span>
                                <span class="stat-value" id="bengal-salinity">--</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Freshwater Influence:</span>
                                <span class="stat-value" id="bengal-freshwater">--</span>
                            </div>
                        </div>
                        <div class="region-trend" id="bengal-trend">
                            <canvas id="bengal-chart" width="200" height="100"></canvas>
                        </div>
                    </div>
                    
                    <div class="region-card" onclick="dashboard.selectRegion('equatorial_indian_ocean')">
                        <h3>Equatorial Indian Ocean</h3>
                        <div class="region-stats">
                            <div class="stat">
                                <span class="stat-label">Profiles:</span>
                                <span class="stat-value" id="equatorial-profiles">--</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Thermal Structure:</span>
                                <span class="stat-value" id="equatorial-thermal">--</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Current Activity:</span>
                                <span class="stat-value" id="equatorial-current">--</span>
                            </div>
                        </div>
                        <div class="region-trend" id="equatorial-trend">
                            <canvas id="equatorial-chart" width="200" height="100"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Activity -->
            <div class="dashboard-section">
                <div class="section-header">
                    <h2>📈 Recent Activity</h2>
                    <button class="btn btn-outline" onclick="dashboard.viewAllActivity()">
                        View All
                    </button>
                </div>
                <div class="activity-feed" id="recent-activity">
                    <!-- Activity items will be loaded here -->
                </div>
            </div>
        `;
    },

    renderSearchView() {
        return `
            <!-- Advanced Search Interface -->
            <div class="search-interface">
                <div class="search-controls">
                    <div class="search-tabs">
                        <button class="tab-btn active" onclick="dashboard.switchSearchTab('quick')">
                            🔍 Quick Search
                        </button>
                        <button class="tab-btn" onclick="dashboard.switchSearchTab('advanced')">
                            ⚙️ Advanced
                        </button>
                        <button class="tab-btn" onclick="dashboard.switchSearchTab('spatial')">
                            🗺️ Spatial
                        </button>
                    </div>
                    
                    <div class="search-actions">
                        <button class="btn btn-primary" onclick="dashboard.executeSearch()">
                            🔍 Search
                        </button>
                        <button class="btn btn-outline" onclick="dashboard.clearSearch()">
                            🗑️ Clear
                        </button>
                        <button class="btn btn-outline" onclick="dashboard.saveSearch()">
                            💾 Save Search
                        </button>
                    </div>
                </div>
                
                <!-- Quick Search Tab -->
                <div class="search-tab active" id="quick-search-tab">
                    <div class="search-form">
                        <div class="form-group">
                            <label>Search Query</label>
                            <input 
                                type="text" 
                                id="quick-search-input" 
                                placeholder="Enter platform ID, profile parameters, or keywords..."
                                class="form-control"
                            />
                        </div>
                        <div class="search-suggestions" id="search-suggestions">
                            <button class="suggestion-btn" onclick="dashboard.applySuggestion('temperature > 25')">
                                Temperature > 25°C
                            </button>
                            <button class="suggestion-btn" onclick="dashboard.applySuggestion('salinity < 34')">
                                Salinity < 34
                            </button>
                            <button class="suggestion-btn" onclick="dashboard.applySuggestion('depth > 1000')">
                                Depth > 1000m
                            </button>
                            <button class="suggestion-btn" onclick="dashboard.applySuggestion('platform:2903334')">
                                Platform ID: 2903334
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Advanced Search Tab -->
                <div class="search-tab" id="advanced-search-tab">
                    <div class="advanced-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label>Platform ID</label>
                                <input type="text" id="platform-id-input" class="form-control" />
                            </div>
                            <div class="form-group">
                                <label>Cycle Number</label>
                                <input type="number" id="cycle-number-input" class="form-control" />
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label>Temperature Range (°C)</label>
                                <div class="range-inputs">
                                    <input type="number" id="temp-min" placeholder="Min" class="form-control" />
                                    <span>to</span>
                                    <input type="number" id="temp-max" placeholder="Max" class="form-control" />
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Salinity Range</label>
                                <div class="range-inputs">
                                    <input type="number" id="salinity-min" placeholder="Min" class="form-control" />
                                    <span>to</span>
                                    <input type="number" id="salinity-max" placeholder="Max" class="form-control" />
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label>Depth Range (m)</label>
                                <div class="range-inputs">
                                    <input type="number" id="depth-min" placeholder="Min" class="form-control" />
                                    <span>to</span>
                                    <input type="number" id="depth-max" placeholder="Max" class="form-control" />
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Date Range</label>
                                <div class="range-inputs">
                                    <input type="date" id="date-from" class="form-control" />
                                    <span>to</span>
                                    <input type="date" id="date-to" class="form-control" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Spatial Search Tab -->
                <div class="search-tab" id="spatial-search-tab">
                    <div class="spatial-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label>Latitude Range</label>
                                <div class="range-inputs">
                                    <input type="number" id="lat-min" placeholder="Min" class="form-control" step="0.01" />
                                    <span>to</span>
                                    <input type="number" id="lat-max" placeholder="Max" class="form-control" step="0.01" />
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Longitude Range</label>
                                <div class="range-inputs">
                                    <input type="number" id="lon-min" placeholder="Min" class="form-control" step="0.01" />
                                    <span>to</span>
                                    <input type="number" id="lon-max" placeholder="Max" class="form-control" step="0.01" />
                                </div>
                            </div>
                        </div>
                        
                        <div class="predefined-regions">
                            <h4>Quick Regions</h4>
                            <div class="region-buttons">
                                <button class="btn btn-outline" onclick="dashboard.selectPredefinedRegion('arabian_sea')">
                                    Arabian Sea
                                </button>
                                <button class="btn btn-outline" onclick="dashboard.selectPredefinedRegion('bay_of_bengal')">
                                    Bay of Bengal
                                </button>
                                <button class="btn btn-outline" onclick="dashboard.selectPredefinedRegion('equatorial')">
                                    Equatorial Ocean
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Search Results -->
            <div class="search-results" id="search-results">
                <div class="results-header">
                    <h3 id="results-title">Search Results</h3>
                    <div class="results-actions">
                        <select id="sort-select" onchange="dashboard.sortResults(this.value)">
                            <option value="date_desc">Newest First</option>
                            <option value="date_asc">Oldest First</option>
                            <option value="platform_asc">Platform ID A-Z</option>
                            <option value="depth_desc">Deepest First</option>
                        </select>
                        <button class="btn btn-outline" onclick="dashboard.exportSearchResults()">
                            📤 Export Results
                        </button>
                    </div>
                </div>
                
                <div class="results-container" id="results-container">
                    <div class="no-results">
                        <p>No search performed yet. Use the search controls above to find ARGO profiles.</p>
                    </div>
                </div>
                
                <div class="results-pagination" id="results-pagination" style="display: none;">
                    <!-- Pagination controls will be added here -->
                </div>
            </div>
        `;
    },

    renderAnalyticsView() {
        return `
            <!-- Analytics Dashboard -->
            <div class="analytics-dashboard">
                <!-- Analytics Controls -->
                <div class="analytics-controls">
                    <div class="analytics-tabs">
                        <button class="tab-btn active" onclick="dashboard.switchAnalyticsTab('trends')">
                            📈 Trends
                        </button>
                        <button class="tab-btn" onclick="dashboard.switchAnalyticsTab('distributions')">
                            📊 Distributions
                        </button>
                        <button class="tab-btn" onclick="dashboard.switchAnalyticsTab('correlations')">
                            🔗 Correlations
                        </button>
                        <button class="tab-btn" onclick="dashboard.switchAnalyticsTab('anomalies')">
                            ⚠️ Anomalies
                        </button>
                    </div>
                    
                    <div class="analytics-actions">
                        <button class="btn btn-primary" onclick="dashboard.generateReport()">
                            📄 Generate Report
                        </button>
                        <button class="btn btn-outline" onclick="dashboard.exportAnalytics()">
                            📤 Export Data
                        </button>
                    </div>
                </div>
                
                <!-- Trends Tab -->
                <div class="analytics-tab active" id="trends-tab">
                    <div class="charts-grid">
                        <div class="chart-container">
                            <h3>Temperature Trends</h3>
                            <canvas id="temperature-trend-chart" width="400" height="200"></canvas>
                        </div>
                        <div class="chart-container">
                            <h3>Salinity Trends</h3>
                            <canvas id="salinity-trend-chart" width="400" height="200"></canvas>
                        </div>
                        <div class="chart-container">
                            <h3>Profile Activity</h3>
                            <canvas id="profile-activity-chart" width="400" height="200"></canvas>
                        </div>
                        <div class="chart-container">
                            <h3>Regional Comparison</h3>
                            <canvas id="regional-comparison-chart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
                
                <!-- Distributions Tab -->
                <div class="analytics-tab" id="distributions-tab">
                    <div class="distributions-content">
                        <div class="distribution-controls">
                            <select id="parameter-select" onchange="dashboard.updateDistribution(this.value)">
                                <option value="temperature">Temperature</option>
                                <option value="salinity">Salinity</option>
                                <option value="depth">Depth</option>
                                <option value="pressure">Pressure</option>
                            </select>
                            <select id="region-select" onchange="dashboard.updateDistribution()">
                                <option value="all">All Regions</option>
                                <option value="arabian_sea">Arabian Sea</option>
                                <option value="bay_of_bengal">Bay of Bengal</option>
                                <option value="equatorial">Equatorial Ocean</option>
                            </select>
                        </div>
                        
                        <div class="distribution-chart">
                            <canvas id="distribution-chart" width="800" height="400"></canvas>
                        </div>
                        
                        <div class="distribution-stats">
                            <div class="stat-card">
                                <h4>Mean</h4>
                                <span id="dist-mean">--</span>
                            </div>
                            <div class="stat-card">
                                <h4>Median</h4>
                                <span id="dist-median">--</span>
                            </div>
                            <div class="stat-card">
                                <h4>Std Dev</h4>
                                <span id="dist-stddev">--</span>
                            </div>
                            <div class="stat-card">
                                <h4>Range</h4>
                                <span id="dist-range">--</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Correlations Tab -->
                <div class="analytics-tab" id="correlations-tab">
                    <div class="correlation-matrix">
                        <h3>Parameter Correlations</h3>
                        <canvas id="correlation-chart" width="600" height="600"></canvas>
                    </div>
                    
                    <div class="correlation-insights">
                        <h4>Key Insights</h4>
                        <div id="correlation-insights-list">
                            <!-- Insights will be populated here -->
                        </div>
                    </div>
                </div>
                
                <!-- Anomalies Tab -->
                <div class="analytics-tab" id="anomalies-tab">
                    <div class="anomaly-detection">
                        <div class="anomaly-controls">
                            <select id="anomaly-parameter" onchange="dashboard.detectAnomalies(this.value)">
                                <option value="temperature">Temperature Anomalies</option>
                                <option value="salinity">Salinity Anomalies</option>
                                <option value="depth">Depth Anomalies</option>
                            </select>
                            <select id="anomaly-threshold">
                                <option value="2">2 Sigma</option>
                                <option value="3" selected>3 Sigma</option>
                                <option value="4">4 Sigma</option>
                            </select>
                            <button class="btn btn-primary" onclick="dashboard.detectAnomalies()">
                                🔍 Detect Anomalies
                            </button>
                        </div>
                        
                        <div class="anomaly-results" id="anomaly-results">
                            <div class="no-anomalies">
                                <p>Click "Detect Anomalies" to identify unusual measurements in the data.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    async init() {
        console.log('📊 Initializing Dashboard Component');
        
        // Load initial data
        await this.loadDashboardData();
        
        // Setup auto-refresh
        this.setupAutoRefresh();
        
        // Initialize charts
        this.initializeCharts();
        
        // Load recent activity
        this.loadRecentActivity();
    },

    async loadDashboardData() {
        try {
            // Load metrics
            const metrics = await api.getDashboardMetrics(this.filters);
            this.updateMetrics(metrics);
            
            // Load regional data
            const regionalData = await api.getRegionalData(this.filters);
            this.updateRegionalData(regionalData);
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            appState.addNotification({
                type: 'error',
                title: 'Data Load Error',
                message: 'Failed to load dashboard data'
            });
        }
    },

    updateMetrics(metrics) {
        const updates = {
            'total-profiles': metrics.totalProfiles?.toLocaleString() || '--',
            'active-platforms': metrics.activePlatforms?.toLocaleString() || '--',
            'avg-temperature': metrics.avgTemperature ? `${metrics.avgTemperature.toFixed(1)}°C` : '--°C',
            'avg-salinity': metrics.avgSalinity?.toFixed(2) || '--',
            'profiles-change': this.formatChange(metrics.profilesChange),
            'platforms-change': this.formatChange(metrics.platformsChange),
            'temperature-change': this.formatChange(metrics.temperatureChange),
            'salinity-change': this.formatChange(metrics.salinityChange)
        };
        
        Object.entries(updates).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });
    },

    updateRegionalData(regionalData) {
        // Update regional statistics
        const regions = ['arabian', 'bengal', 'equatorial'];
        regions.forEach(region => {
            const data = regionalData[region];
            if (data) {
                const updates = {
                    [`${region}-profiles`]: data.profiles?.toLocaleString() || '--',
                    [`${region}-temp`]: data.avgTemperature ? `${data.avgTemperature.toFixed(1)}°C` : '--°C',
                    [`${region}-salinity`]: data.avgSalinity?.toFixed(2) || '--',
                    [`${region}-upwelling`]: data.upwelling || '--',
                    [`${region}-freshwater`]: data.freshwater || '--',
                    [`${region}-thermal`]: data.thermal || '--',
                    [`${region}-current`]: data.current || '--'
                };
                
                Object.entries(updates).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) element.textContent = value;
                });
            }
        });
    },

    formatChange(change) {
        if (!change) return '--';
        const sign = change > 0 ? '+' : '';
        return `${sign}${change.toFixed(1)}%`;
    },

    switchView(view) {
        this.currentView = view;
        
        // Update view toggle buttons
        document.querySelectorAll('.view-toggle .btn').forEach(btn => {
            btn.className = btn.onclick.toString().includes(view) ? 'btn btn-primary' : 'btn btn-outline';
        });
        
        // Update content
        const content = document.getElementById('dashboard-content');
        if (content) {
            content.innerHTML = this.renderCurrentView();
            
            // Initialize view-specific functionality
            if (view === 'analytics') {
                this.initializeCharts();
            }
        }
    },

    updateFilter(filterType, value) {
        this.filters[filterType] = value;
        this.loadDashboardData();
    },

    handleSearchInput(value) {
        this.filters.searchQuery = value;
        
        // Debounce search
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            if (this.currentView === 'search') {
                this.executeSearch();
            }
        }, 500);
    },

    clearSearch() {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.value = '';
            this.filters.searchQuery = '';
        }
        
        // Clear search results
        const resultsContainer = document.getElementById('results-container');
        if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="no-results"><p>Search cleared.</p></div>';
        }
    },

    async executeSearch() {
        const resultsContainer = document.getElementById('results-container');
        const resultsTitle = document.getElementById('results-title');
        
        if (!resultsContainer) return;
        
        try {
            resultsContainer.innerHTML = '<div class="loading">🔍 Searching...</div>';
            
            const searchParams = this.buildSearchParams();
            const results = await api.searchProfiles(searchParams);
            
            if (results && results.length > 0) {
                resultsTitle.textContent = `Search Results (${results.length})`;
                this.renderSearchResults(results);
            } else {
                resultsContainer.innerHTML = '<div class="no-results"><p>No profiles found matching your search criteria.</p></div>';
                resultsTitle.textContent = 'Search Results (0)';
            }
            
        } catch (error) {
            console.error('Search error:', error);
            resultsContainer.innerHTML = '<div class="error">❌ Search failed. Please try again.</div>';
            
            appState.addNotification({
                type: 'error',
                title: 'Search Error',
                message: 'Failed to execute search'
            });
        }
    },

    buildSearchParams() {
        const params = { ...this.filters };
        
        // Add advanced search parameters if in advanced mode
        if (this.currentView === 'search') {
            const advancedParams = [
                'platform-id-input', 'cycle-number-input',
                'temp-min', 'temp-max', 'salinity-min', 'salinity-max',
                'depth-min', 'depth-max', 'date-from', 'date-to',
                'lat-min', 'lat-max', 'lon-min', 'lon-max'
            ];
            
            advancedParams.forEach(id => {
                const element = document.getElementById(id);
                if (element && element.value) {
                    params[id.replace('-', '_')] = element.value;
                }
            });
        }
        
        return params;
    },

    renderSearchResults(results) {
        const resultsContainer = document.getElementById('results-container');
        
        const html = results.map(profile => `
            <div class="search-result-item">
                <div class="result-header">
                    <h4>Profile ${profile.profile_id || 'N/A'}</h4>
                    <span class="result-date">${utils.formatDate(profile.date)}</span>
                </div>
                <div class="result-content">
                    <div class="result-details">
                        <span><strong>Platform:</strong> ${profile.platform_id || 'N/A'}</span>
                        <span><strong>Cycle:</strong> ${profile.cycle_number || 'N/A'}</span>
                        <span><strong>Location:</strong> ${profile.latitude?.toFixed(2) || '--'}°N, ${profile.longitude?.toFixed(2) || '--'}°E</span>
                        <span><strong>Max Depth:</strong> ${profile.max_depth || '--'}m</span>
                    </div>
                    <div class="result-parameters">
                        ${profile.temperature ? `<span class="param-tag">🌡️ ${profile.temperature.toFixed(1)}°C</span>` : ''}
                        ${profile.salinity ? `<span class="param-tag">🧂 ${profile.salinity.toFixed(2)}</span>` : ''}
                        ${profile.pressure ? `<span class="param-tag">📏 ${profile.pressure.toFixed(0)} dbar</span>` : ''}
                    </div>
                </div>
                <div class="result-actions">
                    <button class="btn btn-sm btn-outline" onclick="dashboard.viewProfile('${profile.profile_id}')">
                        👁️ View
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="dashboard.exportProfile('${profile.profile_id}')">
                        📤 Export
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="dashboard.analyzeProfile('${profile.profile_id}')">
                        🤖 Analyze with AI
                    </button>
                </div>
            </div>
        `).join('');
        
        resultsContainer.innerHTML = html;
    },

    async refreshData() {
        await this.loadDashboardData();
        
        appState.addNotification({
            type: 'success',
            title: 'Data Refreshed',
            message: 'Dashboard data has been updated'
        });
    },

    exportData() {
        appState.addNotification({
            type: 'info',
            title: 'Export Feature',
            message: 'Data export functionality coming soon!'
        });
    },

    selectRegion(region) {
        this.updateFilter('region', region);
        
        appState.addNotification({
            type: 'info',
            title: 'Region Selected',
            message: `Filtering data for ${region.replace('_', ' ')}`
        });
    },

    setupAutoRefresh() {
        // Refresh data every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 300000);
    },

    initializeCharts() {
        // Initialize Chart.js charts for analytics
        // This would include temperature trends, salinity distributions, etc.
        console.log('📊 Initializing charts...');
    },

    loadRecentActivity() {
        // Load and display recent profile activity
        const activityContainer = document.getElementById('recent-activity');
        if (activityContainer) {
            // Mock activity data for demonstration
            activityContainer.innerHTML = `
                <div class="activity-item">
                    <div class="activity-icon">📡</div>
                    <div class="activity-content">
                        <p><strong>New profile received</strong> from platform 2903334</p>
                        <small>2 minutes ago • Arabian Sea</small>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">🌡️</div>
                    <div class="activity-content">
                        <p><strong>Temperature anomaly detected</strong> in Bay of Bengal</p>
                        <small>15 minutes ago • Automated alert</small>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">🔄</div>
                    <div class="activity-content">
                        <p><strong>Data processing completed</strong> for 47 new profiles</p>
                        <small>1 hour ago • Batch processing</small>
                    </div>
                </div>
            `;
        }
    },

    viewProfile(profileId) {
        appState.set('selectedProfile', profileId);
        appState.addNotification({
            type: 'info',
            title: 'Profile Viewer',
            message: `Profile viewing feature coming soon!`
        });
    },

    analyzeProfile(profileId) {
        appState.set('pendingQuery', `Analyze profile ${profileId} in detail`);
        router.navigate('/chat');
    },

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Clean up charts
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
    }
};

// Make component available globally
window.dashboard = DashboardComponent;

// Register route
router.addRoute('/dashboard', DashboardComponent);
