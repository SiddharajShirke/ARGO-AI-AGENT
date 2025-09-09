/**
 * Utility Functions Aggregator
 * Combines all utility modules into a single utils object
 */

// Create a unified utils object
const utils = {
    init() {
        console.log('🛠️ Utils initialized');
    },

    // Time and date formatting
    formatTime(date) {
        if (!date) return '--';
        return new Date(date).toLocaleTimeString();
    },

    formatDate(date) {
        if (!date) return '--';
        return new Date(date).toLocaleDateString();
    },

    formatDateTime(date) {
        if (!date) return '--';
        const d = new Date(date);
        return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`;
    },

    // Text utilities
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    truncateText(text, maxLength = 100) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    capitalizeFirst(text) {
        if (!text) return '';
        return text.charAt(0).toUpperCase() + text.slice(1);
    },

    // Number formatting
    formatNumber(num, decimals = 0) {
        if (num === null || num === undefined) return '--';
        return Number(num).toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // URL utilities
    getQueryParam(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    },

    setQueryParam(name, value) {
        const url = new URL(window.location);
        if (value !== null && value !== undefined) {
            url.searchParams.set(name, value);
        } else {
            url.searchParams.delete(name);
        }
        window.history.replaceState({}, '', url);
    },

    // Storage utilities
    setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.warn('Failed to save to localStorage:', error);
            return false;
        }
    },

    getLocalStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.warn('Failed to read from localStorage:', error);
            return defaultValue;
        }
    },

    removeLocalStorage(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.warn('Failed to remove from localStorage:', error);
            return false;
        }
    },

    // Array utilities
    shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    },

    groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            groups[group] = groups[group] || [];
            groups[group].push(item);
            return groups;
        }, {});
    },

    // Object utilities
    deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    },

    isEmpty(value) {
        if (value === null || value === undefined) return true;
        if (typeof value === 'string') return value.trim().length === 0;
        if (Array.isArray(value)) return value.length === 0;
        if (typeof value === 'object') return Object.keys(value).length === 0;
        return false;
    },

    // Validation utilities
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },

    // Debounce and throttle
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Random utilities
    generateId(length = 8) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    },

    randomColor() {
        return '#' + Math.floor(Math.random() * 16777215).toString(16);
    },

    // DOM utilities
    ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    },

    // Animation utilities
    animate(element, keyframes, options = {}) {
        if (!element || !element.animate) return Promise.resolve();

        const animation = element.animate(keyframes, {
            duration: 300,
            easing: 'ease-in-out',
            ...options
        });

        return animation.finished;
    },

    // Error handling
    safeCall(fn, ...args) {
        try {
            return fn(...args);
        } catch (error) {
            console.error('Safe call error:', error);
            return null;
        }
    },

    async safeAsyncCall(fn, ...args) {
        try {
            return await fn(...args);
        } catch (error) {
            console.error('Safe async call error:', error);
            return null;
        }
    }
};

// Make utils available globally
if (typeof window !== 'undefined') {
    window.utils = utils;
    console.log('🛠️ Global utils object created');
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = utils;
}
