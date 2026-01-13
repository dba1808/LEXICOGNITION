"""
Vector Store Module - FAISS-based vector database
"""
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss

from backend.config import settings
from backend.pdf_processor import PDFChunk
from backend.embeddings import get_embedding_engine


class FAISSVectorStore:
    """
    FAISS Vector Store for document retrieval
    """
    
    def __init__(self, session_id: str):
        """
        Initialize vector store for a session
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.embedding_engine = get_embedding_engine()
        
        # FAISS index
        self.index: Optional[faiss.Index] = None
        
        # Metadata storage
        self.chunks: List[PDFChunk] = []
        self.chunk_texts: List[str] = []
        
        # Storage paths
        self.store_dir = settings.vector_db_dir / session_id
        self.index_path = self.store_dir / "faiss.index"
        self.metadata_path = self.store_dir / "metadata.pkl"
    
    def create_index(self, chunks: List[PDFChunk]) -> None:
        """
        Create FAISS index from PDF chunks
        
        Args:
            chunks: List of PDFChunk objects
        """
        if not chunks:
            raise ValueError("No chunks provided for indexing")
        
        self.chunks = chunks
        self.chunk_texts = [chunk.content for chunk in chunks]
        
        # Generate embeddings
        print(f"🔄 Generating embeddings for {len(chunks)} chunks...")
        embeddings = self.embedding_engine.embed_texts(self.chunk_texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        
        # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        print(f"✅ Created FAISS index with {self.index.ntotal} vectors")
        
        # Save index
        self._save()
    
    def search(
        self, 
        query: str, 
        top_k: int = None
    ) -> List[Tuple[PDFChunk, float]]:
        """
        Search for similar chunks
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (chunk, score) tuples
        """
        if self.index is None:
            self._load()
        
        if self.index is None or self.index.ntotal == 0:
            return []
        
        top_k = top_k or settings.top_k_retrieval
        top_k = min(top_k, self.index.ntotal)
        
        # Generate query embedding
        query_embedding = self.embedding_engine.embed_text(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Build results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def get_context(self, query: str, top_k: int = None) -> str:
        """
        Get retrieved context as a formatted string
        
        Args:
            query: Search query
            top_k: Number of chunks to retrieve
            
        Returns:
            Formatted context string
        """
        results = self.search(query, top_k)
        
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for i, (chunk, score) in enumerate(results, 1):
            context_parts.append(
                f"[Context {i}] (Page {chunk.page_number}, Relevance: {score:.2f})\n"
                f"{chunk.content}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def _save(self) -> None:
        """Save index and metadata to disk"""
        self.store_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        
        # Save metadata
        metadata = {
            "chunks": self.chunks,
            "chunk_texts": self.chunk_texts
        }
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"💾 Saved vector store to {self.store_dir}")
    
    def _load(self) -> bool:
        """Load index and metadata from disk"""
        if not self.index_path.exists() or not self.metadata_path.exists():
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            self.chunks = metadata["chunks"]
            self.chunk_texts = metadata["chunk_texts"]
            
            print(f"📂 Loaded vector store from {self.store_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            return False
    
    def exists(self) -> bool:
        """Check if index exists on disk"""
        return self.index_path.exists() and self.metadata_path.exists()
    
    def delete(self) -> None:
        """Delete stored index"""
        import shutil
        if self.store_dir.exists():
            shutil.rmtree(self.store_dir)
            print(f"🗑️ Deleted vector store: {self.store_dir}")


class VectorStoreManager:
    """
    Manager for multiple vector store sessions
    """
    
    _stores: Dict[str, FAISSVectorStore] = {}
    
    @classmethod
    def get_store(cls, session_id: str) -> FAISSVectorStore:
        """Get or create a vector store for a session"""
        if session_id not in cls._stores:
            cls._stores[session_id] = FAISSVectorStore(session_id)
        return cls._stores[session_id]
    
    @classmethod
    def delete_store(cls, session_id: str) -> None:
        """Delete a vector store"""
        if session_id in cls._stores:
            cls._stores[session_id].delete()
            del cls._stores[session_id]


# Factory function
def get_vector_store(session_id: str) -> FAISSVectorStore:
    """Get vector store for a session"""
    return VectorStoreManager.get_store(session_id)
