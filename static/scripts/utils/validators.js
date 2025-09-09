// Form Validation Utilities
class Validators {

    // Email validation
    static email(value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return {
            isValid: emailRegex.test(value),
            message: 'Please enter a valid email address'
        };
    }

    // Password validation
    static password(value, options = {}) {
        const {
            minLength = 8,
            requireUppercase = true,
            requireLowercase = true,
            requireNumbers = true,
            requireSpecialChars = false,
            maxLength = 128
        } = options;

        const errors = [];

        if (value.length < minLength) {
            errors.push(`Password must be at least ${minLength} characters long`);
        }

        if (value.length > maxLength) {
            errors.push(`Password must be no more than ${maxLength} characters long`);
        }

        if (requireUppercase && !/[A-Z]/.test(value)) {
            errors.push('Password must contain at least one uppercase letter');
        }

        if (requireLowercase && !/[a-z]/.test(value)) {
            errors.push('Password must contain at least one lowercase letter');
        }

        if (requireNumbers && !/[0-9]/.test(value)) {
            errors.push('Password must contain at least one number');
        }

        if (requireSpecialChars && !/[^A-Za-z0-9]/.test(value)) {
            errors.push('Password must contain at least one special character');
        }

        return {
            isValid: errors.length === 0,
            message: errors.join('. '),
            errors: errors
        };
    }

    // Required field validation
    static required(value) {
        const isValid = value !== null && value !== undefined && value.toString().trim() !== '';
        return {
            isValid,
            message: 'This field is required'
        };
    }

    // String length validation
    static length(value, min = 0, max = Infinity) {
        const length = value ? value.toString().length : 0;
        let isValid = true;
        let message = '';

        if (length < min) {
            isValid = false;
            message = `Must be at least ${min} characters long`;
        } else if (length > max) {
            isValid = false;
            message = `Must be no more than ${max} characters long`;
        }

        return { isValid, message };
    }

    // Numeric validation
    static number(value, options = {}) {
        const {
            min = -Infinity,
            max = Infinity,
            integer = false,
            positive = false,
            allowZero = true
        } = options;

        const num = parseFloat(value);
        const errors = [];

        if (isNaN(num)) {
            return {
                isValid: false,
                message: 'Please enter a valid number'
            };
        }

        if (integer && !Number.isInteger(num)) {
            errors.push('Must be a whole number');
        }

        if (num < min) {
            errors.push(`Must be at least ${min}`);
        }

        if (num > max) {
            errors.push(`Must be no more than ${max}`);
        }

        if (positive && num < 0) {
            errors.push('Must be a positive number');
        }

        if (!allowZero && num === 0) {
            errors.push('Cannot be zero');
        }

        return {
            isValid: errors.length === 0,
            message: errors.join('. '),
            errors: errors
        };
    }

    // URL validation
    static url(value) {
        try {
            new URL(value);
            return {
                isValid: true,
                message: ''
            };
        } catch {
            return {
                isValid: false,
                message: 'Please enter a valid URL'
            };
        }
    }

    // Phone number validation (basic)
    static phone(value) {
        // Remove all non-digits
        const digitsOnly = value.replace(/\D/g, '');

        // Basic validation: 10-15 digits
        const isValid = digitsOnly.length >= 10 && digitsOnly.length <= 15;

        return {
            isValid,
            message: 'Please enter a valid phone number'
        };
    }

    // Date validation
    static date(value, options = {}) {
        const {
            minDate = null,
            maxDate = null,
            format = 'YYYY-MM-DD'
        } = options;

        const date = new Date(value);
        const errors = [];

        if (isNaN(date.getTime())) {
            return {
                isValid: false,
                message: 'Please enter a valid date'
            };
        }

        if (minDate && date < new Date(minDate)) {
            errors.push(`Date must be after ${minDate}`);
        }

        if (maxDate && date > new Date(maxDate)) {
            errors.push(`Date must be before ${maxDate}`);
        }

        return {
            isValid: errors.length === 0,
            message: errors.join('. '),
            errors: errors
        };
    }

    // Coordinate validation
    static latitude(value) {
        const num = parseFloat(value);
        const isValid = !isNaN(num) && num >= -90 && num <= 90;

        return {
            isValid,
            message: 'Latitude must be between -90 and 90 degrees'
        };
    }

    static longitude(value) {
        const num = parseFloat(value);
        const isValid = !isNaN(num) && num >= -180 && num <= 180;

        return {
            isValid,
            message: 'Longitude must be between -180 and 180 degrees'
        };
    }

