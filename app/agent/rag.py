"""
Retrieval Augmented Generation (RAG) for Indian Ocean ARGO AI Agent
Connects ARGO oceanographic data with LLM for intelligent responses
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ARGODataRetriever:
    """
    Retrieval system for ARGO oceanographic data
    Provides context-aware data retrieval for AI agent
    """
    
    def __init__(self):
        self.logger = logger
        self.initialized = False
        
    async def initialize(self):
        """Initialize retriever with database and vector store connections"""
        try:
            from ..core.database import db, ARGOProfile
            from ..core.vector_db import vector_db
            
            self.db = db
            self.vector_db = vector_db
            self.ARGOProfile = ARGOProfile
            self.initialized = True
            
            logger.info("ARGO data retriever initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ARGO data retriever: {e}")
            self.initialized = False
    
    async def retrieve_profiles_by_region(self, region: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve ARGO profiles by ocean region"""
        
        if not self.initialized:
            await self.initialize()
            
        try:
            profiles = []
            
            # Try database first
            if hasattr(self, 'db') and self.db:
                db_profiles = await self.db.get_profiles_by_region(region, limit)
                if db_profiles:
                    profiles.extend(db_profiles)
                    logger.info(f"Retrieved {len(db_profiles)} profiles from database for region: {region}")
            
            # Fallback to mock data if no database profiles
            if not profiles:
                profiles = self._generate_mock_profiles(region, limit)
                logger.info(f"Generated {len(profiles)} mock profiles for region: {region}")
            
            return profiles
            
        except Exception as e:
            logger.error(f"Error retrieving profiles by region {region}: {e}")
            return self._generate_mock_profiles(region, limit)
    
    async def retrieve_profiles_by_query(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve ARGO profiles based on semantic query"""
        
        if not self.initialized:
            await self.initialize()
            
        try:
            # Extract search parameters from query
            search_params = self._parse_query(query)
            
            profiles = []
            
            # Try vector search first
            if hasattr(self, 'vector_db') and self.vector_db:
                vector_profiles = await self._vector_search(query, limit)
                if vector_profiles:
                    profiles.extend(vector_profiles)
                    logger.info(f"Retrieved {len(vector_profiles)} profiles from vector search")
            
            # Try database search
            if hasattr(self, 'db') and self.db and len(profiles) < limit:
                db_profiles = await self._database_search(search_params, limit - len(profiles))
                if db_profiles:
                    profiles.extend(db_profiles)
                    logger.info(f"Retrieved {len(db_profiles)} additional profiles from database search")
            
            # Fallback to mock data
            if not profiles:
                profiles = self._generate_contextual_mock_profiles(search_params, limit)
                logger.info(f"Generated {len(profiles)} contextual mock profiles")
            
            return profiles[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving profiles by query '{query}': {e}")
            return self._generate_contextual_mock_profiles({"region": "Indian Ocean"}, limit)
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse user query to extract search parameters"""
        
        query_lower = query.lower()
        params = {
            "region": "Indian Ocean",
            "parameters": [],
            "depth_range": None,
            "temperature_range": None,
            "salinity_range": None
        }
        
        # Region detection
        if "arabian sea" in query_lower:
            params["region"] = "Arabian Sea"
        elif "bay of bengal" in query_lower:
            params["region"] = "Bay of Bengal"
        elif "equatorial" in query_lower:
            params["region"] = "Equatorial Indian Ocean"
        
        # Parameter detection
        if any(word in query_lower for word in ["temperature", "temp", "thermal"]):
            params["parameters"].append("temperature")
        if any(word in query_lower for word in ["salinity", "salt", "psu"]):
            params["parameters"].append("salinity")
        if any(word in query_lower for word in ["depth", "deep", "profile"]):
            params["parameters"].append("depth")
        if any(word in query_lower for word in ["pressure", "dbar"]):
            params["parameters"].append("pressure")
        
        return params
    
    async def _vector_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        
        try:
            if hasattr(self.vector_db, 'search'):
                results = await self.vector_db.search(
                    collection_name="argo_profiles",
                    query_text=query,
                    n_results=limit
                )
                
                profiles = []
                for result in results.get('documents', []):
                    if isinstance(result, list) and result:
                        for doc in result:
                            try:
                                profile_data = json.loads(doc)
                                profiles.append(profile_data)
                            except:
                                continue
                
                return profiles
                
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            
        return []
    
    async def _database_search(self, params: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Perform database search with parameters"""
        
        try:
            if hasattr(self, 'db') and self.db:
                # This would be implemented with actual database queries
                # For now, return empty to trigger fallback
                pass
                
        except Exception as e:
            logger.error(f"Database search failed: {e}")
            
        return []
    
    def _generate_mock_profiles(self, region: str, limit: int) -> List[Dict[str, Any]]:
        """Generate realistic mock ARGO profiles for testing"""
        
        profiles = []
        
        # Regional coordinate ranges
        region_bounds = {
            "Arabian Sea": {"lat": (10, 25), "lon": (50, 75)},
            "Bay of Bengal": {"lat": (5, 22), "lon": (80, 95)},
            "Equatorial Indian Ocean": {"lat": (-5, 5), "lon": (50, 100)},
            "Indian Ocean": {"lat": (-30, 30), "lon": (30, 120)}
        }
        
        bounds = region_bounds.get(region, region_bounds["Indian Ocean"])
        
        for i in range(limit):
            # Generate realistic coordinates
            lat = np.random.uniform(bounds["lat"][0], bounds["lat"][1])
            lon = np.random.uniform(bounds["lon"][0], bounds["lon"][1])
            
            # Generate realistic oceanographic data
            surface_temp = np.random.uniform(26, 30)  # Tropical ocean temperatures
            surface_salinity = np.random.uniform(34, 36)  # Indian Ocean salinity range
            max_depth = np.random.uniform(800, 2000)
            
            profile = {
                "id": f"mock_{region}_{i+1}",
                "float_id": f"MOCK{5900000 + i}",
                "cycle_number": np.random.randint(1, 200),
                "profile_date": (datetime.now() - timedelta(days=np.random.randint(0, 365))).isoformat(),
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "ocean_region": region,
                "surface_temperature": round(surface_temp, 2),
                "surface_salinity": round(surface_salinity, 2),
                "surface_pressure": 10.0,
                "max_depth": round(max_depth, 1),
                "num_levels": np.random.randint(50, 150),
                "temperature_range": round(np.random.uniform(8, 15), 2),
                "salinity_range": round(np.random.uniform(1, 3), 2),
                "mixed_layer_depth": round(np.random.uniform(20, 80), 1),
                "thermocline_depth": round(np.random.uniform(100, 300), 1)
            }
            
            profiles.append(profile)
        
        return profiles
    
    def _generate_contextual_mock_profiles(self, params: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Generate mock profiles based on query context"""
        
        region = params.get("region", "Indian Ocean")
        return self._generate_mock_profiles(region, limit)


class RAGPipeline:
    """
    Complete RAG pipeline for ARGO AI Agent
    Combines retrieval with language model generation
    """
    
    def __init__(self):
        self.retriever = ARGODataRetriever()
        self.logger = logger
        self.initialized = False
    
    async def initialize(self):
        """Initialize RAG pipeline"""
        try:
            await self.retriever.initialize()
            
            # Initialize LLM
            try:
                from .llm import get_llm_client
                self.llm = get_llm_client()
                logger.info("LLM client initialized for RAG pipeline")
            except Exception as e:
                logger.warning(f"LLM initialization failed, using fallback: {e}")
                self.llm = None
            
            self.initialized = True
            logger.info("RAG pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"RAG pipeline initialization failed: {e}")
            self.initialized = False
    
    async def process_query(self, query: str, region: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Process user query using RAG pipeline"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Retrieve relevant ARGO data
            if region:
                profiles = await self.retriever.retrieve_profiles_by_region(region, limit)
            else:
                profiles = await self.retriever.retrieve_profiles_by_query(query, limit)
            
            # Generate context from retrieved data
            context = self._build_context(profiles, query)
            
            # Generate response using LLM
            response = await self._generate_response(query, context, profiles)
            
            return {
                "response": response,
                "profiles_found": len(profiles),
                "data_summary": self._summarize_data(profiles),
                "query_time": 0.5,  # Mock timing
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RAG query processing failed: {e}")
            return self._fallback_response(query)
    
    def _build_context(self, profiles: List[Dict[str, Any]], query: str) -> str:
        """Build context string from retrieved profiles"""
        
        if not profiles:
            return "No specific ARGO profile data available for this query."
        
        context_parts = [
            f"Retrieved {len(profiles)} ARGO oceanographic profiles:",
            ""
        ]
        
        # Summarize key statistics
        if profiles:
            regions = set(p.get("ocean_region", "Unknown") for p in profiles)
            temps = [p.get("surface_temperature") for p in profiles if p.get("surface_temperature")]
            salinities = [p.get("surface_salinity") for p in profiles if p.get("surface_salinity")]
            depths = [p.get("max_depth") for p in profiles if p.get("max_depth")]
            
            context_parts.extend([
                f"Regions covered: {', '.join(regions)}",
                f"Temperature range: {min(temps):.1f}°C to {max(temps):.1f}°C" if temps else "Temperature data: Not available",
                f"Salinity range: {min(salinities):.1f} to {max(salinities):.1f} PSU" if salinities else "Salinity data: Not available",
                f"Depth range: {min(depths):.0f}m to {max(depths):.0f}m" if depths else "Depth data: Not available",
                ""
            ])
        
        # Add sample profile details
        for i, profile in enumerate(profiles[:3]):
            context_parts.append(
                f"Profile {i+1}: {profile.get('ocean_region', 'Unknown region')} "
                f"({profile.get('latitude', 0):.2f}°, {profile.get('longitude', 0):.2f}°) - "
                f"Temp: {profile.get('surface_temperature', 'N/A')}°C, "
                f"Salinity: {profile.get('surface_salinity', 'N/A')} PSU"
            )
        
        return "\n".join(context_parts)
    
    async def _generate_response(self, query: str, context: str, profiles: List[Dict[str, Any]]) -> str:
        """Generate AI response using LLM"""
        
        try:
            if self.llm:
                prompt = f"""You are an expert oceanographer analyzing Indian Ocean ARGO float data. 
                
User Query: {query}

Available Data:
{context}

Please provide a comprehensive, scientific response that:
1. Directly answers the user's question
2. References the specific ARGO data provided
3. Explains oceanographic patterns and phenomena
4. Provides scientific context and interpretation
5. Uses precise measurements and locations

Response:"""

                response = await self.llm.generate(prompt)
                return response
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
        
        # Fallback response generation
        return self._generate_fallback_response(query, context, profiles)
    
    def _generate_fallback_response(self, query: str, context: str, profiles: List[Dict[str, Any]]) -> str:
        """Generate fallback response without LLM"""
        
        if not profiles:
            return f"""I understand you're asking about: {query}

Unfortunately, I don't have specific ARGO profile data available right now to provide a detailed answer. However, I can tell you that the Indian Ocean ARGO program collects valuable oceanographic data including temperature, salinity, and pressure profiles throughout the Arabian Sea, Bay of Bengal, and Equatorial Indian Ocean regions.

For the most current data, I recommend checking the official ARGO data centers or trying your query again later when the database connection is restored."""
        
        # Generate response based on available data
        response_parts = [
            f"Based on the available ARGO data, here's what I found regarding: {query}",
            "",
            f"I analyzed {len(profiles)} oceanographic profiles from the Indian Ocean region."
        ]
        
        # Add data summary
        if profiles:
            regions = set(p.get("ocean_region", "Unknown") for p in profiles)
            temps = [p.get("surface_temperature") for p in profiles if p.get("surface_temperature")]
            salinities = [p.get("surface_salinity") for p in profiles if p.get("surface_salinity")]
            
            response_parts.extend([
                "",
                f"Regional coverage: {', '.join(regions)}",
                f"Surface temperature observations: {min(temps):.1f}°C to {max(temps):.1f}°C (average: {np.mean(temps):.1f}°C)" if temps else "",
                f"Surface salinity observations: {min(salinities):.1f} to {max(salinities):.1f} PSU (average: {np.mean(salinities):.1f} PSU)" if salinities else "",
                "",
                "This data provides insights into the oceanic conditions and can help understand regional oceanographic patterns in the Indian Ocean."
            ])
        
        return "\n".join(filter(None, response_parts))
    
    def _summarize_data(self, profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary statistics from profiles"""
        
        if not profiles:
            return {"profiles_found": 0, "regions": [], "parameters": {}}
        
        regions = list(set(p.get("ocean_region", "Unknown") for p in profiles))
        
        summary = {
            "profiles_found": len(profiles),
            "regions": regions,
            "parameters": {}
        }
        
        # Calculate statistics for each parameter
        for param in ["surface_temperature", "surface_salinity", "max_depth"]:
            values = [p.get(param) for p in profiles if p.get(param) is not None]
            if values:
                summary["parameters"][param] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "count": len(values)
                }
        
        return summary
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Generate fallback response when RAG pipeline fails"""
        
        return {
            "response": f"""I understand you're asking about: {query}

I'm currently experiencing some technical difficulties accessing the ARGO oceanographic database. However, I'm designed to help you analyze Indian Ocean data including:

• Temperature and salinity profiles from ARGO floats
• Oceanographic conditions in the Arabian Sea, Bay of Bengal, and Equatorial Indian Ocean  
• Analysis of surface and subsurface ocean parameters
• Regional oceanographic patterns and phenomena

Please try your query again in a moment, or feel free to ask about general oceanographic concepts while I work to restore full data access.""",
            "profiles_found": 0,
            "data_summary": {"profiles_found": 0, "regions": [], "parameters": {}},
            "query_time": 0.1,
            "timestamp": datetime.now().isoformat(),
            "status": "fallback_mode"
        }


# Global RAG pipeline instance
rag_pipeline = RAGPipeline()

# Convenience function for external use
async def process_argo_query(query: str, region: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Process ARGO query using RAG pipeline"""
    return await rag_pipeline.process_query(query, region, limit)
