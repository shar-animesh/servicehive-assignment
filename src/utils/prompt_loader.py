"""
Utility for loading and rendering Jinja2 prompt templates.

This module provides functionality to load prompt templates from
markdown files and render them with dynamic variables.
"""

import os
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, Template

from src.config.settings import get_settings


class PromptLoader:
    """
    Loads and renders Jinja2 prompt templates from markdown files.
    
    Provides a clean interface for managing prompts separately from code,
    allowing easy updates and maintenance of prompt templates.
    """
    
    def __init__(self):
        """Initialize the prompt loader with settings."""
        self.settings = get_settings()
        self.prompts_path = self.settings.prompts_path
        
        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.prompts_path),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def load_template(self, template_name: str) -> Template:
        """
        Load a Jinja2 template by name.
        
        Args:
            template_name: Name of the template file (e.g., 'system_prompt.md')
            
        Returns:
            Jinja2 Template object
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = os.path.join(self.prompts_path, template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(
                f"Prompt template not found: {template_path}"
            )
        
        return self.env.get_template(template_name)
    
    def render(
        self, 
        template_name: str, 
        variables: Dict[str, Any] = None
    ) -> str:
        """
        Load and render a template with the given variables.
        
        Args:
            template_name: Name of the template file
            variables: Dictionary of variables to render in the template
            
        Returns:
            Rendered template as a string
        """
        template = self.load_template(template_name)
        variables = variables or {}
        return template.render(**variables)
    
    def load_prompt(self, template_name: str, **kwargs) -> str:
        """
        Convenience method to load and render a prompt.
        
        Args:
            template_name: Name of the template file
            **kwargs: Variables to pass to the template
            
        Returns:
            Rendered prompt string
        """
        return self.render(template_name, kwargs)
