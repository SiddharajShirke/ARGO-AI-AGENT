"""
Complete Production Environment Setup Script for Indian Ocean ARGO AI Agent
Initializes database, vector database, validates configuration, and creates sample data
"""

import sys
import logging
import time
import traceback
from pathlib import Path
from datetime import datetime, timedelta
import json
import uuid

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import db, DataProcessingLog, ARGOProfile, SystemHealth
from app.core.vector_db import vector_db
from app.core.config import settings

# Configure comprehensive logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('setup.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

class ProductionSetupManager:
    """Comprehensive production environment setup manager"""
    
    def __init__(self):
        self.setup_steps = []
        self.start_time = datetime.utcnow()
        self.errors = []
        self.warnings = []
        
    def run_complete_setup(self) -> bool:
        """Execute complete production setup process"""
        
        logger.info("INDIAN OCEAN ARGO AI AGENT - PRODUCTION SETUP")
        logger.info("=" * 80)
        logger.info(f"Setup started at: {self.start_time}")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Python version: {sys.version}")
        logger.info("=" * 80)
        
        setup_phases = [
            ("Phase 1: Configuration Validation", self._validate_configuration),
            ("Phase 2: Database Infrastructure Setup", self._setup_database_infrastructure),
            ("Phase 3: Vector Database Initialization", self._setup_vector_database),
            ("Phase 4: Sample Data Creation", self._create_comprehensive_sample_data),
            ("Phase 5: System Integration Testing", self._run_integration_tests),
            ("Phase 6: Production Readiness Validation", self._validate_production_readiness),
            ("Phase 7: Performance Benchmarking", self._run_performance_benchmarks)
        ]
        
        for phase_name, phase_function in setup_phases:
            success = self._execute_phase(phase_name, phase_function)
            if not success and phase_name not in ["Phase 7: Performance Benchmarking"]:
                logger.error(f"[CRITICAL] Critical phase failed: {phase_name}")
                return False
        
        return self._generate_setup_summary()
    
    def _execute_phase(self, phase_name: str, phase_function) -> bool:
        """Execute a setup phase with comprehensive error handling"""
        
        logger.info(f"\n[PHASE] {phase_name}")
        logger.info("-" * 60)
        
        phase_start = datetime.utcnow()
        
        try:
            result = phase_function()
            duration = (datetime.utcnow() - phase_start).total_seconds()
            
            if result:
                logger.info(f"[SUCCESS] {phase_name} completed successfully in {duration:.2f}s")
                self.setup_steps.append({
                    "phase": phase_name,
                    "status": "success", 
                    "duration": duration,
                    "timestamp": phase_start.isoformat()
                })
                return True
            else:
                logger.error(f"[FAILED] {phase_name} failed after {duration:.2f}s")
                self.setup_steps.append({
                    "phase": phase_name,
                    "status": "failed",
                    "duration": duration,
                    "timestamp": phase_start.isoformat()
                })
                return False
                
        except Exception as e:
            duration = (datetime.utcnow() - phase_start).total_seconds()
            error_msg = f"{phase_name} failed with exception: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            logger.debug(f"Exception details: {traceback.format_exc()}")
            
            self.errors.append(error_msg)
            self.setup_steps.append({
                "phase": phase_name,
                "status": "error",
                "duration": duration,
                "error": str(e),
                "timestamp": phase_start.isoformat()
            })
            return False
    
    def _validate_configuration(self) -> bool:
        """Comprehensive configuration validation"""
        
        logger.info("Validating system configuration...")
        
        validation_checks = []
        
        # Check environment variables
        required_configs = {
            'DATABASE_URL': settings.DATABASE_URL,
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            'SECRET_KEY': settings.SECRET_KEY,
            'CHROMA_PATH': settings.CHROMA_PATH
        }
        
        for config_name, config_value in required_configs.items():
            if not config_value or config_value in ['your_api_key_here', 'development-secret-key']:
                logger.warning(f"WARNING: {config_name} not properly configured")
                self.warnings.append(f"{config_name} needs proper configuration")
                validation_checks.append(False)
            else:
                logger.info(f"SUCCESS: {config_name} configured")
                validation_checks.append(True)
        
        # Check directory creation
        directories = [settings.CHROMA_PATH, settings.SAMPLES_PATH, settings.EXPORTS_PATH, "logs"]
        for directory in directories:
            if Path(directory).exists():
                logger.info(f"SUCCESS: Directory exists: {directory}")
                validation_checks.append(True)
            else:
                try:
                    Path(directory).mkdir(parents=True, exist_ok=True)
                    logger.info(f"SUCCESS: Created directory: {directory}")
                    validation_checks.append(True)
                except Exception as e:
                    logger.error(f"FAILED: Failed to create directory {directory}: {e}")
                    validation_checks.append(False)
        
        # Validate geographic boundaries
        test_coordinates = [
            (15.0, 65.0, "arabian_sea"),
            (15.0, 88.0, "bay_of_bengal"),
            (0.0, 80.0, "equatorial_indian")
        ]
        
        for lat, lon, expected_region in test_coordinates:
            actual_region = settings.classify_region(lat, lon)
            if actual_region == expected_region:
                logger.info(f"SUCCESS: Regional classification: ({lat}, {lon}) -> {actual_region}")
                validation_checks.append(True)
            else:
                logger.error(f"FAILED: Regional classification failed: ({lat}, {lon}) -> {actual_region} (expected {expected_region})")
                validation_checks.append(False)
        
        # System information logging
        system_info = settings.get_system_info()
        logger.info(f"SUCCESS: System Info: {json.dumps(system_info, indent=2)}")
        
        success_rate = sum(validation_checks) / len(validation_checks)
        logger.info(f"Configuration validation success rate: {success_rate*100:.1f}%")
        
        return success_rate >= 0.8  # Allow 20% non-critical failures
    
    def _setup_database_infrastructure(self) -> bool:
        """Setup and validate PostgreSQL database infrastructure"""
        
        logger.info("Setting up PostgreSQL database infrastructure...")
        
        try:
            # Test database connectivity
            health_check = db.health_check()
            if not health_check.get("database_connected", False):
                logger.error("FAILED: Database connection failed!")
                logger.info("Database configuration:")
                logger.info(f"  DATABASE_URL: {settings.DATABASE_URL}")
                logger.info("Please ensure PostgreSQL is running and credentials are correct")
                return False
            
            logger.info("SUCCESS: Database connection established")
            
            # Create tables and indexes
            logger.info("Creating database schema...")
            db.create_tables()
            
            # Verify table creation
            with db.get_session() as session:
                # Check table existence
                from sqlalchemy import text
                tables_result = session.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)).fetchall()
                
                table_names = [row[0] for row in tables_result]
                expected_tables = ['argo_profiles', 'argo_profile_details', 'processing_logs', 'system_health']
                
                missing_tables = set(expected_tables) - set(table_names)
                if missing_tables:
                    logger.error(f"FAILED: Missing tables: {missing_tables}")
                    return False
                
                logger.info(f"SUCCESS: All required tables created: {table_names}")
                
                # Check indexes
                indexes_result = session.execute(text("""
                    SELECT indexname, tablename
                    FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND tablename = 'argo_profiles'
                    ORDER BY indexname
                """)).fetchall()
                
                index_count = len(indexes_result)
                logger.info(f"SUCCESS: Created {index_count} indexes for optimized queries")
                
                # Add initial system health record
                initial_health = SystemHealth(
                    total_profiles=0,
                    high_quality_profiles=0,
                    recent_profiles=0,
                    avg_query_time=0.0,
                    active_connections=1,
                    cache_hit_rate=0.0,
                    overall_health="healthy",
                    alerts_active=0
                )
                session.add(initial_health)
                session.commit()
                
                logger.info("SUCCESS: Initial system health record created")
            
            # Test database performance
            performance_start = datetime.utcnow()
            stats = db.get_comprehensive_stats()
            performance_time = (datetime.utcnow() - performance_start).total_seconds()
            
            if performance_time > 2.0:
                logger.warning(f"WARNING: Database query performance slow: {performance_time:.2f}s")
            else:
                logger.info(f"SUCCESS: Database performance good: {performance_time:.3f}s")
            
            logger.info("SUCCESS: Database infrastructure setup completed")
            return True
            
        except Exception as e:
            logger.error(f"FAILED: Database setup failed: {str(e)}")
            return False
    
    def _setup_vector_database(self) -> bool:
        """Setup and validate Chroma vector database"""
        
        logger.info("Setting up Chroma vector database...")
        
        try:
            # Test vector database health
            health_status = vector_db.health_check()
            
            if not health_status.get("server_healthy", False):
                logger.error("FAILED: Vector database connection failed!")
                logger.info(f"  Chroma Path: {settings.CHROMA_PATH}")
                logger.info(f"  Server Status: {health_status.get('server_status', 'unknown')}")
                return False
            
            logger.info("SUCCESS: Vector database connected")
            
            # Initialize embedding model in vector database manager
            if not vector_db.initialize_embedding_model():
                logger.error("FAILED: Embedding model failed to load")
                return False
            
            logger.info("SUCCESS: Sentence transformer embedding model loaded")
            
            # Initialize the vector database collection
            if not vector_db.initialize_collections():
                logger.error("FAILED: Vector database collection initialization failed")
                return False
            
            logger.info("SUCCESS: Vector database collection initialized")
            
            # Get and log vector database statistics
            stats = vector_db.get_comprehensive_stats()
            collection_info = stats.get("collection_info", {})
            
            logger.info(f"SUCCESS: Vector database initialized:")
            logger.info(f"  Collection: {collection_info.get('collection_name')}")
            logger.info(f"  Total profiles: {collection_info.get('total_profiles', 0)}")
            logger.info(f"  Embedding model: {collection_info.get('embedding_model')}")
            logger.info(f"  Embedding dimension: {collection_info.get('embedding_dimension')}")
            
            # Test embedding generation
            test_text = "Test oceanographic profile in Arabian Sea with high temperature"
            test_start = datetime.utcnow()
            test_embedding = vector_db.embeddings_model.encode([test_text])
            embedding_time = (datetime.utcnow() - test_start).total_seconds()
            
            if len(test_embedding[0]) == 384:
                logger.info(f"SUCCESS: Embedding generation working: {embedding_time:.3f}s")
            else:
                logger.error(f"FAILED: Embedding generation failed: wrong dimension {len(test_embedding[0])}")
                return False
            
            logger.info("SUCCESS: Vector database setup completed")
            return True
            
        except Exception as e:
            logger.error(f"FAILED: Vector database setup failed: {str(e)}")
            return False
    
    def _create_comprehensive_sample_data(self) -> bool:
        """Create comprehensive sample ARGO data for development and testing"""
        
        logger.info("Creating comprehensive sample ARGO data...")
        
        try:
            # Check if sample data already exists
            with db.get_session() as session:
                existing_count = session.query(ARGOProfile).filter(
                    ARGOProfile.float_id.like('SAMPLE_%')
                ).count()
                
                # Also check vector database
                vector_stats = vector_db.get_comprehensive_stats()
                vector_count = vector_stats.get("collection_info", {}).get("total_profiles", 0)
                
                if existing_count > 20 and vector_count > 20:
                    logger.info(f"SUCCESS: Sample data already exists: {existing_count} profiles in DB, {vector_count} in vector DB")
                    return True
                elif existing_count > 20 and vector_count == 0:
                    logger.info(f"INFO: Found {existing_count} profiles in DB but 0 in vector DB - will add to vector database")
                    # Load existing profiles for vector database
                    existing_profiles = session.query(ARGOProfile).filter(
                        ARGOProfile.float_id.like('SAMPLE_%')
                    ).all()
                    
                    # Convert to dictionaries for vector database
                    profile_dicts = []
                    for profile in existing_profiles:
                        profile_dict = {
                            'id': profile.id,
                            'float_id': profile.float_id,
                            'latitude': profile.latitude,
                            'longitude': profile.longitude,
                            'profile_date': profile.profile_date,
                            'ocean_region': profile.ocean_region,
                            'surface_temperature': profile.surface_temperature,
                            'surface_salinity': profile.surface_salinity,
                            'max_depth': profile.max_depth,
                            'data_quality_score': profile.data_quality_score
                        }
                        profile_dicts.append(profile_dict)
                    
                    # Add to vector database
                    vector_results = vector_db.add_profiles_advanced(profile_dicts)
                    
                    if vector_results.get("profiles_added", 0) > 0:
                        logger.info(f"SUCCESS: Added {vector_results['profiles_added']} existing profiles to vector database")
                        return True
                    else:
                        logger.warning("WARNING: Failed to add existing profiles to vector database")
                        if vector_results.get("errors"):
                            for error in vector_results["errors"]:
                                logger.warning(f"  {error}")
                
                logger.info(f"INFO: Need to create sample data (DB: {existing_count}, Vector: {vector_count})")
            
            # Generate diverse sample profiles
            sample_profiles = self._generate_sample_profiles()
            
            logger.info(f"Generated {len(sample_profiles)} sample profiles")
            
            # Insert profiles into PostgreSQL
            profile_objects = []
            profile_dicts = []
            with db.get_session() as session:
                for profile_data in sample_profiles:
                    profile = ARGOProfile(**profile_data)
                    session.add(profile)
                    profile_objects.append(profile)
                    # Convert to dictionary for vector database
                    profile_dict = profile_data.copy()
                    profile_dict['id'] = len(profile_dicts) + 1  # Add an ID
                    profile_dicts.append(profile_dict)
                
                session.commit()
                logger.info(f"SUCCESS: Inserted {len(profile_objects)} profiles into PostgreSQL")
            
            # Add profiles to vector database using dictionaries
            vector_results = vector_db.add_profiles_advanced(profile_dicts)
            
            if vector_results.get("profiles_added", 0) > 0:
                logger.info(f"SUCCESS: Added {vector_results['profiles_added']} profiles to vector database")
                logger.info(f"  Embeddings generated: {vector_results.get('embeddings_generated', 0)}")
                logger.info(f"  Processing time: {vector_results.get('processing_time_seconds', 0):.2f}s")
            else:
                logger.warning("WARNING: Vector database addition had issues")
                if vector_results.get("errors"):
                    for error in vector_results["errors"]:
                        logger.warning(f"  {error}")
            
            # Create processing log entry
            with db.get_session() as session:
                log_entry = DataProcessingLog(
                    operation_type="sample_data_creation",
                    operation_status="success",
                    records_processed=len(sample_profiles),
                    records_accepted=len(profile_objects),
                    records_rejected=0,
                    processing_time_seconds=vector_results.get('processing_time_seconds', 0),
                    processing_parameters=json.dumps({
                        "sample_data_version": "2.0",
                        "profiles_per_region": 10,
                        "quality_range": [3.0, 5.0],
                        "temporal_range": "2023-2024"
                    })
                )
                session.add(log_entry)
                session.commit()
            
            logger.info("SUCCESS: Sample data creation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"FAILED: Sample data creation failed: {str(e)}")
            return False
    
    def _generate_sample_profiles(self) -> list:
        """Generate realistic ARGO sample profiles for each region"""
        
        import random
        from datetime import timedelta
        
        profiles = []
        base_date = datetime(2023, 1, 1)
        
        # Regional characteristics for realistic data generation
        regional_configs = {
            "arabian_sea": {
                "lat_range": (10, 25),
                "lon_range": (55, 75),
                "temp_range": (24, 32),
                "sal_range": (35.0, 37.0),
                "depth_range": (1800, 2200),
                "characteristics": "High salinity, seasonal upwelling"
            },
            "bay_of_bengal": {
                "lat_range": (8, 20),
                "lon_range": (80, 95),
                "temp_range": (26, 31),
                "sal_range": (32.0, 35.0),
                "depth_range": (1600, 2000),
                "characteristics": "Low salinity, river influence"
            },
            "equatorial_indian": {
                "lat_range": (-5, 5),
                "lon_range": (60, 90),
                "temp_range": (26, 29),
                "sal_range": (34.5, 35.5),
                "depth_range": (1700, 2100),
                "characteristics": "Stable temperatures, equatorial currents"
            }
        }
        
        float_id_counter = 1
        
        for region, config in regional_configs.items():
            for i in range(12):  # 12 profiles per region
                # Generate realistic coordinates
                lat = random.uniform(*config["lat_range"])
                lon = random.uniform(*config["lon_range"])
                
                # Generate realistic measurements
                surface_temp = random.uniform(*config["temp_range"])
                surface_sal = random.uniform(*config["sal_range"])
                max_depth = random.uniform(*config["depth_range"])
                
                # Generate profile date (spread over 2 years)
                days_offset = random.randint(0, 730)
                profile_date = base_date + timedelta(days=days_offset)
                
                # Generate quality score (mostly high quality)
                quality_score = random.uniform(3.5, 5.0)
                
                # Generate mixed layer and thermocline depths
                mld = random.uniform(15, 80)
                thermocline = mld + random.uniform(20, 60)
                
                profile_data = {
                    'id': uuid.uuid4(),
                    'float_id': f'SAMPLE_{float_id_counter:03d}',
                    'cycle_number': random.randint(1, 200),
                    'profile_date': profile_date,
                    'latitude': lat,
                    'longitude': lon,
                    'ocean_region': region,
                    'surface_temperature': surface_temp,
                    'surface_salinity': surface_sal,
                    'surface_pressure': random.uniform(0.5, 2.0),
                    'max_depth': max_depth,
                    'num_levels': random.randint(80, 120),
                    'mixed_layer_depth': mld,
                    'thermocline_depth': thermocline,
                    'temperature_range': random.uniform(8, 20),
                    'salinity_range': random.uniform(1.0, 3.0),
                    'data_quality_score': quality_score,
                    'position_accuracy': random.choice(['high', 'standard', 'low']),
                    'processing_level': random.choice(['real_time', 'delayed_mode']),
                    'has_temperature': True,
                    'has_salinity': True,
                    'has_pressure': True,
                    'has_oxygen': random.choice([True, False]),
                    'profile_summary': f'High-quality {region.replace("_", " ")} profile with {config["characteristics"].lower()}',
                    'scientific_summary': f'Representative profile for {region.replace("_", " ")} showing typical {profile_date.strftime("%B")} conditions'
                }
                
                profiles.append(profile_data)
                float_id_counter += 1
        
        return profiles
    
    def _run_integration_tests(self) -> bool:
        """Run comprehensive integration tests"""
        
        logger.info("Running system integration tests...")
        
        test_results = []
        
        # Test 1: Database query performance
        try:
            start_time = datetime.utcnow()
            with db.get_session() as session:
                profile_count = session.query(ARGOProfile).count()
                recent_profiles = session.query(ARGOProfile).filter(
                    ARGOProfile.profile_date > datetime.utcnow() - timedelta(days=365)
                ).count()
            
            query_time = (datetime.utcnow() - start_time).total_seconds()
            
            if query_time < 1.0 and profile_count > 0:
                logger.info(f"SUCCESS: Database query test: {profile_count} profiles, {query_time:.3f}s")
                test_results.append(True)
            else:
                logger.warning(f"WARNING: Database query slow: {query_time:.3f}s")
                test_results.append(False)
                
        except Exception as e:
            logger.error(f"FAILED: Database query test failed: {e}")
            test_results.append(False)
        
        # Test 2: Vector database search
        try:
            test_queries = [
                "Arabian Sea temperature profiles during monsoon",
                "Bay of Bengal salinity data",
                "High quality oceanographic measurements"
            ]
            
            search_times = []
            for query in test_queries:
                start_time = datetime.utcnow()
                results = vector_db.advanced_search(query, n_results=5)
                search_time = (datetime.utcnow() - start_time).total_seconds()
                search_times.append(search_time)
                
                if results.get("results") and search_time < 2.0:
                    logger.info(f"SUCCESS: Vector search: '{query[:30]}...' - {len(results['results'])} results, {search_time:.3f}s")
                else:
                    logger.warning(f"WARNING: Vector search slow or no results: {search_time:.3f}s")
            
            avg_search_time = sum(search_times) / len(search_times)
            test_results.append(avg_search_time < 1.5)
            
        except Exception as e:
            logger.error(f"FAILED: Vector search test failed: {e}")
            test_results.append(False)
        
        # Test 3: Regional classification
        try:
            test_coords = [
                (15.0, 65.0, "arabian_sea"),
                (15.0, 88.0, "bay_of_bengal"),
                (0.0, 80.0, "equatorial_indian")
            ]
            
            classification_correct = 0
            for lat, lon, expected in test_coords:
                result = settings.classify_region(lat, lon)
                if result == expected:
                    classification_correct += 1
                    logger.info(f"SUCCESS: Regional classification: ({lat}, {lon}) -> {result}")
                else:
                    logger.error(f"FAILED: Regional classification failed: ({lat}, {lon}) -> {result} (expected {expected})")
            
            test_results.append(classification_correct == len(test_coords))
            
        except Exception as e:
            logger.error(f"FAILED: Regional classification test failed: {e}")
            test_results.append(False)
        
        # Test 4: Configuration access
        try:
            system_info = settings.get_system_info()
            seasonal_context = settings.get_seasonal_context(6)  # June
            
            config_valid = (
                system_info.get("environment") == settings.ENVIRONMENT and
                seasonal_context.get("season") == "southwest_monsoon"
            )
            
            if config_valid:
                logger.info("SUCCESS: Configuration access test passed")
                test_results.append(True)
            else:
                logger.error("FAILED: Configuration access test failed")
                test_results.append(False)
                
        except Exception as e:
            logger.error(f"FAILED: Configuration test failed: {e}")
            test_results.append(False)
        
        success_rate = sum(test_results) / len(test_results)
        logger.info(f"Integration tests success rate: {success_rate*100:.1f}%")
        
        return success_rate >= 0.75  # Require 75% success rate
    
    def _validate_production_readiness(self) -> bool:
        """Validate system is ready for production deployment"""
        
        logger.info("Validating production readiness...")
        
        readiness_checks = []
        
        # Check database health and performance
        db_health = db.health_check()
        db_ready = (
            db_health.get("database_connected", False) and
            db_health.get("tables_exist", False) and
            db_health.get("performance_acceptable", False)
        )
        
        if db_ready:
            logger.info("SUCCESS: Database production ready")
            readiness_checks.append(True)
        else:
            logger.error("FAILED: Database not production ready")
            readiness_checks.append(False)
        
        # Check vector database health
        vector_health = vector_db.health_check()
        vector_ready = (
            vector_health.get("server_healthy", False) and
            vector_health.get("embedding_model_loaded", False) and
            vector_health.get("search_functional", False)
        )
        
        if vector_ready:
            logger.info("SUCCESS: Vector database production ready")
            readiness_checks.append(True)
        else:
            logger.error("FAILED: Vector database not production ready")
            readiness_checks.append(False)
        
        # Check data availability
        stats = db.get_comprehensive_stats()
        profile_stats = stats.get("profile_statistics", {})
        total_profiles = profile_stats.get("total_profiles", 0)
        
        if total_profiles > 0:
            logger.info(f"SUCCESS: Sample data available: {total_profiles} profiles")
            readiness_checks.append(True)
        else:
            logger.error("FAILED: No sample data available")
            readiness_checks.append(False)
        
        # Check configuration completeness
        critical_configs = [
            bool(settings.DATABASE_URL),
            bool(settings.GOOGLE_API_KEY or settings.OPENAI_API_KEY),
            Path(settings.CHROMA_PATH).exists(),
            Path(settings.SAMPLES_PATH).exists(),
            Path(settings.EXPORTS_PATH).exists()
        ]
        
        config_ready = all(critical_configs)
        if config_ready:
            logger.info("SUCCESS: Configuration complete")
            readiness_checks.append(True)
        else:
            logger.error("FAILED: Configuration incomplete")
            readiness_checks.append(False)
        
        # Overall readiness assessment
        all_ready = all(readiness_checks)
        
        if all_ready:
            logger.info("GREAT SUCCESS: System is PRODUCTION READY!")
        else:
            logger.error("FAILED: System NOT ready for production")
            failed_checks = sum(1 for check in readiness_checks if not check)
            logger.error(f"Failed {failed_checks}/{len(readiness_checks)} readiness checks")
        
        return all_ready
    
    def _run_performance_benchmarks(self) -> bool:
        """Run performance benchmarks for optimization"""
        
        logger.info("Running performance benchmarks...")
        
        benchmarks = {}
        
        try:
            # Database query benchmark
            start_time = datetime.utcnow()
            with db.get_session() as session:
                # Complex query benchmark
                from sqlalchemy import text
                result = session.execute(text("""
                    SELECT 
                        ocean_region,
                        COUNT(*) as profile_count,
                        AVG(surface_temperature) as avg_temp,
                        AVG(data_quality_score) as avg_quality
                    FROM argo_profiles 
                    WHERE data_quality_score >= :threshold
                    GROUP BY ocean_region
                    ORDER BY profile_count DESC
                """), {"threshold": settings.DATA_QUALITY_THRESHOLD}).fetchall()
            
            db_benchmark_time = (datetime.utcnow() - start_time).total_seconds()
            benchmarks["database_complex_query"] = db_benchmark_time
            
            # Vector search benchmark
            start_time = datetime.utcnow()
            search_result = vector_db.advanced_search(
                "Arabian Sea temperature profiles with high quality data",
                n_results=10
            )
            vector_benchmark_time = (datetime.utcnow() - start_time).total_seconds()
            benchmarks["vector_search"] = vector_benchmark_time
            
            # Embedding generation benchmark
            test_texts = [
                "ARGO profile in Arabian Sea with high temperature and salinity",
                "Bay of Bengal oceanographic measurements during monsoon season",
                "Equatorial Indian Ocean water mass analysis with deep profile data"
            ]
            
            start_time = datetime.utcnow()
            embeddings = vector_db.embeddings_model.encode(test_texts)
            embedding_benchmark_time = (datetime.utcnow() - start_time).total_seconds()
            benchmarks["embedding_generation"] = embedding_benchmark_time
            
            # Log benchmark results
            logger.info("Performance Benchmark Results:")
            logger.info(f"  Database complex query: {benchmarks['database_complex_query']:.3f}s")
            logger.info(f"  Vector search: {benchmarks['vector_search']:.3f}s") 
            logger.info(f"  Embedding generation (3 docs): {benchmarks['embedding_generation']:.3f}s")
            
            # Performance assessment
            performance_good = (
                benchmarks["database_complex_query"] < 1.0 and
                benchmarks["vector_search"] < 2.0 and
                benchmarks["embedding_generation"] < 1.0
            )
            
            if performance_good:
                logger.info("SUCCESS: Performance benchmarks within acceptable limits")
            else:
                logger.warning("WARNING: Some performance benchmarks exceed recommended limits")
            
            return True
            
        except Exception as e:
            logger.error(f"FAILED: Performance benchmarks failed: {e}")
            return False
    
    def _generate_setup_summary(self) -> bool:
        """Generate comprehensive setup summary and final status"""
        
        total_time = (datetime.utcnow() - self.start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("PRODUCTION SETUP SUMMARY")
        logger.info("=" * 80)
        
        # Phase results
        successful_phases = sum(1 for step in self.setup_steps if step["status"] == "success")
        total_phases = len(self.setup_steps)
        
        logger.info("PHASE RESULTS:")
        for step in self.setup_steps:
            status_icon = "SUCCESS" if step["status"] == "success" else "FAILED"
            duration = step.get("duration", 0)
            logger.info(f"  {status_icon}: {step['phase']}: {step['status'].upper()} ({duration:.2f}s)")
        
        # System statistics
        try:
            db_stats = db.get_comprehensive_stats()
            vector_stats = vector_db.get_comprehensive_stats()
            
            profile_count = db_stats.get("profile_statistics", {}).get("total_profiles", 0)
            vector_count = vector_stats.get("collection_info", {}).get("total_profiles", 0)
            
            logger.info(f"\nSYSTEM STATISTICS:")
            logger.info(f"  Database Profiles: {profile_count}")
            logger.info(f"  Vector DB Profiles: {vector_count}")
            logger.info(f"  High Quality Profiles: {db_stats.get('profile_statistics', {}).get('high_quality_profiles', 0)}")
            logger.info(f"  Regions Covered: {db_stats.get('profile_statistics', {}).get('regions_covered', 0)}")
            
        except Exception as e:
            logger.warning(f"Could not retrieve final statistics: {e}")
        
        # Warnings and errors summary
        if self.warnings:
            logger.info(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.info(f"  WARNING: {warning}")
        
        if self.errors:
            logger.info(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors:
                logger.info(f"  ERROR: {error}")
        
        # Final assessment
        success_rate = successful_phases / total_phases
        overall_success = success_rate >= 0.8  # 80% success rate required
        
        logger.info(f"\n{'SETUP SUCCESSFUL!' if overall_success else 'SETUP FAILED!'}")
        logger.info(f"Success Rate: {success_rate*100:.1f}% ({successful_phases}/{total_phases} phases)")
        logger.info(f"Total Time: {total_time:.1f} seconds")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        
        if overall_success:
            logger.info("\nNEXT STEPS:")
            logger.info("1. Run 'python app/main.py' to start the application")
            logger.info("2. Visit http://localhost:8501 for the Streamlit dashboard")
            logger.info("3. Visit http://localhost:8000/docs for API documentation")
            logger.info("4. Begin Phase 2 development (AI Agent Core)")
        else:
            logger.info("\nREMEDIATION NEEDED:")
            logger.info("1. Review error messages above")
            logger.info("2. Fix configuration issues")
            logger.info("3. Ensure all services are running (PostgreSQL, ChromaDB)")
            logger.info("4. Re-run setup script")
        
        logger.info("=" * 80)
        
        return overall_success

def main():
    """Main setup execution function"""
    
    setup_manager = ProductionSetupManager()
    
    try:
        success = setup_manager.run_complete_setup()
        
        if success:
            print("\nSETUP COMPLETED SUCCESSFULLY!")
            print("Your Indian Ocean ARGO AI Agent infrastructure is ready for development.")
            return 0
        else:
            print("\nSETUP FAILED!")
            print("Please review the error messages and retry setup.")
            return 1
            
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        return 1
    except Exception as e:
        print(f"\nCRITICAL SETUP ERROR: {str(e)}")
        print("Please check logs for details and contact support if needed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
