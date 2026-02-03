"""
Vector search service for semantic similarity (Module 15)
Provides embedding generation and similarity search for help center articles.
"""
from typing import List, Optional, Tuple
import hashlib
import json


class VectorSearchService:
    """
    Semantic search using embeddings.
    
    Production Integration Points:
    - OpenAI Embeddings API (text-embedding-3-small)
    - PostgreSQL pgvector extension
    - Pinecone/Weaviate vector database
    
    Current Implementation: Mock service with keyword-based fallback
    """
    
    def __init__(self):
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text.
        
        Production:
            import openai
            response = openai.Embedding.create(
                model="text-embedding-3-small",
                input=text
            )
            return response['data'][0]['embedding']
        
        Mock: Generate deterministic vector from text hash
        """
        # Mock implementation - deterministic based on text content
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        
        # Generate normalized vector
        vector = []
        for i in range(self.embedding_dimension):
            val = ((seed + i * 7919) % 10000) / 10000.0 - 0.5
            vector.append(val)
        
        # Normalize
        magnitude = sum(x**2 for x in vector) ** 0.5
        return [x / magnitude for x in vector] if magnitude > 0 else vector
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(x**2 for x in vec1) ** 0.5
        mag2 = sum(x**2 for x in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def search_similar(
        self,
        query_embedding: List[float],
        article_embeddings: List[Tuple[str, List[float]]],  # [(article_id, embedding)]
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        Search for similar articles using cosine similarity.
        
        Production with pgvector:
            SELECT article_id, 
                   1 - (embedding_vector <=> %s) AS similarity
            FROM article_search_indexes
            WHERE 1 - (embedding_vector <=> %s) > %s
            ORDER BY embedding_vector <=> %s
            LIMIT %s
        
        Returns: List of (article_id, similarity_score) sorted by relevance
        """
        results = []
        
        for article_id, embedding in article_embeddings:
            similarity = self.cosine_similarity(query_embedding, embedding)
            if similarity >= threshold:
                results.append((article_id, similarity))
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    def is_available(self) -> bool:
        """
        Check if vector search is available.
        
        Production: Check API key and service availability
        Mock: Always return True for keyword fallback
        """
        return True
    
    def get_embedding_info(self) -> dict:
        """Get embedding service configuration"""
        return {
            "service": "mock",
            "model": "deterministic-hash-based",
            "dimension": self.embedding_dimension,
            "production_ready": False,
            "recommended_providers": [
                "OpenAI text-embedding-3-small",
                "PostgreSQL pgvector",
                "Pinecone",
                "Weaviate"
            ]
        }


# Singleton instance
vector_search_service = VectorSearchService()
