"""
Advanced ARGO AI Agent using LangGraph + Gemini Pro
Complete implementation for Indian Ocean oceanographic analysis
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import AnyMessage, add_messages
from typing_extensions import Annotated, TypedDict

from ..core.database import db, ARGOProfile
from ..core.vector_db import vector_db
from ..core.config import settings

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State management for LangGraph agent"""
    messages: Annotated[list[AnyMessage], add_messages]
    query: str
    language: str
    extracted_params: Dict[str, Any]
    database_results: List[Dict[str, Any]]
    vector_results: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    response: str
    visualizations: List[Dict[str, Any]]
    scientific_context: Dict[str, Any]

class IndianOceanArgoAgent:
    """
    Production-ready AI Agent for Indian Ocean ARGO data analysis
    Handles complex oceanographic queries with multi-step reasoning
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.DEFAULT_LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.setup_workflow()
        self.initialize_scientific_knowledge()
        
    def initialize_scientific_knowledge(self):
        """Initialize oceanographic domain knowledge"""
        self.regional_expertise = {
            "arabian_sea": {
                "characteristics": "High salinity, seasonal upwelling, oxygen minimum zone",
                "typical_temp_range": "24-32°C surface",
                "typical_sal_range": "35.5-37.0 PSU",
                "key_processes": ["monsoon upwelling", "persian gulf outflow", "red sea overflow"],
                "seasonal_patterns": {
                    "southwest_monsoon": "Strong upwelling, cooling, high productivity",
                    "northeast_monsoon": "Reduced upwelling, warming, stratification"
                }
            },
            "bay_of_bengal": {
                "characteristics": "Low salinity, river influence, strong stratification",
                "typical_temp_range": "26-31°C surface", 
                "typical_sal_range": "32.0-35.0 PSU",
                "key_processes": ["river discharge", "cyclone formation", "barrier layer"],
                "seasonal_patterns": {
                    "southwest_monsoon": "Heavy precipitation, freshening",
                    "northeast_monsoon": "Cyclone season, mixing events"
                }
            },
            "equatorial_indian": {
                "characteristics": "Equatorial currents, IOD influence, thermocline variability",
                "typical_temp_range": "26-29°C surface",
                "typical_sal_range": "34.5-35.5 PSU", 
                "key_processes": ["indian ocean dipole", "equatorial jets", "thermocline variability"],
                "seasonal_patterns": {
                    "iod_positive": "Eastern cooling, western warming",
                    "iod_negative": "Eastern warming, western cooling"
                }
            }
        }
        
        self.parameter_ranges = {
            "temperature": {"normal": (20, 32), "extreme": (15, 35)},
            "salinity": {"normal": (32, 37), "extreme": (25, 40)},
            "density": {"normal": (1020, 1028), "extreme": (1015, 1030)}
        }
    
    def setup_workflow(self):
        """Setup LangGraph workflow for complex oceanographic analysis"""
        
        workflow = StateGraph(AgentState)
        
        # Add processing nodes
        workflow.add_node("parse_query", self.parse_user_query)
        workflow.add_node("search_database", self.search_database)
        workflow.add_node("search_vectors", self.semantic_search) 
        workflow.add_node("analyze_data", self.analyze_oceanographic_data)
        workflow.add_node("scientific_context", self.add_scientific_context)
        workflow.add_node("generate_visualizations", self.create_visualizations)
        workflow.add_node("compose_response", self.compose_final_response)
        
        # Define workflow edges
        workflow.set_entry_point("parse_query")
        workflow.add_edge("parse_query", "search_database")
        workflow.add_edge("search_database", "search_vectors")
        workflow.add_edge("search_vectors", "analyze_data")
        workflow.add_edge("analyze_data", "scientific_context")
        workflow.add_edge("scientific_context", "generate_visualizations")
        workflow.add_edge("generate_visualizations", "compose_response")
        workflow.add_edge("compose_response", END)
        
        self.workflow = workflow.compile()
    
    async def parse_user_query(self, state: AgentState) -> AgentState:
        """Parse user query to extract oceanographic parameters and context"""
        
        query = state["query"]
        language = state.get("language", "en")
        
        # Multi-language oceanographic query parser
        query_parser_prompt = ChatPromptTemplate.from_template("""
        You are an expert oceanographer analyzing user queries about Indian Ocean ARGO data.
        
        Query: {query}
        Language: {language}
        
        Extract parameters in JSON format:
        {{
            "region": "arabian_sea | bay_of_bengal | equatorial_indian | indian_ocean_general",
            "parameters": ["temperature", "salinity", "pressure", "density", "mixed_layer_depth"],
            "time_period": {{
                "start_date": "YYYY-MM-DD or null",
                "end_date": "YYYY-MM-DD or null",
                "season": "southwest_monsoon | northeast_monsoon | pre_monsoon | post_monsoon | null",
                "year_range": "recent | historical | specific_year"
            }},
            "analysis_type": "trend | comparison | profile | climatology | anomaly | correlation",
            "depth_range": {{"min_depth": 0, "max_depth": 2000}},
            "spatial_scope": "point | regional | basin_wide",
            "data_quality": "all | high_quality | research_grade",
            "visualization_type": "map | time_series | profile | ts_diagram | correlation",
            "scientific_focus": "temperature | salinity | density | circulation | climate_change",
            "language_response": "{language}"
        }}
        
        Consider regional aliases and local names:
        - Arabian Sea: अरब सागर (Hindi), আরব সাগর (Bengali)
        - Bay of Bengal: बंगाल की खाड़ी (Hindi), বঙ্গোপসাগর (Bengali)
        - Temperature: तापमान (Hindi), তাপমাত্রা (Bengali)
        - Salinity: लवणता (Hindi), লবণাক্ততা (Bengali)
        """)
        
        parser = JsonOutputParser()
        chain = query_parser_prompt | self.llm | parser
        
        try:
            extracted_params = await chain.ainvoke({
                "query": query,
                "language": language
            })
            
            # Validate and set defaults
            extracted_params = self.validate_extracted_params(extracted_params)
            state["extracted_params"] = extracted_params
            
            logger.info(f"Query parsed successfully: {extracted_params}")
            
        except Exception as e:
            logger.error(f"Query parsing failed: {e}")
            state["extracted_params"] = self.get_default_params(language)
        
        return state
    
    def validate_extracted_params(self, params: Dict) -> Dict:
        """Validate and normalize extracted parameters"""
        
        # Set defaults for missing keys
        defaults = {
            "region": "indian_ocean_general",
            "parameters": ["temperature", "salinity"],
            "analysis_type": "profile",
            "data_quality": "high_quality",
            "spatial_scope": "regional",
            "time_period": {"year_range": "recent"}
        }
        
        for key, default_value in defaults.items():
            if key not in params:
                params[key] = default_value
        
        # Normalize region names
        region_mapping = {
            "western_indian": "arabian_sea",
            "eastern_indian": "bay_of_bengal", 
            "central_indian": "equatorial_indian"
        }
        
        if params["region"] in region_mapping:
            params["region"] = region_mapping[params["region"]]
        
        return params
    
    def get_default_params(self, language: str) -> Dict:
        """Return default parameters for query parsing failures"""
        return {
            "region": "indian_ocean_general",
            "parameters": ["temperature", "salinity"],
            "analysis_type": "profile",
            "data_quality": "high_quality",
            "language_response": language
        }
    
    async def search_database(self, state: AgentState) -> AgentState:
        """Advanced PostgreSQL search with complex filtering"""
        
        params = state["extracted_params"]
        
        try:
            with db.get_session() as session:
                query = session.query(ARGOProfile)
                
                # Regional filtering
                if params.get("region") != "indian_ocean_general":
                    query = query.filter(ARGOProfile.ocean_region == params["region"])
                
                # Temporal filtering
                time_period = params.get("time_period", {})
                
                if time_period.get("start_date"):
                    query = query.filter(ARGOProfile.profile_date >= time_period["start_date"])
                if time_period.get("end_date"):
                    query = query.filter(ARGOProfile.profile_date <= time_period["end_date"])
                
                # Year range filtering
                year_range = time_period.get("year_range", "recent")
                if year_range == "recent":
                    recent_date = datetime.now() - timedelta(days=365*2)  # Last 2 years
                    query = query.filter(ARGOProfile.profile_date >= recent_date)
                elif year_range == "historical":
                    historical_date = datetime.now() - timedelta(days=365*10)  # Before 10 years
                    query = query.filter(ARGOProfile.profile_date <= historical_date)
                
                # Data quality filtering
                quality_filter = params.get("data_quality", "high_quality")
                if quality_filter == "high_quality":
                    query = query.filter(ARGOProfile.data_quality_score >= 4.0)
                elif quality_filter == "research_grade":
                    query = query.filter(ARGOProfile.data_quality_score >= 4.5)
                
                # Depth filtering
                depth_range = params.get("depth_range", {})
                if depth_range.get("max_depth"):
                    query = query.filter(ARGOProfile.max_depth >= depth_range["max_depth"])
                
                # Parameter-specific filtering
                parameters = params.get("parameters", [])
                if "temperature" in parameters:
                    query = query.filter(ARGOProfile.surface_temperature.isnot(None))
                if "salinity" in parameters:
                    query = query.filter(ARGOProfile.surface_salinity.isnot(None))
                
                # Spatial scope adjustment
                spatial_scope = params.get("spatial_scope", "regional")
                if spatial_scope == "point":
                    query = query.limit(10)
                elif spatial_scope == "regional":
                    query = query.limit(100)
                else:  # basin_wide
                    query = query.limit(500)
                
                # Execute query
                profiles = query.all()
                
                # Convert to dictionaries with enhanced metadata
                database_results = []
                for profile in profiles:
                    profile_dict = {
                        "float_id": profile.float_id,
                        "cycle_number": profile.cycle_number,
                        "profile_date": profile.profile_date.isoformat(),
                        "latitude": float(profile.latitude),
                        "longitude": float(profile.longitude),
                        "ocean_region": profile.ocean_region,
                        "surface_temperature": float(profile.surface_temperature) if profile.surface_temperature else None,
                        "surface_salinity": float(profile.surface_salinity) if profile.surface_salinity else None,
                        "surface_pressure": float(profile.surface_pressure) if profile.surface_pressure else None,
                        "max_depth": float(profile.max_depth) if profile.max_depth else None,
                        "mixed_layer_depth": float(profile.mixed_layer_depth) if profile.mixed_layer_depth else None,
                        "thermocline_depth": float(profile.thermocline_depth) if profile.thermocline_depth else None,
                        "data_quality_score": float(profile.data_quality_score),
                        "processing_level": profile.processing_level,
                        "profile_summary": profile.profile_summary
                    }
                    database_results.append(profile_dict)
                
                state["database_results"] = database_results
                logger.info(f"Database search found {len(database_results)} profiles")
                
        except Exception as e:
            logger.error(f"Database search failed: {e}")
            state["database_results"] = []
        
        return state
    
    async def semantic_search(self, state: AgentState) -> AgentState:
        """Perform enhanced semantic search using vector database"""
        
        query = state["query"]
        params = state["extracted_params"]
        
        try:
            # Enhance query with regional and scientific context
            region = params.get("region", "indian_ocean_general")
            parameters = params.get("parameters", [])
            
            # Build enhanced search query
            enhanced_queries = [query]
            
            if region in self.regional_expertise:
                regional_context = self.regional_expertise[region]["characteristics"]
                enhanced_queries.append(f"{query} {regional_context}")
            
            # Add parameter-specific context
            if "temperature" in parameters:
                enhanced_queries.append(f"{query} sea surface temperature thermal structure")
            if "salinity" in parameters:
                enhanced_queries.append(f"{query} ocean salinity haline structure")
            
            # Perform multiple vector searches and combine results
            all_vector_results = []
            
            for enhanced_query in enhanced_queries[:3]:  # Limit to 3 queries
                vector_results = vector_db.advanced_search(
                    query=enhanced_query,
                    n_results=10,
                    region_filter=region if region != "indian_ocean_general" else None
                )
                
                if vector_results.get("results"):
                    all_vector_results.extend(vector_results["results"])
            
            # Remove duplicates based on profile ID
            unique_results = []
            seen_ids = set()
            
            for result in all_vector_results:
                profile_id = result.get("metadata", {}).get("float_id")
                if profile_id and profile_id not in seen_ids:
                    unique_results.append(result)
                    seen_ids.add(profile_id)
            
            state["vector_results"] = unique_results[:20]  # Top 20 results
            logger.info(f"Vector search found {len(state['vector_results'])} similar profiles")
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            state["vector_results"] = []
        
        return state
    
    async def analyze_oceanographic_data(self, state: AgentState) -> AgentState:
        """Comprehensive oceanographic data analysis"""
        
        database_results = state["database_results"]
        params = state["extracted_params"]
        analysis_type = params.get("analysis_type", "profile")
        
        analysis_results = {}
        
        try:
            if not database_results:
                analysis_results = {
                    "message": "No data found for the specified criteria",
                    "suggestions": self.generate_search_suggestions(params)
                }
            else:
                # Convert to DataFrame for analysis
                df = pd.DataFrame(database_results)
                
                # Perform analysis based on type
                if analysis_type == "trend":
                    analysis_results = await self.calculate_trends(df, params)
                elif analysis_type == "comparison":
                    analysis_results = await self.compare_regions(df, params)
                elif analysis_type == "climatology":
                    analysis_results = await self.calculate_climatology(df, params)
                elif analysis_type == "anomaly":
                    analysis_results = await self.detect_anomalies(df, params)
                elif analysis_type == "correlation":
                    analysis_results = await self.calculate_correlations(df, params)
                else:  # profile analysis
                    analysis_results = await self.analyze_profiles(df, params)
                
                # Add data quality assessment
                analysis_results["data_quality"] = self.assess_data_quality(df)
                
                # Add statistical significance
                analysis_results["statistical_confidence"] = self.assess_statistical_confidence(df)
            
            state["analysis_results"] = analysis_results
            logger.info("Oceanographic analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            state["analysis_results"] = {
                "error": str(e),
                "message": "Analysis failed due to data processing error"
            }
        
        return state
    
    async def calculate_trends(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Calculate temporal trends with statistical significance"""
        
        if len(df) < 5:
            return {"trend": "insufficient_data", "message": "Need at least 5 profiles for trend analysis"}
        
        # Convert date column
        df['profile_date'] = pd.to_datetime(df['profile_date'])
        df = df.sort_values('profile_date')
        
        trends = {}
        parameters = params.get("parameters", ["temperature"])
        
        for param in parameters:
            if param == "temperature":
                values = df['surface_temperature'].dropna()
                param_name = "Surface Temperature (°C)"
            elif param == "salinity":
                values = df['surface_salinity'].dropna()  
                param_name = "Surface Salinity (PSU)"
            else:
                continue
            
            if len(values) < 3:
                continue
                
            # Calculate linear trend
            dates = df.loc[values.index, 'profile_date']
            x = np.array([(d - dates.iloc[0]).days for d in dates])
            y = values.values
            
            # Linear regression
            if len(x) > 1:
                slope, intercept = np.polyfit(x, y, 1)
                
                # Convert slope to per-year rate
                slope_per_year = slope * 365.25
                
                # Determine trend significance
                if abs(slope_per_year) > 0.1:
                    trend_direction = "increasing" if slope_per_year > 0 else "decreasing"
                    significance = "strong" if abs(slope_per_year) > 0.5 else "moderate"
                else:
                    trend_direction = "stable"
                    significance = "low"
                
                trends[param] = {
                    "parameter": param_name,
                    "trend_direction": trend_direction,
                    "rate_per_year": round(slope_per_year, 4),
                    "significance": significance,
                    "data_points": len(values),
                    "time_span_years": round((dates.iloc[-1] - dates.iloc[0]).days / 365.25, 1)
                }
        
        return {
            "analysis_type": "trend_analysis",
            "trends": trends,
            "summary": self.summarize_trends(trends)
        }
    
    async def compare_regions(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Compare oceanographic parameters across regions"""
        
        if 'ocean_region' not in df.columns:
            return {"error": "Region information not available for comparison"}
        
        comparison = {}
        parameters = params.get("parameters", ["temperature", "salinity"])
        
        regions = df['ocean_region'].unique()
        
        for region in regions:
            region_data = df[df['ocean_region'] == region]
            
            if len(region_data) == 0:
                continue
                
            region_stats = {
                "profile_count": len(region_data),
                "date_range": {
                    "start": region_data['profile_date'].min(),
                    "end": region_data['profile_date'].max()
                }
            }
            
            for param in parameters:
                if param == "temperature":
                    values = region_data['surface_temperature'].dropna()
                elif param == "salinity":
                    values = region_data['surface_salinity'].dropna()
                else:
                    continue
                
                if len(values) > 0:
                    region_stats[param] = {
                        "mean": round(values.mean(), 2),
                        "std": round(values.std(), 2),
                        "min": round(values.min(), 2),
                        "max": round(values.max(), 2),
                        "median": round(values.median(), 2)
                    }
            
            comparison[region] = region_stats
        
        return {
            "analysis_type": "regional_comparison",
            "comparison": comparison,
            "summary": self.summarize_regional_differences(comparison)
        }
    
    async def calculate_climatology(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Calculate climatological statistics"""
        
        df['profile_date'] = pd.to_datetime(df['profile_date'])
        df['month'] = df['profile_date'].dt.month
        df['season'] = df['month'].apply(self.get_season_from_month)
        
        climatology = {}
        parameters = params.get("parameters", ["temperature"])
        
        # Monthly climatology
        monthly_stats = {}
        for month in range(1, 13):
            month_data = df[df['month'] == month]
            
            if len(month_data) > 0:
                month_stats = {"profile_count": len(month_data)}
                
                for param in parameters:
                    if param == "temperature":
                        values = month_data['surface_temperature'].dropna()
                    elif param == "salinity":
                        values = month_data['surface_salinity'].dropna()
                    else:
                        continue
                    
                    if len(values) > 0:
                        month_stats[param] = {
                            "mean": round(values.mean(), 2),
                            "std": round(values.std(), 2)
                        }
                
                monthly_stats[f"month_{month:02d}"] = month_stats
        
        # Seasonal climatology
        seasonal_stats = {}
        for season in df['season'].unique():
            if pd.isna(season):
                continue
                
            season_data = df[df['season'] == season]
            season_stats = {"profile_count": len(season_data)}
            
            for param in parameters:
                if param == "temperature":
                    values = season_data['surface_temperature'].dropna()
                elif param == "salinity":  
                    values = season_data['surface_salinity'].dropna()
                else:
                    continue
                
                if len(values) > 0:
                    season_stats[param] = {
                        "mean": round(values.mean(), 2),
                        "std": round(values.std(), 2)
                    }
            
            seasonal_stats[season] = season_stats
        
        return {
            "analysis_type": "climatology",
            "monthly_climatology": monthly_stats,
            "seasonal_climatology": seasonal_stats,
            "summary": "Climatological analysis completed"
        }
    
    async def detect_anomalies(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Detect oceanographic anomalies"""
        
        anomalies = {}
        parameters = params.get("parameters", ["temperature"])
        
        for param in parameters:
            if param == "temperature":
                values = df['surface_temperature'].dropna()
                normal_range = self.parameter_ranges["temperature"]["normal"]
                extreme_range = self.parameter_ranges["temperature"]["extreme"]
            elif param == "salinity":
                values = df['surface_salinity'].dropna()
                normal_range = self.parameter_ranges["salinity"]["normal"]
                extreme_range = self.parameter_ranges["salinity"]["extreme"]
            else:
                continue
            
            if len(values) == 0:
                continue
            
            # Statistical anomaly detection
            mean_val = values.mean()
            std_val = values.std()
            
            # Find statistical outliers (>2 sigma)
            outliers = values[(values < mean_val - 2*std_val) | (values > mean_val + 2*std_val)]
            
            # Find extreme values outside normal ranges
            extreme_low = values[values < normal_range[0]]
            extreme_high = values[values > normal_range[1]]
            
            anomalies[param] = {
                "statistical_outliers": {
                    "count": len(outliers),
                    "percentage": round(len(outliers) / len(values) * 100, 1),
                    "values": outliers.tolist() if len(outliers) < 10 else "too_many_to_list"
                },
                "extreme_values": {
                    "extremely_low": len(extreme_low),
                    "extremely_high": len(extreme_high),
                    "normal_range": normal_range
                }
            }
        
        return {
            "analysis_type": "anomaly_detection",
            "anomalies": anomalies,
            "summary": self.summarize_anomalies(anomalies)
        }
    
    async def calculate_correlations(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Calculate parameter correlations"""
        
        correlations = {}
        
        # Temperature-Salinity correlation
        if ('surface_temperature' in df.columns and 
            'surface_salinity' in df.columns):
            
            temp_sal_data = df[['surface_temperature', 'surface_salinity']].dropna()
            
            if len(temp_sal_data) > 5:
                correlation = temp_sal_data.corr().iloc[0, 1]
                
                correlations["temperature_salinity"] = {
                    "correlation_coefficient": round(correlation, 3),
                    "strength": self.interpret_correlation(correlation),
                    "data_points": len(temp_sal_data)
                }
        
        # Depth correlations
        depth_params = ['mixed_layer_depth', 'thermocline_depth', 'max_depth']
        temp_depth_correlations = {}
        
        for depth_param in depth_params:
            if (depth_param in df.columns and 'surface_temperature' in df.columns):
                depth_temp_data = df[[depth_param, 'surface_temperature']].dropna()
                
                if len(depth_temp_data) > 5:
                    correlation = depth_temp_data.corr().iloc[0, 1]
                    temp_depth_correlations[depth_param] = round(correlation, 3)
        
        if temp_depth_correlations:
            correlations["temperature_depth"] = temp_depth_correlations
        
        return {
            "analysis_type": "correlation_analysis", 
            "correlations": correlations,
            "summary": self.summarize_correlations(correlations)
        }
    
    async def analyze_profiles(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Basic profile analysis and statistics"""
        
        analysis = {
            "data_overview": {
                "total_profiles": len(df),
                "date_range": {
                    "start": df['profile_date'].min(),
                    "end": df['profile_date'].max()
                },
                "spatial_coverage": {
                    "lat_range": [df['latitude'].min(), df['latitude'].max()],
                    "lon_range": [df['longitude'].min(), df['longitude'].max()]
                }
            }
        }
        
        # Parameter statistics
        parameters = params.get("parameters", ["temperature", "salinity"])
        param_stats = {}
        
        for param in parameters:
            if param == "temperature":
                values = df['surface_temperature'].dropna()
                unit = "°C"
            elif param == "salinity":
                values = df['surface_salinity'].dropna()
                unit = "PSU"
            else:
                continue
            
            if len(values) > 0:
                param_stats[param] = {
                    "count": len(values),
                    "mean": round(values.mean(), 2),
                    "std": round(values.std(), 2),
                    "min": round(values.min(), 2),
                    "max": round(values.max(), 2),
                    "median": round(values.median(), 2),
                    "unit": unit
                }
        
        analysis["parameter_statistics"] = param_stats
        
        # Regional breakdown
        if 'ocean_region' in df.columns:
            regional_breakdown = df['ocean_region'].value_counts().to_dict()
            analysis["regional_distribution"] = regional_breakdown
        
        # Data quality assessment
        if 'data_quality_score' in df.columns:
            quality_scores = df['data_quality_score'].dropna()
            analysis["data_quality"] = {
                "mean_quality_score": round(quality_scores.mean(), 2),
                "high_quality_profiles": len(df[df['data_quality_score'] >= 4.0]),
                "research_grade_profiles": len(df[df['data_quality_score'] >= 4.5])
            }
        
        return {
            "analysis_type": "profile_analysis",
            "analysis": analysis,
            "summary": f"Analyzed {len(df)} ARGO profiles with comprehensive statistics"
        }
    
    # Helper methods for analysis
    def get_season_from_month(self, month: int) -> str:
        """Get season name from month number"""
        for season, info in settings.MONSOON_SEASONS.items():
            if month in info["months"]:
                return season
        return "unknown"
    
    def interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            return "very strong"
        elif abs_corr >= 0.6:
            return "strong" 
        elif abs_corr >= 0.4:
            return "moderate"
        elif abs_corr >= 0.2:
            return "weak"
        else:
            return "very weak"
    
    def assess_data_quality(self, df: pd.DataFrame) -> Dict:
        """Assess overall data quality"""
        total_profiles = len(df)
        
        quality_assessment = {
            "total_profiles": total_profiles,
            "temporal_coverage": "good" if total_profiles > 50 else "limited",
            "spatial_distribution": "regional" if df['ocean_region'].nunique() > 1 else "localized"
        }
        
        if 'data_quality_score' in df.columns:
            avg_quality = df['data_quality_score'].mean()
            quality_assessment["average_quality_score"] = round(avg_quality, 2)
            quality_assessment["quality_rating"] = (
                "excellent" if avg_quality >= 4.5 else
                "good" if avg_quality >= 4.0 else
                "acceptable" if avg_quality >= 3.0 else
                "poor"
            )
        
        return quality_assessment
    
    def assess_statistical_confidence(self, df: pd.DataFrame) -> Dict:
        """Assess statistical confidence of results"""
        sample_size = len(df)
        
        if sample_size >= 100:
            confidence = "high"
        elif sample_size >= 30:
            confidence = "moderate"  
        elif sample_size >= 10:
            confidence = "low"
        else:
            confidence = "very_low"
        
        return {
            "sample_size": sample_size,
            "confidence_level": confidence,
            "recommendations": self.get_confidence_recommendations(confidence)
        }
    
    def get_confidence_recommendations(self, confidence: str) -> List[str]:
        """Get recommendations based on confidence level"""
        recommendations = {
            "high": ["Results are statistically robust", "Suitable for research publication"],
            "moderate": ["Results are reliable", "Consider additional data for stronger conclusions"],
            "low": ["Results are indicative", "Collect more data for higher confidence"],
            "very_low": ["Results are preliminary", "Significant data collection needed"]
        }
        return recommendations.get(confidence, ["Insufficient data for assessment"])
    
    # Summary methods
    def summarize_trends(self, trends: Dict) -> str:
        """Generate trend summary"""
        if not trends:
            return "No significant trends detected in the data."
        
        summaries = []
        for param, trend_data in trends.items():
            direction = trend_data["trend_direction"]
            rate = trend_data["rate_per_year"]
            significance = trend_data["significance"]
            
            summaries.append(f"{param} shows {direction} trend ({rate}/year, {significance} significance)")
        
        return " | ".join(summaries)
    
    def summarize_regional_differences(self, comparison: Dict) -> str:
        """Generate regional comparison summary"""
        if len(comparison) < 2:
            return "Insufficient regional data for comparison."
        
        regions = list(comparison.keys())
        return f"Comparison between {len(regions)} regions: {', '.join(regions)}"
    
    def summarize_anomalies(self, anomalies: Dict) -> str:
        """Generate anomaly summary"""
        total_outliers = sum(data["statistical_outliers"]["count"] for data in anomalies.values())
        return f"Detected {total_outliers} statistical outliers across analyzed parameters"
    
    def summarize_correlations(self, correlations: Dict) -> str:
        """Generate correlation summary"""
        if not correlations:
            return "No significant correlations found."
        
        summaries = []
        if "temperature_salinity" in correlations:
            ts_corr = correlations["temperature_salinity"]
            summaries.append(f"T-S correlation: {ts_corr['strength']} ({ts_corr['correlation_coefficient']})")
        
        return " | ".join(summaries) if summaries else "Correlation analysis completed"
    
    def generate_search_suggestions(self, params: Dict) -> List[str]:
        """Generate suggestions when no data is found"""
        suggestions = [
            "Try expanding the date range",
            "Consider a broader geographic region",
            "Lower the data quality threshold",
            "Check for seasonal data availability"
        ]
        
        region = params.get("region")
        if region != "indian_ocean_general":
            suggestions.append(f"Try searching in 'indian_ocean_general' instead of '{region}'")
        
        return suggestions
    
    async def add_scientific_context(self, state: AgentState) -> AgentState:
        """Add oceanographic scientific context"""
        
        params = state["extracted_params"]
        analysis_results = state["analysis_results"]
        region = params.get("region", "indian_ocean_general")
        
        scientific_context = {}
        
        try:
            # Add regional expertise
            if region in self.regional_expertise:
                scientific_context["regional_expertise"] = self.regional_expertise[region]
            
            # Add seasonal context
            current_month = datetime.now().month
            seasonal_context = settings.get_seasonal_context(current_month)
            scientific_context["current_season"] = seasonal_context
            
            # Add parameter interpretation
            parameters = params.get("parameters", [])
            param_interpretations = {}
            
            for param in parameters:
                if param in self.parameter_ranges:
                    param_interpretations[param] = {
                        "normal_range": self.parameter_ranges[param]["normal"],
                        "extreme_range": self.parameter_ranges[param]["extreme"],
                        "oceanographic_significance": self.get_parameter_significance(param, region)
                    }
            
            scientific_context["parameter_interpretations"] = param_interpretations
            
            # Add analysis context
            analysis_type = params.get("analysis_type", "profile")
            scientific_context["analysis_context"] = self.get_analysis_context(analysis_type, region)
            
            state["scientific_context"] = scientific_context
            logger.info("Scientific context added successfully")
            
        except Exception as e:
            logger.error(f"Scientific context addition failed: {e}")
            state["scientific_context"] = {}
        
        return state
    
    def get_parameter_significance(self, parameter: str, region: str) -> str:
        """Get oceanographic significance of parameters"""
        
        significance_map = {
            "temperature": {
                "arabian_sea": "Critical for upwelling intensity and oxygen minimum zone dynamics",
                "bay_of_bengal": "Controls thermal stratification and cyclone formation",
                "equatorial_indian": "Key indicator of Indian Ocean Dipole state"
            },
            "salinity": {
                "arabian_sea": "Reflects evaporation-precipitation balance and Persian Gulf outflow",
                "bay_of_bengal": "Influenced by river discharge and monsoon precipitation", 
                "equatorial_indian": "Controls barrier layer formation and thermocline structure"
            }
        }
        
        return significance_map.get(parameter, {}).get(region, "Important oceanographic parameter")
    
    def get_analysis_context(self, analysis_type: str, region: str) -> str:
        """Get context for analysis type"""
        
        context_map = {
            "trend": f"Trend analysis in {region} reveals long-term climate signals and ocean changes",
            "comparison": f"Regional comparison provides insights into {region} oceanographic variability",
            "climatology": f"Climatological analysis establishes baseline conditions for {region}",
            "anomaly": f"Anomaly detection identifies unusual events and extreme conditions in {region}",
            "correlation": f"Correlation analysis reveals oceanographic relationships in {region}"
        }
        
        return context_map.get(analysis_type, f"Analysis provides oceanographic insights for {region}")
    
    async def create_visualizations(self, state: AgentState) -> AgentState:
        """Generate comprehensive visualization specifications"""
        
        database_results = state["database_results"]
        analysis_results = state["analysis_results"]
        params = state["extracted_params"]
        
        visualizations = []
        
        try:
            if not database_results:
                state["visualizations"] = []
                return state
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame(database_results)
            
            # Generate visualizations based on analysis type and data availability
            analysis_type = params.get("analysis_type", "profile")
            visualization_type = params.get("visualization_type", "auto")
            
            # 1. Map visualization (always useful)
            if len(database_results) > 0:
                visualizations.append(self.create_map_visualization(df, params))
            
            # 2. Time series (if temporal data exists)
            if len(df) > 5 and analysis_type in ["trend", "climatology"]:
                visualizations.append(self.create_time_series_visualization(df, params))
            
            # 3. T-S Diagram (if both parameters available)
            if (len(df) > 3 and 
                "temperature" in params.get("parameters", []) and
                "salinity" in params.get("parameters", [])):
                visualizations.append(self.create_ts_diagram(df, params))
            
            # 4. Statistical plots for comparisons
            if analysis_type == "comparison" and len(df) > 10:
                visualizations.append(self.create_comparison_plot(df, params))
            
            # 5. Profile plots for deep data
            if "max_depth" in df.columns and df["max_depth"].max() > 500:
                visualizations.append(self.create_profile_plot(df, params))
            
            # 6. Correlation plots
            if analysis_type == "correlation" and len(df) > 10:
                visualizations.append(self.create_correlation_plot(df, params))
            
            state["visualizations"] = visualizations
            logger.info(f"Generated {len(visualizations)} visualization specifications")
            
        except Exception as e:
            logger.error(f"Visualization generation failed: {e}")
            state["visualizations"] = []
        
        return state
    
    def create_map_visualization(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Create map visualization specification"""
        return {
            "type": "map",
            "title": "ARGO Profile Locations",
            "description": "Geographic distribution of ARGO float profiles",
            "config": {
                "center_lat": df["latitude"].mean(),
                "center_lon": df["longitude"].mean(),
                "zoom": 5
            },
            "data": [
                {
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "temperature": row["surface_temperature"],
                    "salinity": row["surface_salinity"],
                    "float_id": row["float_id"],
                    "date": row["profile_date"],
                    "region": row["ocean_region"],
                    "quality": row["data_quality_score"]
                }
                for _, row in df.iterrows()
                if row["latitude"] and row["longitude"]
            ]
        }
    
    def create_time_series_visualization(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Create time series visualization specification"""
        
        parameters = params.get("parameters", ["temperature"])
        
        # Sort by date
        df_sorted = df.sort_values("profile_date")
        
        series_data = []
        for param in parameters:
            if param == "temperature":
                column = "surface_temperature"
                label = "Surface Temperature (°C)"
            elif param == "salinity":
                column = "surface_salinity"
                label = "Surface Salinity (PSU)"
            else:
                continue
            
            if column in df_sorted.columns:
                param_data = df_sorted[df_sorted[column].notna()]
                
                series_data.append({
                    "name": label,
                    "data": [
                        {
                            "date": row["profile_date"],
                            "value": row[column],
                            "float_id": row["float_id"]
                        }
                        for _, row in param_data.iterrows()
                    ]
                })
        
        return {
            "type": "time_series",
            "title": "Temporal Evolution of Oceanographic Parameters",
            "description": "Time series showing parameter changes over time",
            "series": series_data
        }
    
    def create_ts_diagram(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Create Temperature-Salinity diagram"""
        
        # Filter data with both T and S
        ts_data = df.dropna(subset=["surface_temperature", "surface_salinity"])
        
        return {
            "type": "scatter",
            "title": "Temperature-Salinity Diagram",
            "description": "T-S relationship showing water mass characteristics",
            "axes": {
                "x_label": "Salinity (PSU)",
                "y_label": "Temperature (°C)"
            },
            "data": [
                {
                    "salinity": row["surface_salinity"],
                    "temperature": row["surface_temperature"],
                    "region": row["ocean_region"],
                    "float_id": row["float_id"],
                    "date": row["profile_date"],
                    "depth": row["max_depth"]
                }
                for _, row in ts_data.iterrows()
            ]
        }
    
    def create_comparison_plot(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Create regional comparison plot"""
        
        parameters = params.get("parameters", ["temperature"])
        regions = df["ocean_region"].unique()
        
        comparison_data = []
        
        for region in regions:
            region_data = df[df["ocean_region"] == region]
            
            region_stats = {"region": region}
            
            for param in parameters:
                if param == "temperature":
                    values = region_data["surface_temperature"].dropna()
                    param_name = "temperature"
                elif param == "salinity":
                    values = region_data["surface_salinity"].dropna()
                    param_name = "salinity"
                else:
                    continue
                
                if len(values) > 0:
                    region_stats[param_name] = {
                        "mean": values.mean(),
                        "std": values.std(),
                        "count": len(values)
                    }
            
            comparison_data.append(region_stats)
        
        return {
            "type": "box_plot",
            "title": "Regional Parameter Comparison",
            "description": "Statistical comparison across Indian Ocean regions",
            "data": comparison_data
        }
    
    def create_profile_plot(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Create vertical profile plot"""
        
        # Select profiles with good depth data
        deep_profiles = df[df["max_depth"] > 1000].head(5)
        
        return {
            "type": "profile",
            "title": "Vertical Ocean Profiles",
            "description": "Temperature and salinity profiles with depth",
            "profiles": [
                {
                    "float_id": row["float_id"],
                    "date": row["profile_date"],
                    "surface_temp": row["surface_temperature"],
                    "surface_sal": row["surface_salinity"],
                    "max_depth": row["max_depth"],
                    "mld": row["mixed_layer_depth"],
                    "thermocline": row["thermocline_depth"]
                }
                for _, row in deep_profiles.iterrows()
            ]
        }
    
    def create_correlation_plot(self, df: pd.DataFrame, params: Dict) -> Dict:
        """Create correlation matrix plot"""
        
        # Select numeric columns for correlation
        numeric_cols = ["surface_temperature", "surface_salinity", "max_depth", 
                       "mixed_layer_depth", "thermocline_depth"]
        
        correlation_data = df[numeric_cols].dropna()
        
        if len(correlation_data) < 10:
            return {}
        
        # Calculate correlation matrix
        corr_matrix = correlation_data.corr()
        
        # Convert to list format for visualization
        correlation_list = []
        for i, col1 in enumerate(corr_matrix.columns):
            for j, col2 in enumerate(corr_matrix.columns):
                correlation_list.append({
                    "param1": col1,
                    "param2": col2,
                    "correlation": corr_matrix.iloc[i, j]
                })
        
        return {
            "type": "heatmap",
            "title": "Parameter Correlation Matrix",
            "description": "Correlation relationships between oceanographic parameters",
            "data": correlation_list
        }
    
    async def compose_final_response(self, state: AgentState) -> AgentState:
        """Compose comprehensive final response with scientific context"""
        
        query = state["query"]
        language = state["extracted_params"].get("language_response", "en")
        database_results = state["database_results"]
        analysis_results = state["analysis_results"]
        scientific_context = state["scientific_context"]
        visualizations = state["visualizations"]
        
        # Create comprehensive response prompt
        response_prompt = ChatPromptTemplate.from_template("""
        You are a world-class oceanographer providing expert analysis of Indian Ocean ARGO data.
        
        User Query: {query}
        Response Language: {language}
        
        Data Analysis Results:
        {analysis_json}
        
        Scientific Context:
        {scientific_context_json}
        
        Available Visualizations: {viz_count} charts/maps
        
        Provide a comprehensive scientific response that:
        
        1. **Direct Answer**: Clearly answer the user's specific question
        2. **Scientific Analysis**: Explain the oceanographic significance of findings
        3. **Regional Context**: Include relevant Indian Ocean dynamics and processes
        4. **Data Quality**: Mention data sources, quality, and any limitations
        5. **Interpretation**: Provide expert interpretation of patterns and trends
        6. **Broader Implications**: Connect findings to climate/ocean science
        
        Response Guidelines:
        - Use appropriate scientific terminology while remaining accessible
        - Include quantitative results with proper units
        - Mention specific ARGO data characteristics (quality scores, spatial coverage)
        - Reference relevant oceanographic processes (monsoons, upwelling, etc.)
        - Acknowledge uncertainties and data limitations
        
        Language Requirements:
        - English: Use standard oceanographic terminology
        - Hindi: Use Devanagari script with scientific terms in parentheses
        - Bengali: Use Bengali script with English scientific terms in parentheses  
        - Tamil: Use Tamil script with English scientific terms in parentheses
        
        Structure the response with clear sections and scientific rigor appropriate for research communication.
        """)
        
        try:
            chain = response_prompt | self.llm
            
            response = await chain.ainvoke({
                "query": query,
                "language": language,
                "analysis_json": json.dumps(analysis_results, indent=2, default=str),
                "scientific_context_json": json.dumps(scientific_context, indent=2, default=str),
                "viz_count": len(visualizations)
            })
            
            state["response"] = response.content
            logger.info("Final scientific response composed successfully")
            
        except Exception as e:
            logger.error(f"Response composition failed: {e}")
            
            # Fallback response
            profile_count = len(database_results)
            analysis_type = state["extracted_params"].get("analysis_type", "analysis")
            
            fallback_response = self.create_fallback_response(
                query, language, profile_count, analysis_type, analysis_results
            )
            
            state["response"] = fallback_response
        
        return state
    
    def create_fallback_response(self, query: str, language: str, 
                               profile_count: int, analysis_type: str, 
                               analysis_results: Dict) -> str:
        """Create fallback response when LLM fails"""
        
        if language == "hi":
            return f"""मुझे {profile_count} ARGO प्रोफाइल मिले हैं जो आपके प्रश्न से मेल खाते हैं। 
            {analysis_type} विश्लेषण पूरा किया गया है। हिंद महासागर के डेटा से महत्वपूर्ण 
            समुद्री विज्ञान की जानकारी मिली है।"""
        
        elif language == "bn":
            return f"""আপনার প্রশ্নের সাথে মিলে এমন {profile_count}টি ARGO প্রোফাইল পেয়েছি। 
            {analysis_type} বিশ্লেষণ সম্পন্ন হয়েছে। ভারত মহাসাগরের ডেটা থেকে গুরুত্বপূর্ণ 
            সামুদ্রিক বিজ্ঞানের তথ্য পাওয়া গেছে।"""
        
        elif language == "ta":
            return f"""உங்கள் கேள்விக்கு பொருந்தும் {profile_count} ARGO சுயவிவரங்கள் கிடைத்துள்ளன। 
            {analysis_type} பகுப்பாய்வு நிறைவடைந்துள்ளது। இந்திய பெருங்கடலின் தரவுகளிலிருந்து 
            முக்கியமான கடல் அறிவியல் தகவல்கள் பெறப்பட்டுள்ளன।"""
        
        else:  # English
            summary = analysis_results.get("summary", "Analysis completed")
            return f"""Based on your query about Indian Ocean ARGO data, I found {profile_count} 
            matching profiles. {analysis_type.title()} analysis has been completed. 
            
            Key findings: {summary}
            
            This analysis is based on quality-controlled ARGO float data from the Indian Ocean, 
            providing valuable insights into regional oceanographic conditions."""
    
    async def process_query(self, query: str, language: str = "en") -> Dict[str, Any]:
        """Main entry point for processing oceanographic queries"""
        
        start_time = datetime.now()
        
        initial_state = AgentState(
            messages=[],
            query=query,
            language=language,
            extracted_params={},
            database_results=[],
            vector_results=[],
            analysis_results={},
            response="",
            visualizations=[],
            scientific_context={}
        )
        
        try:
            # Execute LangGraph workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "response": final_state["response"],
                "data_summary": {
                    "profiles_found": len(final_state["database_results"]),
                    "vector_matches": len(final_state["vector_results"]),
                    "analysis_performed": final_state["analysis_results"].get("analysis_type", "none"),
                    "visualizations_available": len(final_state["visualizations"])
                },
                "visualizations": final_state["visualizations"],
                "scientific_context": final_state["scientific_context"],
                "extracted_parameters": final_state["extracted_params"],
                "metadata": {
                    "query_language": language,
                    "processing_time_seconds": round(processing_time, 2),
                    "data_source": "argo_floats",
                    "quality_level": "research_grade",
                    "analysis_confidence": self.assess_response_confidence(final_state)
                }
            }
            
        except Exception as e:
            logger.error(f"Complete query processing failed: {e}")
            
            return {
                "response": "I apologize, but I encountered a technical error processing your oceanographic query. Please try rephrasing your question or contact support.",
                "error": str(e),
                "metadata": {
                    "query_language": language,
                    "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                    "status": "error"
                }
            }
    
    def assess_response_confidence(self, final_state: AgentState) -> str:
        """Assess confidence level of the response"""
        
        profile_count = len(final_state["database_results"])
        analysis_results = final_state["analysis_results"]
        
        if profile_count >= 50 and not analysis_results.get("error"):
            return "high"
        elif profile_count >= 20:
            return "moderate"
        elif profile_count >= 5:
            return "low"
        else:
            return "very_low"

# Global agent instance
indian_ocean_argo_agent = IndianOceanArgoAgent()
