"""
RAG retriever agent.

Retrieves relevant information from the knowledge base and generates
accurate answers using the retrieved context.
"""

from typing import List

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.settings import get_settings
from src.services.vector_store import VectorStoreManager
from src.utils.prompt_loader import PromptLoader


class RAGRetriever:
    """
    Retrieves information from knowledge base and generates answers.
    
    Uses vector similarity search to find relevant context, then
    generates accurate answers using an LLM.
    """
    
    def __init__(self):
        """Initialize the RAG retriever."""
        self.settings = get_settings()
        self.vector_store_manager = VectorStoreManager()
        self.prompt_loader = PromptLoader()
        
        # Initialize LLM for answer generation
        self.llm = ChatOpenAI(
            model=self.settings.model_name,
            temperature=0.3,  # slightly creative but mostly factual
            openai_api_key=self.settings.openai_api_key
        )
    
    def retrieve_context(self, query: str, k: int = 4) -> str:
        """
        Retrieve relevant context from the knowledge base.
        
        Args:
            query: User's question
            k: Number of documents to retrieve
            
        Returns:
            Formatted context string
        """
        # Search for relevant documents
        docs = self.vector_store_manager.similarity_search(query, k=k)
        
        # Format the context
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"--- Context {i} ---\n{doc.page_content}\n")
        
        return "\n".join(context_parts)
    
    def generate_answer(self, user_question: str, context: str) -> str:
        """
        Generate an answer using retrieved context.
        
        Args:
            user_question: The user's question
            context: Retrieved context from knowledge base
            
        Returns:
            Generated answer
        """
        # Load the RAG prompt template
        prompt = self.prompt_loader.load_prompt(
            "rag_prompt.md",
            user_question=user_question,
            context=context
        )
        
        # Generate answer using LLM
        response = self.llm.invoke([
            SystemMessage(content="You are a helpful assistant for AutoStream."),
            HumanMessage(content=prompt)
        ])
        
        return response.content
    
    def answer_question(self, question: str) -> tuple[str, str]:
        """
        Complete RAG pipeline: retrieve context and generate answer.
        
        Args:
            question: User's question
            
        Returns:
            Tuple of (answer, context_used)
        """
        # Retrieve relevant context
        context = self.retrieve_context(question)
        
        # Generate answer
        answer = self.generate_answer(question, context)
        
        return answer, context
