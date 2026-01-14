"""
Pydantic Models for AutoStream AI Agent
Defines data structures for intent classification, lead capture, and user interactions.
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class IntentType(str, Enum):
    """User intent classification categories"""
    CASUAL_GREETING = "casual_greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    PRICING_INQUIRY = "pricing_inquiry"
    HIGH_INTENT_LEAD = "high_intent_lead"
    SUPPORT_QUESTION = "support_question"
    UNKNOWN = "unknown"


class UserIntent(BaseModel):
    """Classified user intent with confidence score"""
    intent_type: IntentType
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    reasoning: Optional[str] = Field(None, description="Explanation for the classification")
    
    class Config:
        use_enum_values = True


class LeadData(BaseModel):
    """Lead capture information"""
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    plan_interest: Optional[str] = Field(None, description="Basic or Pro plan")
    timestamp: datetime = Field(default_factory=datetime.now)
    conversation_context: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "creator@example.com",
                "name": "John Doe",
                "plan_interest": "Pro",
                "timestamp": "2026-01-14T10:30:00"
            }
        }


class Message(BaseModel):
    """Individual message in conversation"""
    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    intent: Optional[UserIntent] = None


class ConversationContext(BaseModel):
    """Context tracking for the conversation"""
    messages: List[Message] = Field(default_factory=list)
    current_intent: Optional[IntentType] = None
    lead_captured: bool = False
    lead_data: Optional[LeadData] = None
    
    def add_message(self, role: str, content: str, intent: Optional[UserIntent] = None):
        """Add a message to the conversation history"""
        message = Message(role=role, content=content, intent=intent)
        self.messages.append(message)
        
        if intent:
            self.current_intent = intent.intent_type
    
    def get_recent_context(self, n: int = 5) -> str:
        """Get recent conversation context as a formatted string"""
        recent = self.messages[-n:] if len(self.messages) > n else self.messages
        return "\n".join([f"{msg.role}: {msg.content}" for msg in recent])


class RAGResponse(BaseModel):
    """Response from RAG retrieval"""
    answer: str
    source_documents: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class AgentResponse(BaseModel):
    """Complete agent response"""
    message: str
    intent: UserIntent
    should_capture_lead: bool = False
    lead_capture_prompt: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
