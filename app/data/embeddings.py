"""
Text Embeddings and Vector Processing for Indian Ocean ARGO AI Agent
Handles text embeddings, similarity search, and vector operations
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import json
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class EmbeddingProvider:
    """
    Base class for text embedding providers
    Supports multiple embedding models and providers
    """
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        self.dimension = 384  # Default embedding dimension
        self.initialized = False
        
    async def initialize(self):
        """Initialize embedding provider"""
        try:
            # Try to initialize actual embedding models
            await self._initialize_models()
            self.initialized = True
            logger.info(f"Embedding provider initialized: {self.model_name}")
        except Exception as e:
            logger.warning(f"Embedding provider initialization failed: {e}")
            logger.info("Using fallback embedding generation")
            self.initialized = True
    
    async def _initialize_models(self):
        """Initialize specific embedding models"""
        
        # Try to initialize sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info("Sentence-transformers model loaded successfully")
            return
        except ImportError:
            logger.info("Sentence-transformers not available")
        
        # Try to initialize OpenAI embeddings
        try:
            import openai
            from ..core.config import settings
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
                self.model_name = "text-embedding-ada-002"
                self.dimension = 1536
                logger.info("OpenAI embeddings initialized")
                return
        except ImportError:
            logger.info("OpenAI not available")
        
        # Fallback to simple embeddings
        logger.info("Using fallback embedding generation")
        self.model = None
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Use sentence-transformers if available
            if hasattr(self, 'model') and self.model:
                embedding = self.model.encode(text).tolist()
                return embedding
            
            # Use OpenAI if available
            if hasattr(self, 'openai_client'):
                response = await self.openai_client.Embedding.acreate(
                    input=text,
                    model=self.model_name
                )
                return response['data'][0]['embedding']
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
        
        # Fallback to simple hash-based embeddings
        return self._generate_fallback_embedding(text)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        
        return embeddings
    
    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """Generate simple fallback embeddings based on text hash"""
        
        # Create a deterministic embedding based on text content
        hash_val = hash(text.lower().strip())
        np.random.seed(abs(hash_val) % (2**32))
        
        # Generate normalized random vector
        embedding = np.random.normal(0, 1, self.dimension)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0


class ARGOProfileEmbedder:
    """
    Specialized embedder for ARGO oceanographic profiles
    Converts profile data to searchable text and embeddings
    """
    
    def __init__(self):
        self.embedding_provider = EmbeddingProvider()
        self.logger = logger
        
    async def initialize(self):
        """Initialize ARGO profile embedder"""
        await self.embedding_provider.initialize()
        logger.info("ARGO profile embedder initialized")
    
    def profile_to_text(self, profile: Dict[str, Any]) -> str:
        """Convert ARGO profile to searchable text description"""
        
        try:
            # Extract key information
            region = profile.get('ocean_region', 'Unknown region')
            lat = profile.get('latitude', 0)
            lon = profile.get('longitude', 0)
            date = profile.get('profile_date', 'Unknown date')
            
            # Oceanographic parameters
            temp = profile.get('surface_temperature')
            salinity = profile.get('surface_salinity')
            depth = profile.get('max_depth')
            mixed_layer = profile.get('mixed_layer_depth')
            
            # Build descriptive text
            text_parts = [
                f"ARGO oceanographic profile from {region}",
                f"Location: {lat:.2f}°N, {lon:.2f}°E",
                f"Date: {date}"
            ]
            
            if temp is not None:
                text_parts.append(f"Surface temperature: {temp:.1f} degrees Celsius")
            
            if salinity is not None:
                text_parts.append(f"Surface salinity: {salinity:.1f} PSU")
            
            if depth is not None:
                text_parts.append(f"Maximum depth: {depth:.0f} meters")
            
            if mixed_layer is not None:
                text_parts.append(f"Mixed layer depth: {mixed_layer:.0f} meters")
            
            # Add regional context
            if "Arabian Sea" in region:
                text_parts.append("Arabian Sea oceanographic conditions")
            elif "Bay of Bengal" in region:
                text_parts.append("Bay of Bengal oceanographic conditions")
            elif "Equatorial" in region:
                text_parts.append("Equatorial Indian Ocean conditions")
            
            # Add parameter ranges and characteristics
            temp_range = profile.get('temperature_range')
            if temp_range:
                text_parts.append(f"Temperature variation: {temp_range:.1f} degrees")
            
            salinity_range = profile.get('salinity_range')
            if salinity_range:
                text_parts.append(f"Salinity variation: {salinity_range:.1f} PSU")
            
            return ". ".join(text_parts) + "."
            
        except Exception as e:
            logger.error(f"Profile to text conversion failed: {e}")
            return f"ARGO profile data from {profile.get('ocean_region', 'Indian Ocean')}"
    
    async def embed_profile(self, profile: Dict[str, Any]) -> Tuple[str, List[float]]:
        """Convert profile to text and embedding"""
        
        text = self.profile_to_text(profile)
        embedding = await self.embedding_provider.embed_text(text)
        
        return text, embedding
    
    async def embed_profiles(self, profiles: List[Dict[str, Any]]) -> List[Tuple[str, List[float]]]:
        """Embed multiple profiles"""
        
        results = []
        for profile in profiles:
            text, embedding = await self.embed_profile(profile)
            results.append((text, embedding))
        
        return results
    
    async def find_similar_profiles(self, query_text: str, profile_embeddings: List[Tuple[str, List[float]]], top_k: int = 5) -> List[Tuple[str, float]]:
        """Find profiles most similar to query text"""
        
        query_embedding = await self.embedding_provider.embed_text(query_text)
        
        similarities = []
        for text, embedding in profile_embeddings:
            similarity = self.embedding_provider.cosine_similarity(query_embedding, embedding)
            similarities.append((text, similarity))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


class VectorStore:
    """
    In-memory vector store for ARGO profile embeddings
    Provides fast similarity search capabilities
    """
    
    def __init__(self):
        self.embeddings: List[List[float]] = []
        self.texts: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.embedding_provider = EmbeddingProvider()
        self.initialized = False
        
    async def initialize(self):
        """Initialize vector store"""
        await self.embedding_provider.initialize()
        self.initialized = True
        logger.info("Vector store initialized")
    
    async def add_documents(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        """Add documents to vector store"""
        
        if not self.initialized:
            await self.initialize()
        
        # Generate embeddings
        embeddings = await self.embedding_provider.embed_texts(texts)
        
        # Add to store
        self.texts.extend(texts)
        self.embeddings.extend(embeddings)
        
        if metadatas:
            self.metadata.extend(metadatas)
        else:
            self.metadata.extend([{} for _ in texts])
        
        logger.info(f"Added {len(texts)} documents to vector store")
    
    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        
        if not self.initialized:
            await self.initialize()
        
        if not self.embeddings:
            return []
        
        # Generate query embedding
        query_embedding = await self.embedding_provider.embed_text(query)
        
        # Calculate similarities
        similarities = []
        for i, embedding in enumerate(self.embeddings):
            similarity = self.embedding_provider.cosine_similarity(query_embedding, embedding)
            similarities.append((i, similarity))
        
        # Sort and get top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for i, score in similarities[:k]:
            result = {
                "text": self.texts[i],
                "score": score,
                "metadata": self.metadata[i]
            }
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_documents": len(self.texts),
            "embedding_dimension": self.embedding_provider.dimension,
            "model_name": self.embedding_provider.model_name
        }


class ARGOEmbeddingManager:
    """
    Complete embedding management system for ARGO data
    Coordinates profile embedding, storage, and retrieval
    """
    
    def __init__(self):
        self.profile_embedder = ARGOProfileEmbedder()
        self.vector_store = VectorStore()
        self.chromadb_client = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize embedding manager"""
        
        await self.profile_embedder.initialize()
        await self.vector_store.initialize()
        
        # Try to connect to ChromaDB
        try:
            from ..core.vector_db import vector_db
            self.chromadb_client = vector_db
            logger.info("ChromaDB client connected for embeddings")
        except Exception as e:
            logger.warning(f"ChromaDB connection failed: {e}")
        
        self.initialized = True
        logger.info("ARGO embedding manager initialized")
    
    async def process_profiles(self, profiles: List[Dict[str, Any]]) -> bool:
        """Process and store embeddings for ARGO profiles"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Generate embeddings
            profile_embeddings = await self.profile_embedder.embed_profiles(profiles)
            
            # Prepare documents for vector store
            texts = [text for text, _ in profile_embeddings]
            embeddings = [embedding for _, embedding in profile_embeddings]
            metadatas = [{"profile_id": p.get("id", f"profile_{i}")} for i, p in enumerate(profiles)]
            
            # Store in local vector store
            await self.vector_store.add_documents(texts, metadatas)
            
            # Try to store in ChromaDB if available
            if self.chromadb_client:
                try:
                    await self._store_in_chromadb(texts, embeddings, metadatas)
                except Exception as e:
                    logger.error(f"ChromaDB storage failed: {e}")
            
            logger.info(f"Processed embeddings for {len(profiles)} profiles")
            return True
            
        except Exception as e:
            logger.error(f"Profile embedding processing failed: {e}")
            return False
    
    async def search_profiles(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant profiles using embeddings"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Search in local vector store
            results = await self.vector_store.search(query, k)
            
            # Try ChromaDB search if available
            if self.chromadb_client and hasattr(self.chromadb_client, 'search'):
                try:
                    chromadb_results = await self.chromadb_client.search(
                        collection_name="argo_profiles",
                        query_text=query,
                        n_results=k
                    )
                    
                    # Merge results if available
                    if chromadb_results:
                        logger.info("Using ChromaDB search results")
                        return self._format_chromadb_results(chromadb_results)
                        
                except Exception as e:
                    logger.error(f"ChromaDB search failed: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Profile search failed: {e}")
            return []
    
    async def _store_in_chromadb(self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Store embeddings in ChromaDB"""
        
        if self.chromadb_client and hasattr(self.chromadb_client, 'add_documents'):
            await self.chromadb_client.add_documents(
                collection_name="argo_profiles",
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
    
    def _format_chromadb_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format ChromaDB results to standard format"""
        
        formatted_results = []
        documents = results.get('documents', [[]])
        distances = results.get('distances', [[]])
        metadatas = results.get('metadatas', [[]])
        
        if documents and documents[0]:
            for i, doc in enumerate(documents[0]):
                result = {
                    "text": doc,
                    "score": 1.0 - distances[0][i] if distances and distances[0] else 0.5,
                    "metadata": metadatas[0][i] if metadatas and metadatas[0] else {}
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_status(self) -> Dict[str, Any]:
        """Get embedding system status"""
        
        return {
            "initialized": self.initialized,
            "vector_store_stats": self.vector_store.get_stats() if self.initialized else {},
            "chromadb_connected": self.chromadb_client is not None,
            "total_embeddings": len(self.vector_store.embeddings) if self.initialized else 0
        }


# Global embedding manager instance
embedding_manager = ARGOEmbeddingManager()

# Convenience functions for external use
async def process_argo_embeddings(profiles: List[Dict[str, Any]]) -> bool:
    """Process and store embeddings for ARGO profiles"""
    return await embedding_manager.process_profiles(profiles)

async def search_argo_embeddings(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search for relevant ARGO profiles using embeddings"""
    return await embedding_manager.search_profiles(query, k)
