"""
Intent detection agent.

Classifies user messages into intent categories to route the conversation.
"""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from src.config.settings import get_settings
from src.models.state import IntentType
from src.utils.prompt_loader import PromptLoader


class IntentClassification(BaseModel):
    """Structured output for intent classification."""
    intent: IntentType


class IntentDetector:
    """
    Detects user intent from their messages.
    
    Uses an LLM with structured output to classify messages into
    greeting, inquiry, or high_intent_lead categories.
    """
    
    def __init__(self):
        """Initialize the intent detector."""
        self.settings = get_settings()
        self.prompt_loader = PromptLoader()
        
        # Initialize LLM with structured output
        self.llm = ChatOpenAI(
            model=self.settings.model_name,
            temperature=0,  # deterministic for intent classification
            openai_api_key=self.settings.openai_api_key
        ).with_structured_output(IntentClassification)
    
    def detect_intent(self, user_message: str) -> IntentType:
        """
        Detect the intent of a user message.
        
        Args:
            user_message: The user's message to classify
            
        Returns:
            Detected intent type (greeting, inquiry, or high_intent_lead)
        """
        # Load the intent classification prompt
        prompt = self.prompt_loader.load_prompt(
            "intent_classifier.md",
            user_message=user_message
        )
        
        # Get structured classification from LLM
        result = self.llm.invoke([
            SystemMessage(content="You are an expert at classifying user intent."),
            HumanMessage(content=prompt)
        ])
        
        return result.intent
