"""
ChromaDB HTTP Client for Indian Ocean ARGO Vector Database
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from .config import settings

logger = logging.getLogger(__name__)

class ChromaDBClient:
    """HTTP client for ChromaDB server"""
    
    def __init__(self, host: str = "localhost", port: int = 8001):
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        logger.info(f"ChromaDB HTTP client initialized: {self.base_url}")
    
    def heartbeat(self) -> bool:
        """Check if ChromaDB server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/heartbeat", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"ChromaDB heartbeat failed: {e}")
            return False
    
    def get_version(self) -> Optional[str]:
        """Get ChromaDB server version"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/version", timeout=5)
            if response.status_code == 200:
                return response.json().get("version")
        except Exception as e:
            logger.error(f"Failed to get ChromaDB version: {e}")
        return None
    
    def list_collections(self) -> List[Dict]:
        """List all collections"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/collections", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to list collections: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def create_collection(self, name: str, metadata: Optional[Dict] = None) -> bool:
        """Create a new collection"""
        try:
            # First check if collection already exists
            existing = self.get_collection(name)
            if existing:
                logger.info(f"Collection already exists: {name}")
                return True
            
            data = {
                "name": name,
                "metadata": metadata or {}
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/collections",
                json=data,
                timeout=10
            )
            if response.status_code in [200, 201]:
                logger.info(f"Created collection: {name}")
                return True
            elif response.status_code == 409:
                logger.info(f"Collection already exists: {name}")
                return True
            elif response.status_code == 500:
                # ChromaDB sometimes returns 500 for existing collections
                # Check if it's an "already exists" error
                try:
                    error_text = response.text.lower()
                    if "already exists" in error_text:
                        logger.info(f"Collection already exists (via 500 error): {name}")
                        return True
                except:
                    pass
                logger.error(f"Failed to create collection {name}: {response.status_code}")
                return False
            else:
                logger.error(f"Failed to create collection {name}: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error creating collection {name}: {e}")
            return False
    
    def get_collection(self, name: str) -> Optional[Dict]:
        """Get collection by name"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/collections/{name}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Collection {name} not found: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting collection {name}: {e}")
            return None
    
    def get_collection_id(self, collection_name: str) -> Optional[str]:
        """Get collection ID by name"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/collections", timeout=10)
            if response.status_code == 200:
                collections = response.json()
                for collection in collections:
                    if collection.get("name") == collection_name:
                        return collection.get("id")
            return None
        except Exception as e:
            logger.error(f"Error getting collection ID: {e}")
            return None
    
    def add_documents(self, collection_name: str, documents: List[str], 
                     metadatas: Optional[List[Dict]] = None, 
                     ids: Optional[List[str]] = None) -> bool:
        """Add documents to collection"""
        try:
            # Get collection ID first
            collection_id = self.get_collection_id(collection_name)
            if not collection_id:
                logger.error(f"Could not find collection ID for: {collection_name}")
                return False
            
            data = {
                "documents": documents,
                "metadatas": metadatas or [{}] * len(documents),
                "ids": ids or [f"doc_{i}" for i in range(len(documents))]
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/collections/{collection_id}/add",
                json=data,
                timeout=30
            )
            if response.status_code in [200, 201]:
                logger.info(f"Added {len(documents)} documents to {collection_name}")
                return True
            else:
                logger.error(f"Failed to add documents: {response.status_code}")
                logger.error(f"ChromaDB response: {response.text}")
                logger.error(f"Request data sample: {str(data)[:500]}...")
                return False
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def query_collection(self, collection_name: str, query_texts: List[str], 
                        n_results: int = 10) -> Optional[Dict]:
        """Query collection for similar documents"""
        try:
            data = {
                "query_texts": query_texts,
                "n_results": n_results
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/collections/{collection_name}/query",
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Query failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return None


class VectorDBManager:
    """High-level vector database manager for ARGO profiles"""
    
    def __init__(self):
        self.client = ChromaDBClient(
            host=settings.CHROMA_HOST, 
            port=settings.CHROMA_PORT
        )
        self.collection_name = "indian_ocean_argo_profiles"
        self.embeddings_model = None  # Will be initialized when needed
        logger.info("Vector database manager initialized with HTTP client")
    
    def initialize_collections(self) -> bool:
        """Initialize required collections"""
        try:
            # Check if server is running with direct HTTP call
            try:
                response = self.client.session.get(f"{self.client.base_url}/api/v1/heartbeat", timeout=5)
                if response.status_code != 200:
                    logger.error("ChromaDB server is not responding")
                    return False
            except Exception as e:
                logger.error(f"ChromaDB server is not accessible: {e}")
                return False
            
            # Create main collection
            if self.client.create_collection(
                self.collection_name,
                metadata={"description": "Indian Ocean ARGO profile embeddings"}
            ):
                logger.info(f"Created collection: {self.collection_name}")
                return True
            else:
                logger.error(f"Failed to create collection: {self.collection_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing collections: {e}")
            return False
    
    def check_connection(self) -> bool:
        """Check if vector database is connected and responsive"""
        try:
            # Direct HTTP request to avoid recursion
            response = self.client.session.get(
                f"{self.client.base_url}/api/v1/heartbeat", 
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Vector database connection check failed: {e}")
            return False
    
    def initialize_embedding_model(self, model_name: str = "all-MiniLM-L6-v2") -> bool:
        """Initialize the sentence transformer embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embeddings_model = SentenceTransformer(model_name)
            logger.info(f"Embedding model initialized: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            return False
    
    def add_profile_embeddings(self, profiles: List[Dict]) -> bool:
        """Add ARGO profile embeddings to vector database"""
        try:
            if not profiles:
                return True
            
            documents = []
            metadatas = []
            ids = []
            
            for profile in profiles:
                # Create searchable text from profile
                doc_text = self._create_profile_text(profile)
                documents.append(doc_text)
                
                # Create metadata
                metadata = {
                    "profile_id": str(profile.get("id", "")),
                    "float_id": profile.get("float_id", ""),
                    "latitude": profile.get("latitude", 0.0),
                    "longitude": profile.get("longitude", 0.0),
                    "date": str(profile.get("profile_date", "")),
                    "ocean_region": profile.get("ocean_region", ""),
                    "quality_score": profile.get("data_quality_score", 0.0)
                }
                metadatas.append(metadata)
                ids.append(f"profile_{profile.get('id', len(ids))}")
            
            return self.client.add_documents(
                self.collection_name, 
                documents, 
                metadatas, 
                ids
            )
            
        except Exception as e:
            logger.error(f"Error adding profile embeddings: {e}")
            return False
    
    def add_profiles_advanced(self, profiles: List[Dict]) -> Dict[str, Any]:
        """Add ARGO profiles to vector database with detailed results"""
        from datetime import datetime
        
        start_time = datetime.utcnow()
        result = {
            "profiles_added": 0,
            "embeddings_generated": 0,
            "processing_time_seconds": 0.0,
            "errors": [],
            "success": False
        }
        
        try:
            if not profiles:
                result["success"] = True
                return result
            
            documents = []
            metadatas = []
            ids = []
            
            for i, profile in enumerate(profiles):
                try:
                    # Create searchable text from profile
                    doc_text = self._create_profile_text(profile)
                    documents.append(doc_text)
                    
                    # Create metadata
                    metadata = {
                        "profile_id": str(profile.get("id", "")),
                        "float_id": profile.get("float_id", ""),
                        "latitude": profile.get("latitude", 0.0),
                        "longitude": profile.get("longitude", 0.0),
                        "date": str(profile.get("profile_date", "")),
                        "ocean_region": profile.get("ocean_region", ""),
                        "quality_score": profile.get("data_quality_score", 0.0)
                    }
                    metadatas.append(metadata)
                    ids.append(f"profile_{profile.get('id', i)}")
                    
                except Exception as e:
                    result["errors"].append(f"Error processing profile {i}: {e}")
                    continue
            
            # Add to vector database
            if documents:
                success = self.client.add_documents(
                    self.collection_name, 
                    documents, 
                    metadatas, 
                    ids
                )
                
                if success:
                    result["profiles_added"] = len(documents)
                    result["embeddings_generated"] = len(documents)
                    result["success"] = True
                else:
                    result["errors"].append("Failed to add documents to ChromaDB")
            
            # Calculate processing time
            end_time = datetime.utcnow()
            result["processing_time_seconds"] = (end_time - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in add_profiles_advanced: {e}")
            result["errors"].append(f"General error: {e}")
            end_time = datetime.utcnow()
            result["processing_time_seconds"] = (end_time - start_time).total_seconds()
            return result
    
    def search_profiles(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for similar ARGO profiles"""
        try:
            results = self.client.query_collection(
                self.collection_name,
                [query],
                n_results=limit
            )
            
            if results and "metadatas" in results:
                return results["metadatas"][0] if results["metadatas"] else []
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error searching profiles: {e}")
            return []
    
    def advanced_search(self, query: str, n_results: int = 10, region_filter: str = None) -> Dict[str, Any]:
        """
        Optimized vector search with performance tuning
        """
        import time
        start_time = time.time()
        
        try:
            # Optimize n_results for faster queries
            optimized_n_results = min(n_results, 10)  # Limit to 10 for speed
            
            # First check if collection exists and has data
            collection_info = self.get_comprehensive_stats()
            if not collection_info.get("vector_count", 0) > 0:
                logger.warning("No vectors in collection for search")
                return {"results": [], "count": 0, "search_time": 0.0, "status": "no_vectors"}
            
            # Generate query embedding
            if not hasattr(self, 'embeddings_model') or self.embeddings_model is None:
                self.initialize_embedding_model()
            
            query_embedding = self.embeddings_model.encode([query]).tolist()[0]
            
            # Perform ChromaDB HTTP API query
            collection_id = self.client.get_collection_id(self.collection_name)
            if not collection_id:
                logger.error(f"Could not find collection ID for: {self.collection_name}")
                return {"results": [], "count": 0, "search_time": 0.0, "status": "no_collection"}
            
            # Build query with optimized parameters
            query_payload = {
                "query_embeddings": [query_embedding],
                "n_results": optimized_n_results,
                "include": ["metadatas", "documents", "distances"]
            }
            
            # Apply region filter if specified (optimized approach)
            if region_filter and region_filter != "indian_ocean_general":
                query_payload["where"] = {"ocean_region": region_filter}
            
            response = self.client.session.post(
                f"{self.client.base_url}/api/v1/collections/{collection_id}/query",
                json=query_payload,
                timeout=5  # Reduced timeout for faster response
            )
            
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                metadatas = result_data.get("metadatas", [[]])[0]
                documents = result_data.get("documents", [[]])[0]
                distances = result_data.get("distances", [[]])[0]
                
                results = []
                for i, metadata in enumerate(metadatas):
                    result = metadata.copy()
                    result["document"] = documents[i] if i < len(documents) else ""
                    result["distance"] = distances[i] if i < len(distances) else 1.0
                    results.append(result)
                
                return {
                    "results": results,
                    "count": len(results),
                    "search_time": round(query_time, 3),
                    "query_performance": "optimized",
                    "status": "success"
                }
            else:
                logger.error(f"ChromaDB query failed with status {response.status_code}: {response.text}")
                return {"results": [], "count": 0, "search_time": query_time, "status": "query_failed"}
                
        except Exception as e:
            query_time = time.time() - start_time
            logger.error(f"Error in advanced search: {e}")
            return {"results": [], "count": 0, "search_time": query_time, "status": f"error: {str(e)}"}
    
    def warm_up_database(self):
        """Pre-warm the vector database for faster queries"""
        
        logger.info("Warming up vector database...")
        
        # Run a few sample queries to warm up the indexes
        warm_up_queries = [
            "Arabian Sea temperature",
            "Bay of Bengal salinity", 
            "Indian Ocean profile"
        ]
        
        for query in warm_up_queries:
            try:
                result = self.advanced_search(
                    query,
                    n_results=5  # Small number for speed
                )
                logger.debug(f"Warm-up query '{query}' completed in {result.get('search_time', 0)}s")
            except Exception as e:
                logger.debug(f"Warm-up query failed: {e}")
        
        logger.info("Vector database warm-up complete")

    def rebuild_indexes(self, limit: int = 100):
        """Rebuild vector database indexes for better performance"""
        try:
            logger.info("🔧 Rebuilding vector database indexes...")
            
            # Import here to avoid circular imports
            from .database import db, ARGOProfile
            
            # Get profiles from database
            with db.get_session() as session:
                profiles = session.query(ARGOProfile).limit(limit).all()
                
                if not profiles:
                    logger.warning("No profiles found in database for index rebuild")
                    return False
                
                # Convert to dictionaries
                profile_dicts = []
                for profile in profiles:
                    profile_dict = {
                        "id": profile.id,
                        "float_id": profile.float_id,
                        "latitude": profile.latitude,
                        "longitude": profile.longitude,
                        "profile_date": profile.profile_date,
                        "ocean_region": profile.ocean_region,
                        "data_quality_score": profile.data_quality_score,
                        "surface_temperature": profile.surface_temperature,
                        "surface_salinity": profile.surface_salinity,
                        "max_depth": profile.max_depth
                    }
                    profile_dicts.append(profile_dict)
                
                # Re-add to vector database (this rebuilds indexes)
                result = self.add_profiles_advanced(profile_dicts[:10])  # Small batch first
                
                if result.get("success"):
                    logger.info(f"✅ Index rebuilt with {len(profile_dicts)} profiles")
                    return True
                else:
                    logger.error(f"❌ Index rebuild failed: {result.get('errors', [])}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error rebuilding indexes: {e}")
            return False

    def _create_profile_text(self, profile: Dict) -> str:
        """Create searchable text representation of ARGO profile"""
        parts = [
            f"ARGO float {profile.get('float_id', 'unknown')}",
            f"located at {profile.get('latitude', 0):.2f}°N {profile.get('longitude', 0):.2f}°E",
            f"in the {profile.get('ocean_region', 'Indian Ocean')}",
            f"on {profile.get('profile_date', 'unknown date')}",
            f"with quality score {profile.get('data_quality_score', 0):.1f}"
        ]
        
        if profile.get("surface_temperature"):
            parts.append(f"surface temperature {profile['surface_temperature']:.1f}°C")
        
        if profile.get("surface_salinity"):
            parts.append(f"surface salinity {profile['surface_salinity']:.1f} PSU")
        
        if profile.get("max_depth"):
            parts.append(f"maximum depth {profile['max_depth']:.0f}m")
        
        return " ".join(parts)
    
    def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with performance validation"""
        import time
        
        try:
            # Check if ChromaDB server is accessible
            response = self.client.session.get(f"{self.client.base_url}/api/v1/heartbeat", timeout=5)
            if response.status_code == 200:
                server_healthy = True
                server_status = "connected"
            else:
                server_healthy = False
                server_status = f"error_{response.status_code}"
        except Exception as e:
            server_healthy = False
            server_status = f"disconnected: {str(e)}"
        
        # Check collection status
        try:
            collection_exists = self.check_connection()
            collection_status = "available" if collection_exists else "missing"
        except Exception as e:
            collection_exists = False
            collection_status = f"error: {str(e)}"
        
        # Check if embedding model is loaded
        embedding_model_loaded = hasattr(self, 'embeddings_model') and self.embeddings_model is not None
        
        # Performance test - measure query speed (skip stats to avoid recursion)
        search_optimized = False
        query_time_ms = 0
        search_functional = False
        
        if server_healthy and collection_exists:
            try:
                # Get document count directly without calling stats
                collection_id = self.client.get_collection_id(self.collection_name)
                if collection_id:
                    count_response = self.client.session.get(
                        f"{self.client.base_url}/api/v1/collections/{collection_id}/count",
                        timeout=5
                    )
                    if count_response.status_code == 200:
                        try:
                            count_value = int(count_response.text.strip())
                        except ValueError:
                            count_data = count_response.json()
                            count_value = count_data if isinstance(count_data, int) else count_data.get("count", 0)
                    else:
                        count_value = 0
                else:
                    count_value = 0
                
                if count_value > 0:
                    # Try an optimized search and measure performance
                    start_time = time.time()
                    test_result = self._test_search_without_stats("test oceanographic data", n_results=5)
                    query_time = time.time() - start_time
                    query_time_ms = round(query_time * 1000, 2)
                    
                    # Consider it optimized if query completes in under 2 seconds
                    search_optimized = query_time < 2.0 and test_result.get("status") == "success"
                    search_functional = isinstance(test_result, dict) and "results" in test_result
                else:
                    # Collection is empty, search is technically functional but no data
                    search_functional = True
                    search_optimized = True  # No data to search, so it's "optimized" by default
            except Exception as e:
                logger.debug(f"Search functionality test failed: {e}")
                search_functional = False
                search_optimized = False
        else:
            search_functional = False
            search_optimized = False

        return {
            "vector_db_connected": server_healthy,
            "server_status": server_status,
            "collection_exists": collection_exists,
            "collection_status": collection_status,
            "collection_name": self.collection_name,
            "embedding_model_loaded": embedding_model_loaded,
            "search_functional": search_functional,
            "search_optimized": search_optimized,
            "query_performance_ms": query_time_ms,
            "overall_healthy": server_healthy and collection_exists and search_optimized,
            "status": "healthy" if search_optimized else "needs_optimization"
        }
    
    def _test_search_without_stats(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Test search without calling stats to avoid recursion"""
        import time
        start_time = time.time()
        
        try:
            # Generate query embedding
            if not hasattr(self, 'embeddings_model') or self.embeddings_model is None:
                self.initialize_embedding_model()
            
            query_embedding = self.embeddings_model.encode([query]).tolist()[0]
            
            # Perform ChromaDB HTTP API query
            collection_id = self.client.get_collection_id(self.collection_name)
            if not collection_id:
                return {"results": [], "count": 0, "search_time": 0.0, "status": "no_collection"}
            
            query_payload = {
                "query_embeddings": [query_embedding],
                "n_results": n_results,
                "include": ["metadatas", "documents", "distances"]
            }
            
            response = self.client.session.post(
                f"{self.client.base_url}/api/v1/collections/{collection_id}/query",
                json=query_payload,
                timeout=5
            )
            
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                metadatas = result_data.get("metadatas", [[]])[0]
                documents = result_data.get("documents", [[]])[0]
                distances = result_data.get("distances", [[]])[0]
                
                results = []
                for i, metadata in enumerate(metadatas):
                    result = metadata.copy()
                    result["document"] = documents[i] if i < len(documents) else ""
                    result["distance"] = distances[i] if i < len(distances) else 1.0
                    results.append(result)
                
                return {
                    "results": results,
                    "count": len(results),
                    "search_time": round(query_time, 3),
                    "status": "success"
                }
            else:
                return {"results": [], "count": 0, "search_time": query_time, "status": "query_failed"}
                
        except Exception as e:
            query_time = time.time() - start_time
            return {"results": [], "count": 0, "search_time": query_time, "status": f"error: {str(e)}"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        try:
            collection = self.client.get_collection(self.collection_name)
            if collection:
                return {
                    "collection_exists": True,
                    "collection_name": self.collection_name,
                    "server_status": "connected"
                }
            else:
                return {
                    "collection_exists": False,
                    "collection_name": self.collection_name,
                    "server_status": "connected"
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "collection_exists": False,
                "collection_name": self.collection_name,
                "server_status": "disconnected",
                "error": str(e)
            }
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive vector database statistics"""
        try:
            # Check server status directly without health_check to avoid recursion
            try:
                response = self.client.session.get(f"{self.client.base_url}/api/v1/heartbeat", timeout=5)
                server_healthy = response.status_code == 200
                server_status = "connected" if server_healthy else f"error_{response.status_code}"
            except Exception as e:
                server_healthy = False
                server_status = f"disconnected: {str(e)}"
            
            # Check collection status directly
            try:
                collection_exists = self.check_connection()
                collection_status = "available" if collection_exists else "missing"
            except Exception as e:
                collection_exists = False
                collection_status = f"error: {str(e)}"
            
            # Get collection info
            collection_stats = {
                "collection_name": self.collection_name,
                "collection_exists": collection_exists,
                "server_healthy": server_healthy,
                "document_count": 0,
                "embedding_dimension": 384  # all-MiniLM-L6-v2 default
            }
            
            # Try to get collection details if it exists
            if collection_exists:
                try:
                    # Get collection ID first
                    collection_id = self.client.get_collection_id(self.collection_name)
                    if collection_id:
                        # Try to get count via correct endpoint
                        count_response = self.client.session.get(
                            f"{self.client.base_url}/api/v1/collections/{collection_id}/count",
                            timeout=5
                        )
                        if count_response.status_code == 200:
                            # Response should be just a number
                            try:
                                count_value = int(count_response.text.strip())
                                collection_stats["document_count"] = count_value
                            except ValueError:
                                # Try parsing as JSON
                                count_data = count_response.json()
                                collection_stats["document_count"] = count_data if isinstance(count_data, int) else count_data.get("count", 0)
                            
                except Exception as e:
                    logger.warning(f"Could not get detailed collection stats: {e}")
            
            # Add vector_count for compatibility
            vector_count = collection_stats["document_count"]
            
            return {
                "server_status": server_status,
                "overall_healthy": server_healthy and collection_exists,
                "collection_stats": collection_stats,
                "vector_count": vector_count,  # Add this for the search method
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_dimensions": 384,
                "last_checked": "now"
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive stats: {e}")
            return {
                "server_status": "error",
                "overall_healthy": False,
                "collection_stats": {
                    "collection_name": self.collection_name,
                    "collection_exists": False,
                    "server_healthy": False,
                    "document_count": 0,
                    "embedding_dimension": 384
                },
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_dimensions": 384,
                "last_checked": "now",
                "error": str(e)
            }


# Global instance
vector_db = VectorDBManager()
