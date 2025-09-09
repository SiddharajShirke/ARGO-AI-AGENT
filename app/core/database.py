"""
Advanced PostgreSQL Database Infrastructure for Indian Ocean ARGO Data
Production-optimized with comprehensive models, indexing, and connection management
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text, Index, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import uuid
from datetime import datetime, timedelta
import logging
from typing import Generator, List, Dict, Any, Optional, Tuple
import json
from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base for ORM models
Base = declarative_base()

# Advanced Database Models for Indian Ocean ARGO Data
class ARGOProfile(Base):
    """
    Comprehensive ARGO Float Profile model optimized for Indian Ocean research
    Includes advanced indexing for geographic, temporal, and oceanographic queries
    """
    __tablename__ = "argo_profiles"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    float_id = Column(String(20), nullable=False, index=True)
    cycle_number = Column(Integer, nullable=False)
    profile_date = Column(DateTime, nullable=False, index=True)
    
    # Geographic location with precision
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    # Regional classification for Indian Ocean
    ocean_region = Column(String(50), nullable=False, index=True)
    subregion = Column(String(50))  # More specific classification
    
    # Surface measurements (most critical for analysis)
    surface_temperature = Column(Float)  # Celsius
    surface_salinity = Column(Float)     # PSU
    surface_pressure = Column(Float)     # dbar
    surface_density = Column(Float)      # kg/m³
    
    # Profile characteristics
    max_depth = Column(Float)            # Maximum depth reached (meters)
    num_levels = Column(Integer)         # Number of measurement levels
    temperature_range = Column(Float)    # Temperature variation in profile
    salinity_range = Column(Float)       # Salinity variation in profile
    
    # Advanced oceanographic parameters
    mixed_layer_depth = Column(Float)    # Mixed layer depth (meters)
    thermocline_depth = Column(Float)    # Thermocline depth (meters)
    halocline_depth = Column(Float)      # Halocline depth (meters)
    
    # Statistical measures
    temp_mean = Column(Float)            # Profile average temperature
    temp_std = Column(Float)             # Temperature standard deviation
    salinity_mean = Column(Float)        # Profile average salinity
    salinity_std = Column(Float)         # Salinity standard deviation
    
    # Data quality and processing
    data_quality_score = Column(Float, nullable=False, index=True)  # 1-5 scale
    position_accuracy = Column(String(10))   # GPS accuracy class
    time_accuracy = Column(String(10))       # Time accuracy class
    processing_level = Column(String(20), default="real_time")  # real_time, delayed_mode, adjusted
    
    # Data availability flags
    has_temperature = Column(Boolean, default=True)
    has_salinity = Column(Boolean, default=True)
    has_pressure = Column(Boolean, default=True)
    has_oxygen = Column(Boolean, default=False)     # BGC data
    has_ph = Column(Boolean, default=False)         # BGC data
    has_nitrate = Column(Boolean, default=False)    # BGC data
    has_chlorophyll = Column(Boolean, default=False) # BGC data
    
    # Metadata and processing
    data_source = Column(String(100), default="ARGO")
    platform_type = Column(String(50))      # Float type/model
    sensor_type = Column(String(100))       # CTD sensor information
    
    # Timestamps
    processed_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Profile summary for embeddings and search
    profile_summary = Column(Text)       # Rich text for vector embeddings
    scientific_summary = Column(Text)    # Scientific interpretation
    
    # Advanced composite indexes for optimization
    __table_args__ = (
        # Multi-dimensional geographic-temporal index
        Index('idx_location_time_quality', 'latitude', 'longitude', 'profile_date', 'data_quality_score'),
        
        # Regional analysis optimization
        Index('idx_region_season_quality', 'ocean_region', 'profile_date', 'data_quality_score'),
        
        # Float trajectory analysis
        Index('idx_float_trajectory', 'float_id', 'profile_date', 'cycle_number'),
        
        # Surface parameter analysis
        Index('idx_surface_params', 'surface_temperature', 'surface_salinity', 'data_quality_score'),
        
        # Temporal analysis by region
        Index('idx_temporal_regional', 'profile_date', 'ocean_region', 'subregion'),
        
        # Data quality and availability
        Index('idx_quality_flags', 'data_quality_score', 'has_temperature', 'has_salinity'),
        
        # Advanced oceanographic parameters
        Index('idx_oceanographic_params', 'mixed_layer_depth', 'thermocline_depth', 'ocean_region'),
    )
    
    def __repr__(self):
        return (f"<ARGOProfile(float_id='{self.float_id}', "
                f"cycle={self.cycle_number}, "
                f"date='{self.profile_date}', "
                f"region='{self.ocean_region}')>")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'float_id': self.float_id,
            'cycle_number': self.cycle_number,
            'profile_date': self.profile_date.isoformat() if self.profile_date else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'ocean_region': self.ocean_region,
            'subregion': self.subregion,
            'surface_temperature': self.surface_temperature,
            'surface_salinity': self.surface_salinity,
            'surface_pressure': self.surface_pressure,
            'max_depth': self.max_depth,
            'num_levels': self.num_levels,
            'mixed_layer_depth': self.mixed_layer_depth,
            'thermocline_depth': self.thermocline_depth,
            'data_quality_score': self.data_quality_score,
            'processing_level': self.processing_level,
            'has_temperature': self.has_temperature,
            'has_salinity': self.has_salinity,
            'has_pressure': self.has_pressure,
            'processed_date': self.processed_date.isoformat() if self.processed_date else None
        }
    
    @property
    def is_high_quality(self) -> bool:
        """Check if profile meets high quality standards"""
        return (self.data_quality_score >= 4.0 and 
                self.has_temperature and 
                self.has_salinity)
    
    @property
    def location_string(self) -> str:
        """Human-readable location string"""
        lat_dir = "N" if self.latitude >= 0 else "S"
        lon_dir = "E" if self.longitude >= 0 else "W"
        return f"{abs(self.latitude):.2f}°{lat_dir}, {abs(self.longitude):.2f}°{lon_dir}"
    
    @property
    def seasonal_context(self) -> Dict[str, Any]:
        """Get seasonal context for profile date"""
        if self.profile_date:
            return settings.get_seasonal_context(self.profile_date.month)
        return {}
    
    @property
    def regional_context(self) -> Dict[str, Any]:
        """Get regional oceanographic context"""
        return settings.get_regional_context(self.ocean_region)
    
    def get_quality_assessment(self) -> Dict[str, Any]:
        """Comprehensive quality assessment"""
        assessment = {
            "overall_quality": self.data_quality_score,
            "quality_category": self._get_quality_category(),
            "data_completeness": self._assess_data_completeness(),
            "spatial_accuracy": self.position_accuracy or "standard",
            "temporal_accuracy": self.time_accuracy or "standard",
            "processing_level": self.processing_level
        }
        return assessment
    
    def _get_quality_category(self) -> str:
        """Get quality category description"""
        if self.data_quality_score >= 4.5:
            return "excellent"
        elif self.data_quality_score >= 4.0:
            return "high"
        elif self.data_quality_score >= 3.0:
            return "good"
        elif self.data_quality_score >= 2.0:
            return "acceptable"
        else:
            return "poor"
    
    def _assess_data_completeness(self) -> float:
        """Calculate data completeness score"""
        available_params = sum([
            self.has_temperature,
            self.has_salinity, 
            self.has_pressure,
            bool(self.mixed_layer_depth),
            bool(self.thermocline_depth)
        ])
        total_params = 5
        return available_params / total_params

class ARGOProfileDetail(Base):
    """
    Detailed depth-level measurements for ARGO profiles
    Stores complete vertical profile data
    """
    __tablename__ = "argo_profile_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('argo_profiles.id'), nullable=False, index=True)
    
    # Measurement depth and pressure
    depth_level = Column(Float, nullable=False)     # Depth in meters
    pressure = Column(Float, nullable=False)        # Pressure in dbar
    
    # Core measurements
    temperature = Column(Float)                     # Temperature in Celsius
    salinity = Column(Float)                        # Salinity in PSU
    density = Column(Float)                         # Density in kg/m³
    
    # Quality control flags
    temperature_qc = Column(String(1))              # Quality control flag
    salinity_qc = Column(String(1))                 # Quality control flag
    pressure_qc = Column(String(1))                 # Quality control flag
    
    # BGC parameters (if available)
    oxygen = Column(Float)                          # Dissolved oxygen
    ph = Column(Float)                              # pH
    nitrate = Column(Float)                         # Nitrate concentration
    chlorophyll = Column(Float)                     # Chlorophyll concentration
    
    # BGC quality flags
    oxygen_qc = Column(String(1))
    ph_qc = Column(String(1))
    nitrate_qc = Column(String(1))
    chlorophyll_qc = Column(String(1))
    
    # Relationship to main profile
    profile = relationship("ARGOProfile", backref="detail_measurements")
    
    # Optimized indexes
    __table_args__ = (
        Index('idx_profile_depth', 'profile_id', 'depth_level'),
        Index('idx_depth_temperature', 'depth_level', 'temperature'),
        Index('idx_depth_salinity', 'depth_level', 'salinity'),
    )
    
    def __repr__(self):
        return f"<ARGOProfileDetail(profile_id='{self.profile_id}', depth={self.depth_level}m)>"

class DataProcessingLog(Base):
    """
    Comprehensive audit log for all data processing operations
    Critical for tracking data quality, processing history, and system monitoring
    """
    __tablename__ = "processing_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Operation identification
    operation_type = Column(String(50), nullable=False, index=True)
    operation_subtype = Column(String(50))
    operation_status = Column(String(20), nullable=False, index=True)
    
    # Processing statistics
    records_processed = Column(Integer, default=0)
    records_accepted = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    processing_time_seconds = Column(Float)
    memory_usage_mb = Column(Float)
    
    # Timing information
    start_time = Column(DateTime, default=datetime.utcnow, index=True)
    end_time = Column(DateTime)
    
    # Source information
    source_file = Column(String(500))
    source_type = Column(String(50))
    source_size_mb = Column(Float)
    
    # Geographic and temporal scope
    lat_min = Column(Float)
    lat_max = Column(Float)
    lon_min = Column(Float)
    lon_max = Column(Float)
    date_min = Column(DateTime)
    date_max = Column(DateTime)
    
    # Quality metrics
    avg_quality_score = Column(Float)
    quality_distribution = Column(Text)  # JSON string
    
    # Error information
    error_message = Column(Text)
    error_type = Column(String(100))
    error_details = Column(Text)
    
    # Processing context
    processing_parameters = Column(Text)    # JSON configuration
    system_info = Column(Text)             # System state during processing
    
    def __repr__(self):
        return (f"<DataProcessingLog(operation='{self.operation_type}', "
                f"status='{self.operation_status}', "
                f"records={self.records_processed})>")

class SystemHealth(Base):
    """
    System health and performance monitoring
    Tracks system metrics for production monitoring
    """
    __tablename__ = "system_health"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Database metrics
    total_profiles = Column(Integer)
    high_quality_profiles = Column(Integer)
    recent_profiles = Column(Integer)  # Last 24 hours
    
    # System performance
    avg_query_time = Column(Float)     # Average query response time
    active_connections = Column(Integer)
    cache_hit_rate = Column(Float)
    
    # Vector database metrics
    vector_db_size = Column(Integer)
    embedding_generation_time = Column(Float)
    
    # API metrics
    requests_per_hour = Column(Integer)
    error_rate = Column(Float)
    
    # System resources
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    
    # Status flags
    overall_health = Column(String(20))  # healthy, warning, error
    alerts_active = Column(Integer, default=0)

# Advanced Database Manager
class DatabaseManager:
    """
    Production-grade database connection and operation management
    Includes advanced querying, health monitoring, and performance optimization
    """
    
    def __init__(self):
        """Initialize database engine with production optimizations"""
        
        # Create engine with advanced configuration
        engine_config = settings.database_config
        self.engine = create_engine(
            engine_config["url"],
            poolclass=QueuePool,
            pool_size=engine_config["pool_size"],
            max_overflow=engine_config["max_overflow"],
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=engine_config["echo"],
            connect_args=engine_config["connect_args"]
        )
        
        # Session factory with optimizations
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False  # Prevent lazy loading issues
        )
        
        logger.info("Advanced database manager initialized")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Enhanced session context manager with monitoring"""
        session = self.SessionLocal()
        start_time = datetime.utcnow()
        
        try:
            yield session
            session.commit()
            
            # Log successful operations
            duration = (datetime.utcnow() - start_time).total_seconds()
            if duration > 1.0:  # Log slow queries
                logger.warning(f"Slow database operation: {duration:.2f}s")
                
        except Exception as e:
            session.rollback()
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Database session error after {duration:.2f}s: {str(e)}")
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """Create all database tables with comprehensive error handling"""
        try:
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Log successful creation
            with self.get_session() as session:
                # Verify table creation
                tables = session.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)).fetchall()
                
                table_names = [row[0] for row in tables]
                logger.info(f"Created tables: {', '.join(table_names)}")
                
                # Add initial processing log
                initial_log = DataProcessingLog(
                    operation_type="database_initialization",
                    operation_status="success",
                    records_processed=0,
                    processing_time_seconds=0.0,
                    processing_parameters='{"action": "create_tables"}',
                    system_info=json.dumps(settings.get_system_info())
                )
                session.add(initial_log)
                
                # Add initial health record
                initial_health = SystemHealth(
                    total_profiles=0,
                    high_quality_profiles=0,
                    recent_profiles=0,
                    avg_query_time=0.0,
                    active_connections=1,
                    overall_health="healthy"
                )
                session.add(initial_health)
                
                session.commit()
                
            logger.info("Database tables and initial data created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    def initialize_database(self) -> bool:
        """Initialize database with tables and initial data"""
        try:
            self.create_tables()
            logger.info("Database initialization completed successfully")
            return True
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health assessment"""
        health_status = {
            "database_connected": False,
            "tables_exist": False,
            "recent_activity": False,
            "performance_acceptable": False,
            "overall_status": "unhealthy"
        }
        
        try:
            with self.get_session() as session:
                start_time = datetime.utcnow()
                
                # Test basic connectivity
                result = session.execute(text("SELECT 1 as health_check")).scalar()
                health_status["database_connected"] = (result == 1)
                
                # Check table existence
                tables_result = session.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('argo_profiles', 'processing_logs', 'system_health')
                """)).scalar()
                
                health_status["tables_exist"] = (tables_result == 3)
                
                # Check recent activity (last 24 hours)
                if health_status["tables_exist"]:
                    recent_logs = session.execute(text("""
                        SELECT COUNT(*) 
                        FROM processing_logs 
                        WHERE start_time > NOW() - INTERVAL '24 hours'
                    """)).scalar()
                    
                    health_status["recent_activity"] = (recent_logs > 0)
                
                # Measure query performance
                query_time = (datetime.utcnow() - start_time).total_seconds()
                health_status["query_time_seconds"] = query_time
                health_status["performance_acceptable"] = (query_time < settings.MAX_RESPONSE_TIME)
                
                # Overall status
                all_checks = [
                    health_status["database_connected"],
                    health_status["tables_exist"],
                    health_status["performance_acceptable"]
                ]
                
                if all(all_checks):
                    health_status["overall_status"] = "healthy"
                elif any(all_checks):
                    health_status["overall_status"] = "degraded"
                else:
                    health_status["overall_status"] = "unhealthy"
                
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            health_status["error"] = str(e)
        
        return health_status
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            with self.get_session() as session:
                # Profile statistics
                profile_stats = session.execute(text("""
                    SELECT 
                        COUNT(*) as total_profiles,
                        COUNT(*) FILTER (WHERE data_quality_score >= 4.0) as high_quality,
                        COUNT(*) FILTER (WHERE profile_date > NOW() - INTERVAL '30 days') as recent,
                        AVG(data_quality_score) as avg_quality,
                        COUNT(DISTINCT float_id) as unique_floats,
                        COUNT(DISTINCT ocean_region) as regions_covered,
                        MIN(profile_date) as earliest_date,
                        MAX(profile_date) as latest_date
                    FROM argo_profiles
                """)).fetchone()
                
                # Regional distribution
                regional_stats = session.execute(text("""
                    SELECT 
                        ocean_region,
                        COUNT(*) as profile_count,
                        AVG(data_quality_score) as avg_quality,
                        AVG(surface_temperature) as avg_temp,
                        AVG(surface_salinity) as avg_salinity
                    FROM argo_profiles 
                    WHERE data_quality_score >= :threshold
                    GROUP BY ocean_region
                    ORDER BY profile_count DESC
                """), {"threshold": settings.DATA_QUALITY_THRESHOLD}).fetchall()
                
                # Connection pool stats
                pool_stats = self.get_connection_stats()
                
                return {
                    "profile_statistics": {
                        "total_profiles": profile_stats.total_profiles or 0,
                        "high_quality_profiles": profile_stats.high_quality or 0,
                        "recent_profiles": profile_stats.recent or 0,
                        "average_quality": float(profile_stats.avg_quality or 0),
                        "unique_floats": profile_stats.unique_floats or 0,
                        "regions_covered": profile_stats.regions_covered or 0,
                        "date_range": {
                            "earliest": profile_stats.earliest_date.isoformat() if profile_stats.earliest_date else None,
                            "latest": profile_stats.latest_date.isoformat() if profile_stats.latest_date else None
                        }
                    },
                    "regional_distribution": [
                        {
                            "region": row.ocean_region,
                            "profile_count": row.profile_count,
                            "average_quality": float(row.avg_quality or 0),
                            "average_temperature": float(row.avg_temp or 0),
                            "average_salinity": float(row.avg_salinity or 0)
                        }
                        for row in regional_stats
                    ],
                    "connection_pool": pool_stats,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting database statistics: {str(e)}")
            return {"error": str(e)}
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get detailed connection pool statistics"""
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
            "pool_utilization": (pool.checkedout() / (pool.size() + pool.overflow())) * 100
        }
    
    def optimize_performance(self):
        """Run database performance optimization"""
        try:
            with self.get_session() as session:
                # Analyze tables for better query planning
                optimization_queries = [
                    "ANALYZE argo_profiles;",
                    "ANALYZE argo_profile_details;", 
                    "ANALYZE processing_logs;",
                    "REINDEX INDEX CONCURRENTLY idx_location_time_quality;",
                    "VACUUM (ANALYZE) argo_profiles;"
                ]
                
                for query in optimization_queries:
                    try:
                        session.execute(query)
                        logger.info(f"Executed optimization: {query}")
                    except Exception as e:
                        logger.warning(f"Optimization query failed: {query}, Error: {e}")
                
                session.commit()
                logger.info("Database performance optimization completed")
                
        except Exception as e:
            logger.error(f"Performance optimization failed: {str(e)}")

# Global database instance
db = DatabaseManager()

# FastAPI dependency for session injection
def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions with performance monitoring"""
    with db.get_session() as session:
        yield session

# Advanced query helpers for common operations
def get_profiles_by_region(region: str, limit: int = 1000, quality_threshold: float = None) -> List[ARGOProfile]:
    """Get high-quality ARGO profiles for specific region with advanced filtering"""
    quality_threshold = quality_threshold or settings.DATA_QUALITY_THRESHOLD
    
    with db.get_session() as session:
        query = session.query(ARGOProfile).filter(
            ARGOProfile.ocean_region == region,
            ARGOProfile.data_quality_score >= quality_threshold
        ).order_by(ARGOProfile.profile_date.desc())
        
        return query.limit(limit).all()

def get_profiles_by_coordinates(lat_min: float, lat_max: float, lon_min: float, lon_max: float, 
                               limit: int = 1000) -> List[ARGOProfile]:
    """Get profiles within specific coordinate bounds"""
    with db.get_session() as session:
        return session.query(ARGOProfile).filter(
            ARGOProfile.latitude.between(lat_min, lat_max),
            ARGOProfile.longitude.between(lon_min, lon_max),
            ARGOProfile.data_quality_score >= settings.DATA_QUALITY_THRESHOLD
        ).order_by(ARGOProfile.profile_date.desc()).limit(limit).all()

def get_seasonal_profiles(season: str, year: int = None, limit: int = 1000) -> List[ARGOProfile]:
    """Get profiles for specific season and year"""
    season_months = settings.MONSOON_SEASONS.get(season, {}).get("months", [])
    
    if not season_months:
        return []
    
    with db.get_session() as session:
        query = session.query(ARGOProfile).filter(
            ARGOProfile.profile_date.extract('month').in_(season_months),
            ARGOProfile.data_quality_score >= settings.DATA_QUALITY_THRESHOLD
        )
        
        if year:
            query = query.filter(ARGOProfile.profile_date.extract('year') == year)
        
        return query.order_by(ARGOProfile.profile_date.desc()).limit(limit).all()

def search_profiles_advanced(
    regions: List[str] = None,
    date_range: Tuple[datetime, datetime] = None, 
    temperature_range: Tuple[float, float] = None,
    salinity_range: Tuple[float, float] = None,
    quality_min: float = None,
    limit: int = 1000
) -> List[ARGOProfile]:
    """Advanced multi-parameter profile search"""
    
    with db.get_session() as session:
        query = session.query(ARGOProfile)
        
        # Apply filters
        if regions:
            query = query.filter(ARGOProfile.ocean_region.in_(regions))
        
        if date_range:
            query = query.filter(ARGOProfile.profile_date.between(*date_range))
        
        if temperature_range:
            query = query.filter(ARGOProfile.surface_temperature.between(*temperature_range))
        
        if salinity_range:
            query = query.filter(ARGOProfile.surface_salinity.between(*salinity_range))
        
        quality_threshold = quality_min or settings.DATA_QUALITY_THRESHOLD
        query = query.filter(ARGOProfile.data_quality_score >= quality_threshold)
        
        return query.order_by(ARGOProfile.profile_date.desc()).limit(limit).all()

# Batch operations for efficient data processing
class BatchOperations:
    """Efficient batch operations for large-scale data processing"""
    
    @staticmethod
    def bulk_insert_profiles(profiles_data: List[Dict[str, Any]]) -> int:
        """Efficient bulk insert of ARGO profiles"""
        
        if not profiles_data:
            return 0
        
        try:
            with db.get_session() as session:
                # Use SQLAlchemy bulk insert for performance
                session.bulk_insert_mappings(ARGOProfile, profiles_data)
                session.commit()
                
                logger.info(f"Bulk inserted {len(profiles_data)} ARGO profiles")
                return len(profiles_data)
                
        except Exception as e:
            logger.error(f"Bulk insert failed: {str(e)}")
            raise
    
    @staticmethod
    def update_processing_log(log_id: uuid.UUID, updates: Dict[str, Any]) -> bool:
        """Update processing log with batch operation results"""
        
        try:
            with db.get_session() as session:
                session.query(DataProcessingLog).filter(
                    DataProcessingLog.id == log_id
                ).update(updates)
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Processing log update failed: {str(e)}")
            return False


# Module-level convenience functions for main.py
def create_tables():
    """Create all database tables."""
    return db.create_tables()


def check_connection() -> bool:
    """Check database connection health."""
    try:
        health = db.health_check()
        return health.get("database_connected", False)
    except Exception as e:
        logger.error(f"Connection check failed: {e}")
        return False


def get_stats():
    """Get database statistics."""
    return db.get_comprehensive_stats()
