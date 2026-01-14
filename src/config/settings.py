"""
Application settings using Pydantic Settings.

This module loads environment variables and provides a cached settings object
for use throughout the application.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic for validation and type safety. Settings are cached
    using lru_cache to avoid repeated file reads.
    """
    
    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for LLM and embeddings"
    )
    
    # Model Configuration
    model_name: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use for the agent"
    )
    
    # ChromaDB Configuration
    chroma_db_path: str = Field(
        default="./data/chroma_db",
        description="Path to ChromaDB persistent storage"
    )
    
    # Knowledge Base Configuration
    knowledge_base_path: str = Field(
        default="./knowledge_base",
        description="Path to knowledge base documents"
    )
    
    # Prompts Configuration
    prompts_path: str = Field(
        default="./prompts",
        description="Path to prompt template files"
    )
    
    # Lead Capture Configuration
    resend_api_key: str = Field(
        ...,
        description="Resend API key for sending emails"
    )
    
    admin_emails: str = Field(
        ...,
        description="Comma-separated list of admin emails for lead notifications"
    )
    
    from_email: str = Field(
        default="AutoStream Agent <onboarding@resend.dev>",
        description="From email address for lead notifications"
    )
    
    def get_admin_email_list(self) -> list[str]:
        """Parse admin emails into a list."""
        return [email.strip() for email in self.admin_emails.split(",") if email.strip()]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("openai_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that API key is not empty."""
        if not v or v.strip() == "":
            raise ValueError("OpenAI API key cannot be empty")
        return v
    
    @field_validator("chroma_db_path", "knowledge_base_path", "prompts_path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Ensure paths use forward slashes for consistency."""
        return v.replace("\\", "/")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses LRU cache to ensure settings are only loaded once,
    improving performance and consistency.
    
    Returns:
        Settings: Cached settings object
    """
    return Settings()
