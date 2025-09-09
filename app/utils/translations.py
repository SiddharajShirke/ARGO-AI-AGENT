"""
Multi-language support for dashboard
"""

LANGUAGES = {
    "en": {
        "name": "English",
        "flag": "🇺🇸",
        "title": "Indian Ocean ARGO AI Agent",
        "subtitle": "Advanced Oceanographic Analysis with Real ARGO Float Data",
        "query_placeholder": "Ask about Arabian Sea temperature, Bay of Bengal salinity, monsoon patterns...",
        "search_button": "🔍 Analyze Ocean Data",
        "loading": "🌊 Analyzing oceanographic data...",
        # ... add more translations
    },
    "hi": {
        "name": "हिंदी",
        "flag": "🇮🇳",
        "title": "हिंद महासागर ARGO एआई एजेंट",
        "subtitle": "वास्तविक ARGO फ्लोट डेटा के साथ उन्नत समुद्री विज्ञान विश्लेषण",
        "query_placeholder": "अरब सागर के तापमान, बंगाल की खाड़ी लवणता के बारे में पूछें...",
        "search_button": "🔍 समुद्री डेटा का विश्लेषण करें",
        "loading": "🌊 समुद्री विज्ञान डेटा का विश्लेषण कर रहे हैं...",
        # ... add more translations
    },
    # Add Bengali, Tamil translations...
}

def get_text(key: str, language: str = "en") -> str:
    """Get localized text"""
    return LANGUAGES.get(language, LANGUAGES['en']).get(key, key)
