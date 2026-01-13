"""
Embeddings Module - Handles text embeddings using Sentence Transformers
"""
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.config import settings


class EmbeddingEngine:
    """
    Embedding engine using Sentence Transformers
    """
    
    _instance: Optional['EmbeddingEngine'] = None
    _model: Optional[SentenceTransformer] = None
    
    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        print(f"🔄 Loading embedding model: {settings.embedding_model}")
        self._model = SentenceTransformer(settings.embedding_model)
        print(f"✅ Embedding model loaded successfully")
    
    @property
    def model(self) -> SentenceTransformer:
        """Get the embedding model"""
        if self._model is None:
            self._load_model()
        return self._model
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            batch_size: Batch size for encoding
            
        Returns:
            Array of embedding vectors
        """
        embeddings = self.model.encode(
            texts, 
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def compute_similarity(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def compute_batch_similarity(
        self, 
        query_embedding: np.ndarray, 
        corpus_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute similarity between a query and multiple documents
        
        Args:
            query_embedding: Query embedding vector
            corpus_embeddings: Array of document embeddings
            
        Returns:
            Array of similarity scores
        """
        # Normalize query
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        
        # Normalize corpus
        corpus_norms = np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)
        corpus_normalized = corpus_embeddings / corpus_norms
        
        # Compute similarities
        similarities = np.dot(corpus_normalized, query_norm)
        
        return similarities


# Singleton instance
def get_embedding_engine() -> EmbeddingEngine:
    """Get embedding engine instance"""
    return EmbeddingEngine()
