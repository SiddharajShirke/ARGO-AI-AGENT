"""
Production-Grade Configuration Management for Indian Ocean ARGO AI Agent
Handles all environment-specific settings with validation and regional intelligence
"""

from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings with comprehensive validation and regional intelligence"""
    
    # Environment Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    SECRET_KEY: str = "development-secret-key"
    
    # Database Configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "indian_ocean_argo"
    POSTGRES_USER: str = "argo_user"
    POSTGRES_PASSWORD: str = "argo_password"
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # ChromaDB Configuration
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    
    # Vector Database Configuration
    COLLECTION_NAME: str = "indian_ocean_argo_profiles"
    
    # LLM Configuration with Fallbacks
    GEMINI_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.1  # Changed to 0.1 for more deterministic responses
    LLM_MAX_TOKENS: int = 2048  # Increased for detailed responses
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    LLM_REQUEST_TIMEOUT: int = 30
    MAX_RESPONSE_TIME: float = 5.0  # Maximum acceptable database response time in seconds
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8002
    API_RELOAD: bool = True
    CORS_ORIGINS: List[str] = ["*"]
    
    # Dashboard Configuration
    DASHBOARD_HOST: str = "0.0.0.0"
    DASHBOARD_PORT: int = 8501
    PAGE_TITLE: str = "Indian Ocean Argo AI Agent"
    PAGE_ICON: str = "🌊"
    
    # Data Processing Configuration
    DATA_DIR: str = "./data"
    SAMPLES_DIR: str = "./data/samples"
    EXPORTS_DIR: str = "./data/exports"
    MAX_FILE_SIZE_MB: int = 100
    NETCDF_CHUNK_SIZE: int = 1000
    MAX_PROFILES_PER_QUERY: int = 10000
    DATA_QUALITY_THRESHOLD: float = 3.0
    BATCH_SIZE: int = 1000
    
    # Argo Data Configuration
    ARGO_GDAC_URL: str = "https://data-argo.ifremer.fr"
    QC_FLAGS_ACCEPT: List[int] = [1, 2, 5, 8]
    
    # Map Configuration (Indian Ocean focus)
    DEFAULT_LATITUDE: float = -5.0  # Better center for Indian Ocean
    DEFAULT_LONGITUDE: float = 75.0
    DEFAULT_ZOOM: int = 4
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Multi-language Support Configuration
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "bn", "ta", "te"]
    DEFAULT_LANGUAGE: str = "en"
    
    # Indian Ocean Geographic Boundaries (Precise Coordinates)
    INDIAN_OCEAN_BOUNDS: Dict[str, float] = {
        "lat_min": -40.0,
        "lat_max": 30.0,
        "lon_min": 40.0,
        "lon_max": 120.0
    }
    
    # Regional Boundaries for Advanced Classification
    ARABIAN_SEA_BOUNDS: Dict[str, Any] = {
        "lat_min": 8.0,
        "lat_max": 30.0,
        "lon_min": 50.0,
        "lon_max": 78.0,
        "name": "Arabian Sea",
        "characteristics": "High salinity, seasonal upwelling, monsoon influence"
    }
    
    BAY_OF_BENGAL_BOUNDS: Dict[str, Any] = {
        "lat_min": 5.0,
        "lat_max": 24.0,
        "lon_min": 78.0,
        "lon_max": 100.0,
        "name": "Bay of Bengal",
        "characteristics": "Low salinity, river input, cyclone activity"
    }
    
    EQUATORIAL_INDIAN_BOUNDS: Dict[str, Any] = {
        "lat_min": -10.0,
        "lat_max": 10.0,
        "lon_min": 40.0,
        "lon_max": 120.0,
        "name": "Equatorial Indian Ocean",
        "characteristics": "Equatorial currents, stable temperatures"
    }
    
    # Seasonal Definitions for Oceanographic Analysis
    MONSOON_SEASONS: Dict[str, Dict[str, Any]] = {
        "southwest_monsoon": {
            "months": [6, 7, 8, 9],
            "description": "Southwest Monsoon (June-September)",
            "characteristics": "Strong winds, upwelling in Arabian Sea, heavy precipitation"
        },
        "northeast_monsoon": {
            "months": [12, 1, 2],
            "description": "Northeast Monsoon (December-February)",
            "characteristics": "Cooler temperatures, reduced precipitation"
        },
        "pre_monsoon": {
            "months": [3, 4, 5],
            "description": "Pre-monsoon (March-May)",
            "characteristics": "Rising temperatures, low precipitation"
        },
        "post_monsoon": {
            "months": [10, 11],
            "description": "Post-monsoon (October-November)",
            "characteristics": "Retreating monsoon, cyclone season"
        }
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # This fixes the validation error!

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._create_directories()
        self._validate_configuration()
        self._setup_logging()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.CHROMA_PERSIST_DIR,
            self.SAMPLES_DIR,
            self.EXPORTS_DIR,
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ensured: {directory}")
    
    def _validate_configuration(self):
        """Validate critical configuration settings"""
        validation_errors = []
        
        # Check required API keys
        if not self.GEMINI_API_KEY:
            validation_errors.append("GEMINI_API_KEY must be provided for AI functionality")
        
        # Validate database configuration
        if not all([self.POSTGRES_HOST, self.POSTGRES_DB, self.POSTGRES_USER, self.POSTGRES_PASSWORD]):
            validation_errors.append("All PostgreSQL configuration fields must be provided")
        
        # Validate numeric ranges
        if not (0.0 <= self.LLM_TEMPERATURE <= 2.0):
            validation_errors.append("LLM_TEMPERATURE must be between 0.0 and 2.0")
        
        if not (1.0 <= self.DATA_QUALITY_THRESHOLD <= 5.0):
            validation_errors.append("DATA_QUALITY_THRESHOLD must be between 1.0 and 5.0")
        
        # Validate geographic bounds
        bounds = self.INDIAN_OCEAN_BOUNDS
        if bounds["lat_min"] >= bounds["lat_max"] or bounds["lon_min"] >= bounds["lon_max"]:
            validation_errors.append("Invalid geographic bounds configuration")
        
        if validation_errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in validation_errors)
            raise ValueError(error_message)
        
        logger.info("Configuration validation passed")
    
    def _setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("logs/argo_agent.log")
            ]
        )
    
    # Compatibility Properties for Database Code
    @property
    def DATABASE_URL(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property  
    def GOOGLE_API_KEY(self) -> Optional[str]:
        """Get Google API key"""
        return self.GEMINI_API_KEY

    @property
    def CHROMA_PATH(self) -> str:
        """Get Chroma path"""
        return self.CHROMA_PERSIST_DIR

    @property
    def SAMPLES_PATH(self) -> str:
        """Get samples path"""
        return self.SAMPLES_DIR

    @property
    def EXPORTS_PATH(self) -> str:
        """Get exports path"""
        return self.EXPORTS_DIR
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Database configuration dictionary for SQLAlchemy"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": 10,
            "max_overflow": 20,
            "echo": self.DEBUG,
            "connect_args": {
                "connect_timeout": 30,
                "application_name": "indian_ocean_argo_agent"
            }
        }
    
    def is_coordinate_in_indian_ocean(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within Indian Ocean bounds"""
        bounds = self.INDIAN_OCEAN_BOUNDS
        return (
            bounds["lat_min"] <= lat <= bounds["lat_max"] and
            bounds["lon_min"] <= lon <= bounds["lon_max"]
        )
    
    def classify_region(self, lat: float, lon: float) -> str:
        """Classify coordinates into specific Indian Ocean regions"""
        if not self.is_coordinate_in_indian_ocean(lat, lon):
            return "outside_indian_ocean"
        
        # Check specific regions
        regions = {
            "arabian_sea": self.ARABIAN_SEA_BOUNDS,
            "bay_of_bengal": self.BAY_OF_BENGAL_BOUNDS,
            "equatorial_indian": self.EQUATORIAL_INDIAN_BOUNDS
        }
        
        for region_name, bounds in regions.items():
            if (bounds["lat_min"] <= lat <= bounds["lat_max"] and
                bounds["lon_min"] <= lon <= bounds["lon_max"]):
                return region_name
        
        return "indian_ocean_other"
    
    def get_seasonal_context(self, month: int) -> Dict[str, Any]:
        """Get seasonal context for given month"""
        for season_name, season_info in self.MONSOON_SEASONS.items():
            if month in season_info["months"]:
                return {
                    "season": season_name,
                    "description": season_info["description"],
                    "characteristics": season_info["characteristics"]
                }
        
        return {"season": "unknown", "description": "Unknown season", "characteristics": ""}
    
    def get_regional_context(self, region: str) -> Dict[str, Any]:
        """Get detailed context for specific region"""
        region_contexts = {
            "arabian_sea": {
                "full_name": "Arabian Sea",
                "characteristics": self.ARABIAN_SEA_BOUNDS.get("characteristics", ""),
                "typical_temp_range": "24-30°C",
                "typical_salinity_range": ">35.5 PSU",
                "key_phenomena": ["Seasonal upwelling", "High evaporation", "Oxygen minimum zone"]
            },
            "bay_of_bengal": {
                "full_name": "Bay of Bengal",
                "characteristics": self.BAY_OF_BENGAL_BOUNDS.get("characteristics", ""),
                "typical_temp_range": "26-30°C",
                "typical_salinity_range": "<34.5 PSU",
                "key_phenomena": ["River discharge", "Cyclone formation", "Salinity stratification"]
            },
            "equatorial_indian": {
                "full_name": "Equatorial Indian Ocean",
                "characteristics": self.EQUATORIAL_INDIAN_BOUNDS.get("characteristics", ""),
                "typical_temp_range": "26-28°C",
                "typical_salinity_range": "34.5-35.5 PSU",
                "key_phenomena": ["Equatorial currents", "IOD influence", "Seasonal thermocline"]
            }
        }
        
        return region_contexts.get(region, {
            "full_name": "Indian Ocean",
            "characteristics": "Tropical ocean basin",
            "typical_temp_range": "Variable",
            "typical_salinity_range": "Variable",
            "key_phenomena": ["Monsoon influence"]
        })
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system configuration info"""
        return {
            "environment": self.ENVIRONMENT,
            "version": "1.0.0",
            "database_configured": bool(self.POSTGRES_HOST and self.POSTGRES_DB),
            "llm_providers": {
                "gemini": bool(self.GEMINI_API_KEY)
            },
            "supported_languages": self.SUPPORTED_LANGUAGES,
            "regions_supported": list(self.MONSOON_SEASONS.keys()),
            "data_limits": {
                "max_profiles_per_query": self.MAX_PROFILES_PER_QUERY,
                "quality_threshold": self.DATA_QUALITY_THRESHOLD
            }
        }

# Global settings instance
settings = Settings()

# Configuration validation on import
logger.info("Indian Ocean ARGO AI Agent Configuration Loaded")
logger.info(f"Environment: {settings.ENVIRONMENT}")
logger.info(f"Supported Languages: {', '.join(settings.SUPPORTED_LANGUAGES)}")
logger.info(f"LLM Providers Available: Gemini={bool(settings.GEMINI_API_KEY)}")
