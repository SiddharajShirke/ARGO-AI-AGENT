// Translation and Internationalization Utilities
class Translations {
    constructor() {
        this.currentLanguage = 'en';
        this.translations = {};
        this.fallbackLanguage = 'en';
        this.loadedLanguages = new Set();
    }

    // Initialize with default translations
    async init(language = 'en') {
        this.currentLanguage = language;
        await this.loadLanguage(language);

        // Load fallback if different
        if (language !== this.fallbackLanguage) {
            await this.loadLanguage(this.fallbackLanguage);
        }
    }

    // Load translation data for a specific language
    async loadLanguage(languageCode) {
        if (this.loadedLanguages.has(languageCode)) {
            return;
        }

        try {
            // Try to load from data file first
            const response = await fetch(`/static/data/translations/${languageCode}.json`);
            if (response.ok) {
                const translations = await response.json();
                this.translations[languageCode] = translations;
                this.loadedLanguages.add(languageCode);
                return;
            }
        } catch (error) {
            console.warn(`Could not load translations for ${languageCode}:`, error);
        }

        // Fall back to embedded translations
        this.translations[languageCode] = this.getEmbeddedTranslations(languageCode);
        this.loadedLanguages.add(languageCode);
    }

    // Get embedded translations for a language
    getEmbeddedTranslations(languageCode) {
        const translations = {
            en: {
                // Navigation
                'nav.home': 'Home',
                'nav.dashboard': 'Dashboard',
                'nav.chatbot': 'AI Chat',
                'nav.account': 'Account',
                'nav.logout': 'Logout',

                // Common actions
                'action.save': 'Save',
                'action.cancel': 'Cancel',
                'action.edit': 'Edit',
                'action.delete': 'Delete',
                'action.search': 'Search',
                'action.export': 'Export',
                'action.refresh': 'Refresh',
                'action.login': 'Login',
                'action.logout': 'Logout',
                'action.register': 'Register',
                'action.submit': 'Submit',
                'action.continue': 'Continue',
                'action.back': 'Back',
                'action.next': 'Next',
                'action.upload': 'Upload',
                'action.download': 'Download',

                // Home page
                'home.title': 'Argo AI Agent',
                'home.subtitle': 'Intelligent Ocean Data Analysis Platform',
                'home.welcome': 'Welcome to the ocean research platform',
                'home.quickActions': 'Quick Actions',
                'home.systemStatus': 'System Status',
                'home.recentActivity': 'Recent Activity',
                'home.regionalOverview': 'Regional Overview',
                'home.startChat': 'Start AI Chat',
                'home.viewDashboard': 'View Dashboard',
                'home.searchProfiles': 'Search Profiles',
                'home.newAnalysis': 'New Analysis',

                // Dashboard
                'dashboard.title': 'Ocean Data Dashboard',
                'dashboard.subtitle': 'Real-time analysis of Argo float profiles',
                'dashboard.overview': 'Overview',
                'dashboard.search': 'Search',
                'dashboard.analytics': 'Analytics',
                'dashboard.totalProfiles': 'Total Profiles',
                'dashboard.activeRegions': 'Active Regions',
                'dashboard.recentUpdates': 'Recent Updates',
                'dashboard.dataQuality': 'Data Quality',
                'dashboard.temperature': 'Temperature',
                'dashboard.salinity': 'Salinity',
                'dashboard.pressure': 'Pressure',

                // Chat
                'chat.title': 'AI Assistant',
                'chat.subtitle': 'Ask questions about ocean data',
                'chat.placeholder': 'Ask me about ocean data, Argo profiles, or research insights...',
                'chat.send': 'Send',
                'chat.clear': 'Clear Chat',
                'chat.export': 'Export Chat',
                'chat.online': 'AI Online',
                'chat.typing': 'AI is thinking...',
                'chat.welcome': 'Hello! I\'m your AI assistant for ocean data analysis.',

                // Authentication
                'auth.login': 'Sign In',
                'auth.register': 'Create Account',
                'auth.forgotPassword': 'Forgot Password',
                'auth.email': 'Email Address',
                'auth.password': 'Password',
                'auth.confirmPassword': 'Confirm Password',
                'auth.fullName': 'Full Name',
                'auth.organization': 'Organization',
                'auth.rememberMe': 'Remember me',
                'auth.agreeTerms': 'I agree to the Terms of Service',
                'auth.alreadyHaveAccount': 'Already have an account?',
                'auth.dontHaveAccount': 'Don\'t have an account?',
                'auth.signUp': 'Sign up',
                'auth.signIn': 'Sign in',

                // Account
                'account.profile': 'Profile',
                'account.preferences': 'Preferences',
                'account.security': 'Security',
                'account.usage': 'Usage',
                'account.notifications': 'Notifications',
                'account.basicInfo': 'Basic Information',
                'account.contactInfo': 'Contact Information',
                'account.researchInterests': 'Research Interests',
                'account.changePassword': 'Change Password',
                'account.twoFactor': 'Two-Factor Authentication',
                'account.activeSessions': 'Active Sessions',

                // Messages
                'msg.loading': 'Loading...',
                'msg.error': 'An error occurred',
                'msg.success': 'Success',
                'msg.saved': 'Saved successfully',
                'msg.deleted': 'Deleted successfully',
                'msg.noResults': 'No results found',
                'msg.searchResults': 'Search Results',
                'msg.processing': 'Processing...',
                'msg.connecting': 'Connecting...',
                'msg.disconnected': 'Disconnected',
                'msg.reconnecting': 'Reconnecting...',

                // Units and measurements
                'unit.celsius': 'Celsius',
                'unit.fahrenheit': 'Fahrenheit',
                'unit.kelvin': 'Kelvin',
                'unit.meters': 'meters',
                'unit.feet': 'feet',
                'unit.latitude': 'Latitude',
                'unit.longitude': 'Longitude',
                'unit.depth': 'Depth',
                'unit.temperature': 'Temperature',
                'unit.salinity': 'Salinity',

                // Time and dates
                'time.now': 'now',
                'time.minuteAgo': 'minute ago',
                'time.minutesAgo': 'minutes ago',
                'time.hourAgo': 'hour ago',
                'time.hoursAgo': 'hours ago',
                'time.dayAgo': 'day ago',
                'time.daysAgo': 'days ago',
                'time.weekAgo': 'week ago',
                'time.weeksAgo': 'weeks ago',
                'time.monthAgo': 'month ago',
                'time.monthsAgo': 'months ago',
                'time.yearAgo': 'year ago',
                'time.yearsAgo': 'years ago',

                // Regions
                'region.atlantic': 'Atlantic Ocean',
                'region.pacific': 'Pacific Ocean',
                'region.indian': 'Indian Ocean',
                'region.arctic': 'Arctic Ocean',
                'region.southern': 'Southern Ocean',
                'region.mediterranean': 'Mediterranean Sea',
                'region.caribbean': 'Caribbean Sea',
                'region.gulfOfMexico': 'Gulf of Mexico',

                // Analysis types
                'analysis.correlation': 'Correlation Analysis',
                'analysis.trends': 'Trend Analysis',
                'analysis.anomalies': 'Anomaly Detection',
                'analysis.seasonal': 'Seasonal Analysis',
                'analysis.regional': 'Regional Analysis',
                'analysis.temporal': 'Temporal Analysis',

                // Errors
                'error.networkError': 'Network error. Please check your connection.',
                'error.serverError': 'Server error. Please try again later.',
                'error.unauthorized': 'Unauthorized. Please log in again.',
                'error.forbidden': 'Access denied.',
                'error.notFound': 'Resource not found.',
                'error.validationError': 'Please check your input.',
                'error.timeout': 'Request timeout. Please try again.',
                'error.unknown': 'An unexpected error occurred.'
            },

            es: {
                // Navigation
                'nav.home': 'Inicio',
                'nav.dashboard': 'Panel',
                'nav.chatbot': 'Chat IA',
                'nav.account': 'Cuenta',
                'nav.logout': 'Cerrar Sesión',

                // Common actions
                'action.save': 'Guardar',
                'action.cancel': 'Cancelar',
                'action.edit': 'Editar',
                'action.delete': 'Eliminar',
                'action.search': 'Buscar',
                'action.export': 'Exportar',
                'action.refresh': 'Actualizar',
                'action.login': 'Iniciar Sesión',
                'action.logout': 'Cerrar Sesión',
                'action.register': 'Registrarse',
                'action.submit': 'Enviar',
                'action.continue': 'Continuar',
                'action.back': 'Atrás',
                'action.next': 'Siguiente',
                'action.upload': 'Subir',
                'action.download': 'Descargar',

                // Home page
                'home.title': 'Agente IA Argo',
                'home.subtitle': 'Plataforma Inteligente de Análisis de Datos Oceánicos',
                'home.welcome': 'Bienvenido a la plataforma de investigación oceánica',
                'home.quickActions': 'Acciones Rápidas',
                'home.systemStatus': 'Estado del Sistema',
                'home.recentActivity': 'Actividad Reciente',
                'home.regionalOverview': 'Resumen Regional',

                // Messages
                'msg.loading': 'Cargando...',
                'msg.error': 'Ocurrió un error',
                'msg.success': 'Éxito',
                'msg.saved': 'Guardado exitosamente',
                'msg.deleted': 'Eliminado exitosamente',
                'msg.noResults': 'No se encontraron resultados',
                'msg.processing': 'Procesando...',

                // Units
                'unit.meters': 'metros',
                'unit.feet': 'pies',
                'unit.latitude': 'Latitud',
                'unit.longitude': 'Longitud',
                'unit.depth': 'Profundidad',
                'unit.temperature': 'Temperatura',
                'unit.salinity': 'Salinidad',

                // Regions
                'region.atlantic': 'Océano Atlántico',
                'region.pacific': 'Océano Pacífico',
                'region.indian': 'Océano Índico',
                'region.arctic': 'Océano Ártico',
                'region.southern': 'Océano Antártico'
            },

            fr: {
                // Navigation
                'nav.home': 'Accueil',
                'nav.dashboard': 'Tableau de Bord',
                'nav.chatbot': 'Chat IA',
                'nav.account': 'Compte',
                'nav.logout': 'Déconnexion',

                // Common actions
                'action.save': 'Enregistrer',
                'action.cancel': 'Annuler',
                'action.edit': 'Modifier',
                'action.delete': 'Supprimer',
                'action.search': 'Rechercher',
                'action.export': 'Exporter',
                'action.refresh': 'Actualiser',
                'action.login': 'Connexion',
                'action.logout': 'Déconnexion',
                'action.register': 'S\'inscrire',

                // Home page
                'home.title': 'Agent IA Argo',
                'home.subtitle': 'Plateforme Intelligente d\'Analyse de Données Océaniques',
                'home.welcome': 'Bienvenue sur la plateforme de recherche océanique',

                // Messages
                'msg.loading': 'Chargement...',
                'msg.error': 'Une erreur s\'est produite',
                'msg.success': 'Succès',
                'msg.saved': 'Enregistré avec succès',
                'msg.noResults': 'Aucun résultat trouvé',

                // Units
                'unit.meters': 'mètres',
                'unit.temperature': 'Température',
                'unit.salinity': 'Salinité',

                // Regions
                'region.atlantic': 'Océan Atlantique',
                'region.pacific': 'Océan Pacifique',
                'region.indian': 'Océan Indien'
            },

            de: {
                // Navigation
                'nav.home': 'Startseite',
                'nav.dashboard': 'Dashboard',
                'nav.chatbot': 'KI-Chat',
                'nav.account': 'Konto',
                'nav.logout': 'Abmelden',

                // Common actions
                'action.save': 'Speichern',
                'action.cancel': 'Abbrechen',
                'action.edit': 'Bearbeiten',
                'action.delete': 'Löschen',
                'action.search': 'Suchen',
                'action.export': 'Exportieren',
                'action.refresh': 'Aktualisieren',

                // Home page
                'home.title': 'Argo KI-Agent',
                'home.subtitle': 'Intelligente Plattform für Meeresdatenanalyse',
                'home.welcome': 'Willkommen auf der Meeresforschungsplattform',

                // Messages
                'msg.loading': 'Wird geladen...',
                'msg.error': 'Ein Fehler ist aufgetreten',
                'msg.success': 'Erfolgreich',
                'msg.saved': 'Erfolgreich gespeichert',
                'msg.noResults': 'Keine Ergebnisse gefunden',

                // Units
                'unit.meters': 'Meter',
                'unit.temperature': 'Temperatur',
                'unit.salinity': 'Salzgehalt',

                // Regions
                'region.atlantic': 'Atlantischer Ozean',
                'region.pacific': 'Pazifischer Ozean',
                'region.indian': 'Indischer Ozean'
            },

            zh: {
                // Navigation
                'nav.home': '首页',
                'nav.dashboard': '仪表板',
                'nav.chatbot': 'AI对话',
                'nav.account': '账户',
                'nav.logout': '退出',

                // Common actions
                'action.save': '保存',
                'action.cancel': '取消',
                'action.edit': '编辑',
                'action.delete': '删除',
                'action.search': '搜索',
                'action.export': '导出',
                'action.refresh': '刷新',

                // Home page
                'home.title': 'Argo AI 代理',
                'home.subtitle': '智能海洋数据分析平台',
                'home.welcome': '欢迎来到海洋研究平台',

                // Messages
                'msg.loading': '加载中...',
                'msg.error': '发生错误',
                'msg.success': '成功',
                'msg.saved': '保存成功',
                'msg.noResults': '未找到结果',

                // Units
                'unit.meters': '米',
                'unit.temperature': '温度',
                'unit.salinity': '盐度',

                // Regions
                'region.atlantic': '大西洋',
                'region.pacific': '太平洋',
                'region.indian': '印度洋'
            }
        };

        return translations[languageCode] || translations.en;
    }