    // File validation
    static file(file, options = {}) {
        const {
            maxSize = 10 * 1024 * 1024, // 10MB default
            allowedTypes = [],
            allowedExtensions = []
        } = options;

        const errors = [];

        if (!file) {
            return {
                isValid: false,
                message: 'Please select a file'
            };
        }

        // Check file size
        if (file.size > maxSize) {
            const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(1);
            errors.push(`File size must be less than ${maxSizeMB}MB`);
        }

        // Check file type
        if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
            errors.push(`File type must be one of: ${allowedTypes.join(', ')}`);
        }

        // Check file extension
        if (allowedExtensions.length > 0) {
            const extension = file.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(extension)) {
                errors.push(`File extension must be one of: ${allowedExtensions.join(', ')}`);
            }
        }

        return {
            isValid: errors.length === 0,
            message: errors.join('. '),
            errors: errors
        };
    }

    // Custom regex validation
    static pattern(value, regex, message = 'Invalid format') {
        const isValid = regex.test(value);
        return {
            isValid,
            message: isValid ? '' : message
        };
    }

    // Match validation (for password confirmation)
    static match(value, compareValue, fieldName = 'field') {
        const isValid = value === compareValue;
        return {
            isValid,
            message: isValid ? '' : `${fieldName} does not match`
        };
    }

    // Array validation
    static array(value, options = {}) {
        const {
            minLength = 0,
            maxLength = Infinity,
            unique = false
        } = options;

        if (!Array.isArray(value)) {
            return {
                isValid: false,
                message: 'Must be an array'
            };
        }

        const errors = [];

        if (value.length < minLength) {
            errors.push(`Must contain at least ${minLength} items`);
        }

        if (value.length > maxLength) {
            errors.push(`Must contain no more than ${maxLength} items`);
        }

        if (unique && new Set(value).size !== value.length) {
            errors.push('Items must be unique');
        }

        return {
            isValid: errors.length === 0,
            message: errors.join('. '),
            errors: errors
        };
    }

    // Credit card validation (Luhn algorithm)
    static creditCard(value) {
        const cardNumber = value.replace(/\s/g, '');

        if (!/^\d+$/.test(cardNumber)) {
            return {
                isValid: false,
                message: 'Credit card number must contain only digits'
            };
        }

        if (cardNumber.length < 13 || cardNumber.length > 19) {
            return {
                isValid: false,
                message: 'Credit card number must be 13-19 digits long'
            };
        }

        // Luhn algorithm
        let sum = 0;
        let alternate = false;

        for (let i = cardNumber.length - 1; i >= 0; i--) {
            let digit = parseInt(cardNumber.charAt(i));

            if (alternate) {
                digit *= 2;
                if (digit > 9) {
                    digit = Math.floor(digit / 10) + (digit % 10);
                }
            }

            sum += digit;
            alternate = !alternate;
        }

        const isValid = sum % 10 === 0;

        return {
            isValid,
            message: isValid ? '' : 'Invalid credit card number'
        };
    }

    // IP address validation
    static ip(value, version = 'both') {
        const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
        const ipv6Regex = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;

        let isValid = false;

        if (version === 'v4' || version === 'both') {
            if (ipv4Regex.test(value)) {
                // Check if each octet is 0-255
                const octets = value.split('.');
                isValid = octets.every(octet => {
                    const num = parseInt(octet);
                    return num >= 0 && num <= 255;
                });
            }
        }

        if (!isValid && (version === 'v6' || version === 'both')) {
            isValid = ipv6Regex.test(value);
        }

        return {
            isValid,
            message: `Please enter a valid IP${version !== 'both' ? version : ''} address`
        };
    }

    // Social Security Number validation (US format)
    static ssn(value) {
        const ssnRegex = /^\d{3}-?\d{2}-?\d{4}$/;
        const isValid = ssnRegex.test(value);

        return {
            isValid,
            message: 'Please enter a valid SSN (XXX-XX-XXXX)'
        };
    }

    // Postal code validation
    static postalCode(value, country = 'US') {
        const patterns = {
            US: /^\d{5}(-\d{4})?$/,
            CA: /^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$/,
            UK: /^[A-Za-z]{1,2}\d[A-Za-z\d]?\s?\d[A-Za-z]{2}$/,
            DE: /^\d{5}$/,
            FR: /^\d{5}$/
        };

        const pattern = patterns[country.toUpperCase()];

        if (!pattern) {
            return {
                isValid: true,
                message: ''
            };
        }

        const isValid = pattern.test(value);

        return {
            isValid,
            message: `Please enter a valid ${country} postal code`
        };
    }
}

// Form Validation Manager
class FormValidator {
    constructor(form, rules = {}) {
        this.form = form;
        this.rules = rules;
        this.errors = {};
        this.isValid = true;

        this.setupEventListeners();
    }

