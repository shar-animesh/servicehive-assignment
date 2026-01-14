"""
Lead capture tool using Resend to send emails to admins.
"""

import resend
from langchain.tools import tool

from src.config.settings import get_settings


def lead_capture(name: str, email: str, platform: str) -> str:
    """
    Capture lead information and send email notification to admins.
    
    Args:
        name: Lead's full name
        email: Lead's email address
        platform: Content creation platform (YouTube, Instagram, etc.)
        
    Returns:
        Success message confirming lead capture
    """
    settings = get_settings()
    
    # Set Resend API key
    resend.api_key = settings.resend_api_key
    
    # Prepare email content
    subject = f"🎯 New Lead: {name} from {platform}"
    html_content = f"""
    <html>
        <body>
            <h2>New Lead Captured from AutoStream Agent</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Platform:</strong> {platform}</p>
            <hr>
            <p>This lead was captured automatically by the AutoStream AI agent.</p>
        </body>
    </html>
    """
    
    try:
        # Send email to all admin emails
        params = {
            "from": settings.from_email,
            "to": settings.get_admin_email_list(),
            "subject": subject,
            "html": html_content,
        }
        
        resend.Emails.send(params)
        
        # Log successful capture
        print(f"✅ Lead captured: {name} ({email}) - {platform}")
        
        return f"Thank you, {name}! 🎉 Your information has been received. Our team will reach out to you at {email} shortly to help you get started with AutoStream!"
        
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error sending lead email: {str(e)}")
        return f"Thank you for your interest, {name}! We've noted your details and will be in touch soon."


@tool
def lead_capture_tool(name: str, email: str, platform: str) -> str:
    """
    LangChain tool wrapper for lead_capture.
    
    Use this tool when you have collected all required lead information:
    - name: Lead's full name
    - email: Lead's email address  
    - platform: Content creation platform (YouTube, Instagram, TikTok, etc.)
    
    Args:
        name: Lead's full name
        email: Lead's email address  
        platform: Content creation platform
        
    Returns:
        Success message from lead_capture
    """
    return lead_capture(name, email, platform)
