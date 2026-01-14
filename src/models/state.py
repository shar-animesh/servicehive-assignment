"""
State model for LangGraph workflow.

Defines the state structure that flows through the agent's workflow.
"""

from typing import List, Literal, Optional, TypedDict

from langchain_core.messages import BaseMessage

from src.models.lead import LeadData


# Intent types the agent can detect
IntentType = Literal["greeting", "inquiry", "high_intent_lead"]


class AgentState(TypedDict):
    """
    State object that flows through the LangGraph workflow.
    
    This state is passed between nodes and updated as the conversation
    progresses, maintaining context and tracking the agent's progress.
    """
    
    # Conversation messages
    messages: List[BaseMessage]
    
    # Current detected intent
    current_intent: Optional[IntentType]
    
    # Lead data being collected
    lead_data: LeadData
    
    # Whether lead has been successfully captured
    lead_captured: bool
    
    # Conversation history for memory (last 5-6 turns)
    conversation_history: List[str]
    
    # Retrieved context from RAG
    retrieved_context: Optional[str]
    
    # Next action to take
    next_action: Optional[str]
