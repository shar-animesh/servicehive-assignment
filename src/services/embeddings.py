"""
Embedding service for generating vector embeddings using OpenAI.

This module provides a wrapper around OpenAI's embedding models
for consistent usage throughout the application.
"""

from typing import List

from langchain_openai import OpenAIEmbeddings

from src.config.settings import get_settings


class EmbeddingService:
    """
    Service for generating embeddings using OpenAI.
    
    Wraps the OpenAI embeddings API with proper configuration
    and error handling.
    """
    
    def __init__(self):
        """Initialize the embedding service with settings."""
        self.settings = get_settings()
        self._embeddings = None
    
    @property
    def embeddings(self) -> OpenAIEmbeddings:
        """
        Get or create the OpenAI embeddings instance.
        
        Lazy initialization to avoid creating the embeddings object
        until it's actually needed.
        
        Returns:
            OpenAIEmbeddings: Configured embeddings instance
        """
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                openai_api_key=self.settings.openai_api_key,
                model="text-embedding-3-small"  # cost-effective embedding model
            )
        return self._embeddings
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector for the query
        """
        return self.embeddings.embed_query(text)
