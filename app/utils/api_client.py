"""
API Client for Dashboard Backend Communication
"""

import requests
import streamlit as st
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """API client for backend communication"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v2"):
        self.base_url = base_url
    
    def get_system_status(self) -> Optional[Dict]:
        """Get system status from API"""
        try:
            response = requests.get(f"{self.base_url}/system-status", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"API Error: {str(e)}")
        return None
    
    def query_ai_agent(self, query: str, language: str = "en") -> Optional[Dict]:
        """Query the AI agent"""
        try:
            with st.spinner("🌊 Analyzing oceanographic data..."):
                response = requests.post(
                    f"{self.base_url}/query",
                    json={"query": query, "language": language},
                    timeout=45
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    st.error(f"API Error: {response.status_code}")
                    
        except Exception as e:
            st.error(f"Query Error: {str(e)}")
        
        return None
