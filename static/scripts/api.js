// FastAPI Backend Integration
class APIClient {
    constructor() {
        this.baseURL = 'http://localhost:8002/api/v2';
        this.timeout = 30000; // 30 seconds
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second
        this.connected = false;
        this.connectionChecked = false;
        this.metrics = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            averageResponseTime: 0,
            lastRequestTime: 0
        };

        // Test connection on initialization
        this.testConnection();
    }

    async init() {
        console.log('🌐 Initializing API Client...');

        // Test connection
        await this.testConnection();

        // Setup cache
        this.setupCache();

        console.log(`📡 API Client initialized - Connected: ${this.connected}`);
        return this.connected;
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const startTime = performance.now();

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        config.signal = controller.signal;

        try {
            this.metrics.totalRequests++;
            this.metrics.lastRequestTime = Date.now();

            const response = await this.makeRequestWithRetry(url, config);
            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await this.parseErrorResponse(response);
                this.updateMetrics(false, performance.now() - startTime);

                throw new APIError(
                    errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`,
                    response.status,
                    errorData
                );
            }

            const result = await this.parseResponse(response);
            this.updateMetrics(true, performance.now() - startTime);

            return result;

        } catch (error) {
            clearTimeout(timeoutId);

            if (error.name === 'AbortError') {
                this.updateMetrics(false, this.timeout);
                throw new APIError('Request timeout', 408);
            }

            if (error instanceof APIError) {
                throw error;
            }

            this.updateMetrics(false, performance.now() - startTime);
            throw new APIError(`Network error: ${error.message}`, 0, error);
        }
    }

    updateMetrics(success, responseTime) {
        if (success) {
            this.metrics.successfulRequests++;
        } else {
            this.metrics.failedRequests++;
        }

        // Update average response time
        const totalSuccessful = this.metrics.successfulRequests;
        if (totalSuccessful > 0) {
            this.metrics.averageResponseTime =
                (this.metrics.averageResponseTime * (totalSuccessful - 1) + responseTime) / totalSuccessful;
        }
    }

    getMetrics() {
        const total = this.metrics.totalRequests;
        return {
            ...this.metrics,
            successRate: total > 0 ? Math.round((this.metrics.successfulRequests / total) * 100) : 0,
            averageResponseTime: Math.round(this.metrics.averageResponseTime)
        };
    }

    getStatus() {
        return {
            connected: this.connected,
            connectionChecked: this.connectionChecked,
            baseURL: this.baseURL,
            metrics: this.getMetrics()
        };
    }

    async makeRequestWithRetry(url, config, attempt = 1) {
        try {
            return await fetch(url, config);
        } catch (error) {
            if (attempt < this.retryAttempts && this.shouldRetry(error)) {
                console.warn(`Request failed, retrying (${attempt}/${this.retryAttempts})...`);
                await this.delay(this.retryDelay * attempt);
                return this.makeRequestWithRetry(url, config, attempt + 1);
            }
            throw error;
        }
    }

    shouldRetry(error) {
        // Retry on network errors, but not on abort
        return error.name !== 'AbortError';
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async parseResponse(response) {
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }

        return await response.text();
    }

    async parseErrorResponse(response) {
        try {
            return await response.json();
        } catch {
            return { message: await response.text() };
        }
    }

    // HTTP Methods
    async get(endpoint, params = {}) {
        const url = new URL(endpoint, this.baseURL);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });

        return this.request(url.pathname + url.search, {
            method: 'GET'
        });
    }

    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async patch(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    // System Endpoints
    async testConnection() {
        try {
            const response = await this.get('/health');
            this.connected = true;
            this.connectionChecked = true;
            console.log('✅ API connection successful');
            return { connected: true, response };
        } catch (error) {
            this.connected = false;
            this.connectionChecked = true;
            console.warn('⚠️ API connection failed:', error.message);
            return { connected: false, error: error.message };
        }
    }

    async getHealth() {
        return this.get('/health');
    }

    async getSystemStatus() {
        return this.get('/system-status');
    }

    async getDashboardMetrics(filters = {}) {
        // Mock data for now - this endpoint needs to be created in backend
        return {
            totalProfiles: 12500,
            activePlatforms: 45,
            avgTemperature: 24.5,
            avgSalinity: 34.8,
            profilesChange: 2.3,
            platformsChange: -1.1,
            temperatureChange: 0.5,
            salinityChange: -0.2
        };
    }

    async getRegionalData(filters = {}) {
        // Mock data for now - this endpoint needs to be created in backend
        return {
            arabian: {
                profiles: 4500,
                avgTemperature: 26.2,
                upwelling: 'Active'
            },
            bengal: {
                profiles: 3800,
                avgSalinity: 33.2,
                freshwater: 'High'
            },
            equatorial: {
                profiles: 4200,
                thermal: 'Stable',
                current: 'Moderate'
            }
        };
    }

    // Enhanced Chat/AI Endpoints
    async sendChatMessage(message, options = {}) {
        const startTime = performance.now();

        try {
            const response = await this.post('/query', {
                query: message,
                language: options.language || 'en',
                limit: options.limit || 10,
                region: options.region || null,
                include_metadata: true
            });

            const endTime = performance.now();
            this.updateMetrics(true, endTime - startTime);

            return {
                message: response.response || response.message || 'No response received',
                data: response.data_summary?.profiles || [],
                metadata: response.metadata || {},
                profilesFound: response.profiles_found || 0,
                queryTime: response.query_time || 0
            };
        } catch (error) {
            const endTime = performance.now();
            this.updateMetrics(false, endTime - startTime);
            throw error;
        }
    }

    // Profile Endpoints
    async getProfiles(params = {}) {
        return this.get('/profiles', params);
    }

    async getProfile(id) {
        return this.get(`/profiles/${id}`);
    }

    async searchProfiles(searchParams) {
        return this.post('/profiles/search', searchParams);
    }

    // Data Analysis Endpoints
    async analyzeProfile(profileId, analysisType = 'comprehensive') {
        return this.post('/analyze', {
            profile_id: profileId,
            analysis_type: analysisType
        });
    }

    async getAnalytics(params = {}) {
        return this.get('/analytics', params);
    }

    // Region Endpoints
    async getRegions() {
        return this.get('/regions');
    }

    async getRegionAnalysis(region, params = {}) {
        return this.get(`/regions/${region}/analysis`, params);
    }

    // Profile Endpoints
    async getProfiles(params = {}) {
        return this.get('/profiles', params);
    }

    async getProfile(id) {
        return this.get(`/profiles/${id}`);
    }

    async searchProfiles(query, params = {}) {
        return this.post('/profiles/search', { query, ...params });
    }

    // Region Endpoints
    async getRegions() {
        return this.get('/regions');
    }

    async getRegionData(region, params = {}) {
        return this.get(`/regions/${region}`, params);
    }

    // Analysis Endpoints
    async getAnalysis(params = {}) {
        return this.get('/analysis', params);
    }

    async createAnalysis(data) {
        return this.post('/analysis', data);
    }

    // Chat/AI Endpoints
    async sendMessage(message, context = {}) {
        return this.post('/chat/message', {
            message,
            context,
            timestamp: new Date().toISOString()
        });
    }

    async getChatHistory(limit = 50) {
        return this.get('/chat/history', { limit });
    }

    async clearChatHistory() {
        return this.delete('/chat/history');
    }

    // Export Endpoints
    async exportData(format = 'json', params = {}) {
        return this.get('/export', { format, ...params });
    }

    // Upload Endpoints
    async uploadFile(file, onProgress = null) {
        const formData = new FormData();
        formData.append('file', file);

        const config = {
            method: 'POST',
            body: formData,
            headers: {} // Don't set Content-Type for FormData
        };

        // Add progress tracking if callback provided
        if (onProgress && typeof onProgress === 'function') {
            // Note: Progress tracking for uploads would require a more complex implementation
            // with XMLHttpRequest or a library that supports progress events
        }

        return this.request('/upload', config);
    }

    // WebSocket connection for real-time updates
    connectWebSocket(onMessage, onError = null, onClose = null) {
        const wsUrl = this.baseURL.replace('http', 'ws') + '/ws';
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('🔗 WebSocket connected');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (onError) onError(error);
        };

        ws.onclose = (event) => {
            console.log('📡 WebSocket disconnected:', event.code, event.reason);
            if (onClose) onClose(event);
        };

        return ws;
    }

    // Batch requests
    async batchRequest(requests) {
        const promises = requests.map(req => {
            const { method = 'GET', endpoint, data, params } = req;

            switch (method.toUpperCase()) {
                case 'GET':
                    return this.get(endpoint, params);
                case 'POST':
                    return this.post(endpoint, data);
                case 'PUT':
                    return this.put(endpoint, data);
                case 'PATCH':
                    return this.patch(endpoint, data);
                case 'DELETE':
                    return this.delete(endpoint);
                default:
                    throw new Error(`Unsupported method: ${method}`);
            }
        });

        return Promise.allSettled(promises);
    }

    // Cache management
    setupCache() {
        this.cache = new Map();
        this.cacheMaxAge = 5 * 60 * 1000; // 5 minutes
    }

    getCached(key) {
        if (!this.cache) return null;

        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheMaxAge) {
            return cached.data;
        }

        this.cache.delete(key);
        return null;
    }

    setCache(key, data) {
        if (!this.cache) this.setupCache();

        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    clearCache() {
        if (this.cache) {
            this.cache.clear();
        }
    }

    // Utility methods
    isOnline() {
        return navigator.onLine;
    }

    async ping() {
        try {
            await this.getHealth();
            return true;
        } catch {
            return false;
        }
    }
}

// Custom API Error class
class APIError extends Error {
    constructor(message, status = 0, details = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.details = details;
    }

    isNetworkError() {
        return this.status === 0;
    }

    isClientError() {
        return this.status >= 400 && this.status < 500;
    }

    isServerError() {
        return this.status >= 500;
    }

    isTimeout() {
        return this.status === 408;
    }
}

// API Response cache utility
class APICache {
    constructor(maxAge = 5 * 60 * 1000) { // 5 minutes default
        this.cache = new Map();
        this.maxAge = maxAge;
    }

    get(key) {
        const entry = this.cache.get(key);
        if (entry && Date.now() - entry.timestamp < this.maxAge) {
            return entry.data;
        }

        this.cache.delete(key);
        return null;
    }

    set(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    clear() {
        this.cache.clear();
    }

    has(key) {
        return this.get(key) !== null;
    }

    delete(key) {
        return this.cache.delete(key);
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, APIError, APICache };
}

// Create global instance for browser use
if (typeof window !== 'undefined') {
    window.api = new APIClient();
    console.log('🌐 Global API client instance created');
}
