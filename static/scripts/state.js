// Global State Management
class AppState {
    constructor() {
        this.state = new Map();
        this.listeners = new Map();
        this.history = [];
        this.maxHistorySize = 50;
    }

    // Get state value
    get(key) {
        return this.state.get(key);
    }

    // Set state value
    set(key, value) {
        const oldValue = this.state.get(key);

        // Only update if value changed
        if (oldValue !== value) {
            // Store in history
            this.addToHistory(key, oldValue, value);

            // Update state
            this.state.set(key, value);

            // Notify listeners
            this.notifyListeners(key, value, oldValue);
        }

        return this;
    }

    // Update nested object properties
    update(key, updates) {
        const current = this.get(key) || {};
        const updated = { ...current, ...updates };
        this.set(key, updated);
        return this;
    }

    // Delete state value
    delete(key) {
        const oldValue = this.state.get(key);

        if (this.state.has(key)) {
            this.addToHistory(key, oldValue, undefined);
            this.state.delete(key);
            this.notifyListeners(key, undefined, oldValue);
        }

        return this;
    }

    // Check if key exists
    has(key) {
        return this.state.has(key);
    }

    // Get all keys
    keys() {
        return Array.from(this.state.keys());
    }

    // Get all values
    values() {
        return Array.from(this.state.values());
    }

    // Get state as object
    toObject() {
        const result = {};
        for (const [key, value] of this.state) {
            result[key] = value;
        }
        return result;
    }

    // Clear all state
    clear() {
        const oldState = this.toObject();
        this.state.clear();

        // Notify all listeners
        for (const key of Object.keys(oldState)) {
            this.notifyListeners(key, undefined, oldState[key]);
        }

        return this;
    }

    // Subscribe to state changes
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }

        this.listeners.get(key).add(callback);

        // Return unsubscribe function
        return () => {
            const keyListeners = this.listeners.get(key);
            if (keyListeners) {
                keyListeners.delete(callback);
                if (keyListeners.size === 0) {
                    this.listeners.delete(key);
                }
            }
        };
    }

    // Subscribe to all state changes
    subscribeAll(callback) {
        return this.subscribe('*', callback);
    }

    // Unsubscribe from state changes
    unsubscribe(key, callback) {
        const keyListeners = this.listeners.get(key);
        if (keyListeners) {
            keyListeners.delete(callback);
            if (keyListeners.size === 0) {
                this.listeners.delete(key);
            }
        }
        return this;
    }

    // Notify listeners of state changes
    notifyListeners(key, newValue, oldValue) {
        // Notify specific key listeners
        const keyListeners = this.listeners.get(key);
        if (keyListeners) {
            keyListeners.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('State listener error:', error);
                }
            });
        }

        // Notify global listeners
        const globalListeners = this.listeners.get('*');
        if (globalListeners) {
            globalListeners.forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error('Global state listener error:', error);
                }
            });
        }
    }

    // History management
    addToHistory(key, oldValue, newValue) {
        this.history.push({
            timestamp: Date.now(),
            key,
            oldValue,
            newValue
        });

        // Trim history if too large
        if (this.history.length > this.maxHistorySize) {
            this.history = this.history.slice(-this.maxHistorySize);
        }
    }

    // Get state history
    getHistory(key = null) {
        if (key) {
            return this.history.filter(entry => entry.key === key);
        }
        return [...this.history];
    }

    // Clear history
    clearHistory() {
        this.history = [];
        return this;
    }

    // Persistence methods
    saveToLocalStorage(storageKey = 'argo-app-state') {
        try {
            const stateObject = this.toObject();
            localStorage.setItem(storageKey, JSON.stringify(stateObject));
        } catch (error) {
            console.error('Failed to save state to localStorage:', error);
        }
        return this;
    }

    loadFromLocalStorage(storageKey = 'argo-app-state') {
        try {
            const saved = localStorage.getItem(storageKey);
            if (saved) {
                const stateObject = JSON.parse(saved);
                for (const [key, value] of Object.entries(stateObject)) {
                    this.set(key, value);
                }
            }
        } catch (error) {
            console.error('Failed to load state from localStorage:', error);
        }
        return this;
    }

    // Computed values
    computed(key, computeFn, dependencies = []) {
        const compute = () => {
            try {
                const result = computeFn();
                this.set(key, result);
            } catch (error) {
                console.error(`Computed property error for ${key}:`, error);
            }
        };

        // Initial computation
        compute();

        // Subscribe to dependencies
        const unsubscribers = dependencies.map(dep =>
            this.subscribe(dep, compute)
        );

        // Return cleanup function
        return () => {
            unsubscribers.forEach(unsub => unsub());
        };
    }

    // Debugging helpers
    debug() {
        console.group('🔍 App State Debug');
        console.log('Current State:', this.toObject());
        console.log('Listeners:', Object.fromEntries(
            Array.from(this.listeners.entries()).map(([key, listeners]) => [
                key,
                listeners.size
            ])
        ));
        console.log('History entries:', this.history.length);
        console.groupEnd();
    }

    // Watch for changes and log them
    enableLogging() {
        return this.subscribeAll((newValue, oldValue, key) => {
            console.log(`📊 State changed: ${key}`, {
                old: oldValue,
                new: newValue
            });
        });
    }
}

// State validation helpers
class StateValidator {
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    static isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    static isValidDate(date) {
        return date instanceof Date && !isNaN(date);
    }

    static isValidNumber(value, min = -Infinity, max = Infinity) {
        return typeof value === 'number' &&
            !isNaN(value) &&
            value >= min &&
            value <= max;
    }

    static isValidString(value, minLength = 0, maxLength = Infinity) {
        return typeof value === 'string' &&
            value.length >= minLength &&
            value.length <= maxLength;
    }
}

// State selectors for complex queries
class StateSelectors {
    constructor(state) {
        this.state = state;
    }

    // Get user information
    getUser() {
        return this.state.get('user') || null;
    }

    isAuthenticated() {
        const user = this.getUser();
        return user && user.id;
    }

    // Get system status
    getSystemStatus() {
        return this.state.get('systemStatus') || { status: 'unknown' };
    }

    isSystemHealthy() {
        const status = this.getSystemStatus();
        return status.status === 'healthy';
    }

    // Get UI state
    getCurrentLanguage() {
        return this.state.get('currentLanguage') || 'en';
    }

    getCurrentTheme() {
        return this.state.get('currentTheme') || 'default';
    }

    getTranslations() {
        return this.state.get('translations') || {};
    }

    // Get chat state
    getChatMessages() {
        return this.state.get('chatMessages') || [];
    }

    isChatLoading() {
        return this.state.get('chatLoading') || false;
    }

    // Get dashboard state
    getDashboardData() {
        return this.state.get('dashboardData') || {};
    }

    getSelectedFilters() {
        return this.state.get('selectedFilters') || {};
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AppState, StateValidator, StateSelectors };
}

// Create global instance for browser use
if (typeof window !== 'undefined') {
    window.appState = new AppState();
    console.log('📊 Global appState instance created');
}
