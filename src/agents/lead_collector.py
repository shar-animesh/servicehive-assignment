"""
Lead collector agent.

Manages the process of collecting lead information from users
who show high intent to purchase.
"""

import re
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.settings import get_settings
from src.models.lead import LeadData
from src.utils.prompt_loader import PromptLoader


class LeadCollector:
    """
    Collects lead information step by step.
    
    Tracks which fields have been collected and guides the conversation
    to gather all required information (name, email, platform).
    """
    
    def __init__(self):
        """Initialize the lead collector."""
        self.settings = get_settings()
        self.prompt_loader = PromptLoader()
        
        # Initialize LLM for conversational lead collection
        self.llm = ChatOpenAI(
            model=self.settings.model_name,
            temperature=0.7,  # more conversational
            openai_api_key=self.settings.openai_api_key
        )
    
    def extract_info_from_message(
        self, 
        message: str, 
        current_lead_data: LeadData
    ) -> LeadData:
        """
        Extract lead information from user's message.
        
        Uses pattern matching and heuristics to extract name, email,
        and platform from natural conversation.
        
        Args:
            message: User's message
            current_lead_data: Current state of lead data
            
        Returns:
            Updated lead data
        """
        # Extract email using regex
        if not current_lead_data.email:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, message)
            if email_match:
                current_lead_data.email = email_match.group(0)
        
        # Extract platform mentions
        if not current_lead_data.platform:
            platforms = [
                "YouTube", "Instagram", "TikTok", "Facebook", 
                "Twitter", "Twitch", "LinkedIn"
            ]
            message_lower = message.lower()
            for platform in platforms:
                if platform.lower() in message_lower:
                    current_lead_data.platform = platform
                    break
        
        # Extract name (if it looks like a name and we don't have one yet)
        if not current_lead_data.name:
            # Simple heuristic: if message is short and contains capital letters
            # and no email/platform keywords, might be a name
            words = message.strip().split()
            if 1 <= len(words) <= 4:
                # Check if it looks like a name (starts with capital)
                if all(word[0].isupper() or word.lower() in ['van', 'de', 'von'] 
                       for word in words if word):
                    # Make sure it's not a platform or common phrase
                    common_phrases = ['yes', 'sure', 'ok', 'yeah', 'no', 'thanks']
                    if message.lower() not in common_phrases:
                        current_lead_data.name = message.strip()
        
        return current_lead_data
    
    def generate_collection_message(self, lead_data: LeadData) -> str:
        """
        Generate a message to collect missing lead information.
        
        Args:
            lead_data: Current lead data state
            
        Returns:
            Message asking for next piece of information
        """
        missing = lead_data.missing_fields()
        
        # Load the lead capture prompt
        prompt = self.prompt_loader.load_prompt(
            "lead_capture_prompt.md",
            name=lead_data.name,
            email=lead_data.email,
            platform=lead_data.platform,
            missing_fields=missing
        )
        
        # Generate conversational message
        response = self.llm.invoke([
            SystemMessage(content="You are a friendly assistant collecting lead information."),
            HumanMessage(content=prompt)
        ])
        
        return response.content
    
    def is_ready_for_capture(self, lead_data: LeadData) -> bool:
        """
        Check if all required information has been collected.
        
        Args:
            lead_data: Current lead data
            
        Returns:
            True if ready to call lead capture tool
        """
        return lead_data.is_complete()