    // Get translated text
    t(key, params = {}) {
        const languageData = this.translations[this.currentLanguage] || {};
        const fallbackData = this.translations[this.fallbackLanguage] || {};

        let text = languageData[key] || fallbackData[key] || key;

        // Replace parameters in text
        Object.keys(params).forEach(paramKey => {
            text = text.replace(new RegExp(`{{${paramKey}}}`, 'g'), params[paramKey]);
        });

        return text;
    }

    // Set current language
    async setLanguage(languageCode) {
        await this.loadLanguage(languageCode);
        this.currentLanguage = languageCode;
        this.updatePage();
    }

    // Get current language
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    // Get available languages
    getAvailableLanguages() {
        return [
            { code: 'en', name: 'English', nativeName: 'English' },
            { code: 'es', name: 'Spanish', nativeName: 'Español' },
            { code: 'fr', name: 'French', nativeName: 'Français' },
            { code: 'de', name: 'German', nativeName: 'Deutsch' },
            { code: 'zh', name: 'Chinese', nativeName: '中文' }
        ];
    }

    // Update page text with current language
    updatePage() {
        // Update elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.dataset.i18n;
            const translatedText = this.t(key);

            if (element.tagName === 'INPUT' && (element.type === 'text' || element.type === 'email')) {
                element.placeholder = translatedText;
            } else {
                element.textContent = translatedText;
            }
        });

        // Update title attribute
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.dataset.i18nTitle;
            element.title = this.t(key);
        });

        // Update aria-label attribute
        document.querySelectorAll('[data-i18n-aria]').forEach(element => {
            const key = element.dataset.i18nAria;
            element.setAttribute('aria-label', this.t(key));
        });

        // Trigger custom event for components to update
        document.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: this.currentLanguage }
        }));
    }

    // Format numbers according to locale
    formatNumber(number, options = {}) {
        const locales = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'zh': 'zh-CN'
        };

        const locale = locales[this.currentLanguage] || 'en-US';

        return new Intl.NumberFormat(locale, options).format(number);
    }

    // Format dates according to locale
    formatDate(date, options = {}) {
        const locales = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'zh': 'zh-CN'
        };

        const locale = locales[this.currentLanguage] || 'en-US';

        return new Intl.DateTimeFormat(locale, options).format(new Date(date));
    }

    // Format relative time (e.g., "2 hours ago")
    formatRelativeTime(date) {
        const now = new Date();
        const target = new Date(date);
        const diffMs = now - target;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        const diffWeeks = Math.floor(diffDays / 7);
        const diffMonths = Math.floor(diffDays / 30);
        const diffYears = Math.floor(diffDays / 365);

        if (diffSecs < 60) {
            return this.t('time.now');
        } else if (diffMins < 60) {
            return diffMins === 1 ?
                `1 ${this.t('time.minuteAgo')}` :
                `${diffMins} ${this.t('time.minutesAgo')}`;
        } else if (diffHours < 24) {
            return diffHours === 1 ?
                `1 ${this.t('time.hourAgo')}` :
                `${diffHours} ${this.t('time.hoursAgo')}`;
        } else if (diffDays < 7) {
            return diffDays === 1 ?
                `1 ${this.t('time.dayAgo')}` :
                `${diffDays} ${this.t('time.daysAgo')}`;
        } else if (diffWeeks < 4) {
            return diffWeeks === 1 ?
                `1 ${this.t('time.weekAgo')}` :
                `${diffWeeks} ${this.t('time.weeksAgo')}`;
        } else if (diffMonths < 12) {
            return diffMonths === 1 ?
                `1 ${this.t('time.monthAgo')}` :
                `${diffMonths} ${this.t('time.monthsAgo')}`;
        } else {
            return diffYears === 1 ?
                `1 ${this.t('time.yearAgo')}` :
                `${diffYears} ${this.t('time.yearsAgo')}`;
        }
    }

    // Get direction for text (LTR/RTL)
    getTextDirection() {
        const rtlLanguages = ['ar', 'he', 'fa', 'ur'];
        return rtlLanguages.includes(this.currentLanguage) ? 'rtl' : 'ltr';
    }

    // Pluralization helper
    plural(count, singularKey, pluralKey = null) {
        if (count === 1) {
            return this.t(singularKey);
        }

        if (pluralKey) {
            return this.t(pluralKey);
        }

        // Try to find plural form by adding 's' to the singular key
        const pluralKeyGenerated = singularKey + 's';
        return this.t(pluralKeyGenerated);
    }

    // Currency formatting
    formatCurrency(amount, currency = 'USD') {
        const locales = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'zh': 'zh-CN'
        };

        const locale = locales[this.currentLanguage] || 'en-US';

        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    // Detect browser language
    detectBrowserLanguage() {
        const browserLanguage = navigator.language || navigator.userLanguage;
        const languageCode = browserLanguage.split('-')[0];

        // Check if we support this language
        const availableLanguages = this.getAvailableLanguages().map(lang => lang.code);

        return availableLanguages.includes(languageCode) ? languageCode : this.fallbackLanguage;
    }

    // Add translation key dynamically
    addTranslation(language, key, value) {
        if (!this.translations[language]) {
            this.translations[language] = {};
        }

        this.translations[language][key] = value;
    }

    // Check if translation exists
    hasTranslation(key, language = null) {
        const lang = language || this.currentLanguage;
        const languageData = this.translations[lang] || {};
        return key in languageData;
    }

    // Get all translations for a language
    getLanguageData(language = null) {
        const lang = language || this.currentLanguage;
        return this.translations[lang] || {};
    }

    // Export translations
    exportTranslations(language = null) {
        const lang = language || this.currentLanguage;
        const data = this.getLanguageData(lang);

        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `translations-${lang}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Create global instance
const translations = new Translations();

// Convenience function for translations
function t(key, params = {}) {
    return translations.t(key, params);
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Translations, translations, t };
}
