"""
Vector store manager for ChromaDB integration.

Handles document loading, chunking, embedding, and retrieval
using ChromaDB as the vector database.
"""

import os
from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.config.settings import get_settings
from src.services.embeddings import EmbeddingService


class VectorStoreManager:
    """
    Manages the vector store for RAG-based retrieval.
    
    Handles loading documents from the knowledge base, splitting them
    into chunks, generating embeddings, and storing in ChromaDB.
    """
    
    def __init__(self):
        """Initialize the vector store manager."""
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()
        self._vector_store: Optional[Chroma] = None
        
        # Text splitter configuration for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # reasonable chunk size for context
            chunk_overlap=200,  # overlap to maintain context between chunks
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents(self) -> List[Document]:
        """
        Load all markdown documents from the knowledge base directory.
        
        Returns:
            List of loaded documents
        """
        kb_path = self.settings.knowledge_base_path
        
        # Check if knowledge base directory exists
        if not os.path.exists(kb_path):
            raise FileNotFoundError(
                f"Knowledge base directory not found: {kb_path}"
            )
        
        # Load all markdown files from the knowledge base
        loader = DirectoryLoader(
            kb_path,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        documents = loader.load()
        
        if not documents:
            raise ValueError(
                f"No documents found in knowledge base: {kb_path}"
            )
        
        print(f"Loaded {len(documents)} documents from knowledge base")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of document chunks
        """
        chunks = self.text_splitter.split_documents(documents)
        print(f"Split documents into {len(chunks)} chunks")
        return chunks
    
    def initialize_vector_store(self, force_reload: bool = False) -> Chroma:
        """
        Initialize or load the ChromaDB vector store.
        
        Args:
            force_reload: If True, reload documents even if store exists
            
        Returns:
            Initialized ChromaDB vector store
        """
        db_path = self.settings.chroma_db_path
        
        # Create directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Check if vector store already exists and we're not forcing reload
        if not force_reload and os.path.exists(os.path.join(db_path, "chroma.sqlite3")):
            print("Loading existing vector store...")
            self._vector_store = Chroma(
                persist_directory=db_path,
                embedding_function=self.embedding_service.embeddings
            )
        else:
            print("Creating new vector store...")
            # Load and process documents
            documents = self.load_documents()
            chunks = self.split_documents(documents)
            
            # Create vector store with embeddings
            self._vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding_service.embeddings,
                persist_directory=db_path
            )
            print("Vector store created and persisted")
        
        return self._vector_store
    
    @property
    def vector_store(self) -> Chroma:
        """
        Get the vector store instance, initializing if necessary.
        
        Returns:
            ChromaDB vector store
        """
        if self._vector_store is None:
            self.initialize_vector_store()
        return self._vector_store
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 4
    ) -> List[Document]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        return self.vector_store.similarity_search(query, k=k)
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 4
    ) -> List[tuple[Document, float]]:
        """
        Search for documents with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        return self.vector_store.similarity_search_with_score(query, k=k)
