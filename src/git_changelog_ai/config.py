"""
Configuration management for git-changelog-ai.

API keys should be set via environment variables for security.
"""

import os
from typing import Dict, Optional
from .constants import DEFAULT_AI_PROVIDER

# Type definition for AI service config
class AIConfig:
    """AI service configuration"""
    def __init__(self, base_url: str, api_key_env: str, model: str):
        self.base_url = base_url
        self.api_key_env = api_key_env
        self.model = model
    
    @property
    def api_key(self) -> str:
        """Get API key from environment variable"""
        return os.environ.get(self.api_key_env, "")


# AI service configurations
AI_CONFIGS: Dict[str, AIConfig] = {
    'gemini': AIConfig(
        base_url='https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        api_key_env='GOOGLE_API_KEY',
        model='gemini-3-flash-preview'
    ),
    'openai': AIConfig(
        base_url='https://api.openai.com/v1/chat/completions',
        api_key_env='OPENAI_API_KEY',
        model='gpt-4o'
    ),
    'deepseek': AIConfig(
        base_url='https://api.deepseek.com/v1/chat/completions',
        api_key_env='DEEPSEEK_API_KEY',
        model='deepseek-chat'
    )
}


def get_ai_config(provider: str = DEFAULT_AI_PROVIDER) -> Optional[AIConfig]:
    """
    Get AI service configuration.
    
    Args:
        provider: AI service provider name
        
    Returns:
        AIConfig instance or None if provider not found
    """
    return AI_CONFIGS.get(provider)


def get_api_key(provider: str) -> str:
    """
    Get API key for the specified provider from environment variable.
    
    Args:
        provider: AI service provider name
        
    Returns:
        API key string (empty if not configured)
    """
    config = get_ai_config(provider)
    if config:
        return config.api_key
    return ""


def validate_api_key(provider: str) -> bool:
    """
    Check if API key is configured for the provider.
    
    Args:
        provider: AI service provider name
        
    Returns:
        True if API key is configured, False otherwise
    """
    return bool(get_api_key(provider))


def get_available_providers() -> list:
    """
    Get list of available AI providers.
    
    Returns:
        List of provider names
    """
    return list(AI_CONFIGS.keys())
