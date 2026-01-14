"""
Mock lead capture tool.

Implements the mock_lead_capture function as specified in the assignment.
"""

from langchain.tools import tool

from src.models.lead import LeadCaptureInput


def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Mock function to capture lead information.
    
    This function simulates lead capture by printing the information
    to the console, as specified in the assignment requirements.
    
    Args:
        name: Lead's full name
        email: Lead's email address
        platform: Content creation platform (YouTube, Instagram, etc.)
        
    Returns:
        Success message confirming lead capture
    """
    # Print to console as required by assignment
    print(f"Lead captured successfully: {name}, {email}, {platform}")
    
    # Return success message for the agent
    return f"✅ Lead captured successfully! Welcome aboard, {name}! We'll reach out to you at {email} soon."


@tool
def lead_capture_tool(name: str, email: str, platform: str) -> str:
    """
    LangChain tool wrapper for mock_lead_capture.
    
    This tool is called by the agent when all lead information
    has been collected and validated.
    
    Args:
        name: Lead's full name
        email: Lead's email address  
        platform: Content creation platform
        
    Returns:
        Success message from mock_lead_capture
    """
    return mock_lead_capture(name, email, platform)