    // Setup real-time validation
    setupEventListeners() {
        if (!this.form) return;

        // Validate on blur
        this.form.addEventListener('blur', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.validateField(e.target);
            }
        }, true);

        // Validate on submit
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();

            if (this.validateForm()) {
                this.onValidSubmit();
            } else {
                this.onInvalidSubmit();
            }
        });

        // Clear errors on input
        this.form.addEventListener('input', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.clearFieldError(e.target);
            }
        });
    }

    // Add validation rule for a field
    addRule(fieldName, validator, options = {}) {
        if (!this.rules[fieldName]) {
            this.rules[fieldName] = [];
        }

        this.rules[fieldName].push({
            validator,
            options,
            message: options.message || ''
        });
    }

    // Validate a single field
    validateField(field) {
        const fieldName = field.name || field.id;
        const fieldRules = this.rules[fieldName];

        if (!fieldRules) return true;

        const value = this.getFieldValue(field);
        let isValid = true;

        for (const rule of fieldRules) {
            let result;

            if (typeof rule.validator === 'string') {
                // Use built-in validator
                if (Validators[rule.validator]) {
                    result = Validators[rule.validator](value, rule.options);
                } else {
                    console.warn(`Unknown validator: ${rule.validator}`);
                    continue;
                }
            } else if (typeof rule.validator === 'function') {
                // Use custom validator function
                result = rule.validator(value, rule.options);
            } else {
                console.warn('Invalid validator type');
                continue;
            }

            if (!result.isValid) {
                isValid = false;
                this.showFieldError(field, rule.message || result.message);
                break;
            }
        }

        if (isValid) {
            this.clearFieldError(field);
        }

        return isValid;
    }

    // Validate entire form
    validateForm() {
        this.errors = {};
        this.isValid = true;

        const fields = this.form.querySelectorAll('input, textarea, select');

        fields.forEach(field => {
            if (!this.validateField(field)) {
                this.isValid = false;
            }
        });

        return this.isValid;
    }

    // Get field value
    getFieldValue(field) {
        if (field.type === 'checkbox') {
            return field.checked;
        } else if (field.type === 'radio') {
            const checked = this.form.querySelector(`input[name="${field.name}"]:checked`);
            return checked ? checked.value : '';
        } else if (field.type === 'file') {
            return field.files[0] || null;
        } else {
            return field.value;
        }
    }

    // Show field error
    showFieldError(field, message) {
        const fieldName = field.name || field.id;
        this.errors[fieldName] = message;

        // Add error class
        field.classList.add('error', 'invalid');

        // Find or create error element
        let errorElement = this.form.querySelector(`[data-error-for="${fieldName}"]`);

        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            errorElement.setAttribute('data-error-for', fieldName);

            // Insert after the field
            field.parentNode.insertBefore(errorElement, field.nextSibling);
        }

        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }

    // Clear field error
    clearFieldError(field) {
        const fieldName = field.name || field.id;
        delete this.errors[fieldName];

        // Remove error class
        field.classList.remove('error', 'invalid');

        // Hide error element
        const errorElement = this.form.querySelector(`[data-error-for="${fieldName}"]`);
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }

    // Clear all errors
    clearAllErrors() {
        this.errors = {};

        // Remove error classes
        this.form.querySelectorAll('.error, .invalid').forEach(element => {
            element.classList.remove('error', 'invalid');
        });

        // Hide error messages
        this.form.querySelectorAll('.field-error').forEach(element => {
            element.style.display = 'none';
        });
    }

    // Get form data
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            if (data[key]) {
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

    // Set form data
    setFormData(data) {
        Object.keys(data).forEach(key => {
            const field = this.form.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox' || field.type === 'radio') {
                    field.checked = !!data[key];
                } else {
                    field.value = data[key];
                }
            }
        });
    }

    // Event handlers (override these)
    onValidSubmit() {
        console.log('Form is valid, submitting...');
        // Override this method
    }

    onInvalidSubmit() {
        console.log('Form has errors:', this.errors);
        // Focus first invalid field
        const firstErrorField = this.form.querySelector('.error');
        if (firstErrorField) {
            firstErrorField.focus();
        }
    }

    // Destroy validator
    destroy() {
        this.clearAllErrors();
        // Remove event listeners would require keeping references
        // For now, just clear the rules
        this.rules = {};
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Validators, FormValidator };
}

// Create global instances for browser use
if (typeof window !== 'undefined') {
    window.validators = Validators;
    window.FormValidator = FormValidator;
    console.log('✅ Global validators instances created');
}
