// DOM Manipulation and Utility Helpers
class DOMHelpers {

    // Element creation and manipulation
    static createElement(tag, attributes = {}, children = []) {
        const element = document.createElement(tag);

        // Set attributes
        Object.keys(attributes).forEach(key => {
            if (key === 'className') {
                element.className = attributes[key];
            } else if (key === 'textContent') {
                element.textContent = attributes[key];
            } else if (key === 'innerHTML') {
                element.innerHTML = attributes[key];
            } else if (key.startsWith('data-')) {
                element.setAttribute(key, attributes[key]);
            } else if (key === 'style' && typeof attributes[key] === 'object') {
                Object.assign(element.style, attributes[key]);
            } else {
                element[key] = attributes[key];
            }
        });

        // Add children
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child instanceof Element) {
                element.appendChild(child);
            }
        });

        return element;
    }

    // Query selectors with error handling
    static $(selector, parent = document) {
        try {
            return parent.querySelector(selector);
        } catch (error) {
            console.error('Invalid selector:', selector, error);
            return null;
        }
    }

    static $$(selector, parent = document) {
        try {
            return Array.from(parent.querySelectorAll(selector));
        } catch (error) {
            console.error('Invalid selector:', selector, error);
            return [];
        }
    }

    // Element visibility
    static isVisible(element) {
        if (!element) return false;

        const style = window.getComputedStyle(element);
        return style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            style.opacity !== '0';
    }

    static show(element, displayType = 'block') {
        if (element) {
            element.style.display = displayType;
        }
    }

    static hide(element) {
        if (element) {
            element.style.display = 'none';
        }
    }

    static toggle(element, displayType = 'block') {
        if (!element) return;

        if (this.isVisible(element)) {
            this.hide(element);
        } else {
            this.show(element, displayType);
        }
    }

    // CSS class manipulation
    static addClass(element, className) {
        if (element && className) {
            element.classList.add(className);
        }
    }

    static removeClass(element, className) {
        if (element && className) {
            element.classList.remove(className);
        }
    }

    static toggleClass(element, className) {
        if (element && className) {
            element.classList.toggle(className);
        }
    }

    static hasClass(element, className) {
        return element && className && element.classList.contains(className);
    }

    // Attributes
    static getAttribute(element, name) {
        return element ? element.getAttribute(name) : null;
    }

    static setAttribute(element, name, value) {
        if (element) {
            element.setAttribute(name, value);
        }
    }

    static removeAttribute(element, name) {
        if (element) {
            element.removeAttribute(name);
        }
    }

    // Data attributes
    static getData(element, key) {
        return element ? element.dataset[key] : null;
    }

    static setData(element, key, value) {
        if (element) {
            element.dataset[key] = value;
        }
    }

    // Event handling
    static on(element, event, handler, options = {}) {
        if (element && event && handler) {
            element.addEventListener(event, handler, options);
        }
    }

    static off(element, event, handler, options = {}) {
        if (element && event && handler) {
            element.removeEventListener(event, handler, options);
        }
    }

    static once(element, event, handler) {
        if (element && event && handler) {
            element.addEventListener(event, handler, { once: true });
        }
    }

    static trigger(element, eventType, detail = null) {
        if (!element) return;

        const event = detail ?
            new CustomEvent(eventType, { detail }) :
            new Event(eventType);

        element.dispatchEvent(event);
    }

    // Position and dimensions
    static getPosition(element) {
        if (!element) return { x: 0, y: 0 };

        const rect = element.getBoundingClientRect();
        return {
            x: rect.left + window.scrollX,
            y: rect.top + window.scrollY
        };
    }

    static getDimensions(element) {
        if (!element) return { width: 0, height: 0 };

        const rect = element.getBoundingClientRect();
        return {
            width: rect.width,
            height: rect.height
        };
    }

    static getOffset(element) {
        if (!element) return { top: 0, left: 0 };

        let top = 0;
        let left = 0;

        while (element) {
            top += element.offsetTop;
            left += element.offsetLeft;
            element = element.offsetParent;
        }

        return { top, left };
    }

    // Scrolling
    static scrollToElement(element, options = {}) {
        if (!element) return;

        const defaultOptions = {
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest'
        };

        element.scrollIntoView({ ...defaultOptions, ...options });
    }

    static scrollToTop(element = window, smooth = true) {
        if (element === window) {
            window.scrollTo({
                top: 0,
                behavior: smooth ? 'smooth' : 'auto'
            });
        } else {
            element.scrollTop = 0;
        }
    }

    static getScrollPosition(element = window) {
        if (element === window) {
            return {
                x: window.scrollX || window.pageXOffset,
                y: window.scrollY || window.pageYOffset
            };
        }

        return {
            x: element.scrollLeft,
            y: element.scrollTop
        };
    }

    // DOM ready
    static ready(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    }

    // Element insertion
    static append(parent, child) {
        if (parent && child) {
            parent.appendChild(child);
        }
    }

    static prepend(parent, child) {
        if (parent && child) {
            parent.insertBefore(child, parent.firstChild);
        }
    }

    static insertAfter(newElement, targetElement) {
        if (newElement && targetElement && targetElement.parentNode) {
            targetElement.parentNode.insertBefore(newElement, targetElement.nextSibling);
        }
    }

    static insertBefore(newElement, targetElement) {
        if (newElement && targetElement && targetElement.parentNode) {
            targetElement.parentNode.insertBefore(newElement, targetElement);
        }
    }

    // Element removal
    static remove(element) {
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }

    static empty(element) {
        if (element) {
            while (element.firstChild) {
                element.removeChild(element.firstChild);
            }
        }
    }

    // Text content
    static text(element, value = null) {
        if (!element) return '';

        if (value !== null) {
            element.textContent = value;
            return element;
        }

        return element.textContent;
    }

    static html(element, value = null) {
        if (!element) return '';

        if (value !== null) {
            element.innerHTML = value;
            return element;
        }

        return element.innerHTML;
    }

    // Form helpers
    static getValue(element) {
        if (!element) return '';

        if (element.type === 'checkbox' || element.type === 'radio') {
            return element.checked;
        }

        return element.value;
    }

    static setValue(element, value) {
        if (!element) return;

        if (element.type === 'checkbox' || element.type === 'radio') {
            element.checked = !!value;
        } else {
            element.value = value;
        }
    }

    static getFormData(form) {
        if (!form) return {};

        const formData = new FormData(form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            if (data[key]) {
                // Handle multiple values (like checkboxes)
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }

        return data;
    }

    static validateForm(form) {
        if (!form) return false;

        const invalidElements = form.querySelectorAll(':invalid');
        return invalidElements.length === 0;
    }

    // Animation helpers
    static fadeIn(element, duration = 300) {
        if (!element) return Promise.resolve();

        return new Promise(resolve => {
            element.style.opacity = '0';
            element.style.display = 'block';

            const startTime = performance.now();

            function animate(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                element.style.opacity = progress.toString();

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            }

            requestAnimationFrame(animate);
        });
    }

    static fadeOut(element, duration = 300) {
        if (!element) return Promise.resolve();

        return new Promise(resolve => {
            const startOpacity = parseFloat(element.style.opacity) || 1;
            const startTime = performance.now();

            function animate(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                element.style.opacity = (startOpacity * (1 - progress)).toString();

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    element.style.display = 'none';
                    resolve();
                }
            }

            requestAnimationFrame(animate);
        });
    }

    static slideDown(element, duration = 300) {
        if (!element) return Promise.resolve();

        return new Promise(resolve => {
            element.style.overflow = 'hidden';
            element.style.height = '0px';
            element.style.display = 'block';

            const targetHeight = element.scrollHeight;
            const startTime = performance.now();

            function animate(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                element.style.height = (targetHeight * progress) + 'px';

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    element.style.height = '';
                    element.style.overflow = '';
                    resolve();
                }
            }

            requestAnimationFrame(animate);
        });
    }

    static slideUp(element, duration = 300) {
        if (!element) return Promise.resolve();

        return new Promise(resolve => {
            const startHeight = element.offsetHeight;
            element.style.overflow = 'hidden';
            element.style.height = startHeight + 'px';

            const startTime = performance.now();

            function animate(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                element.style.height = (startHeight * (1 - progress)) + 'px';

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    element.style.display = 'none';
                    element.style.height = '';
                    element.style.overflow = '';
                    resolve();
                }
            }

            requestAnimationFrame(animate);
        });
    }

    // Utility functions
    static isElementInViewport(element) {
        if (!element) return false;

        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    static getClosest(element, selector) {
        if (!element) return null;

        // Use native closest if available
        if (element.closest) {
            return element.closest(selector);
        }

        // Fallback for older browsers
        while (element && element.nodeType === 1) {
            if (element.matches(selector)) {
                return element;
            }
            element = element.parentElement;
        }

        return null;
    }

    static siblings(element) {
        if (!element || !element.parentNode) return [];

        return Array.from(element.parentNode.children).filter(child => child !== element);
    }

    static nextSibling(element) {
        if (!element) return null;

        let next = element.nextSibling;
        while (next && next.nodeType !== 1) {
            next = next.nextSibling;
        }

        return next;
    }

    static previousSibling(element) {
        if (!element) return null;

        let prev = element.previousSibling;
        while (prev && prev.nodeType !== 1) {
            prev = prev.previousSibling;
        }

        return prev;
    }

    // Copy to clipboard
    static async copyToClipboard(text) {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                return true;
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();

                const success = document.execCommand('copy');
                document.body.removeChild(textArea);

                return success;
            }
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            return false;
        }
    }

    // Download data as file
    static downloadFile(data, filename, type = 'text/plain') {
        const blob = new Blob([data], { type });
        const url = URL.createObjectURL(blob);

        const a = this.createElement('a', {
            href: url,
            download: filename,
            style: { display: 'none' }
        });

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Load external script
    static loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = this.createElement('script', {
                src: src,
                async: true
            });

            script.onload = resolve;
            script.onerror = reject;

            document.head.appendChild(script);
        });
    }

    // Load external CSS
    static loadCSS(href) {
        return new Promise((resolve, reject) => {
            const link = this.createElement('link', {
                rel: 'stylesheet',
                href: href
            });

            link.onload = resolve;
            link.onerror = reject;

            document.head.appendChild(link);
        });
    }

    // Debounce function
    static debounce(func, wait, immediate = false) {
        let timeout;

        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };

            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);

            if (callNow) func.apply(this, args);
        };
    }

    // Throttle function
    static throttle(func, limit) {
        let inThrottle;

        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Create convenient aliases
const dom = DOMHelpers;
const $ = DOMHelpers.$;
const $$ = DOMHelpers.$$;

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DOMHelpers, dom, $, $$ };
}

// Create global instances for browser use
if (typeof window !== 'undefined') {
    window.domHelpers = {
        init() { console.log('🏗️ DOM helpers initialized'); },
        ...DOMHelpers
    };
    window.dom = dom;
    window.$ = $;
    window.$$ = $$;
    console.log('🏗️ Global DOM helpers instances created');
}
