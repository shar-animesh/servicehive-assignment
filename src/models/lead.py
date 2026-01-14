"""
Data models for lead capture.

Defines Pydantic models for lead data validation and type safety.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class LeadData(BaseModel):
    """
    Model for lead information collected from users.
    
    Validates all lead data to ensure quality before capture.
    """
    
    name: Optional[str] = Field(
        None,
        description="Lead's full name",
        min_length=2,
        max_length=100
    )
    
    email: Optional[EmailStr] = Field(
        None,
        description="Lead's email address"
    )
    
    platform: Optional[str] = Field(
        None,
        description="Content creation platform (YouTube, Instagram, TikTok, etc.)"
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean the name field."""
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Name must be at least 2 characters")
        return v
    
    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize platform name."""
        if v is not None:
            v = v.strip().title()  # Capitalize properly
            # Common platform names
            platform_mapping = {
                "Youtube": "YouTube",
                "Tiktok": "TikTok",
                "Instagram": "Instagram",
                "Facebook": "Facebook",
                "Twitter": "Twitter",
                "Twitch": "Twitch",
                "Linkedin": "LinkedIn"
            }
            # Try to match common platforms
            for key, value in platform_mapping.items():
                if v.lower() == key.lower():
                    return value
        return v
    
    def is_complete(self) -> bool:
        """
        Check if all required fields are collected.
        
        Returns:
            True if all fields (name, email, platform) are present
        """
        return all([self.name, self.email, self.platform])
    
    def missing_fields(self) -> list[str]:
        """
        Get list of missing required fields.
        
        Returns:
            List of field names that are still None
        """
        missing = []
        if not self.name:
            missing.append("name")
        if not self.email:
            missing.append("email")
        if not self.platform:
            missing.append("platform")
        return missing


class LeadCaptureInput(BaseModel):
    """
    Input model for the lead capture tool.
    
    Used when calling the mock_lead_capture function.
    """
    
    name: str = Field(..., description="Lead's full name")
    email: EmailStr = Field(..., description="Lead's email address")
    platform: str = Field(..., description="Content creation platform")
